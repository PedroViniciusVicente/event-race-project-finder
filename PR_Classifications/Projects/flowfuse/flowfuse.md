# flowfuse
PR URL: https://github.com/FlowFuse/flowfuse/pull/4260

## Pull Request Title and Description
![PR Title and Description](image2.png)

## Pull Request Code
![PR Code](image1.png)

## Our Pattern Classification
**Stabilization Race:**
In this scenario, the test triggers the startup of multiple instances, including `app.containers.start(thirdInstance)` whose startup process is asynchronous. The test proceeds to validate the application state and completes without awaiting the full stabilization and resolution of this asynchronous operation.

## Wang Pattern Classification
**Order Violation:**
The intended execution order is that the asynchronous startup operations, particularly the initialization of the third instance, should complete before the test finishes. However, in the original code, the test does not enforce this ordering and allows completion to occur before the `startThirdResult.started` promise resolves.
This leads to a situation where operations that are logically expected to occur earlier (full initialization of the instance) are not guaranteed to complete before later events (test termination). The fix enforces the correct sequencing by explicitly awaiting the completion of the startup process.

## Setup
```
git clone https://github.com/FlowFuse/flowfuse.git
cd flowfuse
git checkout -f 223b40875b49cc4fa7e17f96f843978248aa5862

nvm use 20
npm install
npm run build
npm run test:unit
```

## Reported flaky tests
```
npx mocha 'test/unit/forge/routes/api/team_spec.js' --timeout 10000 --node-option=unhandled-rejections=strict -g 'with all instances and their status'
```

## Utlized config on run-tests.py
```
# ============= CONFIGS =============
PROJECT_ROOT = "projects/flowfuse"
LOG_DIRECTORY = "PRs/pr1510/logs_flowfuse"
TOTAL_RUNS = 1000
LOG_INTERVAL = 20

COMMAND = [
    'npx', 'mocha', 
    'test/unit/forge/routes/api/team_spec.js',
    '--node-option=unhandled-rejections=strict',
    '-g', 'with all instances and their status'
    ]
# ===================================
```