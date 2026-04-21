# hls-video-element
PR URL: https://github.com/muxinc/hls-video-element/pull/32

## Pull Request Title and Description
![PR Title and Description](image1.png)

## Pull Request Code
![PR Code](image2.png)

## Our Pattern Classification
**Lifecycle Race:**
The issue is related to the improper sequencing of operations during the lifecycle of a custom video element.
When the `src` attribute changes, the `load()` method is triggered, which internally calls `#destroy()` to clean up any existing HLS instance before initializing a new one. However, without proper synchronization, the initialization logic may execute before all relevant attributes are fully applied to the element.
The fix introduces an `await Promise.resolve()` to wait for one microtask tick in the `load()` method. This ensures that all pending attribute updates and lifecycle callbacks are completed before proceeding with the initialization of the HLS instance.

## Wang Pattern Classification
**Order Violation:**
The correct behavior requires a strict ordering: (1) all attribute updates (especially `src`) must be fully applied, (2) previous resources must be destroyed, and only then (3) a new HLS instance should be initialized. However, due to the asynchronous nature of attribute propagation and lifecycle callbacks, the initialization logic may run before the system has completed earlier steps.

## Setup
```
git clone https://github.com/muxinc/hls-video-element.git
cd hls-video-element
git checkout -f 0fcd2f848465fc8bde99dd9a6f3a560988f5d016

nvm use 22
yarn --frozen-lockfile
yarn test
```
go to hls-video-element.js in lines 24 and 32
```
- async load() {
+ load() {

...

// Wait 1 tick to allow other attributes to be set.
- await Promise.resolve();
```

## Reported flaky tests
```
yarn test
```

## Utlized config on run-tests.py
```
# ============= CONFIGS =============
PROJECT_ROOT = "projects/hls-video-element"
LOG_DIRECTORY = "PRs/pr1145/logs_hlsvideo"
TOTAL_RUNS = 1000
LOG_INTERVAL = 20

COMMAND = [
    'yarn', 'test'
]
# ===================================
```