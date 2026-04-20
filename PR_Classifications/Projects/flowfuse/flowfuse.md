PR URL: https://github.com/FlowFuse/flowfuse/pull/4260

## Setup
```
git clone https://github.com/FlowFuse/flowfuse.git
cd flowfuse
git checkout -f 223b40875b49cc4fa7e17f96f843978248aa5862

nvm use 20
npm install
npm run build
npm run test:unit
```

## Reported flaky tests
```
npx mocha 'test/unit/forge/routes/api/team_spec.js' --timeout 10000 --node-option=unhandled-rejections=strict -g 'with all instances and their status'
```

## Utlized config on run-tests.py
```
# ============= CONFIGS =============
PROJECT_ROOT = "projects/flowfuse"
LOG_DIRECTORY = "PRs/pr1510/logs_flowfuse"
TOTAL_RUNS = 1000
LOG_INTERVAL = 20

COMMAND = [
    'npx', 'mocha', 
    'test/unit/forge/routes/api/team_spec.js',
    '--node-option=unhandled-rejections=strict',
    '-g', 'with all instances and their status'
    ]
# ===================================
```