# Changelog

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
