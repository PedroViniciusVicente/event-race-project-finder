# Classification, Setup, Logs and Discussions for Pull Requests:

Inside the [Projects](Projects) folder we present the following artifcats for each of the 22 analyzed projects:

- Information from the Pull Request reporting the concurrency issue;
- Project setup and test execution instructions;
- Logs of the flaky behavior;
- Classification table with the rationale from both researchers.


## Classification Table:

| PR | Project Name | My Pattern | Wang Pattern | Main Layer(s) Affected |
| :--- | :--- | :--- | :--- | :--- |
| https://github.com/cs4218/cs4218-2420-ecom-project-team15/pull/21 | cs4218-2420-ecom-project-team15 | External Nondeterminism | Order Violation | Backend - DBMS MongoDB |
| https://github.com/magento/pwa-studio/pull/743 | pwa-studio | Stabilization Race | Order Violation | FrontEnd - React |
| https://github.com/skholkhojaev/milo/pull/1 | milo | Stabilization Race | Order Violation | FrontEnd |
| https://github.com/WordPress/gutenberg/pull/58629 | gutenberg | Stabilization Race | Order Violation | FrontEnd - React |
| https://github.com/goodeggs/express-promise-middleware/pull/2 | express-promise-middleware | Stabilization Race | Order Violation | BackEnd - Express |
| https://github.com/ONSdigital/eq-author-app/pull/100 | eq-author-app | Concurrent Access Race | Order Violation | FrontEnd - React |
| https://github.com/BrightspaceUI/core/pull/1120 | core | Stabilization Race | Order Violation | FrontEnd - Timezone |
| https://github.com/pouchdb/pouchdb/pull/8513 | pouchdb | Lifecycle Race | Starvation | FrontEnd - Browser DBMS |
| https://github.com/YunzheZJU/holo-schedule/pull/117 | holo-schedule | Concurrent Access Race | Atomicity Violation | FrontEnd - LocalStorage |
| https://github.com/cozy/cozy-drive/pull/2940 | cozy-drive | Lifecycle Race | Order Violation | FrontEnd - React |
| https://github.com/holepunchto/bare-http1/pull/17 | bare-http1 | Lifecycle Race | Order Violation | BackEnd |
| https://github.com/adobe/fetch/pull/396 | fetch | Lifecycle Race | Order Violation | BackEnd |
| https://github.com/pinojs/pino/pull/1186 | pino | Lifecycle Race | Order Violation | BackEnd |
| https://github.com/prisma/prisma/pull/26331 | prisma | External Nondeterminism | Order Violation | BackEnd - Database |
| https://github.com/FlowFuse/flowfuse/pull/4260 | flowfuse | Stabilization Race | Order Violation | BackEnd |
| https://github.com/ing-bank/lion/pull/1387 | lion | Lifecycle Race | Order Violation | FrontEnd - LocalStorage |
| https://github.com/muxinc/hls-video-element/pull/32 | hls-video-element | Lifecycle Race | Order Violation | FrontEnd |
| https://github.com/ReactiveX/rxjs/pull/7005 | rxjs | Lifecycle Race | Atomicity Violation | BackEnd and (mainly) FrontEnd |
| https://github.com/tldr-pages/tldr-node-client/pull/329 | tldr-node-client | External Nondeterminism | Order Violation | BackEnd - Cache |
| https://github.com/miguelcobain/ember-css-transitions/pull/114 | ember-css-transitions | Stabilization Race | Order Violation | FrontEnd |
| https://github.com/natcap/invest-workbench/pull/156 | invest-workbench | Lifecycle Race | Order Violation | FrontEnd - React |
| https://github.com/adfinis/timed-frontend/pull/583 | timed-frontend | Stabilization Race | Order Violation | FrontEnd |