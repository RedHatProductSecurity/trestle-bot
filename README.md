# trestle-bot

trestle-bot assists users in leveraging [Compliance-Trestle](https://github.com/IBM/compliance-trestle) in automated workflows for [OSCAL](https://github.com/usnistgov/OSCAL) formatted compliance content management.

> WARNING: This project is currently under initial development. APIs may be changed incompatibly from one commit to another.

## Getting Started

## GitHub Actions

For detailed documentation on how to use each action see the README.md each each folder under [actions](./actions/).

The `autosync` action will sync trestle-generated Markdown files to OSCAL JSON files in a trestle workspace. All content under the provided markdown directory when the action is run. This action supports all top-level models [supported by compliance-trestle for authoring](https://ibm.github.io/compliance-trestle/tutorials/ssp_profile_catalog_authoring/ssp_profile_catalog_authoring/).

The `rules-transform` actions can be used when managing [OSCAL Component Definitions](https://pages.nist.gov/OSCAL-Reference/models/v1.1.1/component-definition/json-outline/) in a trestle workspace. The action will transform rules defined in the rules YAML view to an OSCAL Component Definition JSON file.

### GitLab CI

> Coming Soon

## Contributing

For information about contributing to trestle-bot see the [contributing guide](./CONTRIBUTING.md)

See `TROUBLESHOOTING.md` for additional information.