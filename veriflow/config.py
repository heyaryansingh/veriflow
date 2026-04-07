"""Configuration loading and validation for Veriflow.

This module handles loading, validating, and discovering Veriflow configuration
files. Supports both veriflow.yaml and .veriflow.yaml (hidden) config files.

The module searches up the directory tree from the current working directory
to find configuration files, similar to how tools like git find .gitconfig.

Functions:
    load_config: Load and validate a config file from a specific path.
    find_config_file: Search directory tree for veriflow.yaml.
    get_config: Convenience function to find and load config.

Example:
    >>> from veriflow.config import get_config
    >>> config = get_config()  # Auto-discovers config file
    >>> print(config.model.path)

    >>> from veriflow.config import load_config
    >>> config = load_config("./custom-config.yaml")
"""

import yaml
from pathlib import Path
from typing import Optional
from veriflow.schema import VeriflowConfig


def load_config(path: str | Path) -> VeriflowConfig:
    """
    Load and validate a Veriflow config file.
    
    Args:
        path: Path to veriflow.yaml file
        
    Returns:
        Validated VeriflowConfig instance
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If YAML parsing fails
        pydantic.ValidationError: If config doesn't match schema
    """
    config_path = Path(path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in config file: {e}") from e
    
    if data is None:
        data = {}
    
    try:
        return VeriflowConfig(**data)
    except Exception as e:
        raise ValueError(f"Config validation failed: {e}") from e


def find_config_file(start_dir: Path = None) -> Optional[Path]:
    """
    Search up directory tree for veriflow.yaml or .veriflow.yaml.
    
    Args:
        start_dir: Directory to start search from (defaults to current directory)
        
    Returns:
        Path to config file if found, None otherwise
    """
    if start_dir is None:
        start_dir = Path.cwd()
    
    current = Path(start_dir).resolve()
    
    # Search up to filesystem root
    while current != current.parent:
        # Check for veriflow.yaml
        config_file = current / "veriflow.yaml"
        if config_file.exists():
            return config_file
        
        # Check for .veriflow.yaml
        hidden_config = current / ".veriflow.yaml"
        if hidden_config.exists():
            return hidden_config
        
        current = current.parent
    
    return None


def get_config() -> VeriflowConfig:
    """
    Find and load Veriflow config from current directory tree.
    
    Returns:
        Validated VeriflowConfig instance
        
    Raises:
        FileNotFoundError: If no config file found
    """
    config_path = find_config_file()
    
    if config_path is None:
        raise FileNotFoundError(
            "No veriflow.yaml or .veriflow.yaml found. "
            "Run 'veriflow init' to create one."
        )
    
    return load_config(config_path)
