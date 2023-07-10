## Contributing

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
poetry run trestle-bot
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