# Trestle Bot Sync Upstreams Action

## Basic Configuration


```yaml

name: Example Workflow
...

    steps:
      - uses: actions/checkout@v3
      - name: Run trestlebot
        id: trestlebot
        uses: RedHatProductSecurity/trestle-bot/actions/sync-upstreams@main
        with:
          sources: https://github.com/myorg/myprofiles@main
```

## Action Inputs

<!-- START_ACTION_INPUTS -->
| Name | Description | Default | Required |
| --- | --- | --- | --- |
| sources | A newline separated list of upstream sources to sync with a repo@branch format. For example, `https://github.com/myorg/myprofiles@main` | None | True |
| github_token | GitHub token used to make authenticated API requests | None | False |
| include_model_names | Comma-separated glob pattern list of model names (i.e. trestle directory name) to include in the sync. For example, `*framework-v2`. Defaults to include all model names. | None | False |
| exclude_model_names | Comma-separated glob pattern of model names (i.e. trestle directory name) to exclude from the sync. For example, `*framework-v1`. Defaults to skip no model names. | None | False |
| skip_validation | Skip validation of the upstream OSCAL content. Defaults to false | false | False |
| commit_message | Commit message | Sync automatic updates | False |
| pull_request_title | Custom pull request title | Automatic updates from trestlebot | False |
| branch | Name of the Git branch to which modifications should be pushed. Required if Action is used on the `pull_request` event. | ${{ github.ref_name }} | False |
| target_branch | Target branch (or base branch) to create a pull request against. If unset, no pull request will be created. If set, a pull request will be created using the `branch` field as the head branch. | None | False |
| file_pattern | Comma-separated file pattern list used for `git add`. For example `component-definitions/*,*json`. Defaults to (`.`) | . | False |
| repository | Local file path to the git repository with a valid trestle project root relative to the GitHub workspace. Defaults to the current directory (`.`) | . | False |
| commit_user_name | Name used for the commit user | github-actions[bot] | False |
| commit_user_email | Email address used for the commit user | 41898282+github-actions[bot]@users.noreply.github.com | False |
| commit_author_name | Name used for the commit author. Defaults to the username of whoever triggered this workflow run. | ${{ github.actor }} | False |
| commit_author_email | Email address used for the commit author. | ${{ github.actor }}@users.noreply.github.com | False |
| verbose | Enable verbose logging | false | False |

<!-- END_ACTION_INPUTS -->

## Action Outputs

<!-- START_ACTION_OUTPUTS -->
| Name | Description |
| --- | --- |
| changes | Value is "true" if changes were committed back to the repository. |
| commit | Full hash of the created commit. Only present if the "changes" output is "true". |
| pr_number | Number of the submitted pull request. Only present if a pull request is submitted. |

<!-- END_ACTION_OUTPUTS -->

## Action Behavior

The purpose of this action is to sync a local repository with upstream sources.  The action will clone the repository, sync the upstream sources, validate the OSCAL content, and commit the changes back to the repository. The action can also be configured to create a pull request with the changes.

> IMPORTANT: Both the upstream repo and the local repo must be valid trestle workspaces.

Below are the main use-cases/workflows available:

- The default behavior of this action is to run sync the changes to the workspace and commit the changes back to the branch the workflow ran from ( `github.ref_name` ). The branch can be changed by setting the field `branch`. If no changes exist or the changes do not exist with the file pattern set, no changes will be made and the action will exit successfully.

```yaml
  steps:
    - uses: actions/checkout@v3
    - name: Run trestlebot
      id: trestlebot
      uses: RedHatProductSecurity/trestle-bot/actions/sync-upstreams@main
      with:
        sources: https://github.com/myorg/myprofiles@main
        branch: "another-branch"
```

- If the `target_branch` field is set, a pull request will be made using the `target_branch` as the base branch and `branch` as the head branch.

```yaml
  steps:
    - uses: actions/checkout@v3
    - name: Run trestlebot
      id: trestlebot
      uses: RedHatProductSecurity/trestle-bot/actions/sync-upstreams@main
      with:
        sources: https://github.com/myorg/myprofiles@main
        branch: "autoupdate-${{ github.run_id }}"
        target_branch: "main"
        github_token: ${{ secret.GITHUB_TOKEN }}
```

- Update more than one upstream source:

```yaml
  steps:
    - uses: actions/checkout@v3
    - name: Run trestlebot
      id: trestlebot
      uses: RedHatProductSecurity/trestle-bot/actions/sync-upstreams@main
      with:
        sources: |
          https://github.com/myorg/myprofiles@main
          https://github.com/myorg/mycomps@main
``````

- Use includes and excludes to limit the models that are synced:

   This example only syncs model content that contain the string "rev5" in the name.

```yaml
  steps:
    - uses: actions/checkout@v3
    - name: Run trestlebot
      id: trestlebot
      uses: RedHatProductSecurity/trestle-bot/actions/sync-upstreams@main
      with:
        sources: |
          https://github.com/myorg/myprofiles@main
          https://github.com/myorg/mycomps@main
        include_model_names: "*rev5*"
```