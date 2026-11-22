# Workflow Evaluation

A packaged Skill passing structural checks is not evidence of improved software outcomes. Compare observed results under controlled conditions.

## Paired trial procedure

1. Choose realistic, reproducible tasks with independently checkable outcomes.
2. Pin a clean repository snapshot, dependency versions, environment, tool permissions, time limits, and equivalent execution conditions.
3. Define a grading rubric before viewing the outputs. Include expected behavior, prohibited actions, test results, and resource use.
4. Run a baseline without the Skill and a trial with the Skill in separate isolated environments. Randomize order when feasible.
5. Inspect diffs, actual test results, runtime evidence, and unintended side effects. Do not score self-reported success.
6. Record **PASS**, **FAIL**, **BLOCKED**, or **NOT RUN**, with evidence for every scored outcome.
7. Repeat trials, report sample size and missing pairs, and describe cost and time changes alongside correctness.

Use [evaluation scenarios](../evals/scenarios.json) as task ideas, not as proof of performance. The [result summarizer](../scripts/summarize_evals.py) processes actual paired records. Empty results must remain `NO_MEASUREMENTS`.
