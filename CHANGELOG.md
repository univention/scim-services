# Changelog

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
