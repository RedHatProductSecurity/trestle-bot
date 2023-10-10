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
          rules_view_path: "rules/"
```

## Action Behavior

The purpose of this action is to sync the rules view data in YAML to OSCAL with `compliance-trestle` and commit changes back to the branch or submit a pull request (if desired). Below are the main use-cases/workflows available:

- The default behavior of this action is to run the rules transformation and commit the changes back to the branch the workflow ran from ( `github.ref_name` ). The branch can be changed by setting the field `branch`. If no changes exist or the changes do not exist with the file pattern set, no changes will be made and the action will exit successfully.

```yaml
  steps:
    - uses: actions/checkout@v3
    - name: Run trestlebot
      id: trestlebot
      uses: RedHatProductSecurity/trestle-bot/actions/rules-transform@main
      with:
        rules_view_path: "rules/"
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
        rules_view_path: "rules/"
        branch: "transform-${{ github.run_id }}"
        target_branch: "main"
        github_token: ${{ secret.GITHUB_TOKEN }}
```