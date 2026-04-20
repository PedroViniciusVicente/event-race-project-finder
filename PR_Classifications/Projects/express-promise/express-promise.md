PR URL: https://github.com/goodeggs/express-promise-middleware/pull/2/files

## Setup
```
git clone https://github.com/goodeggs/express-promise-middleware.git
cd express-promise-middleware/
git checkout -f 385feebe9725197af8934cfe3f0a9602b7636269

nvm use 22
yarn
yarn test
```

## Reported flaky tests
```
npm run test:mocha -- src/test.js --grep "respondJson should not call response.json if the handler sets response.finished"
npm run test:mocha -- src/test.js --grep "respondJson should reject and not call next\(\) with an error if the handler sets response.finished and also rejects"

npm run test:mocha -- src/test.js --grep "promiseMiddleware should return a middleware that calls next when the promise resolves"
npm run test:mocha -- src/test.js --grep "promiseMiddleware should not call next if the handler sets response.finished"
```

## Utlized config on run-tests.py
```
# ============= CONFIGS =============
PROJECT_ROOT = "projects/express-promise-middleware"
LOG_DIRECTORY = "PRs/pr6/express-promise"
TOTAL_RUNS = 1000
LOG_INTERVAL = 20

COMMAND = [
    'npm', 'run', 'test:mocha', 
    '--', 'src/test.js',
    '--grep', 'respondJson should not call response.json if the handler sets response.finished'
]
# ===================================
```