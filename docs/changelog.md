# Changelog

All notable changes to the Content Triage Agent project.

- Added: Full implementation – project skeleton, config, .env.example, DB schema (normalized_text, idempotency_key), CRUD, seed script, triage service with LLM tool (submit_triage_result), routing stubs, FastAPI POST /submissions with rate limit and request ID, CLI/UI (run_triage.py -f/-c/-u, TRIAGE AGENT banner, pipeline steps, static UI), tests (triage, dedup, edge cases, idempotency, rate limit), README, docs/overview.md (implementation, 2025-03-05)
- Changed: Triage prompt moved to YAML (prompts/triage_system.yaml) for controlled prompt + instructions in one file; added prompt_loader and fallback to .txt (docs/changelog, 2025-03-05)
- Changed: Config and .env.example – added CUSTOM_LLM_PROVIDER (openai), LITELLM_TEMPERATURE, LITELLM_API_VERSION, LITELLM_API_BASE for custom LLM provider (docs/changelog, 2025-03-05)
- Changed: README – run from code folder; added run.sh for one-step -c/-u; -f kept manual; document run service then console (docs/changelog, 2025-03-05)
- Added: setup.sh to install packages and run seed; run.sh now requires .env and checks DATABASE_URL, LITELLM_MODEL (docs/changelog, 2025-03-05)
- Changed: Input sanitization – strip leading/trailing whitespace and collapse internal spaces for submission text (docs/changelog, 2025-03-05)
- Changed: POST /submissions handles DB failures gracefully (503, no DB details leaked) (docs/changelog, 2025-03-05)
