# trestlebot Rules Transform Action

## Basic Configuration


```yaml

name: Example Workflow
...

    steps:
      - uses: actions/checkout@v3
      - name: Run trestlebot
        id: trestlebot
        uses: RedHatProductSecurity/trestle-bot/actions/rules-transform@main
        with:
          markdown_dir: "markdown/components"
          
```

With custom rules directory:
  
```yaml 
  steps:
    - uses: actions/checkout@v3
    - name: Run trestlebot
      id: trestlebot
      uses: RedHatProductSecurity/trestle-bot/actions/rules-transform@main
      with:
        markdown_dir: "markdown/components"
        rules_view_dir: "custom-rules-dir/"
  ```

## Action Inputs

<!-- START_ACTION_INPUTS -->
| Name | Description | Default | Required |
| --- | --- | --- | --- |
| markdown_dir | Path relative to the repository path to create markdown files. See action README.md for more information. | None | True |
| rules_view_dir | Path relative to the repository path where the Trestle rules view files are located. Defaults to `rules/`. | rules/ | False |
| dry_run | Runs tasks without pushing changes to the repository. | false | False |
| github_token | "GitHub token used to make authenticated API requests. Note: You should use a defined secret like "secrets.GITHUB_TOKEN" in your workflow file, do not hardcode the token." | None | False |
| skip_items | Comma-separated glob patterns list of content by Trestle name to skip during task execution. For example `compdef_x,compdef_y*,`. | None | False |
| commit_message | Commit message | Sync automatic updates | False |
| branch | Name of the Git branch to which modifications should be pushed. Required if Action is used on the `pull_request` event. | ${{ github.ref_name }} | False |
| target_branch | Target branch (or base branch) to create a pull request against. If unset, no pull request will be created. If set, a pull request will be created using the `branch` field as the head branch. | None | False |
| file_patterns | Comma separated file pattern list used for `git add`. For example `component-definitions/*,*json`. Defaults to (`.`) | . | False |
| repo_path | Local file path to the git repository with a valid trestle project root relative to the GitHub workspace. Defaults to the current directory (`.`) | . | False |
| commit_user_name | Name used for the commit user | github-actions[bot] | False |
| commit_user_email | Email address used for the commit user | 41898282+github-actions[bot]@users.noreply.github.com | False |
| commit_author_name | Name used for the commit author. Defaults to the username of whoever triggered this workflow run. | ${{ github.actor }} | False |
| commit_author_email | Email address used for the commit author. | ${{ github.actor }}@users.noreply.github.com | False |
| debug | Enable debug logging messages. | false | False |
| config | Path to trestlebot configuration file. | .trestlebot/config.yml | False |

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

The purpose of this action is to sync the rules view data in YAML to OSCAL with `compliance-trestle` and generation corresponding Markdown and commit changes back to the branch or submit a pull request (if desired). Below are the main use-cases/workflows available:

- The default behavior of this action is to run the rules transformation and commit the changes back to the branch the workflow ran from ( `github.ref_name` ). The branch can be changed by setting the field `branch`. If no changes exist or the changes do not exist with the file pattern set, no changes will be made and the action will exit successfully.

```yaml
  steps:
    - uses: actions/checkout@v3
    - name: Run trestlebot
      id: trestlebot
      uses: RedHatProductSecurity/trestle-bot/actions/rules-transform@main
      with:
        branch: "another-branch"
```

- If the `target_branch` field is set, a pull request will be made using the `target_branch` as the base branch and `branch` as the head branch.

```yaml
  steps:
    - uses: actions/checkout@v3
    - name: Run trestlebot
      id: trestlebot
      uses: RedHatProductSecurity/trestle-bot/actions/rules-transform@main
      with:
        branch: "transform-${{ github.run_id }}"
        target_branch: "main"
        github_token: ${{ secret.GITHUB_TOKEN }}
```
