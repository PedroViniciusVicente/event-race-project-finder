# Core
PR URL: https://github.com/BrightspaceUI/core/pull/1120

## Pull Request Title and Description
![PR Title and Description](image2.png)

## Pull Request Code
![PR Code](image1.png)

## Our Pattern Classification
Stabilization Race:

## Wang Pattern Classification
Order Violation:


## Setup
```
git clone https://github.com/BrightspaceUI/core.git
cd core
git checkout -f 4f483a3d455a46baa80c5eba3fa31d1ec5b2d5b8

nvm use 10
npm install
npm run build
npm start
npm test
```

## Reported flaky tests
```
go to components/inputs/test/input-date-time-range.test.js

add .only at describe.only('utility', () => { in line 36
```

## Utlized config on run-tests.py
```
# ============= CONFIGS =============
PROJECT_ROOT = "projects/core"
LOG_DIRECTORY = "PRs/pr378/logs_core"
TOTAL_RUNS = 1000
LOG_INTERVAL = 20

COMMAND = [
    'npx', 'karma', 'start'
]
# ===================================
```