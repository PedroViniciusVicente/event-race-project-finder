PR: https://github.com/skholkhojaev/milo/pull/1

the PR above was merged into a test branch, the merge in the used branch (stage) was made here: https://github.com/skholkhojaev/milo/commit/b1351a6df6de10659dad4dba7bb4a9ade8e5b838


commit history: https://github.com/skholkhojaev/milo/commits/stage/?since=2025-01-13&until=2025-01-15


## Setup Projeto
```
git clone https://github.com/skholkhojaev/milo.git
cd milo/
git checkout -f 6718d230085d08935b73fb4c43499cb461f52b60 # Versao antes do fix

# Steps according to readme.md (na verdade, esses passos aparentam não ser totalmente essenciais)
sudo npm install -g @adobe/aem-cli
In a terminal, run "aem up" in this repo's folder.

nvm use 20
npm install

```

## Reported flaky tests
```
npm run test:file -- test/utils/logWebVitalsUtils.test.js
npm run test:file -- test/utils/logWebVitals.test.js

ou
npx wtr --config ./web-test-runner.config.mjs --node-resolve --port=2000 test/utils/logWebVitalsUtils.test.js
npx wtr --config ./web-test-runner.config.mjs --node-resolve --port=2000 test/utils/logWebVitals.test.js
```

## Utlized config on run-tests.py
```
# ============= CONFIGS =============
PROJECT_ROOT = "projects/milo"
LOG_DIRECTORY = "PRs/pr1640/logs_milo"
TOTAL_RUNS = 1000
LOG_INTERVAL = 20

COMMAND = [
    'npx', 'wtr', 
    '--config', './web-test-runner.config.mjs',
    '--node-resolve', '--port=2000',
    'test/utils/logWebVitalsUtils.test.js'
]
# ===================================
```