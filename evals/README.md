# Evaluation Scenarios

The scenarios in `scenarios.json` define test tasks and observable requirements. They are **not completed evaluations**.

For a controlled comparison:

1. Prepare isolated repository fixtures for the selected tasks.
2. Use matched environments and tool permissions for runs with and without the Skill.
3. Verify outcomes from files, test output, and runtime evidence rather than written claims.
4. Record actual results in the format shown by `run-results.empty.json`.
5. Run `python scripts/summarize_evals.py path/to/results.json`.

The empty template returns `NO_MEASUREMENTS`. Never populate results with invented runs.
