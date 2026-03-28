# Conversation Summary Template

> This template defines the structure for summarizing a long-running agentic conversation
> so it can be continued in a new context window. The summary must preserve enough
> detail for the receiving agent to continue seamlessly — as if the conversation never broke.
>
> This template is domain-agnostic — it works for any task type: research, planning,
> analysis, design, creative work, operations, or any other agentic workflow.

---

<template>

## 1. Primary Request and Intent

<!--
What is the user trying to accomplish at the highest level?
- Core objective or task description
- Key requirements and constraints (explicit and inferred from corrections)
- Approach, methodology, or philosophy the user has chosen
- Non-negotiable decisions the user has stated or enforced through pushback
- Scope boundaries — what's included and what's excluded
-->

## 2. Key Decisions and Concepts

<!--
Important decisions, strategies, frameworks, or domain concepts established during the conversation.
Each entry should include:
- **Decision/concept name** (bolded)
- What it is and why it was chosen
- How it connects to other decisions or the overall objective
- Alternatives that were considered and rejected (and why)

Only include items essential for continuing the work without contradicting prior agreements.
-->

## 3. Artifacts and Outputs

<!--
Every artifact produced, significantly modified, or central to the work.
An "artifact" is anything the agent created or the user provided as a working object:
documents, plans, datasets, analyses, designs, templates, configurations, reports,
frameworks, models, schemas, deliverables, etc.

For each artifact:
- **Name/identifier** and type
- Purpose — what it contains and why it exists
- Key content — summarize the structure and main elements
- Critical details to preserve verbatim (specific criteria, definitions, formulas,
  taxonomies, schemas, or configurations that will be referenced later — include
  these in fenced blocks or quoted text)
- Dependencies — which other artifacts reference or depend on it

If a work structure or deliverable hierarchy was established, include it.
-->

## 4. Corrections and Pivots

<!--
Misalignments, rejected approaches, or course corrections that occurred.
For each:
- **Description** (severity: major/minor)
  - What went wrong or was misaligned with the user's intent
  - The user's feedback or correction (preserve their exact words for key moments)
  - How it was resolved
  - Lesson for continuation (so the same mistake isn't repeated)

Order by significance, most impactful first.
Include pivots — moments where the user changed direction or rejected an approach entirely.
-->

## 5. User Messages (Chronological)

<!--
A chronological list of every user message as short quoted summaries.
- Preserve order — this shows the evolution of the user's thinking
- Include confirmations ("ok", "yes", "let's continue") — they signal approval
- Include enough context to understand what each message was responding to
- Do NOT skip messages — gaps create ambiguity about what was approved
-->

## 6. Resolved Questions

<!--
Questions, problems, or open issues that were explicitly raised and resolved.
For each:
- **Resolved**: [question/problem] → [answer/solution]
Keep concise — supporting details should already be in sections 2–4.
-->

## 7. Pending Tasks

<!--
Tasks mentioned or implied but NOT yet completed.
- List explicitly requested but unfinished work
- State clearly if no tasks are pending
- Distinguish between:
  - "User requested but not done" (high priority)
  - "Logically next but not requested" (suggestion only)
-->

## 8. Current State

<!--
The most recently completed work — what was the last thing done?
- List the final 1–3 completed actions in order
- Include the agent's last status message or deliverable
- Note any in-progress work that was interrupted
- This is the "you are here" marker for the continuing session
-->

## 9. Suggested Next Steps

<!--
What would logically come next based on the conversation trajectory?
- Suggested next actions (note: user has NOT explicitly requested these)
- Likely starting points if the user says "continue" or "what's next"
- Any context the new session might need to decide direction
-->

</template>

---

<usage_notes>

## Template Usage Notes

- **Completeness over brevity**: The continuing agent needs enough detail to avoid
  asking the user to repeat themselves. When in doubt, include it.
- **Critical details verbatim**: Include exact definitions, criteria, constraints,
  or specifications that will be referenced later. Paraphrasing these risks drift.
- **User voice**: Preserve the user's exact phrasing for key decisions and corrections —
  it reveals intent that paraphrasing might lose.
- **Dependencies**: Note which artifacts/decisions depend on each other so the
  continuing agent understands the dependency graph.
- **Recency bias**: Give more detail to recent work (sections 8–9) since that's
  where continuation will pick up.

</usage_notes>
