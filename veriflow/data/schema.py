"""Schema consistency checking for Veriflow."""

from dataclasses import dataclass
from pathlib import Path
from typing import Union, Optional
import pandas as pd
from veriflow.data.loader import load_dataset


@dataclass
class DatasetSchema:
    """Represents the schema of a dataset."""
    columns: dict[str, str]  # column name -> dtype string
    nullable_columns: set[str]  # columns that allow null values
    row_count: int


def extract_schema(df: pd.DataFrame) -> DatasetSchema:
    """Extracts schema from a DataFrame.
    
    Args:
        df: pandas DataFrame
        
    Returns:
        DatasetSchema object with column info, nullability, and row count
    """
    columns = {}
    nullable_columns = set()
    
    for col in df.columns:
        dtype_str = str(df[col].dtype)
        columns[col] = dtype_str
        
        # Check if column is nullable
        # Pandas nullable types: Int64, Float64, boolean, string, etc.
        # Non-nullable types: int64, float64, bool, object (for strings)
        if dtype_str.startswith(("Int", "Float", "boolean", "string")):
            nullable_columns.add(col)
        elif df[col].isna().any():
            # If column has any NaN values, it's nullable
            nullable_columns.add(col)
    
    return DatasetSchema(
        columns=columns,
        nullable_columns=nullable_columns,
        row_count=len(df)
    )


def compare_schemas(schema1: DatasetSchema, schema2: DatasetSchema) -> dict:
    """Compares two schemas and reports differences.
    
    Args:
        schema1: First schema to compare
        schema2: Second schema to compare
        
    Returns:
        Dictionary with keys:
        - missing_columns: List of columns in schema1 but not in schema2
        - extra_columns: List of columns in schema2 but not in schema1
        - type_changes: List of dicts with column name and type changes
        - nullable_changes: List of dicts with column name and nullability changes
    """
    cols1 = set(schema1.columns.keys())
    cols2 = set(schema2.columns.keys())
    
    missing_columns = list(cols1 - cols2)
    extra_columns = list(cols2 - cols1)
    
    type_changes = []
    nullable_changes = []
    
    # Check common columns for type and nullability changes
    common_cols = cols1 & cols2
    for col in common_cols:
        # Type change
        if schema1.columns[col] != schema2.columns[col]:
            type_changes.append({
                "column": col,
                "old_type": schema1.columns[col],
                "new_type": schema2.columns[col]
            })
        
        # Nullability change
        nullable1 = col in schema1.nullable_columns
        nullable2 = col in schema2.nullable_columns
        if nullable1 != nullable2:
            nullable_changes.append({
                "column": col,
                "was_nullable": nullable1,
                "is_nullable": nullable2
            })
    
    return {
        "missing_columns": missing_columns,
        "extra_columns": extra_columns,
        "type_changes": type_changes,
        "nullable_changes": nullable_changes
    }


def validate_schema_consistency(schemas: list[DatasetSchema]) -> dict:
    """Validates that multiple schemas are consistent.
    
    Args:
        schemas: List of DatasetSchema objects to compare
        
    Returns:
        Dictionary with keys:
        - passed: bool indicating if all schemas are consistent
        - errors: List of error dicts describing inconsistencies
    """
    if len(schemas) < 2:
        return {"passed": True, "errors": []}
    
    errors = []
    reference = schemas[0]
    
    for i, schema in enumerate(schemas[1:], start=1):
        comparison = compare_schemas(reference, schema)
        
        if (comparison["missing_columns"] or 
            comparison["extra_columns"] or 
            comparison["type_changes"] or 
            comparison["nullable_changes"]):
            errors.append({
                "schema_index": i,
                "comparison": comparison
            })
    
    return {
        "passed": len(errors) == 0,
        "errors": errors
    }


def check_schema_consistency(
    dataset_paths: list[Union[str, Path]], 
    reference_schema: Optional[DatasetSchema] = None
) -> dict:
    """Checks schema consistency across multiple datasets.
    
    Args:
        dataset_paths: List of paths to dataset files
        reference_schema: Optional reference schema to compare against
        
    Returns:
        Dictionary with keys:
        - passed: bool indicating if all schemas are consistent
        - errors: List of dicts with dataset path and mismatch details
        - summary: Human-readable summary string
    """
    errors = []
    schemas = []
    
    # Load schemas from all datasets
    for path in dataset_paths:
        try:
            df = load_dataset(path)
            schema = extract_schema(df)
            schemas.append((path, schema))
        except Exception as e:
            errors.append({
                "dataset": str(path),
                "error": f"Failed to load dataset: {e}"
            })
            continue
    
    if not schemas:
        return {
            "passed": False,
            "errors": errors,
            "summary": "No datasets could be loaded"
        }
    
    # Compare schemas
    if reference_schema:
        # Compare all against reference
        for path, schema in schemas:
            comparison = compare_schemas(reference_schema, schema)
            if (comparison["missing_columns"] or 
                comparison["extra_columns"] or 
                comparison["type_changes"] or 
                comparison["nullable_changes"]):
                errors.append({
                    "dataset": str(path),
                    "comparison": comparison
                })
    else:
        # Compare all against first schema
        reference = schemas[0][1]
        for path, schema in schemas[1:]:
            comparison = compare_schemas(reference, schema)
            if (comparison["missing_columns"] or 
                comparison["extra_columns"] or 
                comparison["type_changes"] or 
                comparison["nullable_changes"]):
                errors.append({
                    "dataset": str(path),
                    "comparison": comparison
                })
    
    # Build summary
    if errors:
        summary = f"Schema inconsistencies found in {len(errors)} dataset(s)"
    else:
        summary = f"All {len(schemas)} datasets have consistent schemas"
    
    return {
        "passed": len(errors) == 0,
        "errors": errors,
        "summary": summary
    }
