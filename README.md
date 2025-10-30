# Awating Trouble: Source Code and Artifacts Repository

This repository contains the source code and artifacts needed to replicate the experiments presented in the paper "Awaiting Trouble: An Preliminary Study on Event Races and Flaky Tests in Modern JavaScript Applications", submitted to [ICSE's 3rd International Flaky Tests Workshop 2026 (FTW 2026)](https://conf.researchr.org/home/icse-2026/ftw-2026).

In this repository, JavaScript projects containing event races, a special form of race condition, were searched, filtered and analaysed using Pull Requests (PRs) collected from the GitHub API. The 20 analyzed projects described in the shortpaper were also classified according to its caracteristics and reproduced following a protocol to reveal flaky tests.


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

1. The initial list of JavaScript projects was sourced from the curated lists detailed in the [awesome nodejs lists](awesome_lists/README.md).

2. A broad search of Pull Requests in JavaScript projects was conducted by searchs using the GitHub API in [pr_search.py](github_searches/pr_search.py).

3. The [filter_search.py](github_searches/filter_search.py) script was used to filter all the collected data, filtering for PRs that match our criteria (mention keywords: "event race", "race condition", "concurrency bug", "race bug", "flaky test"; modify test files with keywords: "test", "it", "describe"; and modify JavaScript files with modern resources: "promises", "async", "await").


### Flaky Tests Reproduction

Our analysis resulted in a dataset of 20 curated bugs that were manually analyzed.

- The projects pre-fix commit, are available as compacted archives in our Google Drive folder: 
[Compacted Projects](https://drive.google.com/drive/folders/1X4r3UzZLAkntMeO5bltF-uxXzP-9v28V?usp=sharing).

- For each project, we have created a step-by-step guide detailing the setup, the exact commands used to run, and the logs of the flaky behavior:
[Projects Setup and Flakiness Logs](https://drive.google.com/drive/folders/1JgY6P6Uz4JqIeuQgYF6njTuTbQQvWXA1?usp=drive_link).