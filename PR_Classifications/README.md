# Classification, Setup, Logs and Discussions for Pull Requests:

Inside the [Projects](Projects) folder we present the following artifcats for each of the 27 analyzed projects:

- Information from the Pull Request reporting the concurrency issue;
- Project setup and test execution instructions;
- Logs of the flaky behavior;
- Classification table with the rationale from both researchers.


## Classification Table:

| PR | Project Name | My Pattern | Wang Pattern | Main Layer(s) Affected |
| :--- | :--- | :--- | :--- | :--- |
| https://github.com/cs4218/cs4218-2420-ecom-project-team15/pull/21 | cs4218-2420-ecom-project-team15 | External Race | N/A | Database - Mongodb (Backend <-> DBMS) |
| https://github.com/magento/pwa-studio/pull/743 | pwa-studio | Stabilization Race | Order Violation | FrontEnd - React |
| https://github.com/skholkhojaev/milo/pull/1 | milo | Stabilization Race | Order Violation | FrontEnd |
| https://github.com/CesiumGS/cesium/pull/8444 | cesium | External Race and Other | Starvation | BackEnd |
| https://github.com/WordPress/gutenberg/pull/58629 | gutenberg | Stabilization Race | Order Violation | FrontEnd - React |
| https://github.com/goodeggs/express-promise-middleware/pull/2 | express-promise-middleware | Stabilization Race | Atomic Violation | BackEnd - Express |
| https://github.com/ONSdigital/eq-author-app/pull/100 | eq-author-app | Concurrent Access Race | Atomic Violation | FrontEnd - React |
| https://github.com/BrightspaceUI/core/pull/1120 | core | Stabilization Race | Order Violation | BackEnd |
| https://github.com/pouchdb/pouchdb/pull/8513 | pouchdb | Lifecycle Race | Starvation | Database - PouchDB |
| https://github.com/YunzheZJU/holo-schedule/pull/117 | holo-schedule | Concurrent Access Race | Atomic Violation | FrontEnd - Storage |
| https://github.com/tshino/vscode-vz-like-keymap/pull/227 | vscode-vz-like-keymap | External Race and Other | N/A | FrontEnd - IDE VSCode |
| https://github.com/cozy/cozy-drive/pull/2940 | cozy-drive | Stabilization Race | N/A | FrontEnd - React |
| https://github.com/holepunchto/bare-http1/pull/17 | bare-http1 | Lifecycle Race | Order Violation | BackEnd |
| https://github.com/adobe/fetch/pull/396 | fetch | External Race | Order Violation | BackEnd |
| https://github.com/pinojs/pino/pull/1186 | pino | Lifecycle Race | Order Violation | BackEnd |
| https://github.com/prisma/prisma/pull/26331 | prisma | External Race and Other | Starvation | Database - PostgreSQL |
| https://github.com/FlowFuse/flowfuse/pull/4260 | flowfuse | Stabilization Race | Order Violation | BackEnd |
| https://github.com/ing-bank/lion/pull/1387 | lion | Lifecycle Race | Order Violation | BackEnd |
| https://github.com/muxinc/hls-video-element/pull/32 | hls-video-element | Lifecycle Race | Order Violation | FrontEnd |
| https://github.com/ReactiveX/rxjs/pull/7005 | rxjs | Lifecycle Race | Atomic Violation | BackEnd |
| https://github.com/tldr-pages/tldr-node-client/pull/329 | tldr-node-client | External Race and Other | Starvation | BackEnd - Cache |
| https://github.com/fastify/session/pull/242 | session | External Race and Other | N/A | BackEnd - Date |
| https://github.com/miguelcobain/ember-css-transitions/pull/114 | ember-css-transitions | Stabilization Race | Order Violation | FrontEnd |
| https://github.com/docknetwork/sdk/pull/259 | sdk | External Race | N/A | Backend - util-crypto |
| https://github.com/ATMmonitor667/Stockify/pull/18 | Stockify | External Race | N/A | Database - Supabase |
| https://github.com/natcap/invest-workbench/pull/156 | invest-workbench | Stabilization Race | Order Violation | FrontEnd - React |
| https://github.com/adfinis/timed-frontend/pull/583 | timed-frontend | Stabilization Race | Order Violation | FrontEnd |