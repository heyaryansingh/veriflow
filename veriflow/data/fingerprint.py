"""Dataset fingerprinting for change detection.

This module provides functionality to create deterministic fingerprints of datasets,
enabling change detection between runs without comparing full data contents.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Union
import hashlib
import json
import pandas as pd


@dataclass
class DatasetFingerprint:
    """Represents a fingerprint of a dataset."""
    row_count: int
    column_hash: str
    content_hash: str
    timestamp: datetime
    
    def to_dict(self) -> dict:
        """Converts fingerprint to dictionary for JSON serialization."""
        return {
            "row_count": self.row_count,
            "column_hash": self.column_hash,
            "content_hash": self.content_hash,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "DatasetFingerprint":
        """Creates fingerprint from dictionary."""
        return cls(
            row_count=data["row_count"],
            column_hash=data["column_hash"],
            content_hash=data["content_hash"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )


def compute_fingerprint(df: pd.DataFrame) -> DatasetFingerprint:
    """Computes a deterministic fingerprint for a DataFrame.
    
    Args:
        df: pandas DataFrame
        
    Returns:
        DatasetFingerprint object
    """
    row_count = len(df)
    
    # Column hash: hash of sorted column names
    column_names = sorted(df.columns.tolist())
    column_str = ",".join(column_names)
    column_hash = hashlib.sha256(column_str.encode("utf-8")).hexdigest()
    
    # Content hash: hash of sorted row hashes
    if row_count == 0:
        content_hash = hashlib.sha256(b"").hexdigest()
    else:
        # Hash each row (convert to string representation, then hash)
        row_hashes = []
        for _, row in df.iterrows():
            # Convert row to string representation (sorted by column name for consistency)
            row_str = ",".join(str(row[col]) for col in column_names)
            row_hash = hashlib.sha256(row_str.encode("utf-8")).hexdigest()
            row_hashes.append(row_hash)
        
        # Sort row hashes and hash the sorted list
        sorted_hashes = sorted(row_hashes)
        content_str = ",".join(sorted_hashes)
        content_hash = hashlib.sha256(content_str.encode("utf-8")).hexdigest()
    
    return DatasetFingerprint(
        row_count=row_count,
        column_hash=column_hash,
        content_hash=content_hash,
        timestamp=datetime.now(timezone.utc)
    )


def save_fingerprint(path: Union[str, Path], fingerprint: DatasetFingerprint) -> None:
    """Saves fingerprint to JSON file.
    
    Args:
        path: Path to save fingerprint (will be created in .veriflow/fingerprints/)
        fingerprint: DatasetFingerprint to save
    """
    # Create fingerprints directory if needed
    fingerprint_dir = Path(".veriflow") / "fingerprints"
    fingerprint_dir.mkdir(parents=True, exist_ok=True)
    
    # Create filename from path (sanitize)
    if isinstance(path, str):
        path = Path(path)
    
    # Create a safe filename from the dataset path
    safe_name = str(path).replace("/", "_").replace("\\", "_").replace(":", "_")
    fingerprint_file = fingerprint_dir / f"{safe_name}.json"
    
    # Save fingerprint
    with open(fingerprint_file, "w", encoding="utf-8") as f:
        json.dump(fingerprint.to_dict(), f, indent=2)


def load_fingerprint(path: Union[str, Path]) -> Optional[DatasetFingerprint]:
    """Loads fingerprint from JSON file.
    
    Args:
        path: Path to dataset (used to find fingerprint file)
        
    Returns:
        DatasetFingerprint if found, None otherwise
    """
    fingerprint_dir = Path(".veriflow") / "fingerprints"
    
    if isinstance(path, str):
        path = Path(path)
    
    # Create safe filename
    safe_name = str(path).replace("/", "_").replace("\\", "_").replace(":", "_")
    fingerprint_file = fingerprint_dir / f"{safe_name}.json"
    
    if not fingerprint_file.exists():
        return None
    
    try:
        with open(fingerprint_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return DatasetFingerprint.from_dict(data)
    except Exception:
        return None


def compare_fingerprints(fp1: DatasetFingerprint, fp2: DatasetFingerprint) -> dict:
    """Compares two fingerprints and reports differences.
    
    Args:
        fp1: First fingerprint
        fp2: Second fingerprint
        
    Returns:
        Dictionary with keys:
        - changed: bool indicating if fingerprints differ
        - row_count_diff: Difference in row counts
        - column_changed: bool indicating if columns changed
        - content_changed: bool indicating if content changed
        - details: Human-readable description of changes
    """
    row_count_diff = fp2.row_count - fp1.row_count
    column_changed = fp1.column_hash != fp2.column_hash
    content_changed = fp1.content_hash != fp2.content_hash
    changed = row_count_diff != 0 or column_changed or content_changed
    
    # Build details string
    details_parts = []
    if row_count_diff != 0:
        details_parts.append(f"Row count changed: {fp1.row_count} -> {fp2.row_count}")
    if column_changed:
        details_parts.append("Columns changed")
    if content_changed:
        details_parts.append("Content changed")
    if not changed:
        details_parts.append("No changes detected")
    
    details = "; ".join(details_parts)
    
    return {
        "changed": changed,
        "row_count_diff": row_count_diff,
        "column_changed": column_changed,
        "content_changed": content_changed,
        "details": details
    }
