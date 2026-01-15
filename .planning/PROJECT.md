# Veriflow

## What This Is

An opinionated verification harness that enforces data, model, evaluation, and product-level correctness for ML and LLM systems before they ship. Veriflow turns assumptions into executable checks, runs them locally and in CI, fails loudly when guarantees are violated, and produces human-readable evidence explaining why. For ML engineers shipping models into real products, AI-first startups with frontends tied to model outputs, applied researchers transitioning work into production, and advanced students building serious AI systems.

## Core Value

Make **trust a build artifact**, not a feeling. Veriflow must catch failures before merge, explain what broke, and point to the exact regression. If everything else fails, this must work.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Single orchestrator coordinating data checks, model evaluations, regression comparisons, frontend/API verification, reporting, and CI gating
- [ ] Single config file (`veriflow.yaml`) as source of truth with sensible defaults
- [ ] Data verification: schema consistency, dataset fingerprinting, exact overlap detection, distribution deltas vs baseline
- [ ] Evaluation harness: classic ML metrics (accuracy, F1, ROC-AUC, calibration) with deterministic reruns and bootstrap confidence intervals
- [ ] LLM/RAG evaluation: prompt/version hashing, dataset replay, judge model support, structured output validation, optional human annotation hooks
- [ ] Regression gates: minimum improvement, maximum allowed regression, absolute thresholds per metric with statistical significance checks
- [ ] Frontend & product verification: E2E UI tests (Playwright), API/contract tests (JSON schema validation), AI-aware assertions (structure not exact text)
- [ ] AI-assisted invariant generation: user provides natural language invariants, system generates executable tests
- [ ] CLI: `veriflow init`, `veriflow run`, `veriflow compare` with readable output
- [ ] CI integration: GitHub Actions workflow running on PRs, caching dependencies, uploading artifacts, commenting summary, blocking merge on failure
- [ ] Reporting: Markdown summary (high-level verdict, passed/failed checks, metric deltas) and HTML report (visual diffs, metric plots, UI screenshots, links to artifacts)
- [ ] One LLM template and one classic ML template out-of-the-box
- [ ] Integration in under 15 minutes

### Out of Scope

- **Distributed training** — Veriflow verifies, doesn't train
- **Online monitoring** — Focus on pre-deployment verification, not production monitoring
- **Cloud dashboards** — Static reports only, no live dashboards
- **Auto-tuning** — No hyperparameter optimization
- **Multi-repo orchestration** — Single repo only for MVP
- **RAG contamination detection** — Deferred to future
- **Probabilistic robustness testing** — Deferred to future
- **Accessibility audits** — Deferred to future
- **Canary deployments** — Deferred to future
- **Synthetic monitoring** — Deferred to future
- **Replacing MLflow, W&B, DVC, or Arize** — Veriflow integrates with existing stacks, doesn't replace them
- **No-code platform** — Code-first approach
- **Abstracting away ML frameworks** — Users work with their frameworks directly

## Context

AI systems fail **after** training. Failures are rarely syntax errors, crashes during training, or obvious metric drops. They're usually silent data leakage, schema drift breaking frontends, prompt changes that "feel better" but regress behavior, latency increases that stall UIs, evaluation scripts that cannot be reproduced, or AI-generated code that looks correct but violates invariants.

Current tooling tracks experiments, monitors production, and logs metrics, but **does not enforce correctness at the decision point**: "Should this change be allowed to merge or deploy?" This gap produces verification debt and fragile AI products.

Veriflow is opinionated: executable guarantees beat flexibility, deterministic when possible, local-first and CI-native, AI-aware testing that tolerates stochastic outputs while enforcing structure and invariants.

## Constraints

None — no hard constraints specified.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Single config file (`veriflow.yaml`) | Reduces cognitive load, ensures single source of truth, enables opinionated defaults | — Pending |
| Local-first, CI-native | If it fails in CI, it must fail locally — reproducibility is first-class | — Pending |
| Opinionated defaults over flexibility | Users can extend later; MVP must work out-of-the-box | — Pending |
| Executable guarantees | Every promise must run as code — no vague assertions | — Pending |
| AI-aware testing | Assertions tolerate stochastic outputs while enforcing structure and invariants | — Pending |
| Static reports only | HTML reports are self-contained, no cloud dependencies | — Pending |
| GitHub Actions only for MVP | Focus on one CI system first, expand later | — Pending |

---
*Last updated: 2025-01-27 after initialization*
