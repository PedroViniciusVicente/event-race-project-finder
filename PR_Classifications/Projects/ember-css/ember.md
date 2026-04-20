PR URL: https://github.com/miguelcobain/ember-css-transitions/pull/114

## Setup
```
git clone https://github.com/miguelcobain/ember-css-transitions.git
cd ember-css-transitions
git checkout -f e0c866630b99ae2397632fd4bcad9e555ff6091d

nvm use 18 #v18.20.8
pnpm i && pnpm i # aparentemente são 2 vezes

colocar o .only no teste na linha 45 do arquivo: test-app/tests/integration/components/css-transition-test.js:
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