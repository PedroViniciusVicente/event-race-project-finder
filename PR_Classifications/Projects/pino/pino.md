# Pino
PR URL: https://github.com/pinojs/pino/pull/1186

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
git clone https://github.com/pinojs/pino.git
cd pino
git checkout -f e5f17ae4dc1b46c33da16d9e1e5f817a2bacfc7c

nvm use 18
npm install
npm run test-ci
```
go to test/transport/core.test.js and comment the following line: (line 226)
```
  await once(transport, 'ready')
```

## Reported flaky tests
```
npx tap test/transport/core.test.js -g "autoEnd = false" --no-coverage
```

## Utlized config on run-tests.py
```
# ============= CONFIGS =============
PROJECT_ROOT = "projects/pino"
LOG_DIRECTORY = "PRs/pr673/logs_pino"
TOTAL_RUNS = 1000
LOG_INTERVAL = 20

COMMAND = [
    'npx', 'tap', 
    'test/transport/core.test.js',
    '-g', 'autoEnd = false',
    '--no-coverage'
]
# ===================================
```

to use with nacd, nvm use 22