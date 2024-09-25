# Changelog

## [0.12.0](https://github.com/RedHatProductSecurity/trestle-bot/compare/v0.11.0...v0.12.0) (2024-09-25)


### ⚠ BREAKING CHANGES

* default module entrypoint is now the init command
* Modifies the existing behavior of the rules transform entrypoint
* The check_only flag is no longer available
* Class name update; breaking change to the public API.
* skip_model_list in tasks have been replace with ModelFilter
* This changes the outcome of create_new_default method for component definitions from OSCAL JSON to the rules YAML.

### refactor

* decouples AuthoredObject configuration from tasks ([#98](https://github.com/RedHatProductSecurity/trestle-bot/issues/98)) ([a65042f](https://github.com/RedHatProductSecurity/trestle-bot/commit/a65042f654b955d6b30d2d381419bbf57ece8a9b))


### PSCE-257

* feat(authored): adds rules view creation for component definitions ([#59](https://github.com/RedHatProductSecurity/trestle-bot/issues/59)) ([8261e91](https://github.com/RedHatProductSecurity/trestle-bot/commit/8261e917ca77f42f605570f2fcb2584af3d69ea7))


### Features

* add create-cd entrypoint for component definition bootstrapping ([#67](https://github.com/RedHatProductSecurity/trestle-bot/issues/67)) ([7a73162](https://github.com/RedHatProductSecurity/trestle-bot/commit/7a7316215c84b581e831208554152dbcef0a6fe7))
* add fixes for GitHub Actions integration ([87149dd](https://github.com/RedHatProductSecurity/trestle-bot/commit/87149dd17bcf4450c37657ca28e0301c463c9569))
* add pr_number as an optional output on the action ([ad0d720](https://github.com/RedHatProductSecurity/trestle-bot/commit/ad0d720de665ab2020c62b6b1e3dd400b6dc2fd9))
* add support for nested namespaces in gitlab ([41dfeea](https://github.com/RedHatProductSecurity/trestle-bot/commit/41dfeeabbe4aa88efb13882a4a62ff3b0cb0fcd5))
* adding init command to entrypoints ([#326](https://github.com/RedHatProductSecurity/trestle-bot/issues/326)) ([868c1fa](https://github.com/RedHatProductSecurity/trestle-bot/commit/868c1fae3bb2fa85df734905aa38b33dc37c9b47))
* adds AssembleTask and bot pre-tasks ([360e4e6](https://github.com/RedHatProductSecurity/trestle-bot/commit/360e4e6c1abb87dd18ce8fb1f051889d7d51d7c4))
* adds automated GH pull request creation to trestlebot ([58173bc](https://github.com/RedHatProductSecurity/trestle-bot/commit/58173bca9b26bdc495312c9f03c633dd96f7d4d2))
* adds check to TrestleRule to match compliance-trestle CSV fields ([#173](https://github.com/RedHatProductSecurity/trestle-bot/issues/173)) ([5e64a4a](https://github.com/RedHatProductSecurity/trestle-bot/commit/5e64a4aaf3090107b4eec61a2dfdc76712b4bc01))
* adds component creation default lib for utility ([73d068a](https://github.com/RedHatProductSecurity/trestle-bot/commit/73d068a2438633f9b414de0773b5a4fcd02c6abe))
* adds create default profile logic to AuthoredProfile type ([174497a](https://github.com/RedHatProductSecurity/trestle-bot/commit/174497aacd09c9e7f961dd105fc5f4c3f0669307))
* adds custom dev container configuration ([#84](https://github.com/RedHatProductSecurity/trestle-bot/issues/84)) ([10f93ea](https://github.com/RedHatProductSecurity/trestle-bot/commit/10f93ea9e1f0dc2580513150a78c48c4a73d5859))
* adds image scanning between build and push ([e6e083e](https://github.com/RedHatProductSecurity/trestle-bot/commit/e6e083e413810f7b31926200639978ca146b1fd1))
* adds initial feature for git commits and remote pushes ([d9638d0](https://github.com/RedHatProductSecurity/trestle-bot/commit/d9638d0532751aea30f7b0385842477957544aca))
* adds main_comp_only to create_new_with_filter in ssp.py ([#179](https://github.com/RedHatProductSecurity/trestle-bot/issues/179)) ([398c196](https://github.com/RedHatProductSecurity/trestle-bot/commit/398c196cbbc73995cc275f59d2486b7d6992a32f))
* adds markdown generation to the rules transform entrypoint ([#282](https://github.com/RedHatProductSecurity/trestle-bot/issues/282)) ([84dec70](https://github.com/RedHatProductSecurity/trestle-bot/commit/84dec70d7810abf7306b708104b4c7bf682a49ad))
* adds outputs to Action and CLI ([e9cee26](https://github.com/RedHatProductSecurity/trestle-bot/commit/e9cee269abc084faa3a468364e76b63ceacef10d))
* adds regenerate task task testing to trestlebot pretasks ([68cedab](https://github.com/RedHatProductSecurity/trestle-bot/commit/68cedabc7470c4073ba50aeaa44f57a442584a5f))
* adds support for GitLab as a Provider type ([b39e90e](https://github.com/RedHatProductSecurity/trestle-bot/commit/b39e90efb502dd891d4172aae7abbbeaa0828e20))
* adds version flag to autosync command for assembly task ([#187](https://github.com/RedHatProductSecurity/trestle-bot/issues/187)) ([b9af089](https://github.com/RedHatProductSecurity/trestle-bot/commit/b9af089842b2fb67aa23bbd489c4a8352e2469ca))
* adds workflow to publish container image to GHCR ([3f63bed](https://github.com/RedHatProductSecurity/trestle-bot/commit/3f63bed1d1db08840f09f6030017c39f4d11ddd0))
* allows pull request title to be configurable ([9fee86d](https://github.com/RedHatProductSecurity/trestle-bot/commit/9fee86d56895dd88223ee47843cded398dbf230b))
* **authored:** adds yaml header path to ssp index ([#157](https://github.com/RedHatProductSecurity/trestle-bot/issues/157)) ([1680bdc](https://github.com/RedHatProductSecurity/trestle-bot/commit/1680bdcde3aff3d51050cc082060cad5b0ef185a))
* configure logger for module and control from actions files ([#63](https://github.com/RedHatProductSecurity/trestle-bot/issues/63)) ([1c6e387](https://github.com/RedHatProductSecurity/trestle-bot/commit/1c6e3874671fff5e2b3c9ef7295e882115b0bd27))
* removes provider from init and moves CI templates ([#344](https://github.com/RedHatProductSecurity/trestle-bot/issues/344)) ([21b4043](https://github.com/RedHatProductSecurity/trestle-bot/commit/21b40432f446323ded883c248feaa064ea1cabd6))
* replaces 'check_only' with 'dry_run' option ([#195](https://github.com/RedHatProductSecurity/trestle-bot/issues/195)) ([6e87853](https://github.com/RedHatProductSecurity/trestle-bot/commit/6e87853fbb76a41cbcbf03c21497dea1ac7b80b0))
* **transformer:** Add CSV to YAML with empty writer ([#48](https://github.com/RedHatProductSecurity/trestle-bot/issues/48)) ([fb1ad0b](https://github.com/RedHatProductSecurity/trestle-bot/commit/fb1ad0b2988c6df815e0a5642633c8b955dff083))
* tutorial for GitHub and init command ([#333](https://github.com/RedHatProductSecurity/trestle-bot/issues/333)) ([6334c1f](https://github.com/RedHatProductSecurity/trestle-bot/commit/6334c1f16fffa94bacbb250c95f754ed80abff9b))
* update module default to use init entrypoint ([#329](https://github.com/RedHatProductSecurity/trestle-bot/issues/329)) ([d1490cb](https://github.com/RedHatProductSecurity/trestle-bot/commit/d1490cbde72b204875260cd210f61760e9f3c056))
* updates create_new_with_filter with more filter types and management operations ([#88](https://github.com/RedHatProductSecurity/trestle-bot/issues/88)) ([fa4d953](https://github.com/RedHatProductSecurity/trestle-bot/commit/fa4d953be1f7944a30afbddbf95ccb7df62b4c6a))
* updates skip_items to accept glob patterns ([bb6326f](https://github.com/RedHatProductSecurity/trestle-bot/commit/bb6326f08766f85b5ae80f4cf343eab912506eb7))
* updates SSP generation to include all parts ([#348](https://github.com/RedHatProductSecurity/trestle-bot/issues/348)) ([18c6600](https://github.com/RedHatProductSecurity/trestle-bot/commit/18c6600a47d9833811a045fa60e167608f06a180))


### Bug Fixes

* add markdown-include package to workflow and poetry ([#339](https://github.com/RedHatProductSecurity/trestle-bot/issues/339)) ([c7a05ee](https://github.com/RedHatProductSecurity/trestle-bot/commit/c7a05eebe87f853a435b31abadba8db05d2458a2))
* adds an example row to final CSV to account for skipped rows ([#58](https://github.com/RedHatProductSecurity/trestle-bot/issues/58)) ([b4998f4](https://github.com/RedHatProductSecurity/trestle-bot/commit/b4998f4eb7fa3115c395191dcb91f2b9e8ea5333))
* adds fixes in Dockerfile from Sonarlint ([bff5215](https://github.com/RedHatProductSecurity/trestle-bot/commit/bff5215721b7f158f8e628e3b2e47a5364ca1515))
* adds linter reccomendations ([64613ed](https://github.com/RedHatProductSecurity/trestle-bot/commit/64613ede524841674fc608613b686d84b2d70857))
* adds OSCAL validated component definition types to create-cd ([#191](https://github.com/RedHatProductSecurity/trestle-bot/issues/191)) ([393fd85](https://github.com/RedHatProductSecurity/trestle-bot/commit/393fd8531ab1fa4d657951ecdd7ccde9c9185a74))
* adds quotes around GITHUB_ENV and GITHUB_OUTPUT ([d6eec34](https://github.com/RedHatProductSecurity/trestle-bot/commit/d6eec34fac04a84fbec063ea287fb7a5fd23cda2))
* deletes top level action file from the repository ([#64](https://github.com/RedHatProductSecurity/trestle-bot/issues/64)) ([60ecd41](https://github.com/RedHatProductSecurity/trestle-bot/commit/60ecd41d74f6ac4a88b456f91305801f44e29351))
* **entrypoint:** fixes top level ModelFilter logic ([#71](https://github.com/RedHatProductSecurity/trestle-bot/issues/71)) ([b28e496](https://github.com/RedHatProductSecurity/trestle-bot/commit/b28e4968044430f138d76156868044e9287660f3))
* fixes errors in pre-task execution in cli.py ([cc5f189](https://github.com/RedHatProductSecurity/trestle-bot/commit/cc5f189704f3514b1521b877f02ee82155b82622))
* fixes if statement in get_authored_types and adds unit tests ([17b0497](https://github.com/RedHatProductSecurity/trestle-bot/commit/17b049732d6dfb4d3929cc9b32f9d5e1688b20c2))
* fixes import sorting ([002ba16](https://github.com/RedHatProductSecurity/trestle-bot/commit/002ba16d211cdb9a46d9ca4035c7066392ab8c21))
* fixes syntax error on action.yml ([721008e](https://github.com/RedHatProductSecurity/trestle-bot/commit/721008efbc744060a9f21acaa6826dc6ca061e80))
* fixes table of contents in CONTRIBUTING.md ([#132](https://github.com/RedHatProductSecurity/trestle-bot/issues/132)) ([e8d8372](https://github.com/RedHatProductSecurity/trestle-bot/commit/e8d8372db6146cb31fdb06a7acf5e6d06dbaca5e))
* fixes type hints and simplifies ToRules yaml transformer ([#86](https://github.com/RedHatProductSecurity/trestle-bot/issues/86)) ([dfbf24d](https://github.com/RedHatProductSecurity/trestle-bot/commit/dfbf24ddd01e07576112491bc880f708b1c68464))
* fixes typos in the TrestleBot class in bot.py ([#153](https://github.com/RedHatProductSecurity/trestle-bot/issues/153)) ([12d9b8e](https://github.com/RedHatProductSecurity/trestle-bot/commit/12d9b8e547b8fde140a6958974760c7a6805d816))
* fixes variable spelling error in entrypoint.sh ([3565ed2](https://github.com/RedHatProductSecurity/trestle-bot/commit/3565ed2e43f7508ee62f4009b2025d8067170141))
* prevent extra log messages in stdout ([#199](https://github.com/RedHatProductSecurity/trestle-bot/issues/199)) ([05b0c4c](https://github.com/RedHatProductSecurity/trestle-bot/commit/05b0c4c50f9504bcbc0eee2a65029d90ad04611e))
* remove additional action step for dependency install ([67743e4](https://github.com/RedHatProductSecurity/trestle-bot/commit/67743e4d4d3cd9197d7179bf5b3085c571e20a9a))
* removes default version in GitHub action ([#194](https://github.com/RedHatProductSecurity/trestle-bot/issues/194)) ([a7c6546](https://github.com/RedHatProductSecurity/trestle-bot/commit/a7c6546a9ec7ba79ea6eaa562dc776722dbbe7af))
* retrieve profile path as posix to support relative paths ([b84f38c](https://github.com/RedHatProductSecurity/trestle-bot/commit/b84f38c955336f5c99e3ca2031f57332f6303646))
* updates comparison for ssp type in get_trestle_model_dir ([ed1321c](https://github.com/RedHatProductSecurity/trestle-bot/commit/ed1321ce9d0dab84ae1d9933d24e7e2d88b55ca6))
* updates CSVTransformer to separate controls with spaces instead of commas ([#183](https://github.com/RedHatProductSecurity/trestle-bot/issues/183)) ([30d601a](https://github.com/RedHatProductSecurity/trestle-bot/commit/30d601af463eadc401a7e01d8594558e1922ea2f))
* updates dependabot prefix for conventional commits ([#308](https://github.com/RedHatProductSecurity/trestle-bot/issues/308)) ([ee86f5c](https://github.com/RedHatProductSecurity/trestle-bot/commit/ee86f5c35755686d3fc3adf6ca94e1c4ac8d873e))
* updates Dockerfile entrypoint to show log output ([0cbdcce](https://github.com/RedHatProductSecurity/trestle-bot/commit/0cbdcce0b28069d10ea1db19c5f21aef3a223c7b))
* updates e2e tests checkout ref during image publishing ([#334](https://github.com/RedHatProductSecurity/trestle-bot/issues/334)) ([5439b91](https://github.com/RedHatProductSecurity/trestle-bot/commit/5439b91c7b0ed1d75c7a5ec3f2b3f4e94ea5968a))
* updates entrypoint variable to OSCAL_MODEL from ASSEMBLE_MODEL ([799573e](https://github.com/RedHatProductSecurity/trestle-bot/commit/799573e900ceec69a8410bf8bd487f44bb43e685))
* updates GitHub Actions runner image and restart policy ([#255](https://github.com/RedHatProductSecurity/trestle-bot/issues/255)) ([7fd64e0](https://github.com/RedHatProductSecurity/trestle-bot/commit/7fd64e078bdc445e5a238343dae4c6d34ea1d4ea))
* updates language for linting pre-commit to system ([#133](https://github.com/RedHatProductSecurity/trestle-bot/issues/133)) ([1566b6e](https://github.com/RedHatProductSecurity/trestle-bot/commit/1566b6e3fb4ebb0ec998d55901262b275ab097ff))
* updates logger and entrypoint script to log errors written to stderr ([f9c058b](https://github.com/RedHatProductSecurity/trestle-bot/commit/f9c058b37b1afad1cdb70561a8106632e78ffafb))


### Maintenance

* add a .dockerignore file ([a15bfb6](https://github.com/RedHatProductSecurity/trestle-bot/commit/a15bfb6f83b6514c433e5f62b5b2abe7c3e984e5))
* add branch checkout before pretasks ([bafffec](https://github.com/RedHatProductSecurity/trestle-bot/commit/bafffec8acf5bbdb1708e7bccc4a63eef425cb97))
* adds additional logging messages on bot.py ([7851000](https://github.com/RedHatProductSecurity/trestle-bot/commit/785100082af70fca42c69ad6bf4cafe47354796c))
* adds additional project checks for security and code coverage ([ba88344](https://github.com/RedHatProductSecurity/trestle-bot/commit/ba88344c71f74c4ac183a58022163f588a53faed))
* adds additional type hints to tests and trestlebot pkg ([93f4fc7](https://github.com/RedHatProductSecurity/trestle-bot/commit/93f4fc7caf3d5bf1eadc8ed3da7050ba0f177e27))
* adds automation to update action README.md files ([#123](https://github.com/RedHatProductSecurity/trestle-bot/issues/123)) ([719e2e3](https://github.com/RedHatProductSecurity/trestle-bot/commit/719e2e3365a7f778d5f868ddb3c676d67d3d1ade))
* adds changes to support regeneration features ([a2a3b7e](https://github.com/RedHatProductSecurity/trestle-bot/commit/a2a3b7e0bce1350105548e8a092fa36d1cef3cbd))
* adds correction on how to setup auth for git with user token ([4f5bd4d](https://github.com/RedHatProductSecurity/trestle-bot/commit/4f5bd4d8d2ad9cd821e56da034af8a71683964cf))
* adds docs and gitignore fixes ([71c0b2a](https://github.com/RedHatProductSecurity/trestle-bot/commit/71c0b2ab362ce564a3368cc5b8f65e8b04fc7f47))
* adds E2E tests to ci.yml ([#141](https://github.com/RedHatProductSecurity/trestle-bot/issues/141)) ([c2a47fe](https://github.com/RedHatProductSecurity/trestle-bot/commit/c2a47fe2bb91b45612b423324f8a64f7a1906cec))
* adds fixes for KICS warnings ([#80](https://github.com/RedHatProductSecurity/trestle-bot/issues/80)) ([016438d](https://github.com/RedHatProductSecurity/trestle-bot/commit/016438d0814b239f41c97993efb1e7630237a756))
* adds flake8-print plugin to find unintentional print statements ([07cc533](https://github.com/RedHatProductSecurity/trestle-bot/commit/07cc5337f0d9e11280066a909a4de54abd530d7d))
* adds image signing with cosign to publish.yml ([#82](https://github.com/RedHatProductSecurity/trestle-bot/issues/82)) ([f6f7035](https://github.com/RedHatProductSecurity/trestle-bot/commit/f6f7035303bac110c872708420f3864820d318f6))
* adds initial issues templates ([#73](https://github.com/RedHatProductSecurity/trestle-bot/issues/73)) ([0dafb63](https://github.com/RedHatProductSecurity/trestle-bot/commit/0dafb636b73e34bac7655516cb29be2508fd1fe6))
* adds linting fix ([d7b80f9](https://github.com/RedHatProductSecurity/trestle-bot/commit/d7b80f956046a039e05cdfe29f33ed8e8265e642))
* adds linting fixes from KICS ([4f340f8](https://github.com/RedHatProductSecurity/trestle-bot/commit/4f340f87f4e22e77ba6cb0cc8d32007a4d75c86e))
* adds package information for test packages ([1e4dd70](https://github.com/RedHatProductSecurity/trestle-bot/commit/1e4dd705d5ab7cd24510f6db754605b2bf4fac8c))
* adds semgrep pre-commit and CI action ([#51](https://github.com/RedHatProductSecurity/trestle-bot/issues/51)) ([b522388](https://github.com/RedHatProductSecurity/trestle-bot/commit/b522388a26fc86c55524003d69c0fa95abab572d))
* adds skip-dirs to trivy image scan ([#116](https://github.com/RedHatProductSecurity/trestle-bot/issues/116)) ([3c68011](https://github.com/RedHatProductSecurity/trestle-bot/commit/3c680116d1fa19046972b899e3978f63972f4d34))
* change dependabot frequency to weekly ([#290](https://github.com/RedHatProductSecurity/trestle-bot/issues/290)) ([3da37f7](https://github.com/RedHatProductSecurity/trestle-bot/commit/3da37f7b69538e157b5b48b461140d0f9bfd6d9d))
* changes "in" to "is" in is_gitlab_ci comment ([1db6089](https://github.com/RedHatProductSecurity/trestle-bot/commit/1db6089c5843ad51654319acd75929a9f4d05777))
* changes space separated flag inputs to comma separated ([ad832fe](https://github.com/RedHatProductSecurity/trestle-bot/commit/ad832fedc2417ef34f4262eb1828f7829b8263bb))
* creates composite action with full poetry setup ([88c5bb2](https://github.com/RedHatProductSecurity/trestle-bot/commit/88c5bb2bbddc49e2cf237965def3c058f68edbc6))
* **deps:** adds compliance-trestle-fedramp dependency ([#349](https://github.com/RedHatProductSecurity/trestle-bot/issues/349)) ([aeb6e0c](https://github.com/RedHatProductSecurity/trestle-bot/commit/aeb6e0c59bb0e09ee2142f886e9682a8f8e118e6)), closes [#318](https://github.com/RedHatProductSecurity/trestle-bot/issues/318)
* **deps:** bump compliance-trestle to version 2.5.0 ([#140](https://github.com/RedHatProductSecurity/trestle-bot/issues/140)) ([0485f71](https://github.com/RedHatProductSecurity/trestle-bot/commit/0485f71f352404ae823aafece7569b4ece2b777d))
* **deps:** bump trestle to version v3.3.0 ([#269](https://github.com/RedHatProductSecurity/trestle-bot/issues/269)) ([a2a2db6](https://github.com/RedHatProductSecurity/trestle-bot/commit/a2a2db6bbbcac2bec23b9fe520a0958afc488616))
* **deps:** bumps the default poetry version used in image and the environment to 1.7.1 ([#119](https://github.com/RedHatProductSecurity/trestle-bot/issues/119)) ([aa26991](https://github.com/RedHatProductSecurity/trestle-bot/commit/aa2699199ade9f9197e92ddb97064b5b1ddda479))
* **deps:** updates compliance-trestle to 2.5.1 ([#170](https://github.com/RedHatProductSecurity/trestle-bot/issues/170)) ([8e236d3](https://github.com/RedHatProductSecurity/trestle-bot/commit/8e236d363b76024f527715536958746c22978b08))
* **deps:** updates Dockerfile to upgrade setuptools during build ([#144](https://github.com/RedHatProductSecurity/trestle-bot/issues/144)) ([f7e32d1](https://github.com/RedHatProductSecurity/trestle-bot/commit/f7e32d1451b4b962a22fb769523a056d051f0326))
* docs and config maintenance ([#105](https://github.com/RedHatProductSecurity/trestle-bot/issues/105)) ([ee5cf32](https://github.com/RedHatProductSecurity/trestle-bot/commit/ee5cf328f7af91222c423921c4d81fc8d33c9794))
* fixes comment spelling/grammar errors for run in bot.py ([1c13255](https://github.com/RedHatProductSecurity/trestle-bot/commit/1c13255264f87f8e3676c7bdea7467421103dfb6))
* fixes formatting in bot.py ([84fc114](https://github.com/RedHatProductSecurity/trestle-bot/commit/84fc11479abe29fa10d9929cf60e971a7482b9ac))
* initial python project structure ([6c136af](https://github.com/RedHatProductSecurity/trestle-bot/commit/6c136afe75893f9b79c8b1adb39f59c2d14ebc93))
* **main:** release 0.11.0 ([#307](https://github.com/RedHatProductSecurity/trestle-bot/issues/307)) ([5158116](https://github.com/RedHatProductSecurity/trestle-bot/commit/51581169a383e676f6392d3216f466cb0ed03bfc))
* normalizes and improves readability for container files ([#83](https://github.com/RedHatProductSecurity/trestle-bot/issues/83)) ([70c8950](https://github.com/RedHatProductSecurity/trestle-bot/commit/70c89507393f64efe4349e5cea8bec9793547384))
* remove magic number error codes and replace with constants ([3843611](https://github.com/RedHatProductSecurity/trestle-bot/commit/38436118993037e97317210772413e39adf94c15))
* removes input repository from the safe workspace ([#185](https://github.com/RedHatProductSecurity/trestle-bot/issues/185)) ([983384e](https://github.com/RedHatProductSecurity/trestle-bot/commit/983384ede2f086d3d2c113e8ab88966bda2b0584))
* removes markdown creation from create_new_with_filter ([#159](https://github.com/RedHatProductSecurity/trestle-bot/issues/159)) ([982ba32](https://github.com/RedHatProductSecurity/trestle-bot/commit/982ba32d0e7a7b6480d7e3659373391c7b2bf58c))
* removes todo comments ([#78](https://github.com/RedHatProductSecurity/trestle-bot/issues/78)) ([787fa4f](https://github.com/RedHatProductSecurity/trestle-bot/commit/787fa4f7b1282ff66564f918272958d0fa465304))
* strip any basic auth information before matching ([acc6840](https://github.com/RedHatProductSecurity/trestle-bot/commit/acc6840286bbbc295362cee01f8e62868890e4c1))
* update logging format ([#196](https://github.com/RedHatProductSecurity/trestle-bot/issues/196)) ([87fc2c6](https://github.com/RedHatProductSecurity/trestle-bot/commit/87fc2c693f3282f4a40fa962bc84d87639a5fa26))
* update oscal-model flag in entrypoint.sh ([1998031](https://github.com/RedHatProductSecurity/trestle-bot/commit/1998031bef28b7d65b732caf22744916cef674bf))
* update poetry lock ([#37](https://github.com/RedHatProductSecurity/trestle-bot/issues/37)) ([69a31e5](https://github.com/RedHatProductSecurity/trestle-bot/commit/69a31e5b7555f15078b56ee4e338983feaef6163))
* update publish to push to quay.io ([59ac927](https://github.com/RedHatProductSecurity/trestle-bot/commit/59ac92753f99a13add334bfae18e0df924e9bd04))
* updates code coverage threshold to 80 ([b614cbd](https://github.com/RedHatProductSecurity/trestle-bot/commit/b614cbd6fb1e300f8dd7401a195a742960a10327))
* updates CSVBuilder to handle updates to the compliance-trestle CSVColumns class ([#172](https://github.com/RedHatProductSecurity/trestle-bot/issues/172)) ([bfdd94f](https://github.com/RedHatProductSecurity/trestle-bot/commit/bfdd94f1d6391664b4e7efb3c22f6164e4603089))
* updates descriptions on actions inputs to be more precise ([#184](https://github.com/RedHatProductSecurity/trestle-bot/issues/184)) ([6d42bb4](https://github.com/RedHatProductSecurity/trestle-bot/commit/6d42bb4b93f112e3260e21168cfc4ec140c03b7c))
* updates Dockerfile to comply with GitHub actions guidelines ([ca0a35f](https://github.com/RedHatProductSecurity/trestle-bot/commit/ca0a35fcefba851bd60c98274a8588902620af79))
* updates eval line in entrypoint to fix exit codes ([7ca89d5](https://github.com/RedHatProductSecurity/trestle-bot/commit/7ca89d5c8059e0b0cabe62582ff88f634a041ce3))
* updates how entrypoint handles boolean flags ([9cd4f19](https://github.com/RedHatProductSecurity/trestle-bot/commit/9cd4f194d5a977d0c47ead2b0463dc0b4b9a91e2))
* updates patterns to take a single input from the trestlebot CLI ([ddd0ade](https://github.com/RedHatProductSecurity/trestle-bot/commit/ddd0adec256cef23fe6ba0e0790a092f01072218))
* updates source file header and adds corresponding documentation ([#154](https://github.com/RedHatProductSecurity/trestle-bot/issues/154)) ([929f84c](https://github.com/RedHatProductSecurity/trestle-bot/commit/929f84ca6fa6d282ff6e76198d6d843498d6e75d))
* updates the base images to UBI minimal ([e1e791a](https://github.com/RedHatProductSecurity/trestle-bot/commit/e1e791aaa06738ebcd37d79dec2b7f02654f7557))
* uses predefined GitLab CI variable to find API url ([e3b86e8](https://github.com/RedHatProductSecurity/trestle-bot/commit/e3b86e8ba9000e9aa09bf278319a571e8befcdb2))
* WIP to add ssp creation and ssp index modification ([604e501](https://github.com/RedHatProductSecurity/trestle-bot/commit/604e501b51130eacee03ed838ffa1a5075771569))

## [0.11.0](https://github.com/RedHatProductSecurity/trestle-bot/compare/v0.10.1...v0.11.0) (2024-09-25)


### ⚠ BREAKING CHANGES

* default module entrypoint is now the init command
* Modifies the existing behavior of the rules transform entrypoint

### Features

* adding init command to entrypoints ([#326](https://github.com/RedHatProductSecurity/trestle-bot/issues/326)) ([868c1fa](https://github.com/RedHatProductSecurity/trestle-bot/commit/868c1fae3bb2fa85df734905aa38b33dc37c9b47))
* adds markdown generation to the rules transform entrypoint ([#282](https://github.com/RedHatProductSecurity/trestle-bot/issues/282)) ([84dec70](https://github.com/RedHatProductSecurity/trestle-bot/commit/84dec70d7810abf7306b708104b4c7bf682a49ad))
* removes provider from init and moves CI templates ([#344](https://github.com/RedHatProductSecurity/trestle-bot/issues/344)) ([21b4043](https://github.com/RedHatProductSecurity/trestle-bot/commit/21b40432f446323ded883c248feaa064ea1cabd6))
* tutorial for GitHub and init command ([#333](https://github.com/RedHatProductSecurity/trestle-bot/issues/333)) ([6334c1f](https://github.com/RedHatProductSecurity/trestle-bot/commit/6334c1f16fffa94bacbb250c95f754ed80abff9b))
* update module default to use init entrypoint ([#329](https://github.com/RedHatProductSecurity/trestle-bot/issues/329)) ([d1490cb](https://github.com/RedHatProductSecurity/trestle-bot/commit/d1490cbde72b204875260cd210f61760e9f3c056))
* updates SSP generation to include all parts ([#348](https://github.com/RedHatProductSecurity/trestle-bot/issues/348)) ([18c6600](https://github.com/RedHatProductSecurity/trestle-bot/commit/18c6600a47d9833811a045fa60e167608f06a180))


### Bug Fixes

* add markdown-include package to workflow and poetry ([#339](https://github.com/RedHatProductSecurity/trestle-bot/issues/339)) ([c7a05ee](https://github.com/RedHatProductSecurity/trestle-bot/commit/c7a05eebe87f853a435b31abadba8db05d2458a2))
* updates dependabot prefix for conventional commits ([#308](https://github.com/RedHatProductSecurity/trestle-bot/issues/308)) ([ee86f5c](https://github.com/RedHatProductSecurity/trestle-bot/commit/ee86f5c35755686d3fc3adf6ca94e1c4ac8d873e))
* updates e2e tests checkout ref during image publishing ([#334](https://github.com/RedHatProductSecurity/trestle-bot/issues/334)) ([5439b91](https://github.com/RedHatProductSecurity/trestle-bot/commit/5439b91c7b0ed1d75c7a5ec3f2b3f4e94ea5968a))


### Maintenance

* change dependabot frequency to weekly ([#290](https://github.com/RedHatProductSecurity/trestle-bot/issues/290)) ([3da37f7](https://github.com/RedHatProductSecurity/trestle-bot/commit/3da37f7b69538e157b5b48b461140d0f9bfd6d9d))
* **deps:** adds compliance-trestle-fedramp dependency ([#349](https://github.com/RedHatProductSecurity/trestle-bot/issues/349)) ([aeb6e0c](https://github.com/RedHatProductSecurity/trestle-bot/commit/aeb6e0c59bb0e09ee2142f886e9682a8f8e118e6)), closes [#318](https://github.com/RedHatProductSecurity/trestle-bot/issues/318)
* **deps:** bump trestle to version v3.3.0 ([#269](https://github.com/RedHatProductSecurity/trestle-bot/issues/269)) ([a2a2db6](https://github.com/RedHatProductSecurity/trestle-bot/commit/a2a2db6bbbcac2bec23b9fe520a0958afc488616))
