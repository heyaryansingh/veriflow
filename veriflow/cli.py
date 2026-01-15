"""CLI entry point for Veriflow."""

import sys
import shutil
from pathlib import Path
import click
from veriflow.init import create_project_structure
from veriflow.config import get_config
from veriflow.data.checks import run_data_checks


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
    
    click.echo("Running data verification checks...")
    click.echo("")
    
    # Run data checks
    data_result = run_data_checks(config)
    
    # Print results
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
        click.echo("Add checks to data.checks section to enable verification")
    
    click.echo("")
    click.echo(f"Summary: {data_result['summary']}")
    
    # Exit with error code if checks failed
    if not data_result["passed"]:
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
