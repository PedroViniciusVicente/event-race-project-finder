PR URL: https://github.com/adfinis/timed-frontend/pull/583

## Setup
```
git clone https://github.com/adfinis/timed-frontend.git
cd timed-frontend
git checkout -f 559d20d882c132e19ee0c11555eadaec2fe2ed00

nvm use 14
npm install yarn
npx yarn install
npx yarn test
```

## Reported flaky tests
```
npx ember test --launch Chrome --filter="Acceptance | statistics: can view statistics by task"
```

## Utlized config on run-tests.py
```
# ============= CONFIGS =============
PROJECT_ROOT = "projects/timed-frontend"
LOG_DIRECTORY = "PRs/pr612/logs_timed"
TOTAL_RUNS = 1000
LOG_INTERVAL = 20

COMMAND = [
    'npx', 'ember', 'test', '--launch', 'Chrome', '--filter=Acceptance | statistics: can view statistics by task',
]
# ===================================
```