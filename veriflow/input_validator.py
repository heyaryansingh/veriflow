"""Input validation utilities for VeriFlow.

Provides comprehensive validation for workflow inputs, configuration,
data types, and security constraints.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass


@dataclass
class ValidationError:
    """Validation error details."""
    field: str
    message: str
    code: str
    value: Any = None


class ValidationResult:
    """Result of validation operation."""

    def __init__(self):
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []

    @property
    def is_valid(self) -> bool:
        """Check if validation passed."""
        return len(self.errors) == 0

    @property
    def has_warnings(self) -> bool:
        """Check if there are warnings."""
        return len(self.warnings) > 0

    def add_error(self, field: str, message: str, code: str, value: Any = None) -> None:
        """Add validation error."""
        self.errors.append(ValidationError(field, message, code, value))

    def add_warning(self, field: str, message: str, code: str, value: Any = None) -> None:
        """Add validation warning."""
        self.warnings.append(ValidationError(field, message, code, value))

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "errors": [
                {
                    "field": e.field,
                    "message": e.message,
                    "code": e.code,
                    "value": e.value,
                }
                for e in self.errors
            ],
            "warnings": [
                {
                    "field": w.field,
                    "message": w.message,
                    "code": w.code,
                    "value": w.value,
                }
                for w in self.warnings
            ],
        }


class InputValidator:
    """Input validation utilities."""

    # Common regex patterns
    PATTERNS = {
        "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        "url": r"^https?://[^\s]+$",
        "uuid": r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        "slug": r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        "version": r"^\d+\.\d+\.\d+$",
        "hex_color": r"^#[0-9a-fA-F]{6}$",
        "alphanumeric": r"^[a-zA-Z0-9]+$",
    }

    @staticmethod
    def validate_string(
        value: Any,
        field: str,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        pattern: Optional[str] = None,
        allowed_values: Optional[List[str]] = None,
        required: bool = True,
    ) -> ValidationResult:
        """Validate string input.

        Args:
            value: Value to validate
            field: Field name
            min_length: Minimum length
            max_length: Maximum length
            pattern: Regex pattern to match
            allowed_values: List of allowed values
            required: Whether field is required

        Returns:
            ValidationResult
        """
        result = ValidationResult()

        # Check required
        if value is None or value == "":
            if required:
                result.add_error(field, "Field is required", "REQUIRED")
            return result

        # Check type
        if not isinstance(value, str):
            result.add_error(field, "Must be a string", "TYPE_ERROR", value)
            return result

        # Check length
        if min_length is not None and len(value) < min_length:
            result.add_error(
                field,
                f"Must be at least {min_length} characters",
                "MIN_LENGTH",
                value,
            )

        if max_length is not None and len(value) > max_length:
            result.add_error(
                field,
                f"Must be at most {max_length} characters",
                "MAX_LENGTH",
                value,
            )

        # Check pattern
        if pattern is not None and not re.match(pattern, value):
            result.add_error(field, "Does not match required pattern", "PATTERN", value)

        # Check allowed values
        if allowed_values is not None and value not in allowed_values:
            result.add_error(
                field,
                f"Must be one of: {', '.join(allowed_values)}",
                "ALLOWED_VALUES",
                value,
            )

        return result

    @staticmethod
    def validate_number(
        value: Any,
        field: str,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        integer_only: bool = False,
        required: bool = True,
    ) -> ValidationResult:
        """Validate numeric input.

        Args:
            value: Value to validate
            field: Field name
            min_value: Minimum value
            max_value: Maximum value
            integer_only: Only allow integers
            required: Whether field is required

        Returns:
            ValidationResult
        """
        result = ValidationResult()

        # Check required
        if value is None:
            if required:
                result.add_error(field, "Field is required", "REQUIRED")
            return result

        # Check type
        if not isinstance(value, (int, float)):
            result.add_error(field, "Must be a number", "TYPE_ERROR", value)
            return result

        # Check integer
        if integer_only and not isinstance(value, int):
            result.add_error(field, "Must be an integer", "INTEGER_REQUIRED", value)

        # Check range
        if min_value is not None and value < min_value:
            result.add_error(
                field, f"Must be at least {min_value}", "MIN_VALUE", value
            )

        if max_value is not None and value > max_value:
            result.add_error(field, f"Must be at most {max_value}", "MAX_VALUE", value)

        return result

    @staticmethod
    def validate_boolean(
        value: Any, field: str, required: bool = True
    ) -> ValidationResult:
        """Validate boolean input.

        Args:
            value: Value to validate
            field: Field name
            required: Whether field is required

        Returns:
            ValidationResult
        """
        result = ValidationResult()

        if value is None:
            if required:
                result.add_error(field, "Field is required", "REQUIRED")
            return result

        if not isinstance(value, bool):
            result.add_error(field, "Must be a boolean", "TYPE_ERROR", value)

        return result

    @staticmethod
    def validate_list(
        value: Any,
        field: str,
        min_items: Optional[int] = None,
        max_items: Optional[int] = None,
        item_validator: Optional[Callable] = None,
        required: bool = True,
    ) -> ValidationResult:
        """Validate list input.

        Args:
            value: Value to validate
            field: Field name
            min_items: Minimum number of items
            max_items: Maximum number of items
            item_validator: Function to validate each item
            required: Whether field is required

        Returns:
            ValidationResult
        """
        result = ValidationResult()

        if value is None:
            if required:
                result.add_error(field, "Field is required", "REQUIRED")
            return result

        if not isinstance(value, list):
            result.add_error(field, "Must be a list", "TYPE_ERROR", value)
            return result

        # Check length
        if min_items is not None and len(value) < min_items:
            result.add_error(
                field, f"Must contain at least {min_items} items", "MIN_ITEMS", value
            )

        if max_items is not None and len(value) > max_items:
            result.add_error(
                field, f"Must contain at most {max_items} items", "MAX_ITEMS", value
            )

        # Validate items
        if item_validator is not None:
            for i, item in enumerate(value):
                try:
                    item_validator(item)
                except ValueError as e:
                    result.add_error(f"{field}[{i}]", str(e), "ITEM_INVALID", item)

        return result

    @staticmethod
    def validate_dict(
        value: Any,
        field: str,
        required_keys: Optional[List[str]] = None,
        schema: Optional[Dict[str, Callable]] = None,
        required: bool = True,
    ) -> ValidationResult:
        """Validate dictionary input.

        Args:
            value: Value to validate
            field: Field name
            required_keys: List of required keys
            schema: Dictionary of key validators
            required: Whether field is required

        Returns:
            ValidationResult
        """
        result = ValidationResult()

        if value is None:
            if required:
                result.add_error(field, "Field is required", "REQUIRED")
            return result

        if not isinstance(value, dict):
            result.add_error(field, "Must be a dictionary", "TYPE_ERROR", value)
            return result

        # Check required keys
        if required_keys:
            missing = [k for k in required_keys if k not in value]
            if missing:
                result.add_error(
                    field,
                    f"Missing required keys: {', '.join(missing)}",
                    "MISSING_KEYS",
                    missing,
                )

        # Validate with schema
        if schema:
            for key, validator in schema.items():
                if key in value:
                    key_result = validator(value[key], f"{field}.{key}")
                    result.errors.extend(key_result.errors)
                    result.warnings.extend(key_result.warnings)

        return result

    @staticmethod
    def validate_file_path(
        value: Any,
        field: str,
        must_exist: bool = False,
        must_be_file: bool = False,
        must_be_dir: bool = False,
        allowed_extensions: Optional[List[str]] = None,
        required: bool = True,
    ) -> ValidationResult:
        """Validate file path input.

        Args:
            value: Value to validate
            field: Field name
            must_exist: Path must exist
            must_be_file: Path must be a file
            must_be_dir: Path must be a directory
            allowed_extensions: List of allowed file extensions
            required: Whether field is required

        Returns:
            ValidationResult
        """
        result = ValidationResult()

        if value is None or value == "":
            if required:
                result.add_error(field, "Field is required", "REQUIRED")
            return result

        if not isinstance(value, (str, Path)):
            result.add_error(field, "Must be a path", "TYPE_ERROR", value)
            return result

        path = Path(value)

        # Check existence
        if must_exist and not path.exists():
            result.add_error(field, "Path does not exist", "NOT_FOUND", str(path))

        # Check file vs directory
        if must_be_file and path.exists() and not path.is_file():
            result.add_error(field, "Must be a file", "NOT_FILE", str(path))

        if must_be_dir and path.exists() and not path.is_dir():
            result.add_error(field, "Must be a directory", "NOT_DIR", str(path))

        # Check extension
        if allowed_extensions and path.suffix[1:] not in allowed_extensions:
            result.add_error(
                field,
                f"Extension must be one of: {', '.join(allowed_extensions)}",
                "INVALID_EXTENSION",
                path.suffix,
            )

        return result

    @staticmethod
    def validate_datetime(
        value: Any,
        field: str,
        min_date: Optional[datetime] = None,
        max_date: Optional[datetime] = None,
        required: bool = True,
    ) -> ValidationResult:
        """Validate datetime input.

        Args:
            value: Value to validate
            field: Field name
            min_date: Minimum allowed date
            max_date: Maximum allowed date
            required: Whether field is required

        Returns:
            ValidationResult
        """
        result = ValidationResult()

        if value is None:
            if required:
                result.add_error(field, "Field is required", "REQUIRED")
            return result

        if not isinstance(value, datetime):
            # Try to parse string
            if isinstance(value, str):
                try:
                    value = datetime.fromisoformat(value.replace("Z", "+00:00"))
                except ValueError:
                    result.add_error(
                        field, "Invalid datetime format", "INVALID_FORMAT", value
                    )
                    return result
            else:
                result.add_error(field, "Must be a datetime", "TYPE_ERROR", value)
                return result

        # Check range
        if min_date and value < min_date:
            result.add_error(
                field, f"Must be after {min_date.isoformat()}", "MIN_DATE", value
            )

        if max_date and value > max_date:
            result.add_error(
                field, f"Must be before {max_date.isoformat()}", "MAX_DATE", value
            )

        return result

    @classmethod
    def validate_email(cls, value: Any, field: str, required: bool = True) -> ValidationResult:
        """Validate email address."""
        return cls.validate_string(
            value, field, pattern=cls.PATTERNS["email"], required=required
        )

    @classmethod
    def validate_url(cls, value: Any, field: str, required: bool = True) -> ValidationResult:
        """Validate URL."""
        return cls.validate_string(
            value, field, pattern=cls.PATTERNS["url"], required=required
        )

    @classmethod
    def validate_uuid(cls, value: Any, field: str, required: bool = True) -> ValidationResult:
        """Validate UUID."""
        return cls.validate_string(
            value, field, pattern=cls.PATTERNS["uuid"], required=required
        )


def validate_workflow_config(config: Dict) -> ValidationResult:
    """Validate workflow configuration.

    Args:
        config: Workflow configuration dictionary

    Returns:
        ValidationResult
    """
    result = ValidationResult()
    validator = InputValidator()

    # Validate name
    name_result = validator.validate_string(
        config.get("name"),
        "name",
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_-]+$",
    )
    result.errors.extend(name_result.errors)

    # Validate description
    desc_result = validator.validate_string(
        config.get("description"), "description", max_length=500, required=False
    )
    result.errors.extend(desc_result.errors)

    # Validate steps
    steps_result = validator.validate_list(
        config.get("steps"), "steps", min_items=1
    )
    result.errors.extend(steps_result.errors)

    return result
