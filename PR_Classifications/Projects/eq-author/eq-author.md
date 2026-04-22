# eq-author
PR URL: https://github.com/ONSdigital/eq-author-app/pull/100

## Pull Request Title and Description
![PR Title and Description](image2.png)

## Pull Request Code
![PR Code 1](image1.png)

![PR Code 2](image3.png)

## Our Pattern Classification
**Concurrent Access Race:**
As described in the PR, when a user blurs a field (e.g., alias or title) and simultaneously triggers another UI action (such as adding a section introduction), two update operations are fired almost concurrently. Both updates attempt to modify the same underlying entity and are sent as separate requests.

This behavior reflects a classic concurrent access problem: multiple asynchronous operations accessing and modifying shared state without synchronization. The fix introduces a debouncing mechanism (`debounce(..., 20ms)`), which aggregates rapid successive updates into a single operation. By delaying execution and coalescing updates within a short time window, the solution prevents overlapping mutations and ensures that only a consolidated, consistent update is sent.

## Wang Pattern Classification
**Atomic Violation:**
The intended behavior is that multiple logically related updates (e.g., modifying a field and creating a section introduction) should be treated as a single, coherent operation on the entity. However, in the original implementation, these updates are executed as separate asynchronous mutations, allowing them to interleave in time. As a result, one update may overwrite or conflict with the effects of another.
This violates the expectation that the sequence of operations should behave atomically: as an indivisible unit without interference from other concurrent operations.

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