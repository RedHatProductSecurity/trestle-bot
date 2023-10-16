# Contributing to trestlebot

Thank you for your interest in the trestlebot project.

Before you start contributing, please take a moment to read through the guide below.

> WARNING: This project is currently under initial development. APIs may be changed incompatibly from one commit to another.

### How To Contribute

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

## Prerequisites

- [Python](https://www.python.org/downloads/) - v3.8+
- [Poetry](https://python-poetry.org/)
- [Podman](https://podman.io/docs/installation)

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

### Format and Styling

```
make format
make lint
```

### Running tests
```
make test
```

### Run with poetry
```
poetry shell
poetry install
poetry run trestlebot-autosync
poetry run trestlebot-rules-transform
```

### Local testing

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
INPUT_CHECK_ONLY=true
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
podman run --entrypoint /entrypoint.sh --secret repo-secret,type=env,target=GITHUB_TOKEN --env-file=envfile -v my-trestle-space:/data -w /data localhost:5000/trestlebot:latest
```