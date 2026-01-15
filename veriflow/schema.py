"""Pydantic models for Veriflow configuration schema."""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class ProjectConfig(BaseModel):
    """Project metadata configuration."""
    name: str
    type: Literal["llm_classification", "tabular", "vision", "rag"]


class BaselineConfig(BaseModel):
    """Baseline reference configuration."""
    ref: str = Field(default="main", description="Git reference for baseline comparison")


class DataChecksConfig(BaseModel):
    """Data verification checks configuration."""
    checks: list[str] = Field(default_factory=list)


class ModelConfig(BaseModel):
    """Model framework configuration."""
    framework: Literal["sklearn", "pytorch", "hf", "api"]
    deterministic: bool = Field(default=True, description="Whether model outputs are deterministic")


class StatisticalTestsConfig(BaseModel):
    """Statistical tests configuration."""
    enabled: bool = Field(default=True)
    method: str = Field(default="bootstrap", description="Statistical test method")


class EvaluationConfig(BaseModel):
    """Evaluation configuration."""
    metrics: dict = Field(default_factory=dict, description="Metric definitions with thresholds")
    statistical_tests: StatisticalTestsConfig = Field(default_factory=StatisticalTestsConfig)


class UIConfig(BaseModel):
    """UI/frontend verification configuration."""
    enabled: bool = Field(default=False)
    runner: str = Field(default="playwright", description="E2E test runner")
    base_url: str = Field(default="http://localhost:3000")
    start: dict = Field(default_factory=dict, description="Commands to start frontend/backend")
    contracts: dict = Field(default_factory=dict, description="API contract test configuration")


class GatesConfig(BaseModel):
    """CI gate configuration."""
    fail_on_regression: bool = Field(default=True)
    fail_on_schema_change: bool = Field(default=True)


class VeriflowConfig(BaseModel):
    """Root Veriflow configuration model."""
    project: Optional[ProjectConfig] = None
    baseline: BaselineConfig = Field(default_factory=BaselineConfig)
    data: DataChecksConfig = Field(default_factory=DataChecksConfig)
    model: Optional[ModelConfig] = None
    evaluation: EvaluationConfig = Field(default_factory=EvaluationConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    gates: GatesConfig = Field(default_factory=GatesConfig)
