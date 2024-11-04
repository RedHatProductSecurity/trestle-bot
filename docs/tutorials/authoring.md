# Authoring Tutorial

This tutorial provides an overview of the authoring process using `trestlebot`.  We will use the component definition created in the [GitHub tutorial](https://redhatproductsecurity.github.io/trestle-bot/tutorials/github/) as our starting point.  This tutorial will demonstrate the workflow for updating Markdown content and syncing those changes to OSCAL.

## 1. Prerequisites

- Complete the [GitHub tutorial](https://redhatproductsecurity.github.io/trestle-bot/tutorials/github/)


## 2. Edit in Markdown

We will begin where we left off at the end of the [GitHub tutorial](https://redhatproductsecurity.github.io/trestle-bot/tutorials/github/).  Our repository has a newly created component definition named `my-first-compdef` with corresponding content in the `markdown/` and `component-definitions/` directories.  We will now demonstrate how to author changes in Markdown and produce updated OSCAL content.

1. Navigate to the `markdown/component-definitions/my-first-compdef/test-component/nist_rev5_800_53/ac` directory and select the `ac-1.md` file.
2. Click the `Edit this file` (pencil) icon.
3. Scroll down to the section titled `## What is the solution and how is it implemented?` and add a new line of text with a brief comment.  For example:

```
## What is the solution and how is it implemented?

Here is where details should be added by the author.
```

4. Click the `Commit changes..` button
5. Select the `Create a new branch for this commit and start a pull request` radio button
6. Click `Propose changes`


The `Open a pull request` page now opens.  Enter any additional details about your changes into the description box.

7. Click `Create pull request`
8. For demo purposes, we will go ahead and merge the pull request ourselves.  In a production setting the pull request process should be used for review, discussion and approval of the proposed changes.  Click `Merge pull request` and then `Confirm merge`.


## Autosync

Once the pull request has been merged the `Trestle-bot rules-transform and autosync` GitHub action will be triggered. We will now validate that action was successful.

1. Navigate to the `Actions` tab of your GitHub repository.
2. The top entry in the list of workflow runs should be titled `Merge pull request #<your PR number> from <your repo/your branch>`.  This action should be either running or have just successfully completed.
3. [Optional] Clicking this entry will allow you to view the detailed steps and log output.
4. Once the action is completed successfully, navigate back to the source code by clicking the `Code` tab of the repo.
5. Click the `component-definitions` folder and navigate to `my-first-compdef/component-definition.json`.
5. The `Last commit date` should align with the time the action completed.
6. Click the `component-definitions.json` file and then click the `History` icon to view the commit history.
7. Ensure the latest commit performed by the GitHub action reflects the changes made in Markdown as shown below:

```
    "description": "",
    "description": "Here is where details should be added by the author",
```

You will also notice the `"last-modified"` timestamp has been updated.


Congrats!  You've successfully authored a change by modifying a Markdown file and letting trestle-bot sync those changes back to the OSCAL content.

