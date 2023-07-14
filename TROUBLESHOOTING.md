# Troubleshooting


## Action does not commit changes back to the correct branch

Verify the trigger you are using. The default branch is set to `github.ref_name`. If triggered on a pull request, you may notice this set to `pr-number/merge`. Set the branch field to `github.heaf_ref` which is set during pull request triggered workflows.

## Action does not have permission to commit

If your workflow requires that this action make changes to your branch, ensure the token being used has `content: write` permissions and the token is being set.

```yaml
## Defaults to ${{ github.token }}
- uses: actions/checkout@v3
  with:
    token: ${{ secrets.TOKEN }}
```

> Note: Using the GitHub token provided with GitHub Actions to commit to a branch will [NOT trigger additional workflows](https://docs.github.com/en/actions/security-guides/automatic-token-authentication#using-the-github_token-in-a-workflow).