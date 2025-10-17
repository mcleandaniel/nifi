---
title: "How to Add a New Prompt Template"
author: "Research Assistant"
date: "2025-10-17"
summary: "A guide on how to add a new prompt template to the `llm-docs/prompts` directory."
category: "LLM"
audience: ["Developers", "AI Engineers"]
context: "Apache NiFi"
verified_against: "N/A"
dependencies: []
related_docs: []
claims:
  claim-prompt-templates-are-markdown-files:
    fragments:
      - [49, 130] # "Prompt templates are stored as Markdown files in the `llm-docs/prompts` directory."
    sources: [src-this-document]
  claim-prompt-convention:
    fragments:
      - [0, 95] # "Prompt templates follow a specific convention to ensure they are easily discoverable and usable by the system."
    sources: [src-this-document]
  claim-prompt-directory-structure:
    fragments:
      - [0, 75] # "All prompt templates must be located in the `llm-docs/prompts` directory."
    sources: [src-this-document]
  claim-prompt-file-naming:
    fragments:
      - [0, 115] # "Prompt files should be named using a descriptive name in `kebab-case`, with a `.md` extension."
    sources: [src-this-document]
  claim-prompt-front-matter:
    fragments:
      - [0, 82] # "Each prompt template must include a YAML front matter with the following fields:"
    sources: [src-this-document]
  claim-prompt-body:
    fragments:
      - [0, 63] # "The body of the Markdown file contains the prompt text itself."
    sources: [src-this-document]
  claim-prompt-variables:
    fragments:
      - [0, 76] # "Variables can be included in the prompt using the `{{variable_name}}` syntax."
    sources: [src-this-document]
  claim-create-new-prompt-file:
    fragments:
      - [0, 71] # "Create a new Markdown file in the `llm-docs/prompts` directory."
    sources: [src-this-document]
  claim-add-front-matter-and-body:
    fragments:
      - [0, 68] # "Add the front matter and the body of the prompt to the file."
    sources: [src-this-document]
  claim-save-the-file:
    fragments:
      - [0, 59] # "Save the file with a descriptive name in `kebab-case`."
    sources: [src-this-document]
sources:
  src-this-document:
    title: "How to Add a New Prompt Template"
    href: "how-to-add-prompts.md"
---

# How to Add a New Prompt Template

This document describes how to add a new prompt template to the Apache NiFi project. <span id="claim-prompt-templates-are-markdown-files">Prompt templates are stored as Markdown files in the `llm-docs/prompts` directory.</span>

## Convention

<span id="claim-prompt-convention">Prompt templates follow a specific convention to ensure they are easily discoverable and usable by the system.</span>

### Directory Structure

<span id="claim-prompt-directory-structure">All prompt templates must be located in the `llm-docs/prompts` directory.</span>

### File Naming

<span id="claim-prompt-file-naming">Prompt files should be named using a descriptive name in `kebab-case`, with a `.md` extension.</span> For example, `my-new-prompt.md`.

### Front Matter

<span id="claim-prompt-front-matter">Each prompt template must include a YAML front matter with the following fields:</span>

*   `title`: A human-readable title for the prompt.
*   `description`: A brief description of what the prompt is for.
*   `author`: The author of the prompt.
*   `version`: The version of the prompt (e.g., `1.0`).

### Prompt Body

<span id="claim-prompt-body">The body of the Markdown file contains the prompt text itself.</span> <span id="claim-prompt-variables">Variables can be included in the prompt using the `{{variable_name}}` syntax.</span>

## Example

Here is an example of a simple prompt template:

```markdown
---
title: "Summarize Text"
description: "A prompt to summarize a given text."
author: "John Doe"
version: "1.0"
---

Summarize the following text:

{{text}}
```

## How to Add a New Prompt

1.  <span id="claim-create-new-prompt-file">Create a new Markdown file in the `llm-docs/prompts` directory.</span>
2.  <span id="claim-add-front-matter-and-body">Add the front matter and the body of the prompt to the file.</span>
3.  <span id="claim-save-the-file">Save the file with a descriptive name in `kebab-case`.</span>
