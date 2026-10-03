---
name: json-schema-contract
description: Enforces flawless JSON formatting, bracket balancing, and character escaping for inter-node communication, preventing downstream parser crashes.
metadata:
  target_node: "Node A & Node C Formatting Engine"
  version: "1.0.0"
---

# JSON Schema Contract Specification

## 1. Syntax Purity Mandates
1. **Zero Text Preamble:** Absolutely NO conversational lead-in (e.g., "Here is the JSON you requested:"). Output must begin with `{` or `[` on line 1, character 1.
2. **Zero Markdown Fencing:** Do NOT wrap output inside triple backtick blocks (````json ... ````) unless explicitly instructed by runtime environment parameters.
3. **Strict Quoting:** Every key and string value must be wrapped in standard double quotes (`"`). Never use single quotes (`'`) or unescaped inner quotation marks.
4. **Trailing Commas Banned:** No trailing commas after the final key-value pair in an object or the final item in an array.

## 2. Checkpointing Recovery Safeguards
If your task prompt indicates you are resuming an interrupted chunk from an API checkpoint:
- Inspect the partial checkpoint buffer.
- Do NOT output repeated opening root brackets if the partial buffer already contains them.
- Seamlessly continue writing valid key-value pairs and close all open objects and arrays cleanly.