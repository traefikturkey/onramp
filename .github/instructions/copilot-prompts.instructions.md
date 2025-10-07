```markdown
---
description: "Guidance for crafting Copilot prompt files in this repo."
applyTo: ".github/prompts/**/*.prompt.md"
---
# Authoring Copilot Prompt Files

When creating or updating any `*.prompt.md` file in this repository, ground your prompts in the official Copilot customization guidance and make sure they support our context-engineering workflow.

## Refer to these resources first
- [Customize chat to your workflow](https://code.visualstudio.com/docs/copilot/customization/overview)
- [Set up a context engineering flow in VS Code](https://code.visualstudio.com/docs/copilot/guides/context-engineering-guide)
- [Create reusable prompt files](https://code.visualstudio.com/docs/copilot/customization/prompt-files)
- [Community examples of Copilot prompt files](https://github.com/github/awesome-copilot/tree/main/prompts)

## Authoring checklist
- Target a single, repeatable workflow per prompt; keep steps explicit and action-oriented.
- Specify relevant chat mode, tools, or context requirements via frontmatter so the agent loads the right capabilities.
- Reinforce links to supporting documentation, templates, or instruction files that authors or the agent should consult.
- Validate that the prompt complements existing instructions and avoids duplicate or conflicting guidance.
- Keep prompts concise, using numbered steps or short paragraphs that the agent can follow deterministically.

## Maintenance reminders
- Revisit the linked documentation when describing new workflows or best practices to stay aligned with current Copilot guidance.
- Update or retire prompts when project conventions, tooling, or workflows change.
- Ensure new prompt files are reviewed alongside related instruction files to maintain consistency across guidance.

```
