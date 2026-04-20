PR URL: https://github.com/adobe/fetch/pull/396


## Setup
```
git clone https://github.com/adobe/fetch
cd fetch
git checkout -f 9d3f33f0e92d919bb4d8d1359b8e3e284a385634

nvm use 18
npm ci
npm test

npx c8 mocha
```

## Reported flaky tests
```
npx mocha test/core/index.test.js -g "supports parallel requests"
```

## Utlized config on run-tests.py
```
# ============= CONFIGS =============
PROJECT_ROOT = "projects/fetch"
LOG_DIRECTORY = "PRs/pr1035/logs_fetch"
TOTAL_RUNS = 1000
LOG_INTERVAL = 20

COMMAND = [
    'npx', 'mocha', 
    'test/core/index.test.js',
    '-g', 'supports parallel requests'
]
# ===================================
```