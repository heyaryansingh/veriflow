"""CLI entry point for Veriflow."""

import shutil
from pathlib import Path
import click
from veriflow.init import create_project_structure


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
    
    click.echo("\n✓ Veriflow project initialized!")
    click.echo("\nNext steps:")
    click.echo("  1. Edit veriflow.yaml to configure your project")
    click.echo("  2. Run 'veriflow run' to execute verification checks")


@cli.command()
def run():
    """Run verification checks."""
    click.echo("veriflow run: Run verification checks (not yet implemented)")


@cli.command()
def compare():
    """Compare against baseline."""
    click.echo("veriflow compare: Compare against baseline (not yet implemented)")


def main():
    """Main entry point for CLI."""
    cli()


if __name__ == "__main__":
    main()
