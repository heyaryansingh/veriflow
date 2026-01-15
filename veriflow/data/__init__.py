"""Data verification module for Veriflow."""

from veriflow.data.loader import load_dataset, get_dataset_info, detect_file_format
from veriflow.data.schema import (
    DatasetSchema,
    extract_schema,
    compare_schemas,
    validate_schema_consistency,
    check_schema_consistency,
)
from veriflow.data.fingerprint import (
    DatasetFingerprint,
    compute_fingerprint,
    save_fingerprint,
    load_fingerprint,
    compare_fingerprints,
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
    "DatasetFingerprint",
    "compute_fingerprint",
    "save_fingerprint",
    "load_fingerprint",
    "compare_fingerprints",
]
