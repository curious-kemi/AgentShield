# Architecture Decision Records

This document records the rationale and tradeoffs behind AgentShield's engineering choices. **Implemented** means the choice appears in the working prototype; it does not mean the resulting design is production-ready. Planned alternatives are not presented as completed work.

## ADR-001 — Extend the existing Microsoft Foundry agent

**Status:** Implemented; agent provisioning is not fully reproducible from the repository.

**Context.** `AgentShield-HR-IT` already provided answers from synthetic Northstar HR/IT knowledge. The next requirement was to let users request a business action without discarding that knowledge configuration.

**Decision.** Continue using the existing agent and its configured `create_incident` function tool in **version 4**, rather than implementing a separate direct model application.

**Rationale.** Reuses the existing knowledge, instructions, and agent tooling while focusing engineering effort on the action boundary.

**Alternative considered.** Build an independent Responses API orchestration application without the existing agent.

**Tradeoff.** The runtime code depends on a preconfigured Foundry agent. Declaring a `FunctionTool` in the Python script does not itself provision version 4. A clean setup must document agent configuration and tool registration separately.

## ADR-002 — Execute function calls in the local Python client

**Status:** Implemented and tested.

**Context.** An agent's function-call response describes an intended action but does not execute a Python function on the developer's machine.

**Decision.** Use `src/foundry_client.py` to inspect returned `function_call` items, recognize `create_incident`, invoke the local implementation, and submit `FunctionCallOutput`.

**Rationale.** Makes the separation between model proposal and application execution observable and easy to debug.

**Alternative considered.** A hosted FastAPI endpoint exposed through an appropriately supported Foundry tool integration.

**Tradeoff.** The local process must be running to execute actions. It provides no hosted employee interface or independent employee authorization.

## ADR-003 — Validate the tool round trip with a mock before writing to ServiceNow

**Status:** Mock and live integration both tested; mock response wording showed inconsistent behavior.

**Context.** The Foundry function-call lifecycle needed validation separately from ServiceNow connectivity.

**Decision.** Return a `simulated` status in the initial test, then replace the mock execution with a real ServiceNow function after verifying the round trip.

**Rationale.** Isolates orchestration errors without generating real incidents during early tests.

**Tradeoff.** A successful mock test demonstrates control flow, not downstream API integration. One later diagnostic showed that the agent could still **claim creation** after receiving a simulated result, so natural-language confirmation cannot be treated as authoritative.

## ADR-004 — Separate Foundry orchestration from ServiceNow API access

**Status:** Implemented and tested.

**Context.** The application must handle model-generated tool requests as well as downstream HTTP authentication and incident creation.

**Decision.** Keep Foundry communication and tool dispatch in `src/foundry_client.py`; keep token acquisition and incident POST logic in `src/servicenow.py`.

**Rationale.** Isolates responsibilities and supports troubleshooting of tool-call, Python, OAuth, and ServiceNow failures independently.

**Tradeoff.** Both modules depend on a consistent tool argument and result contract, which requires explicit validation as the project grows.

## ADR-005 — Use OAuth client credentials for the ServiceNow integration

**Status:** Token acquisition and incident creation verified; permission scope not independently audited.

**Context.** The local integration needs to authenticate to the ServiceNow REST API to create incidents.

**Decision.** Request an OAuth token from `/oauth_token.do` using `client_credentials`, then call `/api/now/table/incident` with the Bearer token.

**Rationale.** Matches the supported authentication configuration exercised in the local ServiceNow test environment.

**Alternative considered.** Other authentication patterns require assessment against the desired end-user identity and authorization model; none was validated as part of this milestone.

**Tradeoff.** Client credentials identify the integration application, **not the requesting employee**. The backend still needs separate identity verification and action-level authorization. ServiceNow role/ACL least privilege remains to be assessed.

## ADR-006 — Preserve function-call and agent context across the round trip

**Status:** Implemented and tested.

**Context.** The application must associate an executed tool result with the correct Foundry function call. A follow-up request initially failed when it omitted the agent reference.

**Decision.** Return `FunctionCallOutput` with the originating `call_id`, reuse `conversation.id`, and include the same `AgentReference(name="AgentShield-HR-IT", version="4")` in both `responses.create()` calls.

**Rationale.** Preserves the tested request/response association and avoids the observed missing-model error.

**Tradeoff.** Request correlation is not a substitute for user identity, authorization, or an audit trail.

## Open decisions

| Question | What needs to be established before deciding |
| --- | --- |
| Hosted tool execution | Validate the supported Foundry integration pattern and API authentication boundaries |
| Employee authorization | Define authenticated user context, permitted actions, and ServiceNow identity model |
| Approval policy | Decide which actions require explicit approval and how to bind approval to an operation |
| Duplicate protection | Define reconciliation and idempotency for ambiguous POST outcomes |
| Audit and secrets design | Establish retention/redaction, operational monitoring, and suitable credential storage |

See [Architecture](architecture.md) for the current execution boundaries and [Week 1](week-01.md) for the implementation narrative.
