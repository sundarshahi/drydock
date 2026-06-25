.PHONY: evals evals-behavioral

# Deterministic eval tier — free, no API key, runs in CI and locally.
evals:
	python3 evals/run_deterministic.py

# Behavioral eval tier — local-only, uses your Claude Code login and spends
# usage. Non-deterministic (temp 1.0); intentionally NOT in CI.
evals-behavioral:
	python3 evals/behavioral/run.py
