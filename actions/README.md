# Actions


Tasks in trestle-bot that we want to expose as an Action are located here. 

# Adding a new Action

> Note to contributors: We are trying to limit the task that we expose as actions to workspace manage operations and checks only.

1. Add a new folder with the action name
2. Add an action.yml
3. Add an entrypoint script to handle inputs from GitHub Actions
4. Add a COPY line in the Dockerfile

