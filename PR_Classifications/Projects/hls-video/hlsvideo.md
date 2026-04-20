# hls-video-element
PR URL: https://github.com/muxinc/hls-video-element/pull/32

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