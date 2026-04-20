# eq-author
PR URL: https://github.com/ONSdigital/eq-author-app/pull/100

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
git clone https://github.com/ONSdigital/eq-author-app.git
cd eq-author-app/
git checkout -f 3d04709ad2c36b49888e8305b855b34f9da0dd20

nvm use 22
cd eq-author
yarn
yarn test
```

## Reported flaky tests
```
npx jest eq-author/src/components/withEntityEditor/index.test.js

npx jest eq-author/src/components/withEntityEditor/index.test.js --t "should run update once if triggered in quick succession"
should not overwrite fields that are being changed
should use the name to create deeply nested entities
```

## Utlized config on run-tests.py
```
# ============= CONFIGS =============
PROJECT_ROOT = "projects/eq-author-app/eq-author"
LOG_DIRECTORY = "PRs/pr5/logs_eq-author"
TOTAL_RUNS = 1000
LOG_INTERVAL = 20

COMMAND = [
    'npx', 'jest', 
    'eq-author/src/components/withEntityEditor/index.test.js', '--t',
    'should run update once if triggered in quick succession'
]
# ===================================
```