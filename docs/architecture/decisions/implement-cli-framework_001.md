---
x-trestle-template-version: 0.0.1
title: Implement CLI Framework
status: accespted
---

# ADR 001 - Implement CLI Framework

## Context


The primary motivation for this ADR is to enhance the user experience by implementing a more robust CLI framework within the trestlebot codebase.   This will address the requirements of [Issue #295](https://github.com/RedHatProductSecurity/trestle-bot/issues/295) and [Issue #342](https://github.com/RedHatProductSecurity/trestle-bot/issues/342) and enable future development of more complex CLI scenarios.  Currently entrypoints leverage the argparse library as the core CLI framework.  However advanced patterns such as command chaining, subcommands, and dependencies between arguments can be difficult to implement.  Moving to the [Click](https://click.palletsprojects.com/en/5.x/) CLI framework will address these challenges and support more complex requirements in the future.  In addition, Click will provide a universal command syntax that can be used in the Python CLI app and container execution.

This ADR also outlines the adoption of environment variables and a configuration file within the CLI.  These will provides alternatives methods of passing arguments to the CLI beyond just command flags.  This provides users with flexibility in how they pass arguments to the CLI and creates a more static option for arguments that tend to remain unchanged between command executions.


## Decision

The trestlebot module will be refactored to remove the use of `argparse` in favor of Click as the CLI framework.  The code contained in `entrypoints` will be converted into Click commands under the `trestlebot` CLI application.  A new `cli.py` module will be created as the main entrypoint.

In addition, support will be added for using a configuration file and environment variables as CLI inputs.  The CLI will prioritize arguments passed as command flags.  If no argument is passed, the CLI will check for an environment variable.  Finally, if no enviroment variable is found, it will look to the configuration file.  

The configuration file will be broken into two primary categories, `global` and `model specific`.  Global configuration will apply across all models and include values such as git provider, markdown directories, etc.  Model specific configuration will apply to the given OSCAL model only.  While it is expected that most repos will be used for authoring a single OSCAL model, the possiblity of authoring more than one model would be supported.  The configuration file would be initialized during the `trestlebot init` command.  Manually creation and editing is also possible.  The user could also specify a configuration file using the `--config | -c` flag.  This would not be required if using the default configuration file location. 

- the default configuration file location will be `.trestlebot/config.yaml`
- all environment variables will have a `TRESTLEBOT_` prefix

#### Example config:

```yaml
---
version: 1
working-dir: "."
markdown-path-ssp: markdown/system-security-plans
markdown-path-profile: markdown/proflies
markdown-path-catalog: markdown/catalogs
markdown-path-compdef: markdown/component-definitions
ssp-index-path: ssp-index.json
profile-upstreams: [<url>]
catalog-upstreams: [<url>]
compdef-upstreams: [<url>]
git-provider-type: github
git-provider-url: github.com
git-committer-name: "Foo Bar"
git-committer-email: foo@bar.com
models:
  # we could allow for multiple or keep this as one
  - oscal-model: "ssp"
    skip-items: [...]
    skip-assemble: true
```


## Consequences

- The existing command syntax will be updated to evolve from a set of independent entrypoint commants to a unified `trestlebot` CLI with multiple "subcommands".  For example, `trestlebot-autosync <args>` becomes `trestlebot autosync <args>`.
- The container entrypoints will be collapsed into a single entrypoint leveraging the Click CLI application.
- CLI command arguments will be passed via flags, environment variables, or configuration file.
