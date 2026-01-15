"""Data verification module for Veriflow."""

from veriflow.data.loader import load_dataset, get_dataset_info, detect_file_format
from veriflow.data.schema import (
    DatasetSchema,
    extract_schema,
    compare_schemas,
    validate_schema_consistency,
    check_schema_consistency,
)

__all__ = [
    "load_dataset",
    "get_dataset_info",
    "detect_file_format",
    "DatasetSchema",
    "extract_schema",
    "compare_schemas",
    "validate_schema_consistency",
    "check_schema_consistency",
]
