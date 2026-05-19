# Awaiting Trouble: Source Code and Artifacts Repository

This repository contains the source code and artifacts needed to replicate, follow and evaluate the study presented in the paper "Awaiting Trouble: Characterizing Asynchronous Concurrency issues in Modern Promise-based JavaScript Applications", submitted to [CBSoft's 30th Brazilian Symposium on Programming Languages (SBLP 2026)](https://cbsoft.sbc.org.br/2026/pt/symposiums/sblp/call/).

In this repository, JavaScript projects containing concurrency issues, were searched, filtered and analyzed using Pull Requests (PRs) collected from the GitHub API. The 22 analyzed projects described in the paper were also classified according to its characteristics by both authors and reproduced following a protocol to reveal flaky tests.


## Prerequisites
- Python 3.x+: For running the data collection scripts.
- Node.js & npm: For setting up and testing the JavaScript projects. We recommend using *nvm* to manage Node.js versions, as different projects may have different requirements.
- A GitHub Personal Access Token (PAT): Required for the pr_search.py script to query the GitHub API. Store it in an environment variable (.env).

To setup the environment and install python dependencies:
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

[Generate your GitHub Token](https://github.com/settings/tokens), rename file .env.example to .env and include:
```
GITHUB_TOKEN=your_github_personal_access_token_here
```

## Replication Workflow

This section provides a step-by-step guide to replicate our study.

### Data Collection

We have already included the [final, filtered Pull Requests dataset](filtered_event_races_pull_requests.csv) in this repository. However, if you wish to re-run the entire data collection and filtering process, follow these steps.

1. The initial list of JavaScript projects is sourced from the curated lists detailed in the [awesome nodejs lists](awesome_lists/README.md).

2. A broad search of Pull Requests in JavaScript projects is conducted by searchs using the GitHub API in [pr_search.py](github_searches/pr_search.py).

3. The [filter_search.py](github_searches/filter_search.py) script is used to filter all the collected data, filtering for PRs that match our criteria (mention keywords: "event race", "race condition", "concurrency bug", "race bug", "flaky test"; modify test files with keywords: "test", "it", "describe"; and modify JavaScript files with modern resources: "promises", "async", "await").


### Flaky Tests Reproduction

Our analysis resulted in a dataset of 22 curated bugs that were manually analyzed.

- The projects pre-fix commit, are available as compacted archives in our Google Drive folder: 
[Compacted Projects](https://drive.google.com/drive/folders/1X4r3UzZLAkntMeO5bltF-uxXzP-9v28V?usp=sharing).

- For each project, we have created a guide detailing the classification proccess of each case issue by both authors in a table format, the setup and the logs of the flaky behavior:
[Classification, Projects Setup and Flakiness Logs](PR_Classifications/README.md).

- To automate the flaky test reproduction protocol, we provide a Python script detailed in [run_tests.py](tests_execution/run_tests.py). The script is used to run the analyzed test multiple times to observe intermittent failures and automatically generate the results logs available in our Google Drive Folders. This is the same tool we used to produce the analysis logs available on Google Drive and to gather the data for Table 1 in our paper.