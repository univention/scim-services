# Changelog

## [0.44.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.43.0...v0.44.0) (2025-09-26)


### Features

* **scim-client:** Allow to configure additional scopes to send when requesting an OIDC auth token ([8c28536](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/8c2853670cf55b2c6f2c1742c4f128e461a1ab38)), closes [univention/dev/internal/team-nubus#1428](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1428)

## [0.43.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.42.6...v0.43.0) (2025-09-22)


### Features

* Add content type negotiation middleware for SCIM server and client ([03233c5](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/03233c5de95d3b0a4287c57c80e56ec5cb2033ab)), closes [univention/dev/internal/team-nubus#1429](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1429)
* Handle JWT and JSON tokens without 'exp' claim optimistically ([dac0772](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/dac0772358f66652104479894568512df43b40ec)), closes [univention/dev/internal/team-nubus#1430](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1430)


### Bug Fixes

* handle plain JSON tokens in addition to JWT in Authenticator ([4f77d88](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/4f77d887aef76942afc886cd1e3796937839313d)), closes [univention/dev/internal/team-nubus#1430](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1430)
* JWT validation ([f35f433](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/f35f4333f373c43ac3813dfeb103cf63106cdc06)), closes [univention/dev/internal/team-nubus#1430](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1430)
* QA suggestions ([1c05f8a](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/1c05f8a711b0b26f8555d25daac0d88f761c299a)), closes [univention/dev/internal/team-nubus#1430](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1430)

## [0.42.6](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.42.5...v0.42.6) (2025-09-12)


### Bug Fixes

* **deps:** Update gitregistry.knut.univention.de/univention/dev/nubus-for-k8s/common-helm/testrunner Docker tag to v0.24.5 ([98ddb28](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/98ddb28e4622226e43e16145c05d18c1fa9e0406)), closes [#0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/issues/0)

## [0.42.5](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.42.4...v0.42.5) (2025-09-11)


### Bug Fixes

* **deps:** Update gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python Docker tag to v5.2.3-build.20250909 ([0ec36cb](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/0ec36cbb1695cca787cad7ea73c8d2f2dd80f581)), closes [#0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/issues/0)

## [0.42.4](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.42.3...v0.42.4) (2025-09-05)


### Bug Fixes

* **deps:** Update gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python Docker tag to v5.2.2-build.20250828 ([5393bbb](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/5393bbba4d4f23ac90712f6f3d722e338393bff4)), closes [#0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/issues/0)
* **deps:** Update gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python Docker tag to v5.2.2-build.20250904 ([b7b618e](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/b7b618e00dc6bbc3d313abdb988820d1e240898d)), closes [#0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/issues/0)

## [0.42.3](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.42.2...v0.42.3) (2025-08-29)


### Bug Fixes

* Update base image to version 5.2.2-build.20250821 ([03f9da7](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/03f9da7f3ec61485d191cdbd8b7787f6b92fa7f8)), closes [univention/dev/internal/team-nubus#1385](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1385)

## [0.42.2](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.42.1...v0.42.2) (2025-08-12)


### Bug Fixes

* **scim-client:** Fix unit tests with latest provisioning ([361f318](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/361f318172dba204e6f8e60b7d633b42d58350d5)), closes [univention/dev/internal/team-nubus#1360](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1360)
* **scim-client:** Reenable scim-client/server integration tests ([f5f6fb4](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/f5f6fb41b1a691b39200e4068a846d7e551bd2ed)), closes [univention/dev/internal/team-nubus#1360](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1360)

## [0.42.1](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.42.0...v0.42.1) (2025-08-08)


### Bug Fixes

* **python-scim:** Update to latest python-scim versions ([7a4201b](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/7a4201b728d3fb0c392c8231197666f4738e8b80)), closes [univention/dev/internal/team-nubus#1360](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1360)
* **scim-client:** Pin provisioning version to 0.60.1 because no messages are received when using latest version 0.60.2 ([f7547c7](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/f7547c794d036b917fa433e70aff834745fc2ded)), closes [univention/dev/internal/team-nubus#1360](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1360)

## [0.42.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.41.3...v0.42.0) (2025-08-05)


### Features

* Add SCIM client and server documentation ([5215c19](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/5215c194751d326b888dbe83115deccfda01c90f)), closes [univention/dev/internal/team-nubus#1190](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1190)

## [0.41.3](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.41.2...v0.41.3) (2025-07-30)


### Bug Fixes

* **scim-consumer:** Assert if tests run into timeout ([eaeac3a](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/eaeac3a130c41caa5111b5c58261b9be30064e88))
* **scim-consumer:** Refactor scim-consumer to use less hardcoded stuff and make it more compatible with different scim-servers ([cfd562e](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/cfd562eec95bc7d61603c0b0625b8671c1f1cb3c)), closes [univention/dev/internal/team-nubus#1361](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1361)
* **udm-transformer-lib:** Add support for pydantic models discovered via ScimClient ([e11a6e4](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/e11a6e47e6acfd07ed23ffe5ac103a4cbacccf2a))

## [0.41.2](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.41.1...v0.41.2) (2025-07-23)


### Bug Fixes

* **scim-udm-transformer-lib:** Correctly generated SCIM name.formatted ([4c0d0ad](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/4c0d0ad8fb6ab9d9d3f0ca3f9c000451237a4dc0)), closes [univention/dev/internal/team-nubus#1346](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1346)

## [0.41.1](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.41.0...v0.41.1) (2025-07-21)


### Bug Fixes

* **scim-server:** Make sure pod is restarted on configmap change ([923f175](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/923f175fa19e94dc2ca7d3e24d6f3fc75256961d)), closes [univention/dev/internal/team-nubus#1345](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1345)

## [0.41.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.40.0...v0.41.0) (2025-07-17)


### Features

* update wait-for-dependency to 0.35.0 ([8a917ec](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/8a917ecd4c81b9292bc6050103ed5e8481949f69)), closes [univention/dev/internal/team-nubus#1320](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1320)

## [0.40.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.39.1...v0.40.0) (2025-07-17)


### Features

* update ucs-base to 5.2.2-build.20250714 ([1afb46e](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/1afb46ebb5117786cad40ae627c27d89d4e11d01)), closes [univention/dev/internal/team-nubus#1320](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1320)


### Bug Fixes

* use ucs-base-python image ([834f5e0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/834f5e0eeec3029058d7d29547adc511841cc8b8)), closes [univention/dev/internal/team-nubus#1320](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1320)

## [0.39.1](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.39.0...v0.39.1) (2025-07-15)


### Bug Fixes

* **scim-server:** Fix unsetting 'secondaryOrgUnits' ([a04ae44](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/a04ae44b980bd88421027abad4624a2319d5a9fb)), closes [univention/dev/internal/team-nubus#1341](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1341)

## [0.39.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.38.2...v0.39.0) (2025-07-15)


### Features

* support unset extended attributes ([4561027](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/456102707dd4eab60758311d403a3e0bc96cecec)), closes [univention/dev/internal/team-nubus#1341](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1341)


### Bug Fixes

* handle schema in SCIM patch operations ([74fb5fe](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/74fb5fef974c759ed69abe8b46003ccd38d65fc9))

## [0.38.2](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.38.1...v0.38.2) (2025-07-15)


### Bug Fixes

* **scim-consumer:** Add additional udm-listener env vars required for latest version ([c865922](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/c8659225e0ae7e2ea76dae5c87cbacfbf465653b)), closes [univention/dev/internal/team-nubus#1327](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1327)
* **scim-server:** Use correct URL to wait for keycloak ([8ab7483](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/8ab7483a7e9533889aee772e4cfa84a24e029278)), closes [univention/dev/internal/team-nubus#1327](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1327)

## [0.38.1](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.38.0...v0.38.1) (2025-07-07)


### Bug Fixes

* **docker:** Make container builds reproducible and cleanup ([31c542d](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/31c542da2a75b62a321548a3c168fe365ee0943a)), closes [univention/dev/internal/team-nubus#1315](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1315)

## [0.38.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.37.1...v0.38.0) (2025-07-04)


### Features

* Add performance tests for SCIM API (MS1) ([0db4e98](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/0db4e9888dc89c5a19583168c700d88ac827401f))

## [0.37.1](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.37.0...v0.37.1) (2025-07-03)


### Bug Fixes

* **scim-server:** Used forked scim2-tester to correctly handle multiple extensions and creating reference objects ([947c240](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/947c2408d1ae11821dbf8cf845bdeda3b0287b0b)), closes [univention/dev/internal/team-nubus#1193](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1193)

## [0.37.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.36.0...v0.37.0) (2025-07-02)


### Features

* **scim-consumer:** Added tests for extensions. ([f5aaf6b](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/f5aaf6b25ed91f8b4bace5afbb2345b66a1010bd)), closes [univention/dev/projects/scim/scim-services#4](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/issues/4)
* **scim-consumer:** Fix pipelines. ([cb74ded](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/cb74ded1ccd543cb08e4bc3040efd87c6e3e5c01)), closes [univention/dev/projects/scim/scim-services#4](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/issues/4)
* **scim-dev-server:** Added extensions to scim-dev-server ([6e647ad](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/6e647ad75afab2f7ba47b82970092ac1cbffc255)), closes [univention/dev/projects/scim/scim-services#4](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/issues/4)


### Bug Fixes

* **scim-consumer:** Fixed profile error in docker compose. ([fba41b6](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/fba41b6dabafbf02da635463c72e13d500fed878)), closes [univention/dev/projects/scim/scim-services#4](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/issues/4)
* **sicm-consumer:** Fix docker-compose.yaml ([1639238](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/1639238a400b314dec46833480631b72e94d48de)), closes [univention/dev/projects/scim/scim-services#4](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/issues/4)

## [0.36.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.35.0...v0.36.0) (2025-07-01)


### Features

* **scim-dev-server:** Added Helm charts for scim2-server ([2c54193](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/2c541937fb08b0dd8aa4d62b7d62deb9f00cb86a)), closes [univention/dev/internal/team-nubus#1280](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1280)


### Bug Fixes

* **scim-consumer:** Changes for Helm deployment. ([8490a28](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/8490a283e2d647480621326bab8b7a0cd3a3b5bf)), closes [univention/dev/internal/team-nubus#1280](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1280)

## [0.35.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.34.0...v0.35.0) (2025-06-27)


### Features

* **scim-server:** Adapt the repo to use  UniventionUser:2.0 ([f983969](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/f983969d52fd3c0c93c4f0bd87df981d6c0f7dff))

## [0.34.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.33.0...v0.34.0) (2025-06-26)


### Features

* **scim-server:** Add support for mapping scim roles to configurable UDM property ([9a89976](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/9a8997602948fc48a94e7e2f9b7800c3be608324)), closes [univention/dev/internal/team-nubus#1256](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1256)

## [0.33.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.32.0...v0.33.0) (2025-06-26)


### Features

* **scim-server:** Ignore password policy and history if password is generated by scim-server ([f1155ee](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/f1155ee32cd1fa66a5201c852f91bacd80b58154)), closes [univention/dev/internal/team-nubus#1198](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1198)

## [0.32.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.31.0...v0.32.0) (2025-06-26)


### Features

* **scim-consumer:** Authenticator class to retrieve a keycloak service account token using the client-credentials flow ([0027c90](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/0027c908e3e6fc13321ffb7c701fa5b112ce47db)), closes [univention/dev/internal/team-nubus#1247](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1247)
* **scim-consumer:** Change from keycloak-specific client-credentials flow inplementation to an IDP agnostic implementation ([9f265fc](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/9f265fc20ae55426465c5e5c1d60d116b7a69d7e)), closes [univention/dev/internal/team-nubus#1247](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1247)
* **scim-consumer:** Integrate the new OIDC authenticator with the scim client and make it a HTTPX authentication plugin ([c841173](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/c8411737558538c9bbb531376c2856c026c3ba67)), closes [univention/dev/internal/team-nubus#1247](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1247)


### Bug Fixes

* **scim-consumer:** Add OIDC configuration to the helm chart ([be9e56f](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/be9e56f0acf9a629c7655519dba3c95621fda839)), closes [univention/dev/internal/team-nubus#1247](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1247)
* **scim-consumer:** Further refinement of the scim-consumer helm chart and tests ([4d51732](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/4d5173222a569d60a3c874f3322f958b92243f36)), closes [univention/dev/internal/team-nubus#1247](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1247)
* **scim-consumer:** Remove unnecessary OIDC audience configuration option ([cefdfb6](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/cefdfb6d765897628c12eecc5101133de5cbc704)), closes [univention/dev/internal/team-nubus#1247](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1247)
* **scim-consumer:** unify back to LDAP_HOST instead of LDAP_URI because ldap3 configures TLS / StartTLS separately ([bc50510](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/bc50510e17bc7408a41cf8b2bfc0cac97384fdda)), closes [univention/dev/internal/team-nubus#1247](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1247)
* **scim-consumer:** Update scim consumer helm chart to better align with the other nubus charts ([38ec8b4](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/38ec8b4325547bcadac991efa93423b272fbeb3e)), closes [univention/dev/internal/team-nubus#1247](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1247)
* Update the helm-test-harness and fix small bugs detected by the new tests ([b136d6b](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/b136d6b0a5e5041dfa1e249e89601780e1e18f6b)), closes [univention/dev/internal/team-nubus#1247](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1247)

## [0.31.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.30.0...v0.31.0) (2025-06-26)


### Features

* **scim-server:** Update auth implementation to allow OIDC client credentials flow tokens ([d06e689](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/d06e689b233d3fdbaea183312b55a36a67eaa6bf)), closes [univention/dev/internal/team-nubus#1279](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1279)


### Bug Fixes

* **scim-server:** Remove helm templates for setting up user and keycloak ([d7f412a](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/d7f412a19e6e6c94119c7c1ed678f026a3ab35d0)), closes [univention/dev/internal/team-nubus#1279](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1279)
* **scim-server:** Update authorization documentation ([e40e838](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/e40e838a3346cdc31446718bf10f1e2fcaa441de)), closes [univention/dev/internal/team-nubus#1279](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1279)

## [0.30.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.29.2...v0.30.0) (2025-06-25)


### Features

* **scim-consumer:** Add support for Univention scim-server as target system. ([8c2a2cf](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/8c2a2cf769f9c1b8f3b1346ed458e4459a2297a9)), closes [univention/dev/internal/team-nubus#1207](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1207)


### Bug Fixes

* Changes and pipeline for scim-server and scim-consumer integration. ([d3c0848](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/d3c0848bf1ae0832545e1bf177211f9ce6d0dfad)), closes [univention/dev/internal/team-nubus#1207](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1207)
* **scim-consumer:** Fixed LDAP connection errors and replaced YAML lib in Helm test. ([9ed282b](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/9ed282b458098de7d2a772abbafd99553db809b6)), closes [univention/dev/internal/team-nubus#1207](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1207)
* **scim-consumer:** Revert Helm chart test to previous version. ([169dfda](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/169dfdabb79c4b7cdd7dc9f25ae0f8450a703d85)), closes [univention/dev/internal/team-nubus#1207](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1207)
* **Sonarqube:** Modified coverage call and pipeline configuration. ([8e71293](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/8e71293fd7b69708887fd13e72c5ae04f69c29c4)), closes [univention/dev/projects/scim/scim-services#2](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/issues/2)

## [0.29.2](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.29.1...v0.29.2) (2025-06-23)


### Bug Fixes

* **scim-server:** Fix some value mappings from scim to UDM ([c280bd2](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/c280bd234c4eae0cf7dcf9db2c5a20888f801c7d)), closes [univention/dev/internal/team-nubus#1191](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1191)

## [0.29.1](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.29.0...v0.29.1) (2025-06-20)


### Bug Fixes

* **scim-consumer:** Add new LDAP env variables to the scim-consumer helm chart ([d5f0c87](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/d5f0c87788def1ce2d79a682bc3297f3b0720f59)), closes [univention/dev/internal/team-nubus#1228](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1228)
* **scim-consumer:** Changes for external_id mappping. ([35cec1b](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/35cec1b8b708293d2af3bb555173d39dd76e73e6)), closes [univention/dev/internal/team-nubus#1228](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1228)
* **scim-consumer:** Fix group sync ([e2ef123](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/e2ef123656c2f8763cc99c52b9240b92c04fe39f)), closes [univention/dev/internal/team-nubus#1228](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1228)

## [0.29.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.28.0...v0.29.0) (2025-06-18)


### Features

* add externalId mapping configuration to helm chart ([6ed6553](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/6ed65530a16d9c4252d6417d43b47311349d4a02)), closes [univention/dev/internal/team-nubus#1235](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1235)
* get by externalId ([977a7ac](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/977a7ace2f433c95353f67161fdaeac06c6dfa3a)), closes [univention/dev/internal/team-nubus#1235](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1235)


### Bug Fixes

* **scim-server:** Implement listing resources on base URL ([2093522](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/20935229e22fd15fd2da0a701289eee0c541ce9b)), closes [univention/dev/internal/team-nubus#1235](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1235)

## [0.28.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.27.0...v0.28.0) (2025-06-13)


### Features

* **scim-server:** Add Customer1 and Univention extensions ([9ea0ffe](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/9ea0ffe5012a9cee1bb013d0134c1ce011fcefdb)), closes [univention/dev/internal/team-nubus#1152](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1152)
* **scim-server:** Apply correct SCIM <-> UDM mapping ([8f82811](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/8f82811df53fad40985bcc7232929d9847f1e780)), closes [univention/dev/internal/team-nubus#1152](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1152)


### Bug Fixes

* **scim-server:** Add unit tests for group and user mapping ([b715288](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/b7152889b0073b914f9db2598f72e40c638e7c93)), closes [univention/dev/internal/team-nubus#1152](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1152)
* **scim-server:** Do not use global app object in tests, make sure every test uses its own app object ([228b934](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/228b9348efde5970ab2475bf50e362991062adb4)), closes [univention/dev/internal/team-nubus#1152](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1152)
* **scim-server:** Fix formarting after rebase ([de949fc](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/de949fc83e453406c58f674fe71e60df7f699e44))
* **scim-server:** Imrpove schema and resource type handling ([685c7bd](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/685c7bdb423163d7b40b9f0351dc3733b67c11c7)), closes [univention/dev/internal/team-nubus#1152](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1152)
* **scim-server:** Move our scim2-models and extensions to own module ([2117a0a](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/2117a0ad2b4b336121dd65f1eaa2c2ea5c1779f0)), closes [univention/dev/internal/team-nubus#1152](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1152)

## [0.27.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.26.0...v0.27.0) (2025-06-13)


### Features

* disable patch ([a172269](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/a1722699d27c83216cb66cfd863ffd5783d05882))
* make patch support configurable ([f4979ce](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/f4979ceebd2926dabb676f7696ce601f822f47bc))

## [0.26.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.25.0...v0.26.0) (2025-06-10)


### Features

* Add correlation ID support to logging ([f6b7761](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/f6b7761be934ce514b422df5649b7012f646237c))

## [0.25.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.24.0...v0.25.0) (2025-06-06)


### Features

* **scim-server:** Delete old e2e tests file ([4dca2de](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/4dca2deb5bda71bc5685f1e8c05ca8d6cd43729f))
* **scim-server:** Move other test files ([c4fc3f0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/c4fc3f0a65a0113de0d7fe255140b7eda67544b4))
* **scim-server:** new patch logic, includes a filter and parser and handling of multi valued attributes ([ebf86fe](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/ebf86fe60b488c90803dc1a719ca34ebe8dfe41b))
* **scim-server:** new patch logic, includes a filter and parser and handling of multi valued attributes as well as some tests ([28e9777](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/28e977783e2ea1dd25529cfa2ddc7a265f412b26))
* **scim-server:** Precommit ([cf37efb](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/cf37efb804840de5513ad9aee8b7474c23023da0))
* **scim-server:** Refactoring tests ([09d35b5](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/09d35b5b7f08566ea1b937ccf0fd8569c0ff32df))
* **scim-server:** Refactoring tests ([b74eba5](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/b74eba5a0e9b4fcb402090c8a7909f313e5403d0))

## [0.24.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.23.0...v0.24.0) (2025-06-05)


### Features

* **scim-consumer:** Added support for filtering actions by attribute ([25991cc](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/25991ccb08555d4db8bf31749afee418dbfd132a)), closes [univention/dev/internal/team-nubus#1203](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1203)
* **scim-consumer:** Changed iterator handling ([3925cef](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/3925cef0080249ecffb85e0338b89eb53db3fa8b)), closes [univention/dev/internal/team-nubus#1172](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1172)
* **scim-consumer:** Merged pytest.ini into pyproject.toml ([7c12bbe](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/7c12bbef1b6f236d46c436d8ebc9e74890f732de)), closes [univention/dev/internal/team-nubus#1172](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1172)
* **scim-consumer:** Refactoring, add new class ScimConsumer ([973f4b5](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/973f4b5771585dcd26525bc006e2c15fad994883)), closes [univention/dev/internal/team-nubus#1203](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1203)
* **scim-consumer:** Updated test call ([71f880c](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/71f880ceb59dc85262606c44fa8bee107c26a1d4)), closes [univention/dev/internal/team-nubus#1172](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1172)

## [0.23.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.22.0...v0.23.0) (2025-06-05)


### Features

* **scim-server:** Implement empty password handling ([f6d7351](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/f6d73516b5553882d4cc8cc1c3c5edc45bde8130)), closes [univention/dev/internal/team-nubus#1198](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1198)


### Bug Fixes

* **scim-server:** Fix schemas route to respond correct scim schemas ([4fdd487](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/4fdd4871bd98315e64a9c9ecdc5688810c31714b)), closes [univention/dev/internal/team-nubus#1198](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1198)

## [0.22.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.21.0...v0.22.0) (2025-06-05)


### Features

* **scim-consumer:** Initial helm chart ([d12e525](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/d12e525fed36eb1cc8fb9dc0e52ff657c30ffb9e)), closes [univention/dev/internal/team-nubus#1173](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1173)


### Bug Fixes

* **scim-consumer:** Allign helm chart with best-practices using the helm-test-harness from common-helm ([bd1650f](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/bd1650f09caf73b61cde1c2ee8abfd9650c932b5)), closes [univention/dev/internal/team-nubus#1173](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1173)
* **scim-consumer:** Fix the entrypoint of the scim-consumer container image ([0b5a779](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/0b5a779f86bc77cf43740c10630cacddc6850955)), closes [univention/dev/internal/team-nubus#1173](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1173)
* **scim-consumer:** Helm chart successfully deploys the scim-consumer ([d142c84](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/d142c84200c13c5ba34d38405723f9d6a3b7ea29)), closes [univention/dev/internal/team-nubus#1173](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1173)

## [0.21.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.20.0...v0.21.0) (2025-06-03)


### Features

* **scim-server:** Fix random_url scim-tester test by adding route for /{id} ([aa850a6](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/aa850a68bf67175243438fd940156d8d82339278)), closes [univention/dev/internal/team-nubus#1194](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1194)

## [0.20.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.19.1...v0.20.0) (2025-05-30)


### Features

* **scim-server:** Group patch and first test ([fa52f96](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/fa52f967b7031e38787bf56c46b5dafaad40f955))
* **scim-server:** More tests for group patch ([03170c7](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/03170c7c4f84fa93e7172677911795065c56d62b))

## [0.19.1](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.19.0...v0.19.1) (2025-05-30)


### Bug Fixes

* **scim-server:** Fix startup without auth for example via env AUTH_ENABLED=[secure] ([9271605](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/927160539274283a3308b5f8529d7ec3345eb31c)), closes [univention/dev/internal/team-nubus#1151](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1151)

## [0.19.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.18.0...v0.19.0) (2025-05-30)


### Features

* **scim-server:** Add id cache and map group members and user groups ([5137fe8](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/5137fe8b7a3dc5fff43a0887516270466504853f)), closes [univention/dev/internal/team-nubus#1175](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1175)


### Bug Fixes

* **scim-server:** Add e2e tests for group member mappings ([4e69417](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/4e69417f3a2d849bfa98a68c787c5946e5edabfa)), closes [univention/dev/internal/team-nubus#1175](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1175)
* **scim-server:** Add test for invalid members of group when mapping from UMD to SCIM ([db88d51](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/db88d51c4232330ad9fa258324a28aa45622b81e)), closes [univention/dev/internal/team-nubus#1175](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1175)
* **scim-server:** Create mock for UDM REST API client and use it, fix detected bugs ([9c4c9dc](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/9c4c9dcb931bc31848deb6262b8caa1363f43733)), closes [univention/dev/internal/team-nubus#1175](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1175)
* **scim-server:** Improve tests by reducing manual specified test fixtures ([cbc78c1](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/cbc78c1c991fae9f36f610345ab74395ebdd9413)), closes [univention/dev/internal/team-nubus#1175](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1175)
* **scim-server:** Make cache optional for udm<->scim mappers ([5336815](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/5336815d6d3deebaf08839483b63eea93d04fa4a)), closes [univention/dev/internal/team-nubus#1175](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1175)
* **scim-server:** Update e2e test to properly test current group members and user groups mapping ([859c2d2](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/859c2d2d90f9b9055f6486d65fff8269fdd935ad)), closes [univention/dev/internal/team-nubus#1175](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1175)

## [0.18.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.17.0...v0.18.0) (2025-05-30)


### Features

* **authz:** Check if user is in a given group, only members of the given group are allowed to access the SCIM API ([4111a8e](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/4111a8e21a7a7266f735ab25652f68bbfdaa6282)), closes [univention/dev/internal/team-nubus#1151](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1151)
* **authz:** Implement proper oauth2 support ([c0c472a](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/c0c472a6e860124b82accc881d2d80edf2b8422e)), closes [univention/dev/internal/team-nubus#1151](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1151)


### Bug Fixes

* **authn:** Check correct claims for nubus keycloak ([36112cb](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/36112cb649dd3cbe0c47242b1b6a8bb7761f49c1)), closes [univention/dev/internal/team-nubus#1151](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1151)
* **helm:** Correctly hand existingSecret for udm-secret ([d06b27c](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/d06b27c544484ebddd5cbca0e97b06bf729bfb31)), closes [univention/dev/internal/team-nubus#1151](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1151)
* **uv:** Do not require explicit python version ([19608c9](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/19608c9e606c0b342481ae87d03f73d3ba64dcaa)), closes [univention/dev/internal/team-nubus#1151](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1151)

## [0.17.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.16.0...v0.17.0) (2025-05-27)


### Features

* **scim-consumer:** Added build and test to CI/CD pipeline. ([83366ae](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/83366ae1fe7a27406eb7ddff1eed810da93d23dc)), closes [univention/dev/internal/team-nubus#1171](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1171)
* **scim-consumer:** Added MR review changes. ([6eea8a6](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/6eea8a60e455abd44b205447e442e10cab5e3752)), closes [univention/dev/internal/team-nubus#1171](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1171)
* **scim-consumer:** Bump UCS image and added dependend project.toml files. ([81b0496](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/81b0496e80e7ef79cd027b6d30a32090986217c1)), closes [univention/dev/internal/team-nubus#1171](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1171)
* **scim-consumer:** First draft ([137a681](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/137a6811ea8c52dc24ecac24028aa29fa0dadfec)), closes [univention/dev/internal/team-nubus#1171](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1171)
* **scim-consumer:** Optimized dockerfile ([a32ce53](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/a32ce53d887437095db7b91bfa33eecf7a052d02)), closes [univention/dev/internal/team-nubus#1171](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1171)
* **scim-consumer:** Refactoring and inline documentation. ([bcb4d0e](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/bcb4d0ec1f78c821cfa77279115d771f70526863)), closes [univention/dev/internal/team-nubus#1171](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1171)
* **scim-consumer:** Refactoring and integration tests ([f30b7f5](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/f30b7f5e27b6c8c58864c1e577ed296708f9d42d)), closes [univention/dev/internal/team-nubus#1171](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1171)

## [0.16.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.15.0...v0.16.0) (2025-05-21)


### Features

* Add request logging middleware ([159cd5b](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/159cd5b190bf226cf876aecb215572ff146aa839))
* add timing middleware ([9a95a3c](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/9a95a3c06fc8f0cab724d97d4dc60a8c72b68158))
* increase max body length for request logging ([8b2873a](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/8b2873ad6e0bbf0b060bfdad807ceb99441455b7))

## [0.15.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.14.0...v0.15.0) (2025-05-19)


### Features

* Add SCIM error handling and schema retrieval improvements ([7c531ab](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/7c531ab5c85b4db260ff64fa869307b02c08493e))

## [0.14.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.13.1...v0.14.0) (2025-05-16)


### Features

* **scim-server:** add a more generic patch function ([04f26b1](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/04f26b184ea1ea347709a75730022c57e5fe5fa0))
* **scim-server:** Add more error tests for unhappy paths ([9c42e8a](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/9c42e8accb5cb26f29e7af388e1e33e6c704539b))
* **scim-server:** comment fixed ([6f01b13](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/6f01b13d40bf5bca4c3203ffc8ed1d5f47e4222c))
* **scim-server:** format ([0df74e2](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/0df74e28c8b530468bab243c050b94916ba081b5))
* **scim-server:** implement SCIM PATCH support for Users with validation and tests ([1cb846e](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/1cb846e716b86e80c8d7c1f370978f2843a1facd))
* **scim-server:** Refactor utils to mixin ([c46b34d](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/c46b34de4e09aac5276e5acfc5a5b9ed1b327e89))
* **scim-server:** remove obsolete prints ([3f95efd](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/3f95efd4783a63ad80686aeacfeeee1fb46fc137))

## [0.13.1](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.13.0...v0.13.1) (2025-05-13)


### Bug Fixes

* add missing enterprise schema to resource type ([adc3e19](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/adc3e1914ab35e77695206bf4d7c6f31a2a915ab))

## [0.13.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.12.2...v0.13.0) (2025-05-13)


### Features

* add e2e tests for DELETE endpoints ([59c4b99](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/59c4b9991fed40fa74aa9a5564ff717246939994))

## [0.12.2](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.12.1...v0.12.2) (2025-05-12)


### Bug Fixes

* SCIM schema endpoint to return ListResponse ([6e1963d](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/6e1963d81fbab1c78ad1da518815d6cdb4123eeb))

## [0.12.1](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.12.0...v0.12.1) (2025-05-12)


### Bug Fixes

* resource types endpoint response model ([a280928](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/a2809287d3956cd14e99c99be32348101a0bc14c))

## [0.12.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.11.1...v0.12.0) (2025-05-11)


### Features

* move and upgrade ucs-base-image to 0.17.3-build-2025-05-11 ([8807f9a](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/8807f9a73469a3f3d962c2af59cac5d3ae3ca45f))

## [0.11.1](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.11.0...v0.11.1) (2025-05-10)


### Bug Fixes

* move addlicense pre-commit hook ([f739004](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/f739004588d325c221e74a7132a0a3fa3693a5fe))
* move docker-services ([ca3a759](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/ca3a75950a25957b4dfaffee309a8696a02c5352))
* update common-ci to main ([3d29386](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/3d29386987c7945f9f71212018f11bda00f33cf4))

## [0.11.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.10.0...v0.11.0) (2025-05-09)


### Features

* implement PUT user and group ([9ccf1cd](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/9ccf1cdb3bfb8d159e429518966938d63f62611d))

## [0.10.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.9.1...v0.10.0) (2025-05-09)


### Features

* create group functionality ([29dcb24](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/29dcb24a3f7228b416b53f477933b18c3d3b12e3))
* create user functionality ([83dd774](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/83dd77423cf515b024a82482b3208f49f17ee24d))

## [0.9.1](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.9.0...v0.9.1) (2025-05-06)


### Bug Fixes

* **tests:** Make sure test docker compose does not write file outside of container ([16ca0e6](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/16ca0e61ea1e10927c1db0ad4c312d6a99ea2f28)), closes [univention/dev/internal/team-nubus#1099](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1099)

## [0.9.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.8.0...v0.9.0) (2025-05-06)


### Features

* **scim-server:** Adding ResourceType endpoint and tests ([0b4840b](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/0b4840be7033c2fc2acf3fb1cf425d78e8083b5a)), closes [univention/dev/internal/team-nubus#1145](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1145)
* **scim-server:** Code Review changes ([1822c23](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/1822c23cb69296e39231e629d3c5a3e1ff9621db)), closes [univention/dev/internal/team-nubus#1145](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1145)
* **scim-server:** Code Review changes ([7cd1f85](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/7cd1f855f9fd6b85617ff3e87390d258e0eb89d9)), closes [univention/dev/internal/team-nubus#1145](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1145)
* **scim-server:** Code Review changes ([38c6a4a](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/38c6a4a3eff7830a5f553b4ab23073634ecf7650)), closes [univention/dev/internal/team-nubus#1145](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1145)
* **scim-server:** E2E Test for ResourceTypes endpoint ([868352f](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/868352f91e5675edbaef1eb94898e146179f848e)), closes [univention/dev/internal/team-nubus#1145](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1145)
* **scim-server:** E2E Test for ResourceTypes endpoint adapted to new test config ([d2b2638](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/d2b263855feec028115fcda1d78f1a50e0eb4baa)), closes [univention/dev/internal/team-nubus#1145](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1145)
* **scim-server:** formatting and linting ([fdda9b2](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/fdda9b2a60736d5c19c9c48cd86442f026a91bdc)), closes [univention/dev/internal/team-nubus#1145](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1145)
* **scim-server:** Pin version of ldap-server, fix env vars to reflect current version 0.38.0 ([bd11917](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/bd11917a744195a0e4738f5caf9f53c6e2d02588)), closes [univention/dev/internal/team-nubus#1145](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1145)

## [0.8.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.7.0...v0.8.0) (2025-05-05)


### Features

* **helm:** Add ingress ([ecf900f](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/ecf900f99327857ec3999854a4cb78921dc028ce)), closes [univention/dev/internal/team-nubus#1112](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1112)
* **helm:** Allow configuring UDM parameters ([80530e5](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/80530e50a87476791bd959f7f19feda8c747015c)), closes [univention/dev/internal/team-nubus#1112](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1112)
* **helm:** Integrate keycloak handling to helm chart ([a6c5289](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/a6c5289db676e6a56a797f394041ff125c4fd1ac)), closes [univention/dev/internal/team-nubus#1112](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1112)

## [0.7.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.6.1...v0.7.0) (2025-05-05)


### Features

* **scim-server:** Implement list groups via Groups endpoint ([7fc6be0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/7fc6be0b64150d6ae4403c6a67829b21a1326194)), closes [univention/dev/internal/team-nubus#1105](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1105)
* **scim-server:** Implement list users via Users endpoint ([d66c866](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/d66c866579f2a2060fcf1a4156b4c79769af2cdb)), closes [univention/dev/internal/team-nubus#1104](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1104)

## [0.6.1](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.6.0...v0.6.1) (2025-04-30)


### Bug Fixes

* **scim-server:** Fix repo dependency injection ([2c5c28f](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/2c5c28f984f1ad21fdaf41451fb511212fb77ec2)), closes [univention/dev/internal/team-nubus#1104](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1104)
* **tests:** Fix startup of ldap-server docker and cleanup docker-compose file ([ba167eb](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/ba167eb74fd22fc30e900602f23593a5d61d1a5d)), closes [univention/dev/internal/team-nubus#1104](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1104)

## [0.6.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.5.0...v0.6.0) (2025-04-28)


### Features

* extend schemas and test ([30a560b](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/30a560b39e590addb9d0f6d4a76a51ef42395886))
* **scim-server:** Add schema endpoint and test ([0a0df3c](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/0a0df3c163fc89406b3b9f66c5fbafd546cc040c)), closes [univention/dev/internal/team-nubus#1145](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1145)
* **scim-server:** Formats and refactoring ([55b260e](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/55b260e07b1db508d4e1e1e4b89df3f60d191d06)), closes [univention/dev/internal/team-nubus#1145](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1145)
* **scim-server:** Formats and refactoring ([d705fb4](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/d705fb4a89e62ae3aaddff9879bdd298d57f42da)), closes [univention/dev/internal/team-nubus#1145](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1145)
* **scim-server:** Working on code review changes ([b128a22](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/b128a22ca66e221d5f36759d33f262486d10736b)), closes [univention/dev/internal/team-nubus#1145](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1145)

## [0.5.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.4.0...v0.5.0) (2025-04-25)


### Features

* **scim-server:** Add logging ([ac5fc9b](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/ac5fc9bf332f57e7059b10a52050a9ba5f7e4cdb)), closes [univention/dev/internal/team-nubus#1145](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1145)
* **scim-server:** Add test adaptions for service configuration endpoint ([e9c25fc](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/e9c25fcee3bf09073af8cba603a12751b0af0707)), closes [univention/dev/internal/team-nubus#1145](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1145)
* **scim-server:** Add test adaptions for service configuration endpoint ([711b534](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/711b534ec9365b2460743bc19673e1f0222c2033)), closes [univention/dev/internal/team-nubus#1145](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1145)
* **scim-server:** Formats and refactoring ([b794a14](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/b794a149b143571069dc0e97a636a8dcb8eb3e43)), closes [univention/dev/internal/team-nubus#1145](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1145)

## [0.4.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.3.4...v0.4.0) (2025-04-24)


### Features

* extend udm2scim mapping for user attributes ([272da7d](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/272da7d1167671d41799fc90af982393949fe96a))
* implement UDM ([1d11b6a](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/1d11b6a1a0c6a73ced7b32545873ecbc35b7653e))
* qa improvements and tests WIP ([c9f64c3](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/c9f64c33164525df569db86f61603cf8586d1198))
* QA suggestions ([568aed1](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/568aed1399803fa55e89ea88d619789b304b98f2))
* use udm-rest-api-client ([e04cb46](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/e04cb46252a05c450e01d3d5d59009a3fdeed249))


### Bug Fixes

* fix problems with running tests locally ([81a85f5](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/81a85f5b11159d032db98a031ebb06379ecb47d2))
* lint ([9a86981](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/9a869817dc1fc251de5da2ad06307db3abf23a45))
* refactor fixes ([d742e5d](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/d742e5d11cb017c87f981287faec24af94b4bb5f))
* remove code spell checking ([c0e603e](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/c0e603e73ac888740380e7dbcdbd231f7259bd32))
* remove non workign date mappings ([f0dace1](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/f0dace1464dca504e69dfc59072536eba04abdf4))

## [0.3.4](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.3.3...v0.3.4) (2025-04-23)


### Bug Fixes

* **authentication:** Fix authentication ([f1eae26](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/f1eae26821b0d62f639ab980f97419091669e354)), closes [univention/dev/internal/team-nubus#1112](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1112)
* **scim-server:** Fix app startup after refactoring ([82d0764](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/82d0764e8aae48c8c22b908a206093ff55259498)), closes [univention/dev/internal/team-nubus#1112](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1112)

## [0.3.3](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.3.2...v0.3.3) (2025-04-15)


### Bug Fixes

* imports and file headers ([30d14d2](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/30d14d288a64e28021e6e16f89b08c2a342536fc))
* use FastAPI dependencies, make imports of DI transparent, simplify REST setup, use HTTP status constants ([b36d218](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/b36d218a88ecfa4ad65406c5ce71da3467019baf))

## [0.3.2](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.3.1...v0.3.2) (2025-04-15)


### Bug Fixes

* **logging:** Use structured logging in rest API ([1768597](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/176859713e773d14fb532892e15dd26c69484633)), closes [univention/dev/internal/team-nubus#1098](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1098)
* **rest-api:** User generic id as logger key for all ids ([785416e](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/785416ef5005dc80fd0063915e9f447329c96bc5)), closes [univention/dev/internal/team-nubus#1098](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1098)

## [0.3.1](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.3.0...v0.3.1) (2025-04-14)

### Bug Fixes

* bad markdown by semantic-release-bot ([1af3720](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/1af37202fee01b40db1426c2a05049d8894dbe96))

## [0.3.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.2.0...v0.3.0) (2025-04-11)

### Features

* **authentication:** Implement OpenID connect authentication ([5da8175](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/5da817558b581d0af3d336021ee796cd555bb4c1)), closes [univention/dev/internal/team-nubus#1098](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1098)

## [0.2.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.1.1...v0.2.0) (2025-04-08)

### Features

* add CrudManager intermediate layer ([d1faa7c](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/d1faa7c5572e0755d72eac64e5b753c5256f8c17))

## [0.1.1](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.1.0...v0.1.1) (2025-04-03)

### Bug Fixes

* **project:** Add license information to package ([909a7b9](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/909a7b924473b78649dcd6e8291519285daf66eb))

## [0.1.0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/compare/v0.0.1...v0.1.0) (2025-04-03)

### Features

* Add dependency injection and add authentication stub allow all ([2bf94de](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/2bf94de72155965a9d4499af2f10df77be6018f7)), closes [univention/dev/internal/team-nubus#1097](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1097)
* Add unit test for authentication ([2aaf5f0](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/2aaf5f04926083f16d3ac4a798b1716c14befbf1)), closes [univention/dev/internal/team-nubus#1097](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1097)
* boilerplate code ([8e9e999](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/8e9e999088d5d2be6453f9e76d51cd1aae07cbe5))
* **dependency-injection:** Move services and repos to dependency injection ([5313a45](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/5313a450fc9f671630533a964e3df9337310d817)), closes [univention/dev/internal/team-nubus#1097](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1097)

### Bug Fixes

* Add nested type for ListResponse ([37b83e9](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/37b83e937962457aea98cc78b1267086b3c1f3c9)), closes [univention/dev/internal/team-nubus#1097](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1097)
* add type hints to rest endpoints ([e77385d](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/e77385da4355741afcaa12b63f11ada92c3d7c88))
* add type hints to UDM and SCIM mappers ([ab36310](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/ab363102620082d5e08ff6296fc605e9e12e7806))
* Improve auth Depends ([1e34144](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/1e34144a9bd036c9031e3f71600a8f35ad9f7c3d)), closes [univention/dev/internal/team-nubus#1097](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1097)
* **pipeline:** Add conventional-pre-commit pre-commit for common-ci lint-commit-message job ([fc64225](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/fc64225377ef91fb15d8a991ab230a0312848892)), closes [univention/dev/internal/team-nubus#1097](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1097)
* **tests:** Allow running tests without the need of rebuilding the test docker image ([b712f6f](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/b712f6f271eb5786114141e485f58196da057432)), closes [univention/dev/internal/team-nubus#1097](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1097)
* **tests:** Fix running tests in pipeline ([87c211e](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/87c211eb7a1390e6a1c79f785d292cacebc26cdc)), closes [univention/dev/internal/team-nubus#1097](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1097)
* **tests:** Improve unit tests and fix pre commit hooks ([e85bca9](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/e85bca9f45136f669c19c3a2061f28985c98d973)), closes [univention/dev/internal/team-nubus#1097](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1097)
* type hints in domain ([c397442](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/c397442cf6867629e86c77f4c1f50e66f247977a))
* typo in file name ([eee71b2](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/eee71b290451ec5c015758bfd2856ee7f9792577))

## 0.0.1 (2025-03-31)

### Features

* Add  simple docker compose file and stuff for compose file to dockerfile, add deps for testing, add copied base and base default conf from directory importer ([f2a57c1](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/f2a57c140afeaf347d643eff0d9b64cabc1c1c3e))
* add a basic fast api app to the scim-server subproject ([779be1d](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/779be1db28eb5227184d00c3ab1ff0c46cb78373))
* add dockerfile ([660cd34](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/660cd3407086a378d6278085d96401a0e22fc30c))
* Add gitlab job for tests ([a52ac60](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/a52ac609713df7ad68150bc9b84de1493eafd53f))
* Add kyverno stubs ([1900c02](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/1900c02f42e5a3dfcdcee8ba55b5ea546d07a268))
* Add more kyverno rules and testing ([91fc03c](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/91fc03cb06f6ba7cff02d3a9880a1cb6cda5f92b))
* add pytest to scim-server ([f09af22](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/f09af22d35e9bc13413fd9bbf0acb289f746f197))
* add requirements.txt ([c55634c](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/c55634c44da55c6c35bcd47912ba95f93de89253))
* add return type to test function ([540f3cf](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/540f3cfd104b26b303db5a76f23b778b31f3c41d))
* add stub Helm chart and boilerplate .helmignore and README.md ([f9813da](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/f9813da44de78d2ee60bed7f79974b79b41f65a4))
* Add values yaml with adapted values from directory importer ([0e7fab4](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/0e7fab48caf2f5ed302eff8b498149b88fc77764))
* Change test dir in gitlab ci ([dfc3a95](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/dfc3a9576f217f2433935956b57d26ed2ff705ed))
* Dockerfile changes ([4e00604](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/4e00604caab3f72f7350f813108c6302b1441e49))
* format changes and readme additions ([7fa12c7](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/7fa12c78bccba63502df78f8dc53fec5f74439d6))
* gitlab ci changes ([1f007af](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/1f007af94014cb1786a96ddc2a4bb4a50cc2878c))
* gitlab ci changes remove linit commit messages for now as it crashes since hooks are missing ([27c534b](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/27c534b8a72119c8f7c0cb96e784cf61bfe7d09e))
* gitlab file changes to include image build and publish ([137ec6c](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/137ec6c166a7496e7c641af93860f2ae36355543))
* pytest for dev deps only ([f2f04bb](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/f2f04bb2f839f45b5cca379992fa96d8550704d4))
* uv lock changes, formatting changes ([b91d3c1](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/b91d3c118bda12ef8902120ecf0349e1335a9736))

### Bug Fixes

* Add some more logging ([9506cfd](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/9506cfdbec7fc000793d702468e5f572deeb6734))
* Get the project and dockerfile into proper shape ([af9336d](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/af9336da4aa2616a7bd96a2426b05dd7213259de))
* pre commit ([3610140](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/36101405bcab0c4a358b37f8ebb5c086c28610e0))
* pre commit for conf files ([ed86e05](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/ed86e055eccd40c5d41be547673118953fca2f6f))
* reactivate and fix private lancelog dependency ([99fe3d4](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/99fe3d4796b808e6b6c6fa89a51b45d3b3077db7))
* refactoring for codespell ([dc6d384](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/commit/dc6d3844265c2410150bbf840cd3e551f842040e))
