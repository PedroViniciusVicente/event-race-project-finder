# Cozy-drive
PR URL: https://github.com/cozy/cozy-drive/pull/2940

## Pull Request Title and Description
![PR Title and Description](image2.png)

## Pull Request Code
![PR Code](image1.png)

## Our Pattern Classification
**Stabilization Race:**
In this test, the `FilesViewer` component triggers a `fetchMore` operation when additional files are needed. The mocked `fetchMore` function introduces an artificial delay (`sleep(10)`), simulating asynchronous data fetching. However, during this delay, the React component may undergo additional re-render cycles due to internal state updates or non-deterministic scheduling in the rendering process.

As a result, the `fetchMore` function may be invoked more than once before the component stabilizes, leading to intermittent failures in the assertion `toHaveBeenCalledTimes(1)`, as shown in the log below. The test assumes a stable, single invocation, but does not adequately wait for the component’s state and side effects to settle. This aligns with the definition of a Stabilization Race, where the failure is caused by observing the system before all asynchronous effects and re-renders have completed.

```
yarn run v1.22.22
$ env NODE_ENV='test' cozy-scripts test src/drive/web/modules/viewer/FilesViewer.spec.jsx
info Visit https://yarnpkg.com/en/docs/cli/run for documentation about this command.

=== ERROS ===
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

## Wang Pattern Classification
**Order Violation:**
The intended behavior assumes a specific ordering: the component should trigger `fetchMore` exactly once in response to its initial render and state conditions. However, due to asynchronous rendering and possible re-renders, additional invocations of `fetchMore` may occur before the system reaches a stable state. This indicates that the expected sequence of events: initial render -> single `fetchMore` call -> stable UI, is not being strictly enforced.

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