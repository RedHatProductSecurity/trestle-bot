# End-to-End Testing

End-to-end tests are used to verify the CLI functionality of trestle-bot from a user's perspective, running in a containerized environment.

## Prerequisites

Before running the end-to-end tests, ensure you have the following prerequisites installed:

- [Podman](https://podman.io/docs/installation) - Container management tool
- [Python 3](https://www.python.org/downloads/) - Required for test automation
- [Poetry](https://python-poetry.org/docs/#installation) - Dependency management

## Resources

- **`mappings`**: This directory contains JSON mappings used with WireMock to mock the Git server endpoints.
- **`play-kube.yml`**: This file includes Kubernetes resources for deploying the mock API server in a pod.
- **`Dockerfile`**: The Dockerfile used to build the mock server container image.

## Running the Tests

To run the end-to-end tests, follow these steps:

1. Clone the project repository:

   ```bash
   git clone https://github.com/RedHatProductSecurity/trestle-bot.git
   cd trestle-bot
   ```

2. Install the project dependencies:

   ```bash
   poetry install --without dev --no-root
   ```

3. Run the tests:

   ```bash
    make test-e2e
   ```

   > **Note:** This should always be run from the root of the project directory.

## Additional Notes
- The WireMock tool is used to mock Git server endpoints for testing.
- Podman is used for container and pod management and to build the container image for the mock API server.

## Future Improvements
- Provide an option to use pre-built trestle-bot container images from a registry instead of building them locally.
- Create endpoints that mock GitHub and GitLab API calls for pull request creation.
- Add more end-to-end tests to cover more use cases.