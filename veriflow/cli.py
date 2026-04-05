"""CLI entry point for Veriflow ML verification harness.

Provides command-line interface for running ML model verification including:
- Data quality checks (overlap detection, drift analysis, schema validation)
- Evaluation metrics computation with bootstrap confidence intervals
- Baseline comparison for regression testing

Commands:
    init     - Initialize a new Veriflow project with config template
    check    - Run data verification checks (overlap, drift, schema)
    metrics  - Compute ML evaluation metrics from prediction data
    run      - Run complete verification suite
    compare  - Compare current results against baseline

Example:
    Initialize and run checks::

        $ veriflow init
        $ veriflow check --verbose
        $ veriflow metrics -d eval_data.npz

    Complete verification pipeline::

        $ veriflow run
"""

import shutil
import sys
from pathlib import Path

import click
import numpy as np

from veriflow.config import get_config
from veriflow.data.checks import run_data_checks
from veriflow.evaluation.comparison import compare_vs_baseline
from veriflow.evaluation.evaluator import run_ml_evaluation
from veriflow.init import create_project_structure


@click.group()
def cli():
    """Veriflow - An opinionated verification harness for ML and LLM systems."""


@cli.command()
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite existing veriflow.yaml without prompting",
)
def init(force: bool):
    """Initialize a new Veriflow project."""
    base_path = Path.cwd()
    config_path = base_path / "veriflow.yaml"

    if config_path.exists() and not force:
        if not click.confirm(
            "veriflow.yaml already exists. Overwrite it?",
            default=False,
        ):
            click.echo("Cancelled. Existing veriflow.yaml preserved.")
            return

    example_path = Path(__file__).parent.parent / "veriflow.yaml.example"
    if example_path.exists():
        shutil.copy2(example_path, config_path)
        click.echo("Created veriflow.yaml from template")
    else:
        config_path.write_text(
            "# Veriflow Configuration\n"
            "# See veriflow.yaml.example for full options\n\n"
            "baseline:\n"
            "  ref: main\n",
            encoding="utf-8",
        )
        click.echo("Created minimal veriflow.yaml (template not found)")

    create_project_structure(base_path)

    click.echo("\nVeriflow project initialized!")
    click.echo("\nNext steps:")
    click.echo("  1. Edit veriflow.yaml to configure your project")
    click.echo("  2. Run 'veriflow check' to run data verification checks")
    click.echo("  3. Run 'veriflow metrics' to compute evaluation metrics")


@cli.command()
@click.option("--verbose", "-v", is_flag=True, help="Show detailed output")
def check(verbose: bool):
    """Run data verification checks."""
    try:
        config = get_config()
    except FileNotFoundError:
        click.echo("Error: No veriflow.yaml found. Run 'veriflow init' first.", err=True)
        sys.exit(1)
    except Exception as exc:
        click.echo(f"Error loading config: {exc}", err=True)
        sys.exit(1)

    click.echo("Running data verification checks...\n")
    data_result = run_data_checks(config)

    if data_result["results"]:
        for check_name, result in data_result["results"].items():
            status = "[PASS]" if result.get("passed", False) else "[FAIL]"
            click.echo(f"{status} {check_name}: {result.get('message', 'N/A')}")

            if verbose or not result.get("passed", False):
                for error in result.get("errors", []):
                    click.echo(f"  Error: {error}")

                for overlap in result.get("overlaps", []):
                    click.echo(
                        f"  Overlap: {overlap.get('split1')} <-> "
                        f"{overlap.get('split2')}: {overlap.get('details', 'N/A')}"
                    )

                for drift in result.get("drift_results", []):
                    if not drift.get("passed", False) or verbose:
                        click.echo(
                            f"  Drift in {drift.get('split')}: "
                            f"{drift.get('summary', 'N/A')}"
                        )
                        for col in drift.get("drifted_columns", []):
                            click.echo(
                                f"    - {col.get('column')}: "
                                f"{col.get('details', 'N/A')}"
                            )
    else:
        click.echo("No data checks configured in veriflow.yaml")

    click.echo(f"\nSummary: {data_result['summary']}")

    if not data_result["passed"]:
        sys.exit(1)


@cli.command()
@click.option(
    "--data", "-d",
    type=click.Path(),
    default=None,
    help="Path to evaluation data file (default: eval_data.npz)",
)
@click.option("--verbose", "-v", is_flag=True, help="Show detailed output")
def metrics(data: str, verbose: bool):
    """Compute ML evaluation metrics from prediction data."""
    try:
        config = get_config()
    except FileNotFoundError:
        click.echo("Error: No veriflow.yaml found. Run 'veriflow init' first.", err=True)
        sys.exit(1)
    except Exception as exc:
        click.echo(f"Error loading config: {exc}", err=True)
        sys.exit(1)

    eval_data_path = Path(data) if data else Path("eval_data.npz")

    if not eval_data_path.exists():
        click.echo(f"Error: Evaluation data file not found: {eval_data_path}", err=True)
        click.echo("\nCreate eval_data.npz with:")
        click.echo("  import numpy as np")
        click.echo(
            "  np.savez('eval_data.npz', y_true=labels, "
            "y_pred=predictions, y_scores=probabilities)"
        )
        sys.exit(1)

    click.echo(f"Loading evaluation data from {eval_data_path}...")

    try:
        npz_data = np.load(eval_data_path)

        if "y_true" not in npz_data:
            click.echo("Error: eval_data.npz must contain 'y_true' array", err=True)
            sys.exit(1)
        if "y_pred" not in npz_data:
            click.echo("Error: eval_data.npz must contain 'y_pred' array", err=True)
            sys.exit(1)

        y_true = npz_data["y_true"]
        y_pred = npz_data["y_pred"]
        y_scores = npz_data.get("y_scores", None)

        click.echo(f"  Samples: {len(y_true)}")
        click.echo(f"  Classes: {len(np.unique(y_true))}")
        if y_scores is not None:
            click.echo("  Scores: provided")
        click.echo("")

    except Exception as exc:
        click.echo(f"Error loading evaluation data: {exc}", err=True)
        sys.exit(1)

    click.echo("Computing metrics...\n")

    try:
        eval_result = run_ml_evaluation(config, y_true, y_pred, y_scores)

        click.echo("Metrics:")
        for metric_name, value in eval_result["result"].metrics.items():
            ci = eval_result["result"].bootstrap_cis.get(metric_name, {})
            ci_str = (
                f" [95% CI: {ci.get('ci_lower', 0):.4f}, "
                f"{ci.get('ci_upper', 0):.4f}]"
                if ci
                else ""
            )
            click.echo(f"  {metric_name}: {value:.4f}{ci_str}")

        if eval_result["comparison"]:
            click.echo("\nComparison vs baseline:")
            for comp in eval_result["comparison"]["comparisons"]:
                status = (
                    "[PASS]"
                    if comp["status"] in ["improved", "unchanged"]
                    else "[FAIL]"
                )
                click.echo(f"  {status} {comp['details']}")

        click.echo(f"\nSummary: {eval_result['summary']}")

        if not eval_result["passed"]:
            sys.exit(1)

    except Exception as exc:
        click.echo(f"Error running ML evaluation: {exc}", err=True)
        if verbose:
            import traceback
            click.echo(traceback.format_exc())
        sys.exit(1)


@cli.command()
def run():
    """Run verification checks."""
    try:
        config = get_config()
    except FileNotFoundError:
        click.echo("Error: No veriflow.yaml found. Run 'veriflow init' first.", err=True)
        sys.exit(1)
    except Exception as exc:
        click.echo(f"Error loading config: {exc}", err=True)
        sys.exit(1)

    overall_passed = True

    click.echo("Running data verification checks...\n")
    data_result = run_data_checks(config)

    if data_result["results"]:
        for check_name, result in data_result["results"].items():
            status = "PASS" if result.get("passed", False) else "FAIL"
            click.echo(f"{status} {check_name}: {result.get('message', 'N/A')}")

            for error in result.get("errors", []):
                click.echo(f"  Error: {error}")

            for overlap in result.get("overlaps", []):
                click.echo(
                    "  Overlap: "
                    f"{overlap.get('split1')} <-> {overlap.get('split2')}: "
                    f"{overlap.get('details', 'N/A')}"
                )

            for drift in result.get("drift_results", []):
                if drift.get("passed", False):
                    continue
                click.echo(
                    f"  Drift in {drift.get('split')}: {drift.get('summary', 'N/A')}"
                )
                for col in drift.get("drifted_columns", []):
                    click.echo(
                        f"    - {col.get('column')}: {col.get('details', 'N/A')}"
                    )
    else:
        click.echo("No data checks configured in veriflow.yaml")

    if not data_result["passed"]:
        overall_passed = False

    click.echo(f"\nData checks: {data_result['summary']}\n")

    if config.model is not None:
        click.echo("Running ML evaluation...\n")
        eval_data_path = Path("eval_data.npz")

        if eval_data_path.exists():
            data = np.load(eval_data_path)
            y_true = data.get("y_true")
            y_pred = data.get("y_pred")
            y_scores = data.get("y_scores", None)

            try:
                eval_result = run_ml_evaluation(config, y_true, y_pred, y_scores)
                click.echo("Metrics:")
                for metric_name, value in eval_result["result"].metrics.items():
                    ci = eval_result["result"].bootstrap_cis.get(metric_name, {})
                    ci_str = (
                        f" [{ci.get('ci_lower', 0):.4f}, {ci.get('ci_upper', 0):.4f}]"
                        if ci
                        else ""
                    )
                    click.echo(f"  {metric_name}: {value:.4f}{ci_str}")

                if eval_result["comparison"]:
                    click.echo("\nComparison vs baseline:")
                    for comp in eval_result["comparison"]["comparisons"]:
                        status = (
                            "PASS"
                            if comp["status"] in ["improved", "unchanged"]
                            else "FAIL"
                        )
                        click.echo(f"  {status} {comp['details']}")

                click.echo(f"\nML evaluation: {eval_result['summary']}")

                if not eval_result["passed"]:
                    overall_passed = False
            except Exception as exc:
                click.echo(f"Error running ML evaluation: {exc}", err=True)
                overall_passed = False
        else:
            click.echo("No eval_data.npz found, skipping ML evaluation.")

    click.echo("")
    if not overall_passed:
        sys.exit(1)


@cli.command()
@click.option(
    "--current",
    default="artifacts/evaluation_result",
    show_default=True,
    help="Current evaluation result name or path (without .json is allowed).",
)
@click.option(
    "--baseline",
    default="artifacts/baseline_evaluation_result",
    show_default=True,
    help="Baseline evaluation result name or path (without .json is allowed).",
)
def compare(current: str, baseline: str):
    """Compare a current evaluation result against a baseline result."""
    comparison = compare_vs_baseline(current, baseline)
    click.echo(comparison["summary"])

    for comp in comparison["comparisons"]:
        status = comp.get("status", "unknown").upper()
        click.echo(f"{status}: {comp.get('details', comp.get('metric', 'N/A'))}")

    if not comparison["passed"]:
        sys.exit(1)


def main() -> None:
    """Main entry point for Veriflow CLI.

    Called when running ``python -m veriflow`` or the ``veriflow`` command.
    """
    cli()


if __name__ == "__main__":
    main()
