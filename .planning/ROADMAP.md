# Roadmap: Veriflow

## Overview

Build an opinionated verification harness for ML and LLM systems that enforces correctness before deployment. Journey from foundation (CLI skeleton, config parsing) through core verification capabilities (data checks, ML/LLM evaluation, regression gates) to product-level verification (frontend/API tests, AI-assisted invariants), culminating in CI integration, templates, and documentation. Each phase delivers a complete, verifiable capability that builds toward making trust a build artifact.

## Domain Expertise

None

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Foundation** - CLI skeleton, config parsing, project structure
- [ ] **Phase 2: Data Verification** - Schema checks, fingerprinting, overlap detection, drift
- [ ] **Phase 3: Classic ML Evaluation** - Metrics, deterministic reruns, bootstrap intervals, paired comparison
- [ ] **Phase 4: LLM/RAG Evaluation** - Prompt hashing, dataset replay, judge models, structured output validation
- [ ] **Phase 5: Regression Gates** - Comparison logic, statistical tests, failure reporting, CI blocking
- [ ] **Phase 6: Frontend/API Verification** - Playwright setup, E2E tests, contract tests, AI-aware assertions
- [ ] **Phase 7: AI-Assisted Invariant Generation** - Natural language to executable test generation
- [ ] **Phase 8: Reporting** - Markdown summary, HTML report with visual diffs and plots
- [ ] **Phase 9: CI Integration** - GitHub Actions workflow, PR comments, artifact uploads
- [ ] **Phase 10: Templates** - LLM template and classic ML template
- [ ] **Phase 11: Documentation & Polish** - README, examples, integration testing

## Phase Details

### Phase 1: Foundation
**Goal**: Establish CLI skeleton, config parsing (`veriflow.yaml`), and project structure
**Depends on**: Nothing (first phase)
**Research**: Unlikely (standard Python CLI patterns, config parsing)
**Plans**: TBD

### Phase 2: Data Verification
**Goal**: Implement data checks (schema consistency, dataset fingerprinting, exact overlap detection, distribution deltas vs baseline)
**Depends on**: Phase 1
**Research**: Unlikely (standard data validation patterns)
**Plans**: 6 plans completed
**Status**: Complete

### Phase 3: Classic ML Evaluation
**Goal**: Implement classic ML evaluation harness (accuracy, F1, ROC-AUC, calibration) with deterministic reruns, bootstrap confidence intervals, and paired comparison vs baseline
**Depends on**: Phase 2
**Research**: Unlikely (standard ML metrics, bootstrap is well-established)
**Plans**: TBD

### Phase 4: LLM/RAG Evaluation
**Goal**: Implement LLM/RAG evaluation (prompt/version hashing, dataset replay, judge model support, structured output validation, optional human annotation hooks)
**Depends on**: Phase 2
**Research**: Likely (LLM evaluation patterns, judge models, current API patterns)
**Research topics**: LLM evaluation frameworks, judge model integration patterns, prompt versioning strategies, structured output validation approaches
**Plans**: TBD

### Phase 5: Regression Gates
**Goal**: Implement regression gates (minimum improvement, maximum allowed regression, absolute thresholds per metric with statistical significance checks, failure reporting, CI blocking)
**Depends on**: Phase 3, Phase 4
**Research**: Likely (statistical testing approaches, CI integration patterns)
**Research topics**: Bootstrap confidence intervals for ML metrics, paired comparison methods, CI blocking strategies
**Plans**: TBD

### Phase 6: Frontend/API Verification
**Goal**: Implement frontend and product verification (Playwright setup, E2E tests, API/contract tests with JSON schema validation, AI-aware assertions that tolerate stochastic outputs while enforcing structure)
**Depends on**: Phase 1
**Research**: Likely (Playwright patterns, AI-aware assertion strategies)
**Research topics**: Playwright best practices for ML apps, AI-aware assertion patterns (structure vs exact text), contract testing approaches
**Plans**: TBD

### Phase 7: AI-Assisted Invariant Generation
**Goal**: Implement AI-assisted invariant generation (user provides natural language invariants, system generates executable tests, stores generated code explicitly)
**Depends on**: Phase 4
**Research**: Likely (LLM code generation patterns, test generation approaches)
**Research topics**: LLM code generation for test creation, natural language to executable test patterns
**Plans**: TBD

### Phase 8: Reporting
**Goal**: Implement reporting (Markdown summary with high-level verdict, passed/failed checks, metric deltas; HTML report with visual diffs, metric plots, UI screenshots, links to artifacts)
**Depends on**: Phase 5, Phase 6
**Research**: Unlikely (standard reporting patterns, HTML generation)
**Plans**: TBD

### Phase 9: CI Integration
**Goal**: Implement CI integration (GitHub Actions workflow running on PRs, caching dependencies, uploading artifacts, commenting summary on PR, blocking merge on failure)
**Depends on**: Phase 8
**Research**: Likely (GitHub Actions patterns, PR comment APIs)
**Research topics**: GitHub Actions workflow patterns, PR comment APIs, artifact upload strategies
**Plans**: TBD

### Phase 10: Templates
**Goal**: Create one LLM template and one classic ML template out-of-the-box
**Depends on**: Phase 9
**Research**: Unlikely (template creation, following established patterns)
**Plans**: TBD

### Phase 11: Documentation & Polish
**Goal**: Complete documentation (README, examples), final integration testing, ensure 15-minute integration goal
**Depends on**: Phase 10
**Research**: Unlikely (documentation patterns)
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 4/4 | Complete | 2025-01-27 |
| 2. Data Verification | 0/TBD | Not started | - |
| 3. Classic ML Evaluation | 0/TBD | Not started | - |
| 4. LLM/RAG Evaluation | 0/TBD | Not started | - |
| 5. Regression Gates | 0/TBD | Not started | - |
| 6. Frontend/API Verification | 0/TBD | Not started | - |
| 7. AI-Assisted Invariant Generation | 0/TBD | Not started | - |
| 8. Reporting | 0/TBD | Not started | - |
| 9. CI Integration | 0/TBD | Not started | - |
| 10. Templates | 0/TBD | Not started | - |
| 11. Documentation & Polish | 0/TBD | Not started | - |
