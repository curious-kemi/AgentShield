# Test Record

This document records test evidence for the current AgentShield prototype. Results are **manual observations**, not automated regression coverage. A pass refers only to the stated scenario and does not establish production readiness.

## Recorded environment

| Component | Recorded configuration |
| --- | --- |
| Foundry agent | `AgentShield-HR-IT`, version `4` |
| Model | `gpt-4.1-mini` |
| Runtime | Local Python; version 3.14 indicated by package path (patch version not separately confirmed) |
| `azure-ai-projects` | `2.10.0` |
| `azure-identity` | `1.27.0` |
| `openai` | `3.48.0` |
| `requests` | `2.33.0` |
| `python-dotenv` | `1.2.4` |
| External system | ServiceNow test/developer instance, with OAuth client-credentials configuration |

Package versions were reported from the working environment. They are not evidence of a clean-environment installation, complete dependency lock, or independently verified agent provisioning procedure.

## Test results

| ID | Scenario | Observed outcome | Assessment |
| --- | --- | --- | --- |
| T-01 | Foundry requests an incident tool | `response.output` contained `function_call` with name `create_incident` | **Pass** |
| T-02 | Initial mock tool round trip | Function returned `simulated`; agent accurately reported no ServiceNow ticket | **Pass** |
| T-03 | Separate simulated diagnostic | Tool returned `simulated`; agent incorrectly implied a ticket was created | **Unexpected / fail** |
| T-04 | Standalone ServiceNow OAuth request | Client-credentials token request succeeded | **Pass** |
| T-05 | ServiceNow incident API test | REST Explorer returned HTTP 201 Created | **Previously reported pass** |
| T-06 | ServiceNow write with misindented return | Record created, but local Python returned `None` | **Partial failure** |
| T-07 | Corrected end-to-end incident creation | Agent returned `INC0010019`; record confirmed in ServiceNow | **Pass** |

T-04 and T-05 were separate integration checks; they should not be presented as successful end-to-end Foundry integration on their own.

## T-07 — End-to-end execution evidence

**Input**

> My laptop won't turn on. Please create an IT support ticket. This is a test.

**Observed terminal output**

```text
Foundry client initialized
Ask AgentShield: My laptop won't turn on. Please create an IT support ticket. This is a test
Agent response: I have created an IT support ticket for your laptop issue. Your ticket number is INC0010019.
```

**Independent confirmation:** The incident was checked in ServiceNow. This supports one successful chain: terminal prompt → Foundry `function_call` → Python `create_incident` → ServiceNow REST API → `FunctionCallOutput` → final agent response.

**Evidence limitations:** The terminal transcript does not independently establish an employee identity, specific ServiceNow ACLs, precise tool arguments used for this request, or reliability under errors and retries. The captured ticket number is a test artifact, not proof of an authorization control.

## Not implemented or not yet tested

| Test area | Expected behavior to validate | Status |
| --- | --- | --- |
| Employee authorization | Unauthorized users cannot trigger ticket creation | Authorization not implemented |
| Tool argument validation | Unexpected, missing, oversized, or unsafe values are rejected in trusted code | Not tested |
| Unknown tools | Unrecognized function calls are explicitly rejected or handled safely | Not tested |
| OAuth errors and ServiceNow outages | Errors produce safe and accurate failure/unknown responses | Not tested end to end |
| Ambiguous completion / retries | An uncertain outcome cannot silently create duplicate tickets | Not implemented |
| Tool-result reporting | Model does not claim success for `simulated`, `unknown`, or `error` results | Known failure; regression suite needed |
| Prompt injection | Untrusted documents and prompts cannot bypass backend action policy | Not tested |
| Hosted API | Authenticated FastAPI execution works without a local client | Not implemented |
| Reproducibility | New environment can install, provision the agent, and run the documented workflow | Not verified |

## Test hygiene

Use synthetic prompts and a permitted ServiceNow test instance. Check for an existing incident before retrying an ambiguous POST. Do not publish OAuth tokens, client secrets, live `.env` files, or employee data in logs or screenshots.

Related records: [Debugging log](debugging-log.md) · [Security findings](security-findings.md) · [Week 1 walkthrough](week-01.md).
