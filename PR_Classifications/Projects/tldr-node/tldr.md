# Tldr-node-client
PR URL: https://github.com/tldr-pages/tldr-node-client/pull/329

## Pull Request Title and Description
![PR Title and Description](image1.png)

## Pull Request Code
![PR Code](image2.png)

## Our Pattern Classification
Stabilization Race:

## Wang Pattern Classification
Order Violation:

## Setup
```
git clone https://github.com/tldr-pages/tldr-node-client.git
cd tldr-node-client/
git checkout -f 6905454f6b9fc3fe572a5d82e90b630cc7cb530c

nvm use 22
npm install
npm test
```

## Reported flaky tests
```
npx mocha test/cache.spec.js -g "should return a positive number on lastUpdate"
```

## Utlized config on run-tests.py
```
# ============= CONFIGS =============
PROJECT_ROOT = "projects/tldr-node-client"
LOG_DIRECTORY = "PRs/pr393/logs_tldr"
TOTAL_RUNS = 1000
LOG_INTERVAL = 20

COMMAND = [
    'npx', 'mocha', 
    'test/cache.spec.js', '-g',
    'should return a positive number on lastUpdate'
]
# ===================================
```