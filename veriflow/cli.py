"""CLI entry point for Veriflow."""

import sys
import shutil
from pathlib import Path
import click
import numpy as np
from veriflow.init import create_project_structure
from veriflow.config import get_config
from veriflow.data.checks import run_data_checks
from veriflow.evaluation.evaluator import run_ml_evaluation


@click.group()
def cli():
    """Veriflow - An opinionated verification harness for ML and LLM systems."""
    pass


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
    
    # Check if config already exists
    if config_path.exists() and not force:
        if not click.confirm(
            f"veriflow.yaml already exists. Overwrite it?",
            default=False,
        ):
            click.echo("Cancelled. Existing veriflow.yaml preserved.")
            return
    
    # Copy example config to veriflow.yaml
    example_path = Path(__file__).parent.parent / "veriflow.yaml.example"
    if example_path.exists():
        shutil.copy2(example_path, config_path)
        click.echo(f"Created veriflow.yaml from template")
    else:
        # Fallback: create minimal config
        config_path.write_text(
            "# Veriflow Configuration\n"
            "# See veriflow.yaml.example for full options\n\n"
            "baseline:\n"
            "  ref: main\n"
        )
        click.echo(f"Created minimal veriflow.yaml (template not found)")
    
    # Create directory structure
    create_project_structure(base_path)
    
    click.echo("\nVeriflow project initialized!")
    click.echo("\nNext steps:")
    click.echo("  1. Edit veriflow.yaml to configure your project")
    click.echo("  2. Run 'veriflow run' to execute verification checks")


@cli.command()
def run():
    """Run verification checks."""
    try:
        config = get_config()
    except FileNotFoundError:
        click.echo("Error: No veriflow.yaml found. Run 'veriflow init' first.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error loading config: {e}", err=True)
        sys.exit(1)
    
    overall_passed = True
    
    # Run data checks
    click.echo("Running data verification checks...")
    click.echo("")
    
    data_result = run_data_checks(config)
    
    # Print data check results
    if data_result["results"]:
        for check_name, result in data_result["results"].items():
            status = "✓" if result.get("passed", False) else "✗"
            click.echo(f"{status} {check_name}: {result.get('message', 'N/A')}")
            
            # Print errors if any
            if "errors" in result and result["errors"]:
                for error in result["errors"]:
                    click.echo(f"  Error: {error}")
            
            # Print overlaps if any
            if "overlaps" in result and result["overlaps"]:
                for overlap in result["overlaps"]:
                    click.echo(f"  Overlap: {overlap.get('split1')} <-> {overlap.get('split2')}: {overlap.get('details', 'N/A')}")
            
            # Print drift results if any
            if "drift_results" in result:
                for drift in result["drift_results"]:
                    if not drift.get("passed", False):
                        click.echo(f"  Drift in {drift.get('split')}: {drift.get('summary', 'N/A')}")
                        for col in drift.get("drifted_columns", []):
                            click.echo(f"    - {col.get('column')}: {col.get('details', 'N/A')}")
    else:
        click.echo("No data checks configured in veriflow.yaml")
    
    if not data_result["passed"]:
        overall_passed = False
    
    click.echo("")
    click.echo(f"Data checks: {data_result['summary']}")
    click.echo("")
    
    # Run ML evaluation if model config exists
    if config.model is not None:
        click.echo("Running ML evaluation...")
        click.echo("")
        
        # Try to load evaluation data from common locations
        # For now, we'll need user to provide data paths or load from files
        # This is a simplified version - in practice, users would provide data
        eval_data_path = Path("eval_data.npz")
        
        if eval_data_path.exists():
            # Load from numpy file
            data = np.load(eval_data_path)
            y_true = data.get("y_true")
            y_pred = data.get("y_pred")
            y_scores = data.get("y_scores", None)
        else:
            # For MVP, skip ML evaluation if data not found
            click.echo("Evaluation data not found. Skipping ML evaluation.")
            click.echo("Create eval_data.npz with y_true, y_pred, y_scores arrays to enable ML evaluation.")
        else:
            try:
                eval_result = run_ml_evaluation(config, y_true, y_pred, y_scores)
                
                # Print metrics
                click.echo("Metrics:")
                for metric_name, value in eval_result["result"].metrics.items():
                    ci = eval_result["result"].bootstrap_cis.get(metric_name, {})
                    ci_str = f" [{ci.get('ci_lower', 0):.4f}, {ci.get('ci_upper', 0):.4f}]" if ci else ""
                    click.echo(f"  {metric_name}: {value:.4f}{ci_str}")
                
                # Print comparison if baseline exists
                if eval_result["comparison"]:
                    click.echo("")
                    click.echo("Comparison vs baseline:")
                    for comp in eval_result["comparison"]["comparisons"]:
                        status_icon = "✓" if comp["status"] in ["improved", "unchanged"] else "✗"
                        click.echo(f"  {status_icon} {comp['details']}")
                
                click.echo("")
                click.echo(f"ML evaluation: {eval_result['summary']}")
                
                if not eval_result["passed"]:
                    overall_passed = False
            except Exception as e:
                click.echo(f"Error running ML evaluation: {e}", err=True)
                overall_passed = False
    
    click.echo("")
    
    # Exit with error code if any checks failed
    if not overall_passed:
        sys.exit(1)


@cli.command()
def compare():
    """Compare against baseline."""
    click.echo("veriflow compare: Compare against baseline (not yet implemented)")


def main():
    """Main entry point for CLI."""
    cli()


if __name__ == "__main__":
    main()
