"""Unit tests for ai-factory core functionality."""
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

import pytest

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import factory


class TestStateManagement:
    """Tests for state.json load/save/mark operations."""

    def test_load_state_missing_file(self):
        """load_state returns default structure when file doesn't exist."""
        with patch("factory.STATE", "/nonexistent/state.json"):
            state = factory.load_state()
            assert state == {"repos": []}

    def test_load_state_existing_file(self):
        """load_state reads and parses existing JSON."""
        test_state = {"repos": [{"name": "test-app-alan-vo", "pushed_at": "2024-01-01T00:00:00"}]}
        with patch("factory.STATE", "/tmp/test_state.json"):
            with patch("builtins.open", mock_open(read_data=json.dumps(test_state))):
                with patch("os.path.exists", return_value=True):
                    state = factory.load_state()
                    assert state == test_state

    def test_save_state_writes_json(self):
        """save_state writes state to file with indentation."""
        test_state = {"repos": [{"name": "test-app-alan-vo", "pushed_at": "2024-01-01T00:00:00"}]}
        with patch("factory.STATE", "/tmp/test_state.json"):
            with patch("builtins.open", mock_open()) as m:
                factory.save_state(test_state)
                m.assert_called_once_with("/tmp/test_state.json", "w")
                handle = m()
                written = "".join(call.args[0] for call in handle.write.call_args_list)
                assert json.loads(written) == test_state

    def test_mark_pushed_new_repo(self):
        """mark_pushed adds new repo with timestamps."""
        with patch("factory.load_state", return_value={"repos": []}):
            with patch("factory.save_state") as mock_save:
                with patch("factory.datetime") as mock_dt:
                    mock_dt.datetime.now.return_value.isoformat.return_value = "2024-01-15T12:00:00"
                    factory.mark_pushed("new-app-alan-vo")
                    saved = mock_save.call_args[0][0]
                    assert len(saved["repos"]) == 1
                    repo = saved["repos"][0]
                    assert repo["name"] == "new-app-alan-vo"
                    assert repo["pushed_at"] == "2024-01-15T12:00:00"
                    assert repo["updated_at"] == "2024-01-15T12:00:00"
                    assert repo["update_count"] == 0

    def test_mark_pushed_existing_repo_update(self):
        """mark_pushed updates timestamp and increments update_count for existing repo."""
        existing = {
            "repos": [
                {"name": "existing-app-alan-vo", "pushed_at": "2024-01-01T00:00:00", "updated_at": "2024-01-10T00:00:00", "update_count": 2}
            ]
        }
        with patch("factory.load_state", return_value=existing):
            with patch("factory.save_state") as mock_save:
                with patch("factory.datetime") as mock_dt:
                    mock_dt.datetime.now.return_value.isoformat.return_value = "2024-01-15T12:00:00"
                    factory.mark_pushed("existing-app-alan-vo", is_update=True)
                    saved = mock_save.call_args[0][0]
                    repo = saved["repos"][0]
                    assert repo["updated_at"] == "2024-01-15T12:00:00"
                    assert repo["update_count"] == 3
                    assert repo["pushed_at"] == "2024-01-01T00:00:00"  # unchanged


class TestRepoNaming:
    """Tests for repository name formatting."""

    def test_repo_name_format(self):
        """repo_name appends -alan-vo suffix."""
        assert factory.repo_name("threat-intel") == "threat-intel-alan-vo"
        assert factory.repo_name("log-anomaly-detector") == "log-anomaly-detector-alan-vo"
        assert factory.repo_name("simple") == "simple-alan-vo"

    def test_repo_name_handles_existing_suffix(self):
        """repo_name doesn't double-append if already suffixed (current behavior)."""
        # Current implementation just appends; this documents behavior
        assert factory.repo_name("app-alan-vo") == "app-alan-vo-alan-vo"


class TestGitHubAPI:
    """Tests for GitHub API helpers (mocked)."""

    @patch("factory.urllib.request.urlopen")
    def test_api_success(self, mock_urlopen):
        """api() returns parsed JSON on success."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"id": 123, "name": "test"}'
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = lambda s, *a: None
        mock_urlopen.return_value = mock_response

        result = factory.api("/repos/ALANDVO/test")
        assert result == {"id": 123, "name": "test"}

    @patch("factory.urllib.request.urlopen")
    def test_api_http_error(self, mock_urlopen):
        """api() returns error JSON on HTTPError."""
        import urllib.error
        mock_error = urllib.error.HTTPError("url", 404, "Not Found", {}, None)
        mock_error.read = lambda: b'{"message": "Not Found", "documentation_url": "..."}'
        mock_urlopen.side_effect = mock_error

        result = factory.api("/repos/ALANDVO/nonexistent")
        assert "message" in result
        assert result["message"] == "Not Found"

    def test_exists_true_when_id_present(self):
        """exists() returns True when repo has id."""
        with patch("factory.api", return_value={"id": 123, "name": "test"}):
            assert factory.exists("test") is True

    def test_exists_false_when_no_id(self):
        """exists() returns False when repo response lacks id."""
        with patch("factory.api", return_value={"message": "Not Found"}):
            assert factory.exists("test") is False


class TestAppLoading:
    """Tests for loading app definitions from modules."""

    def test_load_all_apps_collects_from_modules(self):
        """load_all_apps imports each module and collects APPS lists."""
        mock_module1 = MagicMock()
        mock_module1.APPS = [{"name": "app1"}, {"name": "app2"}]
        mock_module2 = MagicMock()
        mock_module2.APPS = [{"name": "app3"}]
        mock_module3 = MagicMock()
        mock_module3.APPS = []

        with patch("builtins.__import__", side_effect=[mock_module1, mock_module2, mock_module3, MagicMock(), MagicMock(), MagicMock()]):
            with patch("factory.log"):
                apps = factory.load_all_apps()
                assert len(apps) == 3
                assert apps[0]["name"] == "app1"
                assert apps[2]["name"] == "app3"

    def test_load_all_apps_handles_import_error(self):
        """load_all_apps skips modules that fail to import."""
        mock_module = MagicMock()
        mock_module.APPS = [{"name": "app1"}]

        def import_side_effect(name, *args, **kwargs):
            if name == "appdefs":
                return mock_module
            raise ImportError(f"No module named '{name}'")

        with patch("builtins.__import__", side_effect=import_side_effect):
            with patch("factory.log"):
                apps = factory.load_all_apps()
                assert len(apps) == 1
                assert apps[0]["name"] == "app1"

    def test_load_all_apps_handles_missing_APPS_attribute(self):
        """load_all_apps handles modules without APPS attribute."""
        mock_module = MagicMock()
        del mock_module.APPS

        with patch("builtins.__import__", return_value=mock_module):
            with patch("factory.log"):
                apps = factory.load_all_apps()
                assert apps == []


class TestFileGenerationHelpers:
    """Tests for README, LICENSE, requirements, Dockerfile generation."""

    def test_gen_readme_contains_key_sections(self):
        """gen_readme produces markdown with expected sections."""
        readme = factory.gen_readme(
            name="test-app-alan-vo",
            desc="Test description",
            features=["Feature 1", "Feature 2"],
            install="pip install -r requirements.txt",
            usage="python main.py",
            api_key="LLM_API_KEY",
            tech=["Python", "OpenAI"],
            links={"GitHub": "https://github.com/ALANDVO/test"}
        )
        assert "# test-app-alan-vo" in readme
        assert "Test description" in readme
        assert "Feature 1" in readme
        assert "Feature 2" in readme
        assert "pip install -r requirements.txt" in readme
        assert "python main.py" in readme
        assert "LLM_API_KEY" in readme
        assert "Python" in readme
        assert "OpenAI" in readme
    def test_gen_license_is_mit(self):
        """gen_license returns MIT license text with copyright."""
        license_text = factory.gen_license()
        assert "MIT License" in license_text
        assert "Copyright (c)" in license_text
        assert "Alan Vo" in license_text
        assert "PERMISSION IS HEREBY GRANTED" in license_text.upper()

    def test_gen_gitignore_covers_python_artifacts(self):
        """gen_gitignore includes standard Python ignores."""
        gitignore = factory.gen_gitignore()
        assert "__pycache__/" in gitignore
        assert "*.pyc" in gitignore
        assert ".venv/" in gitignore
        assert ".env" in gitignore
        assert "dist/" in gitignore

    def test_gen_requirements_includes_base_deps(self):
        """gen_requirements returns base dependencies."""
        reqs = factory.gen_requirements()
        assert "requests>=" in reqs
        assert "python-dotenv>=" in reqs

    def test_gen_dockerfile_has_python_base(self):
        """gen_dockerfile uses Python slim base."""
        dockerfile = factory.gen_dockerfile()
        assert "FROM python:" in dockerfile
        assert "slim" in dockerfile
        assert "WORKDIR" in dockerfile

    def test_gen_docker_compose_has_services(self):
        """gen_docker_compose defines app service."""
        compose = factory.gen_docker_compose()
        assert "services:" in compose
        assert "app:" in compose

    def test_gen_env_example_has_llm_key(self):
        """gen_env_example includes LLM_API_KEY placeholder."""
        env = factory.gen_env_example("LLM_API_KEY")
        assert "LLM_API_KEY" in env
        assert "your-api-key-here" in env


class TestBuildApp:
    """Tests for build_app directory creation and file writing."""

    def test_build_app_creates_directory_structure(self):
        """build_app creates app directory with all standard files."""
        app_def = {
            "name": "test-app",
            "desc": "Test app description",
            "features": ["Feature 1", "Feature 2"],
            "install": "pip install -r requirements.txt",
            "usage": "python main.py",
            "api_key": "LLM_API_KEY",
            "tech": ["Python", "OpenAI"],
            "main_code": "def main(): pass",
            "links": {"GitHub": "https://github.com/ALANDVO/test"},
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("factory.BASE", tmpdir):
                with patch("factory.create_repo", return_value=True):
                    with patch("factory.push", return_value=(True, "")):
                        with patch("factory.clean_local"):
                            with patch("factory.log"):
                                dir_path, name = factory.build_app(app_def)

                                assert os.path.exists(dir_path)
                                assert name == "test-app-alan-vo"

                                # Check standard files exist
                                for fname in ["README.md", "LICENSE", ".gitignore", "requirements.txt", "Dockerfile", "docker-compose.yml", "CONTRIBUTING.md"]:
                                    assert os.path.exists(os.path.join(dir_path, fname)), f"Missing {fname}"

                                # Check .github/CODEOWNERS
                                assert os.path.exists(os.path.join(dir_path, ".github", "CODEOWNERS"))

    def test_build_app_writes_correct_content(self):
        """build_app writes expected content to each file."""
        app_def = {
            "name": "content-test",
            "desc": "Content test app",
            "features": ["Test feature"],
            "install": "pip install .",
            "usage": "python -m content_test",
            "api_key": "TEST_KEY",
            "tech": ["Python"],
            "main_code": "print('hello')",
            "links": {},
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("factory.BASE", tmpdir):
                with patch("factory.create_repo", return_value=True):
                    with patch("factory.push", return_value=(True, "")):
                        with patch("factory.clean_local"):
                            with patch("factory.log"):
                                dir_path, _ = factory.build_app(app_def)

                                # Verify README content
                                with open(os.path.join(dir_path, "README.md")) as f:
                                    readme = f.read()
                                    assert "content-test-alan-vo" in readme
                                    assert "Content test app" in readme
                                    assert "Test feature" in readme

                                # Verify LICENSE
                                with open(os.path.join(dir_path, "LICENSE")) as f:
                                    license_text = f.read()
                                    assert "MIT License" in license_text

                                # Verify requirements
                                with open(os.path.join(dir_path, "requirements.txt")) as f:
                                    reqs = f.read()
                                    assert "requests" in reqs

    def test_build_app_writes_correct_content(self):
        """build_app writes expected content to each file."""
        app_def = {
            "name": "content-test",
            "desc": "Content test app",
            "features": ["Test feature"],
            "install": "pip install .",
            "usage": "python -m content_test",
            "api_key": "TEST_KEY",
            "tech": ["Python"],
            "main_code": "print('hello')",
            "links": {},
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("factory.BASE", tmpdir):
                with patch("factory.create_repo", return_value=True):
                    with patch("factory.push", return_value=(True, "")):
                        with patch("factory.clean_local"):
                            with patch("factory.log"):
                                dir_path, _ = factory.build_app(app_def)
                            # Verify README content
                            with open(os.path.join(dir_path, "README.md")) as f:
                                readme = f.read()
                                assert "content-test-alan-vo" in readme
                                assert "Content test app" in readme
                                assert "Test feature" in readme

                            # Verify LICENSE
                            with open(os.path.join(dir_path, "LICENSE")) as f:
                                license_text = f.read()
                                assert "MIT License" in license_text

                            # Verify requirements
                            with open(os.path.join(dir_path, "requirements.txt")) as f:
                                reqs = f.read()
                                assert "requests" in reqs


class TestBuildAppInto:
    """Tests for build_app_into (update cycle file writing)."""

    def test_build_app_into_writes_files_to_existing_dir(self):
        """build_app_into writes all standard files into target directory."""
        app_def = {
            "name": "update-test",
            "desc": "Update test app",
            "features": ["Feature A"],
            "install": "pip install -r requirements.txt",
            "usage": "python main.py",
            "api_key": "LLM_API_KEY",
            "tech": ["Python"],
            "main_code": "pass",
            "links": {},
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            factory.build_app_into(app_def, tmpdir)

            for fname in ["README.md", "LICENSE", ".gitignore", "requirements.txt", "Dockerfile", "docker-compose.yml", "CONTRIBUTING.md"]:
                assert os.path.exists(os.path.join(tmpdir, fname)), f"Missing {fname} in update"

            # Check CODEOWNERS
            assert os.path.exists(os.path.join(tmpdir, ".github", "CODEOWNERS"))


class TestMainLogic:
    """Tests for main() orchestration logic."""

    @patch("factory.load_all_apps")
    @patch("factory.load_state")
    def test_main_picks_first_unpushed_app(self, mock_load_state, mock_load_apps):
        """main() selects first app not in pushed set."""
        mock_load_apps.return_value = [
            {"name": "app1", "desc": "App 1", "features": [], "install": "", "usage": "", "api_key": "", "tech": [], "main_code": ""},
            {"name": "app2", "desc": "App 2", "features": [], "install": "", "usage": "", "api_key": "", "tech": [], "main_code": ""},
        ]
        mock_load_state.return_value = {"repos": [{"name": "app1-alan-vo", "pushed_at": "2024-01-01T00:00:00"}]}

        with patch("factory.create_repo", return_value=True) as mock_create:
            with patch("factory.push", return_value=(True, "")) as mock_push:
                with patch("factory.mark_pushed") as mock_mark:
                    with patch("factory.clean_local"):
                        with patch("factory.log"):
                            factory.main(argv=[])

                            mock_create.assert_called_once_with("app2-alan-vo", "App 2")
                            mock_push.assert_called_once()
                            mock_mark.assert_called_once_with("app2-alan-vo")

    @patch("factory.load_all_apps")
    @patch("factory.load_state")
    def test_main_update_cycle_when_all_pushed(self, mock_load_state, mock_load_apps):
        """main() runs update cycle when all apps are pushed."""
        mock_load_apps.return_value = [
            {"name": "app1", "desc": "App 1", "features": [], "install": "", "usage": "", "api_key": "", "tech": [], "main_code": ""},
        ]
        mock_load_state.return_value = {
            "repos": [
                {"name": "app1-alan-vo", "pushed_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00", "update_count": 0}
            ]
        }

        with patch("factory.update_repo") as mock_update:
            with patch("factory.log"):
                factory.main(argv=[])
                mock_update.assert_called_once()
                args = mock_update.call_args[0]
                assert args[0]["name"] == "app1-alan-vo"

    @patch("factory.load_all_apps")
    def test_main_no_apps_found(self, mock_load_apps):
        """main() logs and returns when no apps defined."""
        mock_load_apps.return_value = []
        with patch("factory.log") as mock_log:
            factory.main(argv=[])
            mock_log.assert_any_call("No apps found! Create appdefs files first.")



class TestVersion:
    """Tests for --version flag."""

    def test_version_flag_prints_version(self, capsys):
        """--version prints version and exits."""
        expected_version = factory.get_version()
        factory.main(argv=["--version"])
        captured = capsys.readouterr()
        assert f"ai-factory {expected_version}" in captured.out

    def test_version_flag_exits_early(self):
        """--version exits without loading apps or logging."""
        with patch("factory.load_all_apps") as mock_load_apps:
            with patch("factory.log") as mock_log:
                factory.main(argv=["--version"])
                mock_load_apps.assert_not_called()
                mock_log.assert_not_called()

class TestCleanLocal:
    """Tests for clean_local directory removal."""

    def test_clean_local_removes_directory(self):
        """clean_local removes the app directory if it exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = os.path.join(tmpdir, "test-app-alan-vo")
            os.makedirs(test_dir)
            assert os.path.exists(test_dir)

            with patch("factory.BASE", tmpdir):
                with patch("factory.log") as mock_log:
                    factory.clean_local("test-app-alan-vo")
                    assert not os.path.exists(test_dir)
                    mock_log.assert_called_with("  cleaned local: test-app-alan-vo")

    def test_clean_local_noop_when_missing(self):
        """clean_local does nothing if directory doesn't exist."""
        with patch("factory.BASE", "/nonexistent"):
            with patch("factory.log") as mock_log:
                factory.clean_local("missing-app-alan-vo")
                # Should not error, may or may not log
                # Current implementation only logs if dir existed


# Run with: pytest tests/test_factory.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])