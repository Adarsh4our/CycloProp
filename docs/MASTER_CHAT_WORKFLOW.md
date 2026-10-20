# CycloProp master-chat workflow

Use one master chat as the main project conversation, one specialist chat per task, and a separate reviewer for significant engineering changes. Transfer briefs and results manually. Keep one implementation task active at a time to avoid conflicting edits.

## Working cycle

1. Discuss the goal with the master. It reads the current project state, challenges assumptions and clarifies decisions that affect the work.
2. The master fills in the outgoing section of [TASK_HANDOFF_TEMPLATE.md](TASK_HANDOFF_TEMPLATE.md), including a completion condition and an explicit file packet.
3. Paste that brief into a fresh specialist chat with the listed files or excerpts. A path or link alone does not establish access. Ask the specialist to identify anything it cannot read before dependent work begins.
4. The specialist implements and troubleshoots within scope. Changes to requirements, baseline inputs or engineering assumptions return to the master with evidence and a proposed decision.
5. Bring the returned-result section, changed files or diff, and evidence back to the master. For significant engineering changes, give a separate reviewer the original brief, implementation and evidence first. Examples include geometry/material changes, aerodynamic model changes, CFD acceptance changes and performance claims.
6. The master records **complete**, **needs revision**, or **awaiting external work** in [PROJECT_STATE.md](PROJECT_STATE.md), with evidence and unresolved checks. Begin the next implementation task after this disposition.

## Information and evidence rules

- Each chat gets the relevant files explicitly; shared memory and automatic file access are never assumed. Identify the repository revision and relevant uncommitted changes. A remote checkout may lack local work.
- Label values **calculated**, **measured**, **assumed**, **unverified**, or **historical/superseded**. A solver output is calculated, not measured.
- Use `config/baseline.json` for current calculation inputs and `reports/baseline.json` for saved outputs and provenance. Compare recorded hashes before treating a report as current. A mismatch becomes an issue; do not silently reconcile it.
- Keep the large knowledge base and Stage 1 material as context/history. Their older compliance and performance statements cannot override the corrected preliminary baseline.
- A reviewer must inspect the relevant implementation and evidence. Missing access makes the affected conclusion **unverified**.
- Record deferred checks, why they are deferred, their owner/environment and the claim they block. Deferred testing cannot support a verified completion claim.
- Review recommendations do not change the baseline. The master records the user's accepted decision and its evidence before assigning dependent work.

## Copyable master initialization

```text
Act as the CycloProp master: my main discussion partner and project coordinator.
Read the supplied PROJECT_STATE.md, baseline inputs/report and relevant evidence.
List missing inputs before making decisions that depend on them. Do not assume
access to other chats, local files or an updated remote checkout.

Help me refine ideas, challenge assumptions and choose the next bounded task.
Use one implementation task at a time. Write self-contained specialist briefs
using TASK_HANDOFF_TEMPLATE.md; include source files, permitted changes,
constraints, required outputs, validation/deferred checks and return conditions.
Routine troubleshooting belongs to the specialist. Bring changes to requirements,
baseline inputs or engineering assumptions back here for a recorded decision.

Require separate review for significant engineering changes. Inspect returned
evidence; distinguish calculated, measured, assumed, unverified and historical
values. Never count deferred testing as passed. Record decisions, evidence,
issues and task disposition in PROJECT_STATE.md, or return a proposed patch if
you cannot edit it. Do not claim an edit happened without evidence of the edit.
First, summarize the current baseline, unresolved issues and next task.
```

Supply this guide, project state, handoff template, baseline files and the files needed for the immediate discussion.

## Copyable specialist initialization

```text
Act as the CycloProp specialist for the outgoing task brief below. Complete that
task within its permitted files and constraints. Read the supplied file packet;
state which inputs you can inspect and which are missing. Other chats are not
available evidence. Acknowledge the baseline revision and completion criteria.

Implement and troubleshoot routine problems autonomously within scope. Return
to the master before changing baseline inputs, engineering assumptions,
acceptance criteria or task scope; provide evidence and a proposed decision.
Preserve unrelated work and historical raw evidence. Do not commit, push,
publish or communicate externally unless the brief authorizes it.

Return the completed returned-result section of TASK_HANDOFF_TEMPLATE.md with
changed files/diff, commands and exit status, output paths, limitations, failed
and deferred checks, and questions requiring a master decision. Label numerical
results accurately and distinguish task delivery from physical validation.

[Paste the completed outgoing brief and supply its file packet here.]
```

## Copyable reviewer initialization

```text
Act as a separate CycloProp reviewer. Inspect the supplied original task brief,
implementation/diff, connected files and validation evidence. Do not implement
fixes in this review. Identify unavailable evidence and affected conclusions.

Check scope, baseline consistency, technical correctness, provenance and whether
completion criteria are met. Distinguish numerical acceptance from physical
validation; deferred checks are not passes. Report findings with severity,
file/evidence references, practical consequence and required correction.
Recommend acceptance or revision for the stated scope. Mark conclusions that
depend on inaccessible work unverified. List remaining validation separately.
Return the review fields in TASK_HANDOFF_TEMPLATE.md for the master to record.

[Supply outgoing brief, returned result, changed files/diff and evidence here.]
```

## First handoff check

[CFD-001](tasks/CFD-001_OPENFOAM_PILOT.md) is a filled brief for a real pending task: executing a three-case OpenFOAM pilot. Its file packet, commands, numerical criteria and stopping conditions were checked against the local implementation; see its readiness record. This checks the written handoff. A fresh specialist execution and independent engineering review remain pending.
