# Multi-Chat Knowledge Consolidation Guide & Streamlined Prompts

> For new work, use the [master-chat workflow](MASTER_CHAT_WORKFLOW.md), [project state](PROJECT_STATE.md) and [task handoff](TASK_HANDOFF_TEMPLATE.md). This guide is for historical knowledge extraction. Proposed additions must preserve evidence labels and cannot override the corrected calculation baseline. Return conflicting claims to the master before changing that baseline.

This guide provides the updated workflow and prompts to extract all engineering decisions, CAD modeling steps, CFD settings, parameters, and troubleshooting solutions from your separate ChatGPT threads into [`CYCLOPROP_MASTER_KNOWLEDGE_BASE.md`](../CYCLOPROP_MASTER_KNOWLEDGE_BASE.md).

---

## Supply the source files explicitly

Give each receiving chat the current knowledge base, project state and relevant baseline files by attachment, pasted excerpts or an accessible workspace. Have it confirm what it can inspect. Do not assume another chat's memory, a local path or a remote checkout supplies current evidence.

When returning consolidated material, inspect the proposed changes before replacing the project record. If a chat cannot edit files, request an updated file or patch and save it explicitly.

### Method A: Attach the current files
Instead of pasting thousands of words, you simply click the **Attach (`+` or paperclip) button** in the chat, select `CYCLOPROP_MASTER_KNOWLEDGE_BASE.md` from your root folder, and send **Turn 2**. ChatGPT will read the attached file and use its Python sandbox to provide a **1-click downloadable `.md` file** that you can save straight to your root directory!

### Method B: Supply an accessible workspace
Provide the current source snapshot to the receiving chat and have it explicitly read the relevant files. Confirm versions and access even when files were supplied previously.

---

## Recommended Chat Sequence (Oldest to Newest)

Run this sequence chronologically so that early foundational modeling and material selections naturally build up toward the latest revisions:

1. **`Design Modeling`** *(~1 month ago)*
2. **`Material Properties`** *(~29 days ago)*
3. **`CAD Review Assistance`** *(~29 days ago)*
4. **`CAD Help 1`** *(~29 days ago)*
5. **`CAD Help 2`** *(~29 days ago)*
6. **`CAD Help 3`** *(~12 days ago)*
7. **`Feasibility Assessment`** *(~11 days ago)*
8. **`CAD Help 4`** *(~11 days ago)*
9. **`CAD Help 5`** *(~11 days ago)*
10. **`Ansys Fluent Airfoil CFD Setup`** *(~23 hours ago)*

---

## The Updated 2-Turn Prompts

### Turn 1: Initialization & Audit Directive
*(You have already posted this in each chat)*

```markdown
I am consolidating all knowledge, calculations, CAD details, CFD parameters, design decisions, and troubleshooting steps from across our project chats into a single centralized engineering master document for the CycloProp project.

In my next message, I will provide the current version of the master document.

Your task upon receiving that document:
1. Conduct an exhaustive audit of our ENTIRE conversation history in this specific chat thread.
2. Identify every single piece of knowledge, dimension, formula, CAD modeling step/mate/feature, CFD setting (mesh, boundary condition, solver, polar), material property, COTS component, design rationale, and troubleshooting bug/solution discussed here.
3. Integrate all new or expanded information seamlessly into the master document under the relevant sections:
   - Do NOT omit, truncate, summarize away, or delete ANY existing details or sections in the master document.
   - If this chat contains earlier design revisions (e.g., Rev 1.0, Rev 2.0, Rev 2.1) or conflicting measurements, do NOT blindly overwrite newer baseline specs (Rev 3.0); instead, integrate them with clear revision notes or under the "Design Evolution & Revision History" / "Engineering Workarounds" sections.
   - Maintain the existing clean Markdown formatting, math equations ($...$), and tables.
4. OUTPUT RULE: When you reply to my next message, output ONLY the complete updated Markdown document inside a single raw markdown code block (and generate a downloadable .md file). Do NOT include any conversational commentary, introductory text, or closing remarks.

Please acknowledge that you understand these instructions, and tell me to provide the current master document.
```

---

### Turn 2: Streamlined File-Attached Prompt (No Pasting Huge Text!)

> **How to use:**
> 1. In your chat, click the **Attach (`+`)** icon.
> 2. Select `CYCLOPROP_MASTER_KNOWLEDGE_BASE.md` from `c:\Users\Adarsh Singh\CycloProp\`.
> 3. Send this short message:

```markdown
I have attached the current `CYCLOPROP_MASTER_KNOWLEDGE_BASE.md`.

Please review this file, audit our entire chat history, integrate all technical details and findings according to the instructions in Prompt 1, and output ONLY the complete updated file:
1. Provide the updated document in a raw markdown code block.
2. Also use Python (Code Interpreter) to save and provide a direct download link for the updated `CYCLOPROP_MASTER_KNOWLEDGE_BASE.md` file so I can save it with 1 click.
```

---

## Updating Between Chats
1. When the chat finishes, click the **Download `CYCLOPROP_MASTER_KNOWLEDGE_BASE.md`** link (or click **Copy** on the code block).
2. Save/replace `CYCLOPROP_MASTER_KNOWLEDGE_BASE.md` in your project root folder (`c:\Users\Adarsh Singh\CycloProp\`).
3. In the next chat, attach the newly updated file and send the same short **Turn 2** prompt!
