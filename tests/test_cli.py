from pathlib import Path

from click.testing import CliRunner

from veriflow.cli import cli
from veriflow.evaluation.results import EvaluationResult, save_evaluation_result


def _make_result(metrics: dict[str, float]) -> EvaluationResult:
    from datetime import datetime

    cis = {
        key: {
            "ci_lower": value - 0.01,
            "ci_upper": value + 0.01,
            "confidence": 0.95,
        }
        for key, value in metrics.items()
    }
    return EvaluationResult(
        metrics=metrics,
        bootstrap_cis=cis,
        metadata={"n_samples": 4, "seed": 42, "n_bootstrap": 10},
        timestamp=datetime.now(),
    )


def test_init_creates_project_structure():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["init", "--force"])

        assert result.exit_code == 0
        assert Path("veriflow.yaml").exists()
        assert Path("data_checks/__init__.py").exists()
        assert Path("evals/__init__.py").exists()
        assert Path("artifacts/.gitkeep").exists()
        assert Path(".veriflow/.gitkeep").exists()


def test_run_requires_config():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["run"])

        assert result.exit_code == 1
        assert "Run 'veriflow init' first" in result.output


def test_compare_reports_improvement():
    runner = CliRunner()
    with runner.isolated_filesystem():
        save_evaluation_result(_make_result({"accuracy": 0.90}), "current")
        save_evaluation_result(_make_result({"accuracy": 0.80}), "baseline")

        result = runner.invoke(cli, ["compare", "--current", "current", "--baseline", "baseline"])

        assert result.exit_code == 0
        assert "Improvement detected" in result.output
        assert "IMPROVED" in result.output
