# gutenberg
PR URL: https://github.com/WordPress/gutenberg/pull/58629

## Pull Request Title and Description
![PR Title and Description](image1.png)

## Pull Request Code
![PR Code](image2.png)

## Our Pattern Classification
**Stabilization Race:**
In this case, changes to the selectedTab prop in a React component trigger multiple internal re-renders. These re-renders do not complete immediately, and the test proceeds to execute assertions by checking the selected tab and focus state before the component has reached its final, stable state.

As a result, the test intermittently fails because it observes intermediate UI states rather than the fully updated one. The fix introduces `waitFor`, which repeatedly evaluates the assertion until the expected condition is met or a timeout occurs. This ensures that the test only proceeds once the component has completed its rendering cycle.

## Wang Pattern Classification
**Order Violation:**
The intended order of operations is: (1) trigger a state change (via prop update or user interaction), (2) allow the component to complete its re-rendering process, and (3) perform assertions on the final UI state. However, due to asynchronous rendering, the test executes assertions before the re-rendering has completed.

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