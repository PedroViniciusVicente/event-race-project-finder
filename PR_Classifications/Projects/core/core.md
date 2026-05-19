# Core
PR URL: https://github.com/BrightspaceUI/core/pull/1120

## Pull Request Title and Description
![PR Title and Description](image2.png)

## Pull Request Code
![PR Code](image1.png)

## Description
In this case, the test updates the timezone configuration (`documentLocaleSettings.timezone.identifier`) and immediately invokes the function `getShiftedEndDateTime`, which relies on this updated timezone to compute correct results. Although the assignment itself is synchronous, its propagation, likely through the underlying UI framework, occurs asynchronously. As a result, the system may not yet reflect the updated timezone when the function is executed, leading to intermittent test failures. The absence of an explicit event or callback signaling that the timezone change has been fully applied creates this issue. The introduced fix (`await aTimeout(10)`) artificially delays execution, allowing enough time for the asynchronous propagation of the timezone change to complete.

## Validation Between the Authors
<table>
  <thead>
    <tr>
      <th align="left">Researcher</th>
      <th align="left">Classification</th>
      <th align="left">Bug Pattern</th>
      <th align="left">Rationale</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="2"><b>R1</b></td>
      <td>Wang</td>
      <td>Order Violation</td>
      <td>The intended order was for the timezone to be fully propagated before the date calculation.</td>
    </tr>
    <tr>
      <td>Our</td>
      <td>Stabilization Race</td>
      <td>The test triggers a timezone update but immediately performs a date calculation before the framework’s internal asynchronous update has stabilized.</td>
    </tr>
    <tr>
      <td rowspan="2"><b>R2</b></td>
      <td>Wang</td>
      <td>Order Violation</td>
      <td>The order expected by the dev is violated.</td>
    </tr>
    <tr>
      <td>Our</td>
      <td>Stabilization Race</td>
      <td>Assert some resources (timezone definition) before it is ready.</td>
    </tr>
  </tbody>
</table>

## Setup
```
git clone https://github.com/BrightspaceUI/core.git
cd core
git checkout -f 4f483a3d455a46baa80c5eba3fa31d1ec5b2d5b8

nvm use 10
npm install
npm run build
npm start
npm test
```

## Reported flaky tests
```
go to components/inputs/test/input-date-time-range.test.js

add .only at describe.only('utility', () => { in line 36
```

## Utlized config on run-tests.py
```
# ============= CONFIGS =============
PROJECT_ROOT = "projects/core"
LOG_DIRECTORY = "PRs/pr378/logs_core"
TOTAL_RUNS = 1000
LOG_INTERVAL = 20

COMMAND = [
    'npx', 'karma', 'start'
]
# ===================================
```