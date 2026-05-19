# Rxjs
PR URL: https://github.com/ReactiveX/rxjs/pull/7005

## Pull Request Title and Description
![PR Title and Description](image1.png)

## Pull Request Code
![PR Code](image2.png)

## Description
In this scenario, multiple subscribers are synchronously added and removed (`firstValueFrom(combineLatest([source, source]))`) to a shared observable created with `shareReplay({ refCount: true })`. Due to the internal implementation, the reset (teardown) logic may register before the actual subscription to the source observable occurs. As a result, when subscriptions and unsubscriptions happen almost simultaneously, the teardown logic (reset) may execute before the subscription setup is fully completed leading to an inconsistent internal state.

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
      <td>Atomicity Violation</td>
      <td>The subscribing action of checking the observable reference counter and establishing the connection should be atomic, so the reset of another source does not interfere in the establishment of connection from other source.</td>
    </tr>
    <tr>
      <td>Our</td>
      <td>Lifecycle Race</td>
      <td>The unsubscription teardown logic (reset) can be triggered and executed incorrectly when multiple sources subscribe simultaneously and then immediately unsubscribe from the observer (with FirstValueFrom), causing the observer to lose track of its connections.</td>
    </tr>
    <tr>
      <td rowspan="2"><b>R2</b></td>
      <td>Wang</td>
      <td>Atomicity Violation</td>
      <td>The expected atomic order expected by the dev is violated by multiple calls.</td>
    </tr>
    <tr>
      <td>Our</td>
      <td>Lifecycle Race</td>
      <td>The bug is related to unexpected behavior of the object’s lifecycle.</td>
    </tr>
  </tbody>
</table>

## Setup
```
git clone https://github.com/ReactiveX/rxjs.git
cd rxjs
git checkout -f 5d4c1d9a37b1347217223adb0d9e166fd85f67a9

nvm use 16

<!-- yarn install --frozen-lockfile
yarn nx run-many -t build lint test --exclude=rxjs.dev
yarn workspace rxjs test -->

npm ci
npm test
```

go to src/internal/operators/share.ts and change:

```
if (
    !connection &&
    // Check this shareReplay is still activate - it can be reset to 0
    // and be "unsubscribed" _before_ it actually subscribes.
    // If we were to subscribe then, it'd leak and get stuck.
    refCount > 0
) {
```
to
´´´
if (!connection) {
´´´

## Reported flaky tests
```
<!-- yarn workspace rxjs test -g "should only subscribe once each with multiple synchronous subscriptions and unsubscriptions" -R spec -->

npx cross-env TS_NODE_PROJECT=tsconfig.mocha.json mocha --config spec/support/.mocharc.js \"spec/operators/shareReplay-spec.ts\" -R spec -g "should only subscribe once each with multiple synchronous subscriptions and unsubscriptions"
```

## Utlized config on run-tests.py
```
# ============= CONFIGS =============
PROJECT_ROOT = "projects/rxjs"
LOG_DIRECTORY = "PRs/pr857/logs_rxjs"
TOTAL_RUNS = 1000
LOG_INTERVAL = 20

COMMAND = [
    'npx', 'cross-env', 'TS_NODE_PROJECT=tsconfig.mocha.json', 'mocha',
    '--config', 'spec/support/.mocharc.js', '\"spec/operators/shareReplay-spec.ts\"',
    '-R', 'spec',
    '-g', 'should only subscribe once each with multiple synchronous subscriptions and unsubscriptions'
]
# ===================================
```