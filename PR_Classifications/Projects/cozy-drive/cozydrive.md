# Cozy-drive
PR URL: https://github.com/cozy/cozy-drive/pull/2940

## Pull Request Title and Description
![PR Title and Description](image2.png)

## Pull Request Code
![PR Code](image1.png)

## Description
In this test, the `FilesViewer` component triggers a `fetchMore` operation when additional files are needed. The mocked `fetchMore` function introduces an artificial delay (`sleep(10)`), simulating asynchronous data fetching. However, during this delay, the React component may undergo additional re-render cycles due to internal state updates or non-deterministic scheduling in the rendering process.
As a result, the `fetchMore` function may be invoked more than once, leading to intermittent failures in the assertion `toHaveBeenCalledTimes(1)`, as shown in the log below.

```
yarn run v1.22.22
$ env NODE_ENV='test' cozy-scripts test src/drive/web/modules/viewer/FilesViewer.spec.jsx
info Visit https://yarnpkg.com/en/docs/cli/run for documentation about this command.

(node:14019) [DEP0040] DeprecationWarning: The `punycode` module is deprecated. Please use a userland alternative instead.
(Use `node --trace-deprecation ...` to show where the warning was created)
FAIL src/drive/web/modules/viewer/FilesViewer.spec.jsx
  FilesViewer
    ✓ should render a Viewer (47 ms)
    ✓ should fetch the file if necessary (25 ms)
    ✕ should fetch more files if necessary (43 ms)
    ✓ should get decryption key when file is encrypted (14 ms)

  ● FilesViewer › should fetch more files if necessary

    expect(jest.fn()).toHaveBeenCalledTimes(expected)

    Expected number of calls: 1
    Received number of calls: 2

      135 |     const viewer = await screen.findByText('Viewer')
      136 |     expect(viewer).toBeInTheDocument()
    > 137 |     expect(fetchMore).toHaveBeenCalledTimes(1)
          |                       ^
      138 |   })
      139 | 
      140 |   it('should get decryption key when file is encrypted', async () => {

      at call (src/drive/web/modules/viewer/FilesViewer.spec.jsx:137:23)
      at tryCatch (node_modules/regenerator-runtime/runtime.js:63:40)
      at Generator._invoke (node_modules/regenerator-runtime/runtime.js:293:22)
      at Generator.next (node_modules/regenerator-runtime/runtime.js:118:21)
      at asyncGeneratorStep (node_modules/@babel/runtime/helpers/asyncToGenerator.js:3:24)
      at _next (node_modules/@babel/runtime/helpers/asyncToGenerator.js:25:9)

Test Suites: 1 failed, 1 total
Tests:       1 failed, 3 passed, 4 total
Snapshots:   0 total
Time:        4.053 s
Ran all test suites matching /src\/drive\/web\/modules\/viewer\/FilesViewer.spec.jsx/i.
error Command failed with exit code 1.
```

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
      <td>The intended order was for the single “fetchMore” operation to happen after the non-deterministic re-render operation.</td>
    </tr>
    <tr>
      <td>Our</td>
      <td><s>Stabilization Race</s><br><br><b>[After conflict resolution]</b><br>Lifecycle Race</td>
      <td><s>The test asserts a “fetchMore” call count, but the system observed is not fully stable, so it does not guarantee a single “fetchMore” call due to eventual re-renders or internal updates that trigger redundant executions.</s><br><br> The test asserts a “fetchMore” call count, but fails to understand the component setup lifecycle that does not guarantee a single “fetchMore” call due to eventual re-renders or internal updates that trigger redundant executions.</td>
    </tr>
    <tr>
      <td rowspan="2"><b>R2</b></td>
      <td>Wang</td>
      <td>Order Violation</td>
      <td>The assert expects the function to be called once, but another call(s) may occur before, violating the expected order.</td>
    </tr>
    <tr>
      <td>Our</td>
      <td>Lifecycle Races</td>
      <td>It failed to take the lifecycle of the component into account.</td>
    </tr>
  </tbody>
</table>


## Setup
```
git clone https://github.com/cozy/cozy-drive.git
cd cozy-drive
git checkout -f 6b000507ef2f66f22990b607dafdf564832b8cde

nvm use 22
yarn install
yarn test

(got to file src/drive/web/modules/viewer/FilesViewer.spec.jsx and remove the .skip from test "should fetch more files if necessary")
```

## Reported flaky tests
```
yarn test src/drive/web/modules/viewer/FilesViewer.spec.jsx
```

## Utlized config on run-tests.py
```
# ============= CONFIGS =============
PROJECT_ROOT = "projects/cozy-drive"
LOG_DIRECTORY = "PRs/pr1147/logs_cozydrive"
TOTAL_RUNS = 1000
LOG_INTERVAL = 20

COMMAND = [
    'yarn', 'test',
    'src/drive/web/modules/viewer/FilesViewer.spec.jsx'
]
# ===================================
```