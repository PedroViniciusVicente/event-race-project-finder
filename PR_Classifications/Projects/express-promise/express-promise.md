# express-promise
PR URL: https://github.com/goodeggs/express-promise-middleware/pull/2/files

## Pull Request Title and Description
![PR Title and Description](image2.png)

## Pull Request Code
![PR Code](image1.png)

## Our Pattern Classification
**Stabilization Race:**
In the original implementation, the middleware checks the flag `res.finished` to determine whether a response has already been completed. However, sending a response (e.g., via `res.send`) is an asynchronous operation, and there exists a time window where the response has already been initiated but not yet fully completed. During this window, `res.finished` remains false, even though the response is in progress.

The fix replaces `res.finished` with `res.headersSent`, which is set at the moment the response is initiated. This ensures that the middleware observes a stable and accurate state when making decisions, eliminating the timing window that caused the race.

## Wang Pattern Classification
**Order Violation:**
The intended ordering is that once a response is initiated, the middleware should not proceed to call `next()`. However, due to the asynchronous nature of response completion and the delayed update of `res.finished`, the middleware’s check may occur before the system reflects that the response has already started. The fix ensures that the correct ordering is respected by using `res.headersSent`, which reflects the initiation of the response immediately.


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