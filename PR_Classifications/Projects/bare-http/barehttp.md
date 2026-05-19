# Bare-http1 
PR URL: https://github.com/holepunchto/bare-http1/pull/17

## Pull Request Title and Description
![PR Title and Description](image2.png)

## Pull Request Code
![PR Code](image1.png)

## Description
The issue arises from an incorrect ordering between different phases of the request–response process in a Node.js HTTP server. The server may begin sending the response (`res.write` / `res.end`) before the request body has been fully received and processed (`req.on('end')`). Due to asynchronous scheduling (via `setImmediate`), the response completion may occur before the request stream finishes emitting all its data. This creates a race condition between the request consumption phase and the response finalization phase, which are both part of the server’s management.

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
      <td>The intended order was for the request body to be fully processed before the server finalized.</td>
    </tr>
    <tr>
      <td>Our</td>
      <td>Lifecycle Race</td>
      <td>Conflict between the logic of processing a large request body and a premature response finalization (teardown).</td>
    </tr>
    <tr>
      <td rowspan="2"><b>R2</b></td>
      <td>Wang</td>
      <td>Order Violation</td>
      <td>The order expected by the dev is not followed.</td>
    </tr>
    <tr>
      <td>Our</td>
      <td>Lifecycle Race</td>
      <td>The lifecycle (protocol) expected by the dev is not followed due to a race condition.</td>
    </tr>
  </tbody>
</table>

## Setup
```
git clone https://github.com/holepunchto/bare-http1.git
cd bare-http1
git checkout -f 62eb0ffe5bd187554272684edc24ff23a3e748de

nvm use 22
npm install -g bare-runtime
npm i
npm test
```

## Reported flaky tests
```
(comment all the tests in test.js but "server and client do big writes" and the auxiliar functions)
```

## Utlized config on run-tests.py
```
# ============= CONFIGS =============
PROJECT_ROOT = "projects/bare-http1"
LOG_DIRECTORY = "PRs/pr1529/logs_barehttp1"
TOTAL_RUNS = 1000
LOG_INTERVAL = 20

COMMAND = [
    'npm', 'test'
]
# ===================================
```