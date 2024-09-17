---
x-trestle-template-version: 0.0.1
title: Implement CLI Framework
status: accespted
---

# ADR 001 - Implement CLI Framework

## Context


The primary motivation for this ADR is to enhance the user experience by implementing a more robust CLI framework within the trestlebot codebase.   This will address the requirements of [Issue #295](https://github.com/RedHatProductSecurity/trestle-bot/issues/295) and [Issue #342](https://github.com/RedHatProductSecurity/trestle-bot/issues/342) and enable future development of more complex CLI scenarios.  Currently entrypoints leverage the argparse library as the core CLI framework.  However advanced patterns such as command chaining, subcommands, and dependencies between arguments can be difficult to implement.  Moving to the [Click](https://click.palletsprojects.com/en/5.x/) CLI framework will address these challenges and support more complex requirements in the future.  In addition, Click will provide a universal command syntax that can be used in the Python CLI app and container execution.


## Decision

The trestlebot module will be refactored to remove the use of `argparse` in favor of Click as the CLI framework.  In addition, support will be added for using a configuration file and environment variables as CLI inputs.  The CLI will prioritize arguments passed as command flags.  If no argument is passed, the CLI will check for an environment variable.  Finally, if no enviroment variable is found, it will look to the configuration file.  This provides users with flexibility in how they pass arguments to the CLI and provides a more static option for arguments that tend to remain unchanged between command executions.

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
