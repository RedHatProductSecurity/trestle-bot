# GitHub Actions for trestle-bot

## Introduction

This document provides instructions and examples for creating and using GitHub Actions in the "trestle-bot" project. GitHub Actions are used to automate various tasks related to workspace management and checks.

## Directory Structure

- Actions related to trestle-bot are located in the `trestlebot/actions` directory.
- Entrypoint scripts for actions are stored in the `trestlebot/entrypoints` directory.

## Adding a New Action

Contributors should scope trestle-bot actions to workspace management and checks. To add a new action:

1. Create an entrypoint script for the action in the `trestlebot/entrypoints` directory.
2. Create a new directory in the `trestlebot/actions` directory.
3. In the new directory, create an `action.yml` file that references your entrypoint script.

For more details, consult the [GitHub Actions documentation](https://docs.github.com/en/actions/creating-actions/creating-a-docker-container-action).

## Examples

Here are examples of workflow snippets that demonstrate how to use these actions in the "trestle-bot" project. Each example includes a clear explanation of its purpose and the steps involved.

### Create a New Component

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

## Component Regeneration

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
  regeneration-content:
    name: Regeneration the component definition
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
