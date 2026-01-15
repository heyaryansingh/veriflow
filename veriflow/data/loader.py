"""Data loading utilities for Veriflow."""

from pathlib import Path
from typing import Union
import pandas as pd
import json


def detect_file_format(path: Path) -> str:
    """Detects file format from extension.
    
    Args:
        path: Path to the file
        
    Returns:
        File format string: 'csv', 'parquet', or 'json'
        
    Raises:
        ValueError: If file format is not supported
    """
    ext = path.suffix.lower()
    if ext == ".csv":
        return "csv"
    elif ext in [".parquet", ".pq"]:
        return "parquet"
    elif ext == ".json":
        return "json"
    else:
        raise ValueError(f"Unsupported file format: {ext}. Supported formats: csv, parquet, json")


def load_dataset(path: Union[str, Path]) -> pd.DataFrame:
    """Loads a dataset from CSV, Parquet, or JSON file.
    
    Args:
        path: Path to the dataset file
        
    Returns:
        pandas DataFrame containing the dataset
        
    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file format is not supported or file is invalid
    """
    path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found: {path}")
    
    file_format = detect_file_format(path)
    
    try:
        if file_format == "csv":
            # Try common encodings
            try:
                return pd.read_csv(path)
            except UnicodeDecodeError:
                return pd.read_csv(path, encoding="latin-1")
        elif file_format == "parquet":
            return pd.read_parquet(path)
        elif file_format == "json":
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Handle different JSON structures
            if isinstance(data, list):
                return pd.DataFrame(data)
            elif isinstance(data, dict):
                # Try to find a list of records
                for key, value in data.items():
                    if isinstance(value, list):
                        return pd.DataFrame(value)
                # If no list found, convert dict to DataFrame
                return pd.DataFrame([data])
            else:
                raise ValueError(f"Unexpected JSON structure: {type(data)}")
    except Exception as e:
        raise ValueError(f"Error loading dataset from {path}: {e}") from e


def get_dataset_info(df: pd.DataFrame) -> dict:
    """Extracts metadata from a DataFrame.
    
    Args:
        df: pandas DataFrame
        
    Returns:
        Dictionary with keys:
        - row_count: Number of rows
        - column_count: Number of columns
        - column_names: List of column names
        - dtypes: Dictionary mapping column names to data types
        - memory_usage: Memory usage in bytes
    """
    return {
        "row_count": len(df),
        "column_count": len(df.columns),
        "column_names": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "memory_usage": df.memory_usage(deep=True).sum(),
    }
