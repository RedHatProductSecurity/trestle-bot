# Contributing to trestlebot

Thank you for your interest in the trestlebot project.

Before you start contributing, please take a moment to read through the guide below.

> WARNING: This project is currently under initial development. APIs may be changed incompatibly from one commit to another.

- [Contributing to trestlebot](#contributing-to-trestlebot)
  - [How To Contribute](#how-to-contribute)
  - [Opening a Pull Request](#opening-a-pull-request)
  - [Developer Guide](#developer-guide)
    - [Prerequisites](#prerequisites)
    - [Development Environment](#development-environment)
    - [How It Works](#how-it-works)
      - [Components](#components)
      - [Code structure](#code-structure)
    - [Documentation](#documentation)
      - [Update the `actions` files](#update-the-actions-files)
    - [License Text in Files](#license-text-in-files)
    - [Tools](#tools)
      - [Format and Styling](#format-and-styling)
      - [Type Hints and Static Type Checking](#type-hints-and-static-type-checking)
      - [Analysis Tools](#analysis-tools)
    - [Running tests](#running-tests)
      - [Running tests with make](#running-tests-with-make)
      - [Run with poetry](#run-with-poetry)
      - [Local testing](#local-testing)


## How To Contribute

Some initial contributions could be:

- Improving the documentation
- Adding test coverage
- Try out issues that have the label `good first issue`
- Opening an issue for bugs or feature requests

## Opening a Pull Request

When submitting a pull request, please follow these guidelines:

1. Ensure that you have an issue submitted first and reference it in your pull request.
2. Ensure that your code passes all CI tests.
3. Please keep the pull request focused on a single issue or feature, if possible.

## Developer Guide

### Prerequisites

- [Python](https://www.python.org/downloads/) - v3.8+
- [Poetry](https://python-poetry.org/)
- [Podman](https://podman.io/docs/installation) (Optional) - For testing locally and end-to-end tests

### Development Environment

For a reproducible development environment, we use Dev Containers. See [devcontainer.json](./.devcontainer/devcontainer.json) for more information. Note that this does not include the `podman` installation to avoid the requirement for containers with elevated privileges.

### How It Works

For workflow diagrams, see the [diagrams](./docs/diagrams/) under the `docs` folder.

#### Components

1. CI Provider - Runs or builds and runs trestle-bot container
2. Trestle Bot - Provides logic for managing workspace and containerized environment for use in workflows
3. Compliance-Trestle - Upstream library that provides core logic for how OSCAL content is managed

#### Code structure

- `actions` - Provides specific logic for `trestle-bot` tasks that are packaged as Actions. See [README.md](./actions/README.md) for more information.
- `entrypoints` - Provides top level logic for specific user-facing tasks. These tasks are not necessarily related in any way so they are not organized into a hierarchical command structure, but they do inherit logic and flags from a base class.
- `provider.py, github.py, and gitlab.py` - Git provider abstract class and concrete implementations for interacting with the API.
- `tasks` - Pre-tasks can be configured before the main git logic is run. Any task that does workspace management should go here.
- `tasks/authored` - The `authored` package contains logic for managing authoring tasks for single instances of a top-level OSCAL model. These encapsulate logic from the `compliance-trestle` library and allows loose coupling between `tasks` and `authored` types.
- `transformers` - This contains data transformation logic; specifically for rules.


### Documentation

#### Update the `actions` files

Each `README.md` under the `actions` directory have an Actions Inputs and Action Outputs section. These sections are generated from the `action.yml` file in the directory. To update the `README.md` files, run the following command:

```bash
make update-action-readmes
```

### License Text in Files

Please use the SPDX license identifier in all source files.

```
# SPDX-License-Identifier: Apache-2.0
```

### Tools

#### Format and Styling

This project uses `black` and `isort` for formatting and `flake8` for linting. You can run these commands to format and lint your code.
Linting checks can be run as a pre-commit hook and are verified in CI.

```bash
make format
make lint
```

For non-Python files, we use [Megalinter](https://github.com/oxsecurity/megalinter) to lint in a CI task. See [megalinter.yaml](https://github.com/RedHatProductSecurity/trestle-bot/blob/main/.mega-linter.yml) for more information.

#### Type Hints and Static Type Checking

We encourage the use of type hints in Python code to enhance readability, maintainability, and robustness of the codebase. Type hints serve as documentation and aid in catching potential errors during development. For static type analysis, we utilize `mypy`. Running `make lint` will run `mypy` checks on the codebase.

#### Analysis Tools

- [SonarCloud](https://sonarcloud.io/dashboard?id=rh-psce_trestle-bot) - We use SonarCloud to analyze code quality, coverage, and security. To not break GitHub security model, this will not run on a forked repository.
- [Semgrep](https://semgrep.dev/docs/extensions/overview/#pre-commit) - Identify issues in the local development environment before committing code. These checks are also run in CI.

### Running tests

Run all tests with `make test` or `make test-slow` to run all tests including end-to-end.
For information on end-to-end tests, see [README.md](./tests/e2e/README.md).

#### Running tests with make
```bash
# Run all tests
make test
make test-slow

# Run specific tests
make test-e2e
```

#### Run with poetry
```
make develop
poetry run trestlebot-autosync
poetry run trestlebot-rules-transform
poetry run trestlebot-create-cd
poetry run trestlebot-sync-upstreams
poetry run trestlebot-create-ssp
```

#### Local testing

For this guide, we will be using `podman` to test trestlebot in a running container.

1. Build the image

```bash
podman build -f Dockerfile -t localhost:5000/trestlebot:latest
```

2. Create an environment variables file if testing with the entrypoint script.

> The entrypoint script is where the logic for GitHub specific integrations should be. The environment variables file will contain variables set by GitHub Actions.

Example file named `envfile`

```
cat envfile
...

GITHUB_OUTPUT=
INPUT_SKIP_ITEMS=
INPUT_DRY_RUN=true
INPUT_SKIP_ASSEMBLE=false
INPUT_SKIP_REGENERATE=false
INPUT_REPOSITORY=.
INPUT_BRANCH=test
INPUT_MARKDOWN_PATH=markdown/profiles
INPUT_OSCAL_MODEL=profile
INPUT_SSP_INDEX_PATH=
INPUT_COMMIT_MESSAGE=
INPUT_COMMIT_USER_NAME=testuser
INPUT_COMMIT_USER_EMAIL=test@example.com
INPUT_FILE_PATTERN=*.md,*.json
INPUT_COMMIT_AUTHOR_NAME=
INPUT_COMMIT_AUTHOR_EMAIL=
INPUT_TARGET_BRANCH=
GITHUB_ACTIONS=true

```
3. Use `podman secret` to store sensitive information like API tokens

```bash
cat my-token.txt | podman secret create repo-secret -
```

4. Run the container

```bash
podman run --entrypoint /entrypoint.sh --secret repo-secret,type=env,target=TRESTLEBOT_REPO_ACCESS_TOKEN --env-file=envfile -v my-trestle-space:/data -w /data localhost:5000/trestlebot:latest
```

### Release Process

Once work on a release has been completed:

1. Select the new release number. Use the principles of [semantic versioning](https://semver.org/) to select the new release number.
2. Follow the GitHub documentation on creating a [release](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository#creating-a-release).
3. Once the release is published, the [`publish`](./.github/workflows/publish.yml) workflow will be triggered. An image will be built, tested, and published to `quay.io`. This process also signs and verifies the image with [`cosign`](https://github.com/sigstore/cosign).

- Initial releases will have a `major` tag (if stable), `major`.`minor`, and the full version.
- The latest release will be rebuilt every thirty days to pull in base image updates. The same tags will
be published with the addition of `full-version`.`date` tag.
- Images can be built adhoc for testing purposes with the `workflow_dispatch` trigger.