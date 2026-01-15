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
from veriflow.data.overlap import (
    find_overlap,
    check_train_eval_overlap,
    check_all_splits_overlap,
)
from veriflow.data.drift import (
    compute_distribution_stats,
    compare_distributions,
    check_drift_vs_baseline,
)
from veriflow.data.checks import run_data_checks

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
    "find_overlap",
    "check_train_eval_overlap",
    "check_all_splits_overlap",
    "compute_distribution_stats",
    "compare_distributions",
    "check_drift_vs_baseline",
    "run_data_checks",
]
