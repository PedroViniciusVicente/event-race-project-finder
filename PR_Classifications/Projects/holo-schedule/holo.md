# holo-schedule
PR URL: https://github.com/YunzheZJU/holo-schedule/pull/117

## Pull Request Title and Description
![PR Title and Description](image1.png)

## Pull Request Code
![PR Code](image3.png)

![PR Code](image2.png)


## Description
This case involves multiple asynchronous operations concurrently accessing and modifying a shared resource (`storage.local`) without proper synchronization. In the original implementation, multiple update operations could execute in parallel, each performing a read–modify–write sequence. Without coordination, these operations may interleave in such a way that one update overwrites the result of another, leading to lost updates and an inconsistent final state in local storage.

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
      <td>The actions of reading from and writing to a local storage were intended to be atomic, leading to inconsistent states when used by concurrent operations without a locking mechanism.</td>
    </tr>
    <tr>
      <td>Our</td>
      <td>Concurrent Access</td>
      <td>The test executes concurrent updates to the same local storage to execute updates.</td>
    </tr>
    <tr>
      <td rowspan="2"><b>R2</b></td>
      <td>Wang</td>
      <td>Atomicity Violation</td>
      <td>Atomicity expected between getStorage and storage.set in each line, but subsequent lines can interfere in the atomicity expected.</td>
    </tr>
    <tr>
      <td>Our</td>
      <td>Concurrent Access</td>
      <td>multiple concurrent accesses to the same local storage provokes the bug.</td>
    </tr>
  </tbody>
</table>

## Setup
```
git clone https://github.com/YunzheZJU/holo-schedule.git
cd holo-schedule/
git checkout -f 43f8670b6075e3dd70e7ccf13a46c6e7267bae0a

nvm use 18
yarn
yarn run web-ext:build

yarn run test


```

## Reported flaky tests
```
npx jest projects/holo-schedule/src/background/store/store.test.js -t "should subscribe live" --coverage=false
```

## Utlized config on run-tests.py
```
# ============= CONFIGS =============
PROJECT_ROOT = "projects/holo-schedule"
LOG_DIRECTORY = "PRs/pr727/logs_holo"
TOTAL_RUNS = 1000
LOG_INTERVAL = 20

COMMAND = [
    'npx', 'jest', 
    'projects/holo-schedule/src/background/store/store.test.js', '-t',
    'should subscribe live'
]
# ===================================
```