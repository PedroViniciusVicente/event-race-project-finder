PR URL: https://github.com/WordPress/gutenberg/pull/58629

## Setup
```
git clone https://github.com/WordPress/gutenberg.git
cd gutenberg/
git checkout -f b801b1c15f8daa304ca6f9db0999e35e3088d687

nvm use 20
npm ci
//npm install
//npm run dev
npm test
```

## Reported flaky tests
```
npx jest --config test/unit/jest.config.js packages/components/src/tabs/test/index.tsx -t "should continue to handle arrow key navigation properly" --silent
```

## Utlized config on run-tests.py
```
# ============= CONFIGS =============
PROJECT_ROOT = "projects/gutenberg"
LOG_DIRECTORY = "PRs/pr1304/logs_gutenberg"
TOTAL_RUNS = 1000
LOG_INTERVAL = 20

COMMAND = [
    'npx', 'jest', 
    '--config', 'test/unit/jest.config.js',
    'packages/components/src/tabs/test/index.tsx',
    '-t', 'should continue to handle arrow key navigation properly',
    '--silent'
]
# ===================================
```