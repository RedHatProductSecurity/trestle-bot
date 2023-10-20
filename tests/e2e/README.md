# End to End Testing

The end to end tests are used to verify the CLI from a user perspective running trestle-bot in a container.

Podman is used to build and manage the deployed containers.
The trestlebot container image and container image for the mock API server are built and the mock API server is started in the pod.
WireMock is used to mock the Git server endpoints.

## TODO
- Have the option to use pre-built trestle-bot container images from a registry instead of building them locally.

## Prerequisites

- [Podman](https://podman.io/docs/installation)
- [Python 3](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/docs/#installation)

## Resources

- `mappings` - Contains JSON mappings used with WireMock to mock the Git server endpoints.
- `play-kube.yml` - Contains the Kubernetes resources used to deploy the mock API server in a pod.
- `Dockerfile` - Contains the Dockerfile used to build the mock server container image.

## Running the tests

> Note: This must be run from the project root directory.

### Run all tests

```bash
make test-e2e
```