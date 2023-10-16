# Actions


Tasks in trestle-bot that we want to expose as a GitHub Action are located here. 

# Adding a new Action

> Note to contributors: We are trying to limit the task that we expose as actions to workspace manage operations and checks only.

First, create an entrypoint script for the new action in the `trestlebot/entrypoints` directory. Then add the action by creating a new directory in the `actions` directory with an `action.yml` that references your new entrypoint. See the [GitHub Actions documentation](https://docs.github.com/en/actions/creating-actions/creating-a-docker-container-action) for more information.

