PR URL: https://github.com/holepunchto/bare-http1/pull/17

## Setup
```
git clone https://github.com/holepunchto/bare-http1.git
cd bare-http1
git checkout -f 62eb0ffe5bd187554272684edc24ff23a3e748de

nvm use 22
npm install -g bare-runtime
npm i
npm test
```

## Reported flaky tests
```
(comment all the tests in test.js but "server and client do big writes" and the auxiliar functions)
```

## Utlized config on run-tests.py
```
# ============= CONFIGS =============
PROJECT_ROOT = "projects/bare-http1"
LOG_DIRECTORY = "PRs/pr1529/logs_barehttp1"
TOTAL_RUNS = 1000
LOG_INTERVAL = 20

COMMAND = [
    'npm', 'test'
]
# ===================================
```