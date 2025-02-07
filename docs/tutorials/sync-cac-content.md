# The trestlebot command line sync-cac-content Tutorial

This tutorial provides how to use `trestlebot sync-cac-content` to create OSCAL component definitions by transforming Cac content control files.

The CLI performs the following transformations:

- Populate CaC product information to Oscal component title and description
- Ensure OSCAL component control mappings are populated with rule and rule parameter data from CaC control files
- Create a validation component from SSG rules to check mappings
- Ensure OSCAL Component Definition implemented requirements are populated from control notes in the control file
- Ensure implementation status of an implemented requirement in OSCAL component definitions are populated with the status from CaC control files

## 1. Prerequisites

- Initialize the [trestlebot workspace](https://github.com/complytime/trestle-bot/blob/main/docs/tutorials/github.md#3-initialize-trestlebot-workspace).

- Pull the [CacContent repository](https://github.com/ComplianceAsCode/content).

## 2. Run the CLI sync-cac-content
`poetry run trestlebot sync-cac-content \
  --repo-path $trestlebot_workspace_directory \
  --branch main \
  --cac-content-root ~/content \
  --cac-profile $CacContentRepo/content/products/ocp4/profiles/high-rev-4.profile \
  --oscal-profile $OSCAL-profile-name \
  --committer-email test@redhat.com \
  --committer-name tester \
  --product $productname \
  --dry-run \
  --component-definition-type $type`

For more details about these options and additional flags, you can use the --help flag:
`poetry run trestlebot sync-cac-content --help'
This will display a full list of available options and their descriptions.

After run the CLI with the right options, you would successfully generate an OSCAL component definition under $trestlebot_workplace_director/component-definitions/$product_name.
