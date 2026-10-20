# CycloProp task handoff

Copy the outgoing section into a specialist chat and supply its file packet. Complete the returned section when bringing work back. Use explicit `none`, `not run` or `unverified` entries instead of leaving evidence fields ambiguous.

## Outgoing assignment

- **Task ID / title / discipline:**
- **Status / date / master:**
- **Objective and why it matters:**
- **Completion condition:** What concrete delivery ends this assignment? Distinguish this from broader engineering validation.
- **Baseline revision / repository commit:** Include relevant uncommitted changes or attach a snapshot/diff; a commit alone may be insufficient.

### Current inputs and sources

| File, excerpt or artifact supplied | Revision/hash or source location | Evidence label and purpose |
| --- | --- | --- |
| | | Calculated / measured / assumed / unverified / historical |

List the files that must be attached or made available in the receiving workspace. State whether the specialist can actually read each one. Identify missing access before dependent work.

### Scope and constraints

- **May change:** Exact files, components or fresh output directories.
- **Must preserve:** Unrelated edits and historical evidence.
- **Agreed constraints/decisions:** Geometry, operating inputs, methods, units, conventions and acceptance criteria.
- **Out of scope:**
- **External actions authorized:** For example, solver execution; otherwise none. Specify separately if commit, push or publication is requested.

### Required outputs and validation

- Deliverable files and where they go:
- Commands/procedure and environment requirements:
- Acceptance checks and tolerances, agreed before comparison:
- Required evidence: logs, manifests, hashes, results, command exit status:
- Checks explicitly deferred: reason, owner/environment and claims blocked:

### Return to the master when

List concrete conditions: conflicting sources, unavailable required inputs, proposed baseline/method/acceptance changes, scope expansion or an external dependency. Include the observations, attempted routine fixes and proposed decision. Do not weaken criteria to claim success.

## Returned result

- **Task ID / baseline and source snapshot used:**
- **Outcome:** Delivered / needs revision / awaiting external work.
- **What changed and why:**
- **Files changed / diff / output paths:**
- **Completion criteria:** Met, failed or unverified, each with evidence.

| Check / command | Environment | Exit status / result | Evidence path |
| --- | --- | --- | --- |
| | | Passed / failed / not run / unverified | |

- **Calculated results and assumptions:** Include units and provenance.
- **Measured results:** Include measurement source; otherwise none.
- **Failed/deferred checks:** Reason, owner/environment, next action and claims blocked.
- **Unresolved issues / decisions requested:**
- **Recommended next task:**

### Separate review

- Reviewer / date / scope:
- Implementation and evidence actually inspected:
- Missing access and conclusions left unverified:
- Findings, consequences and required corrections:
- Recommendation: accept / revise; remaining engineering validation:

### Master disposition

- Complete / needs revision / awaiting external work:
- Decision and supporting evidence:
- Baseline change accepted by user, if any:
- PROJECT_STATE.md updates and next task:
