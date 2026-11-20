# Debugging Log

This log records failures observed during AgentShield development, the supporting evidence, the root cause where established, the corrective action, and the result. Proposed hardening work is documented separately from completed fixes.

## DBG-001 — OpenAI client closed before tool-result submission

**Observed symptom**

```text
RuntimeError: Cannot send a request, as the client has been closed.
```

**Investigation and root cause.** The initial `responses.create()` succeeded, but the follow-up call was placed outside `with project_client.get_openai_client() as openai_client:`. The context manager closed the client before the result could be returned to Foundry.

**Fix.** Move the function-call processing and second `responses.create()` call inside the same `with` block.

**Verification.** The next execution reached the API instead of failing on a closed client. A later complete function-calling round trip succeeded.

**Engineering implication.** The client must remain active for both the tool request and the correlated tool-result response.

## DBG-002 — HTTP 400 on second Responses API request

**Observed symptom**

```text
openai.BadRequestError: Error code: 400 - Missing required parameter: 'model'.
```

**Investigation and root cause.** The follow-up request carried `FunctionCallOutput` and the existing conversation ID but omitted `extra_body.agent_reference`.

**Fix.** Include `AgentReference(name="AgentShield-HR-IT", version="4").as_dict()` on **both** `responses.create()` calls.

**Verification.** The follow-up request returned an agent response after the change.

**Engineering implication.** For this tested endpoint pattern, reusing a conversation ID was not sufficient to select the agent.

## DBG-003 — ServiceNow created an incident, but Python returned `None`

**Observed symptom.** An incident appeared in ServiceNow, but `create_incident()` returned `None` and the agent described the operation as unsuccessful.

**Investigation and root cause.** The successful `return` was indented inside `if incident_number is None:`, following an earlier return. With a real incident number, Python skipped the entire conditional and implicitly returned `None`.

**Fix.** Place the success return *after* the missing-number conditional:

```python
if incident_number is None:
    return {
        "status": "unknown",
        "message": "ServiceNow did not return an incident number"
    }

return {
    "status": "success",
    "incident_number": incident_number
}
```

The HTTP exception handler was also corrected to bind the exception with `as e`; the current handler still returns a generic error and does not expose the HTTP status.

**Verification.** The corrected end-to-end test returned `INC0010019`, and ticket creation was confirmed in ServiceNow.

**Engineering implication.** **The absence of a valid local result does not prove an external write failed.** Retrying an uncertain POST can create duplicate incidents; reliable reconciliation and deduplication remain unimplemented.

## DBG-004 — Simulated result reported as a created ticket

**Observed symptom.** A diagnostic function returned:

```json
{"status":"simulated","message":"Diagnostic test only"}
```

The agent nevertheless responded as if it had created a test IT support ticket. A separate earlier mock test had accurately stated that no ticket was created.

**Root cause status.** The response did not faithfully reflect the structured tool result; the internal model behavior causing this inconsistency has not been established.

**Fix status.** **Open.** No verified corrective control has been implemented. Proposed improvements include an explicit outcome contract, regression tests for each status, and a trusted confirmation display for business-critical actions.

**Engineering implication.** Agent-generated prose is not an authoritative receipt for an external operation.

## Troubleshooting sequence for future incidents

When a request fails, inspect these stages separately: (1) Foundry tool-call name and arguments, (2) parsed Python inputs, (3) local function return value, (4) downstream ServiceNow result and actual record, and (5) the final model-generated message. Redact credentials and tokens. Before retrying an ambiguous write, inspect the downstream system for a completed operation.

Related records: [Testing](testing.md) · [Security findings](security-findings.md).
