---
description: "Guidance for crafting Copilot instruction files in this repo."
applyTo: ".github/instructions/**/*.instructions.md"
---
# Authoring Copilot Instruction Files

When creating or updating any `*.instructions.md` file in this repository, ground your changes in the official Copilot customization guidance and make sure we stay aligned with the context-engineering workflow.

## Refer to these resources first
- [Customize chat to your workflow](https://code.visualstudio.com/docs/copilot/customization/overview)
- [Set up a context engineering flow in VS Code](https://code.visualstudio.com/docs/copilot/guides/context-engineering-guide)
- [Use `.instructions.md` files](https://code.visualstudio.com/docs/copilot/customization/custom-instructions#_use-instructionsmd-files)
- [Community examples of Copilot instruction files](https://github.com/github/awesome-copilot/tree/main/instructions)

## Authoring checklist
- Summarize only the most relevant rules for the targeted scope; avoid duplicating content that already lives in project documentation.
- Link to supporting docs or templates that authors should follow.
- When describing new features or best-practice guidance, revisit the linked documentation to confirm the recommendations align with current Copilot customization guidance.
- Note any repo-specific conventions (naming, tooling, review steps) that Copilot must honor.
- Keep instructions concise, declarative, and task-focused so the agent can act on them directly.

## Working with `.github/copilot-instructions.md`
- Treat this file as the single, workspace-wide instruction source described in the [official guidance](https://code.visualstudio.com/docs/copilot/customization/custom-instructions#_use-a-githubcopilotinstructionsmd-file); updates here affect every Copilot chat in VS Code.
- Focus the content on global guardrails—currently "do not create new files without explicit approval"—and defer task- or file-specific advice to scoped `*.instructions.md` files to avoid conflicts.
- When editing the file, preserve its Markdown formatting (frontmatter optional) and ensure each rule stands alone as a short declarative statement; 
- Document any repo-specific guardrails in commit messages or PR descriptions so downstream consumers understand why the global instructions changed.

## Maintenance reminders
- Update this guidance if Microsoft revises the linked documentation or if our workflow changes.
- Remove obsolete or conflicting advice immediately to prevent drift across instruction files.

