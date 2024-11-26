# Changelog

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
