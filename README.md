# Veriflow

Veriflow is a local-first verification harness for ML and LLM systems. It turns common release checks into executable gates so a project can fail fast on data issues, regressions, and evaluation drift before shipping.

## MVP

Current MVP features:

- bootstrap a verification project with `veriflow init`
- validate config and run data checks with `veriflow run`
- compare saved evaluation outputs against a baseline with `veriflow compare`
- save evaluation artifacts locally in `artifacts/`

## Installation

```bash
uv sync --extra dev
```

## Quick Start

```bash
# Initialize a project in the current directory
uv run veriflow init

# Run configured data checks and optional ML evaluation
uv run veriflow run

# Compare current results against a baseline artifact
uv run veriflow compare --current current --baseline baseline
```

## Demo Flow

1. Run `uv run veriflow init` in a fresh folder.
2. Edit `veriflow.yaml` to enable the checks you want.
3. Add files such as `train.csv`, `eval.csv`, `test.csv`, or `baseline.csv`.
4. Optionally add `eval_data.npz` containing `y_true`, `y_pred`, and `y_scores`.
5. Run `uv run veriflow run`.
6. Save or compare results from `artifacts/`.

## Supported Checks

- `schema_consistency`
- `no_train_eval_overlap`
- `drift_vs_baseline`
- accuracy, F1, ROC-AUC, and calibration ECE
- bootstrap confidence intervals for supported metrics

## Testing

```bash
uv run pytest -q
```

## License

MIT
