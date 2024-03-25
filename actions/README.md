# GitHub Actions for trestle-bot

## Introduction

This document provides instructions and examples for creating and using GitHub Actions in the `trestle-bot` project. GitHub Actions are used to automate various tasks related to workspace management and checks.

## Directory Structure

- Actions related to trestle-bot are located in the `actions` directory.
- Actions should correlate an entrypoint under the `trestlebot/entrypoints` directory.

## Adding a New Action

Contributors should scope trestle-bot actions to workspace management and checks. To add a new action:

> Prerequisite: An entrypoint was created under the `trestlebot/entrypoints` directory and added to the `pyproject.toml` under `[tool.poetry.scripts]`

1. Create a new directory in the `actions` directory.
2. In the new directory, create an `action.yml` file that references the Dockerfile in the root of the repository.
3. Add a README with markers to auto update the inputs and outputs from the `action.yml`. See an existing `README.md` for examples.
4. Create a bash script to run the entrypoint command and add any GitHub Actions specific logic. See `actions/common.sh` for reusable logic.
5. Add the the bash script to the Dockerfile to ensure it exists in the built image

For more details, consult the [GitHub Actions documentation](https://docs.github.com/en/actions/creating-actions/creating-a-docker-container-action).

## Examples

Here are examples of workflow snippets that demonstrate how to use these actions in the `trestle-bot` project.
See each action README for more details about the inputs and outputs.

### Create a New Component Definition

```yaml
name: create

on:
  workflow_dispatch:

jobs:
  create-cd:
    name: Create a new component definition
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
      - uses: RedHatProductSecurity/trestle-bot/actions/create-cd@main
        with:
          markdown_path: "markdown/components"
          profile_name: "my-profile"
          component_definition_name: "my-component-definition"
          component_title: "my-component"
          component_description: "My demo component"
          branch: component-create-${{ github.run_id }}
          target_branch: "main"
          github_token: ${{ secrets.GITHUB_TOKEN }}
```

## Transform Rules

```yaml
name: transform

on:
  push:
    branches-ignore:
    - main
  paths:
    - 'rules/**'

jobs:
  transform-rules:
    name: Transform rules content
    runs-on: ubuntu-latest
    permissions:
      content: write
    steps:
      - uses: actions/checkout@v4
      - uses: RedHatProductSecurity/trestle-bot/actions/rules-transform@main

```

## Autosync Markdown and JSON

```yaml
name: autosync

on:
  pull-request:
    branches:
      - 'main'
  paths:
    - 'component-definitions/**'
    - 'markdown/components/**'

jobs:
  autosync:
    name: Sync Markdown and JSON
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - uses: RedHatProductSecurity/trestle-bot/actions/autosync@main
        with:
          markdown_path: "markdown/components"
          oscal_model: "compdef"
          branch: ${{ github.head_ref }}
```

## Propagate changes from upstream sources

### Storing and syncing upstream content

> Note: The upstream repo must be a valid trestle workspace.

```yaml
name: Sync Upstream

on:
  schedule:
    - cron: '0 0 * * *'

jobs:
  upstream-sync:
    name: Sync upstream content
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
    - uses: actions/checkout@v4
    - name: Run trestlebot
      id: trestlebot
      uses: RedHatProductSecurity/trestle-bot/actions/sync-upstreams@main
      with:
        branch: "sync-upstream-${{ github.run_id }}"
        target_branch: "main"
        github_token: ${{ secrets.GITHUB_TOKEN }}
        sources: |
          https://github.com/myorg/myprofiles@main
```

### Component Definition Regeneration

This example demonstrates how to use outputs and also includes labeling pull requests.

```yaml
name: Regenerate Markdown

on:
  push:
    branches:
      - 'main'
  paths:
    paths:
      - 'profiles/**'
      - 'catalogs/**'

jobs:
  regenerate-content:
    name: Regenerate the component definition
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
    - uses: actions/checkout@v4
    - name: Run trestlebot
      id: trestlebot
      uses: RedHatProductSecurity/trestle-bot/actions/autosync@main
      with:
        markdown_path: "markdown/components"
        oscal_model: "compdef"
        branch: "autoupdate-${{ github.run_id }}"
        target_branch: "main"
        skip_assemble: true
        github_token: ${{ secrets.GITHUB_TOKEN }}
    - uses: actions/labeler@v4
      if: steps.trestlebot.outputs.changes == 'true'
      with:   
        pr-number: |
            ${{ steps.trestlebot.outputs.pr_number }} 
```
