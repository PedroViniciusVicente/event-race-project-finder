# Ember-css-transitions
PR URL: https://github.com/miguelcobain/ember-css-transitions/pull/114

## Pull Request Title and Description
![PR Title and Description](image2.png)

## Pull Request Code
![PR Code](image1.png)

## Our Pattern Classification
**Stabilization Race:**
In this test, the code relies on `await waitFor('#my-element_clone.example-leave')` to ensure that a DOM element with a specific transition class is present. However, `waitFor` alone seems to not be sufficient to guarantee that the rendering and animation has completed. As noted in the PR, `waitFor` may resolve too late or at an inconsistent point in the rendering cycle, leading to false-negative failures.
The fix introduces an additional synchronization step using `window.requestAnimationFrame`, which ensures that the browser has completed at least one rendering frame before proceeding. Furthermore, the conditional re-check with `waitFor` reinforces that the DOM has reached the expected state. This combination ensures that the UI has fully stabilized before assertions are made.

## Wang Pattern Classification
**Order Violation:**
The core problem is that the test assumes a specific ordering between asynchronous events: (1) the triggering of a transition, (2) the DOM update reflecting the transition state, and (3) the execution of assertions. However, due to the asynchronous nature of rendering and animation scheduling (e.g., via `requestAnimationFrame`), this order is not reliably enforced.
As a result, assertions may execute before the DOM has been updated to the expected state, violating the intended sequence of operations.

## Setup
```
git clone https://github.com/miguelcobain/ember-css-transitions.git
cd ember-css-transitions
git checkout -f e0c866630b99ae2397632fd4bcad9e555ff6091d

nvm use 18 #v18.20.8
pnpm i && pnpm i

add .only on test in line 45 from file: test-app/tests/integration/components/css-transition-test.js:
      test(`enter and leave transitions work (${i.name})`, async function (assert) {



pnpm run test
``` 

## Reported flaky tests
```
pnpm --filter '*' test:ember
```

## Utlized config on run-tests.py
```
# ============= CONFIGS =============
PROJECT_ROOT = "projects/ember-css-transitions"
LOG_DIRECTORY = "PRs/pr946/logs_ember"
TOTAL_RUNS = 1000
LOG_INTERVAL = 20

COMMAND = [
    'pnpm', '--filter', 
    '*', 'test:ember'
]
# ===================================
```