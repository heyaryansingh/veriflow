"""CLI entry point for Veriflow."""

import click


@click.group()
def cli():
    """Veriflow - An opinionated verification harness for ML and LLM systems."""
    pass


@cli.command()
def init():
    """Initialize a new Veriflow project."""
    click.echo("veriflow init: Initialize project (not yet implemented)")


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
