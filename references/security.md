# Security Review

Security checks must reflect the repository's actual languages, frameworks, deployment model, and exposed interfaces. Do not substitute generic lists for an evidence-based inspection.

## Relevant boundaries

- Entry points: HTTP, CLI, uploads, files, message queues, imports, and parsers.
- Assets: credentials, personal data, business records, filesystem access, compute capacity, integrity-critical operations.
- Controls: authentication, authorization, input validation, transport security, rate limiting, secrets handling, logging and auditability.
- Operations: dependency changes, CI permissions, production settings, data migration, and rollback.

## Workflow

1. Identify in-scope components and trust boundaries from code, configuration, and deployment context.
2. Describe plausible abuse paths with concrete prerequisites and impact.
3. Verify existing controls rather than assuming they exist.
4. Prioritize high-impact findings. Distinguish confirmed vulnerabilities from hypotheses.
5. Add negative tests and targeted mitigations while preserving expected functionality.
6. Recheck the security property after the fix and report any remaining exposure.

For sensitive or production work, obtain necessary approval before accessing protected resources, changing credentials, deploying, or altering permissions.

Never include credentials or sensitive customer data in logs, reports, fixtures, or external tools.
