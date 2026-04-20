"""
================================================================================
  GitHub Pull Request Scraper — Race Condition / Concurrency PRs
  Version 2.0 — Bug-fixed release
================================================================================
  Purpose : Fetch and deeply filter JavaScript PRs related to concurrency /
            race-condition issues from the GitHub Search API, then export
            all qualifying PRs to paginated CSV files.

  BUGS FIXED vs v1.0
  ------------------
  Bug 1 (critical): Removed stars:>= from the /search/issues query.
      The `stars:` qualifier is only valid in /search/repositories.
      When passed to /search/issues it silently kills the result set or
      triggers a 422 error, which is why v1 returned 0 PRs.
      Stars are now filtered AFTER fetching repo metadata (see main()).

  Bug 2: Fixed the PR diff fetch.
      v1 called github.com/<owner>/<repo>/pull/N.diff with the JSON API
      Accept header, which is wrong for that host and endpoint.
      v2 calls api.github.com/repos/<owner>/<repo>/pulls/<N> with
      Accept: application/vnd.github.v3.diff — the documented way to
      retrieve a raw unified diff through the REST API.

  Bug 3: Added the missing post-fetch stars guard in main().
      v1 called get_repo_info() but never checked the returned star count,
      so the MIN_STARS threshold had no effect at runtime.

  ──────────────────────────────────────────────────────────────────────────────
  HOW TO SET YOUR GITHUB PERSONAL ACCESS TOKEN (PAT)
  ──────────────────────────────────────────────────────────────────────────────
  Option 1 — Environment variable (recommended — keeps secret out of source):

      Linux / macOS (Terminal):
          export GITHUB_TOKEN="ghp_YourPersonalAccessTokenHere"
          python github_pr_scraper.py

      Windows (PowerShell):
          $env:GITHUB_TOKEN = "ghp_YourPersonalAccessTokenHere"
          python github_pr_scraper.py

  Option 2 — Hard-code directly (only for local / private use):
      Find the constant below:
          GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
      Replace the empty string with your token:
          GITHUB_TOKEN = "ghp_YourPersonalAccessTokenHere"

  How to generate a PAT:
      GitHub → Settings → Developer settings →
      Personal access tokens → Tokens (classic) →
      Generate new token → select scope: public_repo (read-only is enough)

  ──────────────────────────────────────────────────────────────────────────────
  DEPENDENCIES
  ──────────────────────────────────────────────────────────────────────────────
      pip install requests
  ──────────────────────────────────────────────────────────────────────────────
"""

import os
import csv
import time
import logging
from dotenv import load_dotenv
from datetime import datetime, timedelta

import requests

# ==============================================================================
# CONFIGURATION
# ==============================================================================

# --- Authentication -----------------------------------------------------------
# A PAT raises the rate limit from 60 req/h (unauthenticated) to 5,000 req/h.
# Without a token this script WILL hit the rate limit within minutes.
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")   # <-- or paste your token here

# --- Search parameters --------------------------------------------------------
SEARCH_START_DATE = "2019-01-01"   # inclusive lower bound  (YYYY-MM-DD)
SEARCH_END_DATE   = "2026-01-01"   # exclusive upper bound  (YYYY-MM-DD)
LANGUAGE          = "JavaScript"
MIN_STARS         = 20             # applied post-fetch (see Bug 1 fix notes)
RESULTS_PER_PAGE  = 100            # GitHub Search API maximum per page

# Keywords checked against PR title + body (at least one must match)
KEYWORDS = [
    "race condition",
    "event race",
    "concurrency bug",
    "flaky test",
    "race bug",
]

# Deep-filter terms — evaluated against the PR's unified diff content
TEST_TERMS  = ["describe(", "it(", "test("]   # evidence of automated tests
ASYNC_TERMS = ["promise", "async", "await"]   # evidence of async code

# --- Output settings ----------------------------------------------------------
OUTPUT_DIR  = "."                    # directory where CSV files will be written
BATCH_SIZE  = 100                    # PRs per CSV file before opening a new one
CSV_PREFIX  = "prs_encontrados_lote" # file-name prefix for each output batch

# --- Rate-limit / retry settings ----------------------------------------------
MAX_RETRIES         = 6     # maximum retry attempts per request
BASE_BACKOFF_SEC    = 5     # initial sleep before first retry (doubles each time)
INTER_REQUEST_DELAY = 0.75  # polite pause between successful requests (seconds)


# ==============================================================================
# LOGGING SETUP
# ==============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


# ==============================================================================
# HTTP SESSION
# ==============================================================================

def build_session() -> requests.Session:
    """
    Create a requests.Session pre-configured with GitHub auth headers and a
    descriptive User-Agent (required by GitHub's API acceptable-use policy).

    NOTE: This session's Accept header is set to the JSON API type, which is
    correct for all calls EXCEPT the diff endpoint. The diff fetch function
    overrides Accept per-request — do not change the default here.
    """
    if not GITHUB_TOKEN:
        log.warning(
            "GITHUB_TOKEN is empty! Running without authentication — "
            "rate limit is only 60 requests/hour and the script will stall. "
            "Set your PAT via the GITHUB_TOKEN environment variable."
        )

    session = requests.Session()
    session.headers.update({
        "Accept":     "application/vnd.github.v3+json",
        "User-Agent": "GH-PR-RaceCondition-Scraper/2.0",
    })

    if GITHUB_TOKEN:
        session.headers["Authorization"] = f"token {GITHUB_TOKEN}"

    return session


# ==============================================================================
# RATE-LIMIT AWARE HTTP GET  (general JSON requests)
# ==============================================================================

def safe_get(
    session: requests.Session,
    url: str,
    params: dict = None,
    extra_headers: dict = None,
) -> requests.Response | None:
    """
    Perform a GET request with automatic retry logic for:

      • 403 / 429  — primary or secondary rate-limit.
                     Respects X-RateLimit-Reset and Retry-After headers.
      • 5xx        — transient server errors; exponential back-off.
      • Network errors — exponential back-off.

    Parameters
    ----------
    session       : authenticated requests.Session
    url           : target URL
    params        : optional query-string parameters dict
    extra_headers : optional dict merged into the request headers
                    (used to override Accept for the diff endpoint)

    Returns
    -------
    requests.Response or None — successful response, or None after all retries.
    """
    backoff = BASE_BACKOFF_SEC

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            headers = extra_headers if extra_headers else {}
            response = session.get(url, params=params, headers=headers, timeout=30)

            # ── Primary / secondary rate-limit ───────────────────────────────
            if response.status_code in (403, 429):
                retry_after = response.headers.get("Retry-After")
                reset_ts    = response.headers.get("X-RateLimit-Reset")

                if retry_after:
                    wait = int(retry_after) + 1
                elif reset_ts:
                    wait = max(int(reset_ts) - int(time.time()), 0) + 5
                else:
                    wait = backoff

                log.warning(
                    "Rate-limited (HTTP %d). Sleeping %ds … (attempt %d/%d)",
                    response.status_code, wait, attempt, MAX_RETRIES,
                )
                time.sleep(wait)
                backoff = min(backoff * 2, 120)   # cap back-off at 2 minutes
                continue

            # ── Transient server errors ───────────────────────────────────────
            if response.status_code >= 500:
                log.warning(
                    "Server error %d for %s. Back-off %ds (attempt %d/%d).",
                    response.status_code, url, backoff, attempt, MAX_RETRIES,
                )
                time.sleep(backoff)
                backoff *= 2
                continue

            # ── Success ───────────────────────────────────────────────────────
            if response.ok:
                time.sleep(INTER_REQUEST_DELAY)   # polite throttle
                return response

            # ── Non-retryable client errors (404, 422, …) ────────────────────
            log.error(
                "Non-retryable HTTP %d — %s — %s",
                response.status_code, url, response.text[:300],
            )
            return None

        except requests.exceptions.RequestException as exc:
            log.warning(
                "Network error on attempt %d/%d: %s. Back-off %ds …",
                attempt, MAX_RETRIES, exc, backoff,
            )
            time.sleep(backoff)
            backoff *= 2

    log.error("Exhausted %d retries for URL: %s", MAX_RETRIES, url)
    return None


# ==============================================================================
# DATE-INTERVAL GENERATOR
# ==============================================================================

def generate_weekly_intervals(start: str, end: str):
    """
    Split the date range [start, end) into consecutive weekly windows.

    The GitHub Search API hard-caps results at 1,000 items per query.
    Splitting a 5-year window (~260 weeks) keeps each bucket well below
    that ceiling for typical keyword densities.

    Yields
    ------
    tuple[str, str] — (interval_start, interval_end) as 'YYYY-MM-DD'.
    """
    fmt     = "%Y-%m-%d"
    current = datetime.strptime(start, fmt)
    final   = datetime.strptime(end,   fmt)
    delta   = timedelta(weeks=1)

    while current < final:
        next_week = min(current + delta, final)
        yield current.strftime(fmt), next_week.strftime(fmt)
        current = next_week


# ==============================================================================
# GITHUB SEARCH  —  ONE KEYWORD × ONE WEEKLY INTERVAL
# ==============================================================================

def search_prs_for_interval(
    session:    requests.Session,
    keyword:    str,
    date_start: str,
    date_end:   str,
) -> list[dict]:
    """
    Query the GitHub Search API for a single keyword within a weekly window
    and paginate through all available result pages (up to the 1,000-item cap).

    BUG 1 FIX: stars:>= has been removed from this query entirely.
    The /search/issues endpoint does not support the `stars:` qualifier.
    Star-count filtering is applied post-fetch in main() after calling
    get_repo_info().

    Parameters
    ----------
    session    : authenticated requests.Session
    keyword    : one of the KEYWORDS constants
    date_start : 'YYYY-MM-DD' (inclusive)
    date_end   : 'YYYY-MM-DD' (inclusive end of the week window)

    Returns
    -------
    list[dict] — raw PR items returned by the Search API.
    """
    # ── BUG 1 FIX: stars:>= removed — not valid for /search/issues ──────────
    query = (
        f'"{keyword}" '
        f"is:pr is:merged "
        f"language:{LANGUAGE} "
        f"created:{date_start}..{date_end}"
    )

    url   = "https://api.github.com/search/issues"
    page  = 1
    items = []

    while True:
        params = {
            "q":        query,
            "per_page": RESULTS_PER_PAGE,
            "page":     page,
            "sort":     "created",
            "order":    "asc",
        }

        resp = safe_get(session, url, params=params)

        if resp is None:
            log.error(
                "Failed to fetch page %d — keyword=%r  %s..%s",
                page, keyword, date_start, date_end,
            )
            break

        data       = resp.json()
        page_items = data.get("items", [])
        items.extend(page_items)

        total = data.get("total_count", 0)
        log.info(
            "  keyword=%-20r  %s..%s  page=%d  got=%d  total_reported=%d",
            keyword, date_start, date_end, page, len(page_items), total,
        )

        # Last page reached when fewer items than the page size are returned
        if len(page_items) < RESULTS_PER_PAGE:
            break

        # GitHub Search API hard-limits at 1,000 results (10 pages × 100)
        if page >= 10:
            log.warning(
                "Reached GitHub's 1,000-item ceiling — keyword=%r  %s..%s. "
                "Consider splitting into daily intervals if this window is dense.",
                keyword, date_start, date_end,
            )
            break

        page += 1

    return items


# ==============================================================================
# KEYWORD DETECTION  —  TITLE + BODY
# ==============================================================================

def find_keywords_in_pr(pr: dict) -> list[str]:
    """
    Return every KEYWORDS entry that appears in the PR title or body text.
    The Search API guarantees at least one match per result, but we collect
    ALL matches here to populate the 'terms_found' CSV column.
    """
    combined = " ".join([
        (pr.get("title") or "").lower(),
        (pr.get("body")  or "").lower(),
    ])
    return [kw for kw in KEYWORDS if kw.lower() in combined]


# ==============================================================================
# DEEP FILTER  —  DIFF ANALYSIS
# ==============================================================================

def fetch_pr_diff(
    session:    requests.Session,
    repo_full:  str,
    pr_number:  int,
) -> str | None:
    """
    Download the unified diff for a PR via the GitHub REST API.

    BUG 2 FIX: v1 called  github.com/<owner>/<repo>/pull/N.diff  with the
    JSON API Accept header — wrong host, wrong media type.

    The correct approach is:
        GET api.github.com/repos/{owner}/{repo}/pulls/{number}
        Accept: application/vnd.github.v3.diff

    This is the documented REST API method and returns the raw unified diff
    without any redirect or host-mismatch issue.

    Parameters
    ----------
    session    : authenticated requests.Session
    repo_full  : 'owner/repo' string
    pr_number  : integer PR number

    Returns
    -------
    str  — raw unified diff text, or None on failure.
    """
    url = f"https://api.github.com/repos/{repo_full}/pulls/{pr_number}"

    # Override Accept for this specific request only — the session default
    # (application/vnd.github.v3+json) would return JSON, not the diff.
    resp = safe_get(
        session,
        url,
        extra_headers={"Accept": "application/vnd.github.v3.diff"},
    )

    return resp.text if resp else None


def passes_deep_filter(diff_content: str) -> tuple[bool, bool]:
    """
    Scan the unified diff for async and test-framework indicators.

    We search the entire diff string (including context lines, not just
    added lines) to maximise detection — a call to `describe(` on an
    unchanged line still confirms the file is a test file.

    Returns
    -------
    tuple[bool, bool] — (has_test_terms, has_async_terms).
    Both must be True for the PR to pass.
    """
    if not diff_content:
        return False, False

    lower = diff_content.lower()
    has_tests = any(term.lower() in lower for term in TEST_TERMS)
    has_async = any(term.lower() in lower for term in ASYNC_TERMS)
    return has_tests, has_async


# ==============================================================================
# REPOSITORY METADATA  —  STARS + URL
# ==============================================================================

_repo_cache: dict[str, dict] = {}   # module-level cache avoids redundant calls


def get_repo_info(session: requests.Session, repo_full_name: str) -> dict:
    """
    Retrieve repository star count and HTML URL via the Repos API.
    Results are cached so that multiple PRs from the same repo share one call.

    Used by main() to apply the MIN_STARS filter (Bug 1 fix) and to populate
    the 'repo_url' and 'repo_stars' CSV columns.
    """
    if repo_full_name in _repo_cache:
        return _repo_cache[repo_full_name]

    url  = f"https://api.github.com/repos/{repo_full_name}"
    resp = safe_get(session, url)

    if resp and resp.ok:
        data   = resp.json()
        result = {
            "stars":    data.get("stargazers_count", 0),
            "repo_url": data.get("html_url", f"https://github.com/{repo_full_name}"),
        }
    else:
        result = {
            "stars":    0,
            "repo_url": f"https://github.com/{repo_full_name}",
        }

    _repo_cache[repo_full_name] = result
    return result


# ==============================================================================
# PR METADATA  —  CHANGED FILE COUNT + MERGE DATE
# ==============================================================================

def get_pr_details(
    session:        requests.Session,
    repo_full_name: str,
    pr_number:      int,
) -> dict:
    """
    Fetch the changed_files count and merged_at timestamp for a specific PR.

    These fields are not present in Search API results — they require a
    separate call to the Pull Requests API endpoint.

    NOTE: We already called the pulls endpoint to fetch the diff (Bug 2 fix),
    but that call used Accept: application/vnd.github.v3.diff which returns
    plain text, not JSON. This separate call retrieves the structured metadata.
    """
    url  = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}"
    resp = safe_get(session, url)   # uses the default JSON Accept header

    if resp and resp.ok:
        data = resp.json()
        return {
            "changed_files": data.get("changed_files", 0),
            "merged_at":     data.get("merged_at", ""),
        }

    return {"changed_files": 0, "merged_at": ""}


# ==============================================================================
# CSV OUTPUT
# ==============================================================================

CSV_HEADERS = [
    "pr_url",           # 1. Pull Request link
    "repo_full_name",   # 2. Author/Repo name  (e.g. facebook/react)
    "repo_url",         # 3. Repository link
    "pr_title",         # 4. Pull Request title
    "repo_stars",       # 5. Repository star count
    "changed_files",    # 6. Total files changed in the PR
    "merged_at",        # 7. Merge timestamp (ISO 8601)
    "terms_found",      # 8. Keywords matched in title/body (pipe-separated)
]


def save_batch_to_csv(batch: list[dict], batch_number: int) -> str:
    """
    Write a list of qualifying PR records to a new numbered CSV file.
    A new file is created every BATCH_SIZE records so that no data is
    lost if the script is interrupted mid-run.

    Parameters
    ----------
    batch        : list of record dicts (keys must match CSV_HEADERS)
    batch_number : integer appended to the file name for ordering

    Returns
    -------
    str — absolute path of the written CSV file.
    """
    filename = os.path.join(OUTPUT_DIR, f"{CSV_PREFIX}_{batch_number}.csv")

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(batch)

    log.info(
        "💾  Batch %d saved → %s  (%d records)",
        batch_number, os.path.abspath(filename), len(batch),
    )
    return filename


# ==============================================================================
# MAIN ORCHESTRATOR
# ==============================================================================

def main() -> None:
    """
    End-to-end pipeline (all three bugs fixed):

      1. Split the 5-year date range into weekly intervals to stay under
         GitHub's 1,000-result-per-query ceiling.

      2. For each interval × keyword, query the GitHub Search API
         (WITHOUT stars:>= — Bug 1 fix) and paginate through all pages.

      3. De-duplicate results (same PR may appear under multiple keywords).

      4. For each unique PR, download the unified diff via the correct
         API endpoint and media type (Bug 2 fix) and apply the deep filter
         (must contain test terms AND async terms).

      5. Fetch repo metadata and apply the MIN_STARS guard here in Python
         rather than in the search query (Bug 3 fix).

      6. Enrich passing PRs with PR-level metadata (changed_files, merged_at).

      7. Accumulate records and flush to a new CSV file every BATCH_SIZE PRs.
    """
    log.info("=" * 70)
    log.info("  GitHub PR Scraper v2.0 — Race Condition / Concurrency (JS)")
    log.info("=" * 70)
    log.info("  Date range  : %s → %s", SEARCH_START_DATE, SEARCH_END_DATE)
    log.info("  Language    : %s   |   Min stars: %d (applied post-fetch)",
             LANGUAGE, MIN_STARS)
    log.info("  Keywords    : %s", ", ".join(KEYWORDS))
    log.info("=" * 70)

    session     = build_session()
    seen_ids    = set()     # de-duplication set — GitHub PR node IDs
    batch       = []        # accumulator for the current output CSV batch
    batch_no    = 1
    total_found = 0

    # Counters for a helpful end-of-run summary
    stats = {
        "searched":       0,   # unique PRs evaluated
        "no_keywords":    0,   # dropped: keyword not in title/body
        "diff_failed":    0,   # dropped: diff fetch returned nothing
        "no_tests":       0,   # dropped: no test terms in diff
        "no_async":       0,   # dropped: no async terms in diff
        "below_stars":    0,   # dropped: repo has fewer stars than MIN_STARS
        "qualified":      0,   # passed all filters
    }

    # ── Split date range into weekly windows ─────────────────────────────────
    intervals = list(generate_weekly_intervals(SEARCH_START_DATE, SEARCH_END_DATE))
    log.info("Date range split into %d weekly intervals.\n", len(intervals))

    for idx, (d_start, d_end) in enumerate(intervals, start=1):
        log.info(
            "── Interval %d/%d  [%s → %s] ──────────────────────────────",
            idx, len(intervals), d_start, d_end,
        )

        for keyword in KEYWORDS:
            raw_items = search_prs_for_interval(session, keyword, d_start, d_end)

            for pr in raw_items:
                pr_id = pr["id"]

                # ── De-duplicate across keywords and intervals ────────────
                if pr_id in seen_ids:
                    continue
                seen_ids.add(pr_id)
                stats["searched"] += 1

                pr_number = pr["number"]
                repo_full = pr["repository_url"].split("/repos/")[-1]
                pr_title  = pr.get("title", "")
                pr_url    = pr.get("html_url", "")

                log.info("  ➜  PR #%d  [%s]", pr_number, repo_full)

                # ── Keyword check (title + body) ──────────────────────────
                # The Search API already guarantees a match, but we collect
                # ALL matching keywords for the CSV column.
                terms_found = find_keywords_in_pr(pr)
                if not terms_found:
                    # Rare: can happen when the match was in a comment
                    stats["no_keywords"] += 1
                    log.debug("    ✗ No keywords in title/body — skipping.")
                    continue

                # ── BUG 2 FIX: fetch diff via REST API with correct header ─
                diff_content = fetch_pr_diff(session, repo_full, pr_number)
                if not diff_content:
                    stats["diff_failed"] += 1
                    log.warning("    ✗ Could not retrieve diff — skipping.")
                    continue

                # ── Deep filter: test terms ───────────────────────────────
                has_tests, has_async = passes_deep_filter(diff_content)

                if not has_tests:
                    stats["no_tests"] += 1
                    log.debug("    ✗ No test terms in diff — skipping.")
                    continue

                # ── Deep filter: async terms ──────────────────────────────
                if not has_async:
                    stats["no_async"] += 1
                    log.debug("    ✗ No async terms in diff — skipping.")
                    continue

                # ── BUG 1 + 3 FIX: fetch stars and apply filter here ──────
                # `stars:>=N` is invalid in /search/issues, so we fetch the
                # repo metadata and apply the threshold in Python instead.
                repo_info = get_repo_info(session, repo_full)

                if repo_info["stars"] < MIN_STARS:
                    stats["below_stars"] += 1
                    log.debug(
                        "    ✗ Repo %s has %d stars (min %d) — skipping.",
                        repo_full, repo_info["stars"], MIN_STARS,
                    )
                    continue

                # ── PR-level metadata (changed_files, merged_at) ──────────
                pr_details = get_pr_details(session, repo_full, pr_number)

                record = {
                    "pr_url":         pr_url,
                    "repo_full_name": repo_full,
                    "repo_url":       repo_info["repo_url"],
                    "pr_title":       pr_title,
                    "repo_stars":     repo_info["stars"],
                    "changed_files":  pr_details["changed_files"],
                    "merged_at":      pr_details["merged_at"],
                    "terms_found":    " | ".join(terms_found),
                }

                batch.append(record)
                stats["qualified"] += 1
                total_found += 1

                log.info(
                    "    ✔ Qualified! ⭐ %d  files=%d  terms=%s  "
                    "(batch %d — %d/%d)",
                    repo_info["stars"],
                    pr_details["changed_files"],
                    record["terms_found"],
                    batch_no,
                    len(batch),
                    BATCH_SIZE,
                )

                # ── Flush batch to CSV when BATCH_SIZE is reached ─────────
                if len(batch) >= BATCH_SIZE:
                    save_batch_to_csv(batch, batch_no)
                    batch    = []
                    batch_no += 1

    # ── Flush any remaining records in the last (partial) batch ──────────────
    if batch:
        save_batch_to_csv(batch, batch_no)

    # ── Final summary ─────────────────────────────────────────────────────────
    log.info("")
    log.info("=" * 70)
    log.info("  Scraping complete.")
    log.info("  Total unique PRs evaluated : %d", stats["searched"])
    log.info("  Dropped — no keyword match : %d", stats["no_keywords"])
    log.info("  Dropped — diff fetch error : %d", stats["diff_failed"])
    log.info("  Dropped — no test terms    : %d", stats["no_tests"])
    log.info("  Dropped — no async terms   : %d", stats["no_async"])
    log.info("  Dropped — below min stars  : %d", stats["below_stars"])
    log.info("  ─────────────────────────────────────────────────")
    log.info("  Qualified PRs saved to CSV : %d", stats["qualified"])
    log.info("  Output directory           : %s", os.path.abspath(OUTPUT_DIR))
    log.info("=" * 70)


# ==============================================================================
# ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    main()