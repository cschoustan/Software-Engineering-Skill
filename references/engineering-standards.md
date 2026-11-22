# Engineering Standards

## Data model and state

Before changing a workflow across modules, specify domain entities, identifiers, state ownership, allowed transitions, persistence boundaries, and failure paths. Choose types and constructors that prevent invalid combinations where practical.

For example, prefer separate `Pending`, `Succeeded`, and `Failed` states to a loosely related collection of status flags that can contradict each other.

## Interfaces

- Keep public interfaces small and explicit. A caller should not need knowledge of another module's internals.
- Validate externally supplied values at boundaries. Trust typed internal values only after they have been parsed or checked.
- State ownership must be clear. Avoid hidden shared mutable state, repeated synchronization, and unbounded side effects.
- Keep error handling predictable. Preserve enough context for diagnosis without leaking secrets.
- Use idempotency keys, deduplication, or transactional boundaries when legitimate retries can repeat an operation.

## Implementation

- Prefer the smallest coherent change that meets an acceptance criterion.
- Avoid abstraction layers with no current purpose. Remove obsolete paths only when consumer migration and rollback safety are established.
- Preserve local style, naming conventions, public contracts, and supported versions.
- Keep documentation for non-obvious invariants and decisions. Do not fill code with redundant comments.
- Prefer deterministic checks for mechanical rules. Provide useful diagnostics when a check rejects an implementation.

## Testing

- Assert externally observable behavior and contracts, not incidental internal call order.
- Cover successful and negative paths, permission boundaries, failure handling, and known regressions.
- Apply property-based or model checking when state spaces, concurrency, parsing, or invariants make ordinary examples insufficient.
- Do not turn an entire routine change into a formal verification project without a concrete risk case.

## Repeated failures

When a defect or review correction recurs, identify whether a clearer API, type, schema, lint rule, CI check, or behavior test can prevent it. Demonstrate that the new control rejects a previously invalid example and accepts a valid one.
