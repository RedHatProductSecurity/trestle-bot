# trestle-bot

[![Pre commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![License](https://img.shields.io/badge/license-apache-blue.svg)](http://www.apache.org/licenses/LICENSE-2.0.html)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=rh-psce_trestle-bot&metric=coverage)](https://sonarcloud.io/summary/new_code?id=rh-psce_trestle-bot)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=rh-psce_trestle-bot&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=rh-psce_trestle-bot)



trestle-bot assists users in leveraging [Compliance-Trestle](https://github.com/IBM/compliance-trestle) in CI/CD workflows for [OSCAL](https://github.com/usnistgov/OSCAL) formatted compliance content management.

> WARNING: This project is currently under initial development. APIs may be changed incompatibly from one commit to another.

## Getting Started

### GitHub Actions

For detailed documentation on how to use each action, see the README.md in each folder under [actions](./actions/).

The `autosync` action will sync trestle-generated Markdown files to OSCAL JSON files in a trestle workspace. All content under the provided markdown directory when the action is run will be transformed. This action supports all top-level models [supported by compliance-trestle for authoring](https://ibm.github.io/compliance-trestle/tutorials/ssp_profile_catalog_authoring/ssp_profile_catalog_authoring/).

The `rules-transform` action can be used when managing [OSCAL Component Definitions](https://pages.nist.gov/OSCAL-Reference/models/v1.1.1/component-definition/json-outline/) in a trestle workspace. The action will transform rules defined in the rules YAML view to an OSCAL Component Definition JSON file.

The `create-cd` action can be used to create a new [OSCAL Component Definition](https://pages.nist.gov/OSCAL-Reference/models/v1.1.1/component-definition/json-outline/) in a trestle workspace. The action will create a new Component Definition JSON file and corresponding directories that contain rules YAML files and trestle-generated Markdown files. This action prepares the workspace for use with the `rules-transform` and `autosync` actions.

The `sync-upstreams` action can be used to sync and validate upstream OSCAL content stored in a git repository to a local trestle workspace. Which content is synced is determined by the `include_model_names` and `exclude_model_names` inputs.

### GitLab CI

> Coming Soon

### Run as a Container

Build and run the container locally:

```bash
podman build -f Dockerfile -t trestle-bot .
podman run -v $(pwd):/data -w /data trestle-bot
```

Container images are available in `quay.io`:

```bash
podman run -v $(pwd):/data -w /data quay.io/continuouscompliance/trestle-bot:<tag>
```

## Contributing

For information about contributing to trestle-bot, see the [CONTRIBUTING.md](./CONTRIBUTING.md) file.

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE.md](LICENSE) file for details.

## Troubleshooting

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for troubleshooting tips.