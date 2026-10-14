"""Tests for portfolio.json generation."""
import json
import sys
import tempfile
import os
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))
import factory


class TestPortfolioJson:
    """Tests for portfolio.json generation."""

    def test_gen_portfolio_json_basic_structure(self):
        """gen_portfolio_json returns valid JSON with all required fields."""
        app_def = {
            "name": "test-app",
            "desc": "A test application for AI/ML workloads.",
            "features": ["Feature one", "Feature two", "Feature three"],
            "tech": ["Python", "OpenAI", "FastAPI"],
            "api_key": "LLM_API_KEY",
        }
        repo_name = "test-app-alan-vo"
        result = factory.gen_portfolio_json(app_def, repo_name)
        portfolio = json.loads(result)

        assert portfolio["schema_version"] == 1
        assert portfolio["name"] == repo_name
        assert portfolio["owner"] == "ALANDVO"
        assert portfolio["email"] == "alanvo@gmail.com"
        assert "domain" in portfolio
        assert isinstance(portfolio["workflows"], list)
        assert len(portfolio["workflows"]) >= 3
        assert portfolio["auth"] == "llm-api-key"
        assert portfolio["llm_providers"] == [
            "openai-compatible",
            "anthropic",
            "gemini",
            "ollama",
        ]
        assert "summary" in portfolio
        assert isinstance(portfolio["summary"], str)

    def test_gen_portfolio_json_domain_from_tech(self):
        """Domain is derived from tech tags."""
        app_def = {
            "name": "sec-app",
            "desc": "Security app.",
            "features": ["f1", "f2", "f3"],
            "tech": ["Python", "CVE", "NVD", "MITRE ATT&CK"],
            "api_key": "LLM_API_KEY",
        }
        result = factory.gen_portfolio_json(app_def, "sec-app-alan-vo")
        portfolio = json.loads(result)
        assert "Security" in portfolio["domain"]

        app_def2 = {
            "name": "cloud-app",
            "desc": "Cloud app.",
            "features": ["f1", "f2", "f3"],
            "tech": ["AWS", "Kubernetes", "Terraform"],
            "api_key": "LLM_API_KEY",
        }
        result2 = factory.gen_portfolio_json(app_def2, "cloud-app-alan-vo")
        portfolio2 = json.loads(result2)
        assert "Cloud/Infrastructure" in portfolio2["domain"]

    def test_gen_portfolio_json_workflows_from_features(self):
        """Workflows are derived from features list."""
        app_def = {
            "name": "wf-app",
            "desc": "Workflow app.",
            "features": ["First workflow", "Second workflow", "Third workflow", "Fourth workflow"],
            "tech": ["Python"],
            "api_key": "LLM_API_KEY",
        }
        result = factory.gen_portfolio_json(app_def, "wf-app-alan-vo")
        portfolio = json.loads(result)
        assert portfolio["workflows"][:3] == [
            "First workflow",
            "Second workflow",
            "Third workflow",
        ]
        assert len(portfolio["workflows"]) <= 5

    def test_gen_portfolio_json_few_features_pads_workflows(self):
        """If fewer than 3 features, generic workflows are added."""
        app_def = {
            "name": "few-app",
            "desc": "Few features app.",
            "features": ["Only one feature"],
            "tech": ["Python"],
            "api_key": "LLM_API_KEY",
        }
        result = factory.gen_portfolio_json(app_def, "few-app-alan-vo")
        portfolio = json.loads(result)
        assert len(portfolio["workflows"]) >= 3
        assert portfolio["workflows"][0] == "Only one feature"

    def test_gen_portfolio_json_summary_from_desc(self):
        """Summary is first sentence of description."""
        app_def = {
            "name": "sum-app",
            "desc": "First sentence. Second sentence here.",
            "features": ["f1", "f2", "f3"],
            "tech": ["Python"],
            "api_key": "LLM_API_KEY",
        }
        result = factory.gen_portfolio_json(app_def, "sum-app-alan-vo")
        portfolio = json.loads(result)
        assert portfolio["summary"] == "First sentence."

    def test_build_app_includes_portfolio_json(self):
        """build_app creates portfolio.json in output directory."""
        app_def = {
            "name": "build-test",
            "desc": "Build test app.",
            "features": ["Feature A", "Feature B", "Feature C"],
            "install": "pip install -r requirements.txt",
            "usage": "python main.py",
            "api_key": "LLM_API_KEY",
            "tech": ["Python", "FastAPI"],
            "main_code": "def main():\n    print('hello')\n",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("factory.BASE", tmpdir):
                dir_path, name = factory.build_app(app_def)
                portfolio_path = os.path.join(dir_path, "portfolio.json")
                assert os.path.exists(portfolio_path), "portfolio.json not created"

                with open(portfolio_path) as f:
                    portfolio = json.load(f)

                assert portfolio["name"] == name
                assert portfolio["schema_version"] == 1

    def test_build_app_into_includes_portfolio_json(self):
        """build_app_into writes portfolio.json to existing directory."""
        app_def = {
            "name": "update-test",
            "desc": "Update test app.",
            "features": ["Feature X", "Feature Y", "Feature Z"],
            "install": "pip install -r requirements.txt",
            "usage": "python main.py",
            "api_key": "LLM_API_KEY",
            "tech": ["Python"],
            "main_code": "def main():\n    print('update')\n",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            factory.build_app_into(app_def, tmpdir)
            portfolio_path = os.path.join(tmpdir, "portfolio.json")
            assert os.path.exists(portfolio_path), "portfolio.json not created in update"

            with open(portfolio_path) as f:
                portfolio = json.load(f)

            assert portfolio["schema_version"] == 1
            assert portfolio["name"] == "update-test-alan-vo"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])