# Veriflow

An opinionated verification harness that enforces data, model, evaluation, and product-level correctness for ML and LLM systems before they ship.

Veriflow turns assumptions into executable checks, runs them locally and in CI, fails loudly when guarantees are violated, and produces human-readable evidence explaining why.

## Installation

```bash
pip install -e .
```

## Basic Usage

```bash
# Initialize a new Veriflow project
veriflow init

# Run all verification checks
veriflow run

# Compare against baseline
veriflow compare
```

## Documentation

Full documentation coming soon. See `.planning/PROJECT.md` for project details.
