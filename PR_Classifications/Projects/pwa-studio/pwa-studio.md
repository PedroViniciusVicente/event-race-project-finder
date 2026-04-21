# Pwa-studio
PR: https://github.com/magento/pwa-studio/pull/743

## Pull Request Title and Description
![PR Title and Description](image1.png)

## Pull Request Code
![PR Code](image2.png)

## Our Pattern Classification
**Stabilization Race:**
In the original test, the use of `await wait()` (from the `waait` library) effectively introduces a minimal delay (similar to `setTimeout(0)`), allowing only a single event loop tick before proceeding. However, this approach does not guarantee that all asynchronous rendering and data-fetching operations, especially those involving React have completed.

As a result, the test may execute assertions (e.g., checking the number of `CategoryTile` components) before the component has finished rendering, leading to flaky outcomes. The fix replaces this approach with `wait-for-expect`, which repeatedly evaluates the assertion until it passes or a timeout is reached. This ensures that the component has reached a stable state before validation occurs.

## Wang Pattern Classification
**Order Violation:**
The intended sequence of events is: (1) initiate component rendering and data fetching, (2) complete all asynchronous updates, and (3) perform assertions on the final rendered output. However, the original implementation does not enforce this ordering, as the test proceeds after an arbitrary and insufficient delay.

## Setup Projeto
```
git clone https://github.com/magento/pwa-studio.git
cd pwa-studio
git checkout b6f4118b011a92252504d4edaa6596748d776d7d # versão anterior ao fix
nvm use 10 # segundo arquivo pwa-studio/.circleci/config.yml
npm install
npm test # jest
```

## Reported flaky tests
```
npx jest packages/venia-concept/src/components/CategoryList/__tests__/categoryList.spec.js -t "renders category tiles" --coverage=false
npx jest packages/venia-concept/src/components/CreateAccount/__tests__/createAccount.spec.js -t "executes validators on submit" --coverage=false
npx jest packages/venia-concept/src/components/CreateAccount/__tests__/createAccount.spec.js -t "calls onSubmit if validation passes" --coverage=false
npx jest packages/venia-concept/src/components/Navigation/__tests__/categoryTree.spec.js -t "child node correctly sets new root and parent ids" --coverage=false
```

