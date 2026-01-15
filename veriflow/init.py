"""Project initialization logic for Veriflow."""

from pathlib import Path
import click


def create_project_structure(base_path: Path = None) -> None:
    """
    Create Veriflow project directory structure.
    
    Creates directories as specified in PROJECT.md:
    - data_checks/ (with __init__.py)
    - evals/ (with __init__.py)
    - ui_checks/e2e/
    - ui_checks/contracts/
    - baselines/ (with .gitkeep)
    - artifacts/ (with .gitkeep)
    - reports/ (with .gitkeep)
    - .veriflow/ (with .gitkeep)
    
    Args:
        base_path: Base directory to create structure in (defaults to current directory)
    """
    if base_path is None:
        base_path = Path.cwd()
    
    base_path = Path(base_path).resolve()
    
    # Directories that need __init__.py (Python modules)
    python_dirs = [
        base_path / "data_checks",
        base_path / "evals",
    ]
    
    # Directories that need .gitkeep (empty directories)
    empty_dirs = [
        base_path / "baselines",
        base_path / "artifacts",
        base_path / "reports",
        base_path / ".veriflow",
    ]
    
    # Nested directories
    nested_dirs = [
        base_path / "ui_checks" / "e2e",
        base_path / "ui_checks" / "contracts",
    ]
    
    created = []
    
    # Create Python module directories
    for dir_path in python_dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        init_file = dir_path / "__init__.py"
        if not init_file.exists():
            init_file.write_text('"""Veriflow module."""\n')
            created.append(str(dir_path))
    
    # Create empty directories with .gitkeep
    for dir_path in empty_dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        gitkeep = dir_path / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.write_text("")
            created.append(str(dir_path))
    
    # Create nested directories
    for dir_path in nested_dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        if str(dir_path) not in created:
            created.append(str(dir_path))
    
    if created:
        click.echo("Created directories:")
        for dir_path in sorted(created):
            click.echo(f"  {dir_path}")
    else:
        click.echo("Project structure already exists.")
