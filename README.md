# trestle-bot

trestle-bot assists users in leveraging [Compliance-Trestle](https://github.com/IBM/compliance-trestle) in CI/CD workflows for [OSCAL](https://github.com/usnistgov/OSCAL) formatted compliance content management.

> WARNING: This project is currently under initial development. APIs may be changed incompatibly from one commit to another.

## Getting Started

### GitHub Actions

For detailed documentation on how to use each action see the README.md each each folder under [actions](./actions/).

The `autosync` action will sync trestle-generated Markdown files to OSCAL JSON files in a trestle workspace. All content under the provided markdown directory when the action is run. This action supports all top-level models [supported by compliance-trestle for authoring](https://ibm.github.io/compliance-trestle/tutorials/ssp_profile_catalog_authoring/ssp_profile_catalog_authoring/).

The `rules-transform` actions can be used when managing [OSCAL Component Definitions](https://pages.nist.gov/OSCAL-Reference/models/v1.1.1/component-definition/json-outline/) in a trestle workspace. The action will transform rules defined in the rules YAML view to an OSCAL Component Definition JSON file.

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

For information about contributing to trestle-bot see the [CONTRIBUTING.md](./CONTRIBUTING.md) file.

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE.md](LICENSE) file for details.

## Troubleshooting

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for troubleshooting tips.