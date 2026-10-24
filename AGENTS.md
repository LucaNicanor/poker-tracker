
<!-- codex-antigravity-migration:start -->
## Codex migration from Antigravity

Custom skills are installed at C:/Users/lntri/.codex/skills and exposed through C:/Users/lntri/.agents/skills. Select relevant skills automatically from the user's request; the user need not type a slash command. Prefer the migrated user copy when a project has an older duplicate, since its Windows paths and runtime guidance were adapted. Preserve this project's existing context and canonical workflows.

For coding tasks, use the migrated ponytail skill for simple, complete changes. Use graphify when it is relevant to code relationships or an existing project graph. OmniRoute skills manage OmniRoute only; do not apply their provider or credential recipes to Codex unless requested.

Bun: C:/Users/lntri/.codex/skills/.migration-runtime/node_modules/@oven/bun-windows-x64/bin/bun.exe
To run tools or tests that invoke bun by name, prepend its bin directory to PATH for that process:

```powershell
$env:PATH = 'C:/Users/lntri/.codex/skills/.migration-runtime/node_modules/@oven/bun-windows-x64/bin;' + $env:PATH
```

Vercel CLI: node C:/Users/lntri/.codex/skills/.migration-runtime/vercel.cjs
Graphify and OmniRoute already have commands installed. Check live service availability and authentication when needed. Installed skills alone do not prove external accounts are authenticated.

Continue an authorized task through implementation and appropriate verification. Ask only when a material decision, missing credential, or execution permission blocks progress; do not ask for routine continuation. This guidance does not authorize unrelated work.
<!-- codex-antigravity-migration:end -->

<!-- codex-documentation-plugins:start -->
## Installed documentation plugins

Context7 and OpenAI Developers are installed globally and enabled in Codex. For library/framework work, use Context7 to resolve the installed library/version and query the relevant official documentation. For OpenAI APIs, models, or Codex configuration, use the OpenAI documentation skill and OpenAI Developers workflows as relevant. These are agent tools; do not add them as application dependencies or replace existing AI providers without a product requirement.

Newly installed plugin tools may require a fresh Codex chat to load. If a tool is unavailable or requires account sign-in, report that accurately and continue with installed version-specific documentation or official sources. Never infer that installation proves authentication. Do not copy credentials between projects. Preserve any more specific project instructions.
<!-- codex-documentation-plugins:end -->
