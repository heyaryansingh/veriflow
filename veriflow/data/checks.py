"""Data verification checks orchestrator."""

from pathlib import Path
from typing import Optional
from veriflow.config import VeriflowConfig
from veriflow.data.schema import check_schema_consistency
from veriflow.data.overlap import check_all_splits_overlap
from veriflow.data.drift import check_drift_vs_baseline


def run_data_checks(
    config: VeriflowConfig,
    dataset_paths: Optional[dict[str, str | Path]] = None
) -> dict:
    """Orchestrates all data verification checks.
    
    Args:
        config: VeriflowConfig object
        dataset_paths: Optional dict mapping split names to paths.
                       If None, will attempt to discover datasets from common locations.
        
    Returns:
        Dictionary with keys:
        - passed: bool indicating if all checks passed
        - results: dict mapping check name to result dict
        - errors: list of error messages
        - summary: Human-readable summary string
    """
    results = {}
    errors = []
    
    # Get enabled checks from config
    enabled_checks = config.data.checks if config.data else []
    
    if not enabled_checks:
        return {
            "passed": True,
            "results": {},
            "errors": [],
            "summary": "No data checks configured"
        }
    
    # Default dataset paths if not provided
    if dataset_paths is None:
        dataset_paths = {}
        # Try to discover common dataset files
        base_path = Path.cwd()
        for split_name in ["train", "eval", "test", "validation"]:
            for ext in [".csv", ".parquet", ".json"]:
                potential_path = base_path / f"{split_name}{ext}"
                if potential_path.exists():
                    dataset_paths[split_name] = potential_path
                    break
    
    # Run each enabled check
    for check_name in enabled_checks:
        try:
            if check_name == "schema_consistency":
                result = _check_schema_consistency(dataset_paths)
                results[check_name] = result
            elif check_name == "no_train_eval_overlap":
                result = _check_no_overlap(dataset_paths)
                results[check_name] = result
            elif check_name == "drift_vs_baseline":
                result = _check_drift(config, dataset_paths)
                results[check_name] = result
            else:
                errors.append(f"Unknown check: {check_name}")
                results[check_name] = {
                    "passed": False,
                    "error": f"Unknown check: {check_name}"
                }
        except Exception as e:
            errors.append(f"Error running {check_name}: {e}")
            results[check_name] = {
                "passed": False,
                "error": str(e)
            }
    
    # Determine overall pass/fail
    all_passed = all(
        result.get("passed", False) 
        for result in results.values()
    ) and len(errors) == 0
    
    # Build summary
    passed_count = sum(1 for r in results.values() if r.get("passed", False))
    total_count = len(results)
    
    if all_passed:
        summary = f"All {total_count} data check(s) passed"
    else:
        summary = f"{passed_count}/{total_count} data check(s) passed"
    
    return {
        "passed": all_passed,
        "results": results,
        "errors": errors,
        "summary": summary
    }


def _check_schema_consistency(dataset_paths: dict[str, str | Path]) -> dict:
    """Wrapper for schema consistency check."""
    if not dataset_paths:
        return {
            "passed": True,
            "message": "No datasets found for schema consistency check"
        }
    
    paths_list = list(dataset_paths.values())
    result = check_schema_consistency(paths_list)
    
    return {
        "passed": result["passed"],
        "message": result["summary"],
        "errors": result.get("errors", [])
    }


def _check_no_overlap(dataset_paths: dict[str, str | Path]) -> dict:
    """Wrapper for overlap check."""
    if not dataset_paths:
        return {
            "passed": True,
            "message": "No datasets found for overlap check"
        }
    
    if len(dataset_paths) < 2:
        return {
            "passed": True,
            "message": "Need at least 2 datasets for overlap check"
        }
    
    result = check_all_splits_overlap(dataset_paths)
    
    return {
        "passed": result["passed"],
        "message": result["summary"],
        "overlaps": result.get("overlaps", [])
    }


def _check_drift(config: VeriflowConfig, dataset_paths: dict[str, str | Path]) -> dict:
    """Wrapper for drift check."""
    # For now, check drift against baseline if baseline dataset exists
    # In future, this could use git to checkout baseline version
    baseline_ref = config.baseline.ref if config.baseline else "main"
    
    # Look for baseline dataset
    base_path = Path.cwd()
    baseline_path = None
    
    # Try common baseline locations
    for ext in [".csv", ".parquet", ".json"]:
        potential_path = base_path / f"baseline{ext}"
        if potential_path.exists():
            baseline_path = potential_path
            break
    
    if not baseline_path:
        return {
            "passed": True,
            "message": f"Baseline dataset not found (ref: {baseline_ref})"
        }
    
    # Check drift for each current dataset
    drift_results = []
    for split_name, current_path in dataset_paths.items():
        try:
            result = check_drift_vs_baseline(current_path, baseline_path)
            drift_results.append({
                "split": split_name,
                "passed": result["passed"],
                "drifted_columns": result.get("drifted_columns", []),
                "summary": result["summary"]
            })
        except Exception as e:
            drift_results.append({
                "split": split_name,
                "passed": False,
                "error": str(e)
            })
    
    all_passed = all(r["passed"] for r in drift_results)
    
    return {
        "passed": all_passed,
        "message": f"Drift check against baseline ({baseline_ref})",
        "drift_results": drift_results
    }
