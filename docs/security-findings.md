# Security Findings and Control Backlog

This record distinguishes **observed behavior** from **design gaps and hypothetical attack scenarios**. A successful incident-creation demo is not evidence of employee authorization, least privilege, or resilience to adversarial prompts.

## SF-001 — Inaccurate agent reporting of a simulated action

**Category:** Observed behavior  
**Status:** Open — mitigation not verified

**Evidence.** A diagnostic tool returned `status: simulated`, but the agent stated that a test IT ticket had been created. An earlier mock run accurately disclosed simulation.

**Impact.** Users or dependent workflows could act on a false confirmation even when the actual tool result does not indicate success.

**Recommended control.** Define a strict backend outcome contract (`success`, `error`, `unknown`, `simulated`); regression-test agent wording for every outcome; and use a trusted transaction record or application-rendered confirmation for consequential actions.

**Validation needed.** Verify that simulated, failed, and unknown operations cannot be presented as confirmed creations.

## SF-002 — Downstream write success with an incorrect local return

**Category:** Observed reliability failure with security implications  
**Status:** Return-path bug fixed; duplicate prevention remains open

**Evidence.** ServiceNow created an incident while a Python indentation bug caused the local function to return `None`.

**Impact.** An automated or manual retry after a misleading failure could create duplicate incidents. Similar ambiguity can arise from timeouts after a downstream write.

**Implemented change.** Dedented the success return and confirmed a valid end-to-end incident result (`INC0010019`).

**Recommended control.** Introduce an idempotency or deduplication strategy and reconciliation for outcomes that cannot be confirmed locally. Do not blindly retry ambiguous writes.

## SF-003 — No per-employee authorization for incident creation

**Category:** Design gap; unauthorized-use scenario not tested  
**Status:** Not implemented

**Evidence.** The current CLI accepts a terminal prompt; `DefaultAzureCredential` authenticates to Foundry and ServiceNow OAuth client credentials authenticate the integration application. Neither identifies and authorizes the employee making the request.

**Potential impact.** If this execution path were exposed to untrusted users without an enforcement layer, application privileges could be used to create tickets outside the intended business policy.

**Recommended control.** Authenticate requesters in trusted application code, validate relevant claims, enforce action- and resource-level authorization before API writes, and assess the integration identity's actual ServiceNow roles/ACLs.

## SF-004 — Tool input and execution guardrails are incomplete

**Category:** Design gap; malicious-input behavior not tested  
**Status:** Not implemented

**Evidence.** The script parses model-provided JSON using `json.loads()` and passes values into `create_incident(**arguments)` without comprehensive runtime business validation. The Foundry `FunctionTool` schema is not an authorization policy.

**Potential impact.** Malformed, excessive, or manipulated arguments could cause errors or unintended operations if more powerful tools are added.

**Recommended control.** Validate types, lengths, content, allowed operations, and caller permissions in trusted code; reject unknown tool names and unsafe requests; add tests for malformed and adversarial inputs.

## Additional control backlog

| Area | Current evidence | Planned assessment or mitigation |
| --- | --- | --- |
| Credential management | ServiceNow client secret loaded from local environment; no secret exposure reported | Secure deployment-time secret storage, rotation and redaction; never commit `.env` |
| Integration privilege scope | Incident creation succeeded; ServiceNow roles and ACLs not independently assessed | Audit integration identity, restrict permissions to required operations |
| Error handling | Incident POST checks HTTP errors; some OAuth, timeout, and network failures may raise uncaught exceptions | Standardize safe outcome handling and uncertain-write reconciliation |
| Human approval | No approval gate in tested client | Define an approval policy and enforce it before selected actions |
| Logging and audit | No durable, user-attributed execution log demonstrated | Correlate requester, authorization decision, tool call, and downstream outcome without recording secrets |
| Prompt injection | No adversarial test evidence | Test untrusted retrieved text and prompts; enforce permissions independently of model instructions |
| Secure hosting | Local prototype only | Evaluate authenticated FastAPI hosting, Key Vault, networking, observability and CI/CD protections |

## Enforcement principle

**The model proposes; trusted code authorizes and executes; the downstream system confirms.** The current prototype demonstrates execution and one confirmed incident result. The full authorization, audit, failure-reconciliation and monitoring controls remain future engineering work.

See [Architecture](architecture.md), [Testing](testing.md), and [Decisions](decisions.md) for the system boundaries and evidence behind these findings.
