# Prisma
PR URL: https://github.com/prisma/prisma/pull/26331

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
git clone https://github.com/prisma/prisma.git
cd prisma
git checkout -f d7415932e4a7149f1f4758b3fd573c4ada44dc31

nvm use 18
pnpm i
pnpm build


cd docker (other tab)
docker compose up postgres 

cd packages/migrate
pnpm test
```

## Reported flaky tests
```
pnpm test src/__tests__/DbPull/postgresql-views.test.ts -t "postgresql-views with preview feature, views defined and then removed re-introspection with views removed"

(if other tests are executing, use test.only on the selected test)
```

## Utlized config on run-tests.py
```
# ============= CONFIGS =============
PROJECT_ROOT = "projects/prisma/packages/migrate"
LOG_DIRECTORY = "PRs/pr1667/logs_prisma"
TOTAL_RUNS = 1000
LOG_INTERVAL = 20

COMMAND = [
    'pnpm', 'test', 
    'src/__tests__/DbPull/postgresql-views.test.ts',
    '-t', 'postgresql-views with preview feature, views defined and then removed re-introspection with views removed'
]
# ===================================
```