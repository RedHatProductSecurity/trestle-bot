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

Here are examples of workflow snippets that demonstrate how `trestle-bot` actions can be used for authoring. For the examples below, the OSCAL Component Definition authoring workflow is explored.

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

## Transform and Autosync

Review human-friendly formats in code reviews and apply OSCAL JSON changes after PR merge.
The `autosync` action can be used with any supported model for authoring with Trestle. The 
`transform` action is only supported for component definitions.

```yaml
name: Push to main
on:
  push:
    branches:
      - main
    paths:
      - 'profiles/**'
      - 'catalogs/**'
      - 'component-definitions/**'
      - 'md_comp/**'
      - 'rules/**'

concurrency:
  group: ${{ github.ref }}-${{ github.workflow }}
  cancel-in-progress: true

jobs:
  transform-and-sync:
    name: Automatically Sync Content
    runs-on: ubuntu-latest
    steps:
      - name: Clone
        uses: actions/checkout@v4

      # Update JSON with any markdown edits. Markdown will also be regenerated to
      # follow the generate-edit-assemble workflow. At this stage, we are on the
      # edit step. So autosync runs assemble then generate.
      - name: AutoSync
        id: autosync
        uses: RedHatProductSecurity/trestle-bot/actions/autosync@main
        with:
          markdown_path: "md_comp"
          oscal_model: "compdef"
          commit_message: "Autosync component definition content [skip ci]"
      # Rule transformation is not idempotent, so you may only want to run this
      # if your rules directly has changes to avoid UUID regeneration.
      - uses: dorny/paths-filter@v3
        id: changes
        with:
          filters: |
            rules:
              - 'rules/**'
      # Transformation of rules will updates the OSCAL JSON. These changes will 
      # then be propagated to Markdown. Transformation and regeneration are run together
      # to ensure the Markdown has the most up to date rule information.
      - name: Transform
        if: steps.changes.outputs.rules == 'true'
        id: transform
        uses: RedHatProductSecurity/trestle-bot/actions/rules-transform@main
        with:
          markdown_path: "md_comp"
          commit_message: "Auto-transform rules [skip ci]" 
```

## Verify Changes

Run actions in dry run mode on pull requests to ensure content
can be transformed and assembled on merge without errors.

```yaml
name: Validate PR with CI
on:
  pull_request:
    branches:
      - main
    paths:
      - 'profiles/**'
      - 'catalogs/**'
      - 'component-definitions/**'
      - 'md_comp/**'
      - 'rules/**'

jobs:
  transform-and-regenerate:
    name: Rules Transform and Content Syncing
    runs-on: ubuntu-latest
    steps:
      - name: Clone
        uses: actions/checkout@v4
      - name: AutoSync
        id: autosync
        uses: RedHatProductSecurity/trestle-bot/actions/autosync@main
        with:
          markdown_path: "md_comp"
          oscal_model: "compdef"
          dry_run: true
      - uses: dorny/paths-filter@v3
        id: changes
        with:
          filters: |
            rules:
              - 'rules/**'
      - name: Transform
        if: steps.changes.outputs.rules == 'true'
        id: transform
        uses: RedHatProductSecurity/trestle-bot/actions/rules-transform@main
        with:
          markdown_path: "md_comp"
          dry_run: true
```

## Propagate changes from upstream sources

> Note: The upstream repo must be a valid trestle workspace.

This example demonstrates how to use outputs by labeling pull requests.

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
    - name: Sync content
      id: trestlebot
      uses: RedHatProductSecurity/trestle-bot/actions/sync-upstreams@main
      with:
        branch: "sync-upstream-${{ github.run_id }}"
        # We set the target branch here to create a pull request
        # for review
        target_branch: "main"
        github_token: ${{ secrets.GITHUB_TOKEN }}
        sources: |
          https://github.com/myorg/myprofiles@main
    - uses: actions/labeler@v4
      if: steps.trestlebot.outputs.changes == 'true'
      with:   
        pr-number: |
            ${{ steps.trestlebot.outputs.pr_number }} 
    # Regenerate Markdown for an easier to control diff review and
    # to understand change impact.
    - name: Regenerate markdown (optionally)
      if: steps.trestlebot.outputs.changes == 'true'
      uses: RedHatProductSecurity/trestle-bot/actions/autosync@main
      with:
        markdown_path: "markdown/components"
        oscal_model: "compdef"
        branch: "sync-upstream-${{ github.run_id }}"
        skip_assemble: true
        github_token: ${{ secrets.GITHUB_TOKEN }}
```


## Release

Below is an example release workflow using the `version` on the `autosync` action set the
component definition version in the OSCAL metadata. 

```yaml
name: Release

on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Release version'
        required: true

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: Clone
        uses: actions/checkout@v4
      - name: Autosync
        uses: RedHatProductSecurity/trestle-bot/actions/autosync@main
        with:
          markdown_path: "md_comp"
          oscal_model: "compdef"
          commit_message: "Update content for release [skip ci]"
          version: ${{ github.event.inputs.version }}
      - name: Create and push tags
        env:
          VERSION: ${{ github.event.inputs.version }}
        run: |
            git tag "${VERSION}"
            git push origin "${VERSION}"
      - name: Create Release
        uses: actions/github-script@v7
        with:
          script: |
            await github.rest.repos.createRelease({
              owner: context.repo.owner,
              repo: context.repo.repo,
              tag_name: '${{ github.event.inputs.version }}',
              name: 'Release v${{ github.event.inputs.version }}',
              generate_release_notes: true,
            })
```
