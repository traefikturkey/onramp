---
description: "Guidance for crafting Copilot chat modes in this repo."
applyTo: ".github/chatmodes/**/*.chatmode.md"
---
# Authoring Copilot Chat Modes

When creating or updating any `*.chatmode.md` file in this repository, ground your configurations in the official Copilot customization guidance and ensure they reinforce our context-engineering workflow.

## Refer to these resources first
- [Customize chat to your workflow](https://code.visualstudio.com/docs/copilot/customization/overview)
- [Set up a context engineering flow in VS Code](https://code.visualstudio.com/docs/copilot/guides/context-engineering-guide)
- [Create custom chat modes](https://code.visualstudio.com/docs/copilot/customization/custom-chat-modes)
- [Community examples of Copilot chat modes](https://github.com/github/awesome-copilot/tree/main/chat-modes)

## Authoring checklist
- Define a clear persona and scope for the mode, including its responsibilities, guardrails, and success criteria.
- Configure the `tools`, `mode`, and optional `model` metadata to match the workflow’s needs and avoid over-permissioning.
- Reference supporting documentation, instruction files, or prompt templates that the mode relies on.
- Describe the expected workflow steps so the agent can follow them deterministically.
- Validate that the chat mode complements existing prompts and instructions without duplicating or contradicting guidance.

## Maintenance reminders
- Review the linked documentation when introducing new responsibilities or best practices to keep the mode aligned with current Copilot guidance.
- Update tool access and metadata whenever our available MCP servers or workflows change.
- Retire or refactor modes that overlap in scope or fall out of use to keep the catalog focused and effective.

