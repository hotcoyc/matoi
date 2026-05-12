"""Global and project configuration."""

import json
import os
from pathlib import Path

from pydantic import BaseModel, Field


# Global config lives in ~/.matoi/
GLOBAL_DIR = Path.home() / ".matoi"
GLOBAL_CONFIG_FILE = GLOBAL_DIR / "config.json"

# Project config lives in ./.matoi/ inside user's project
PROJECT_DIR_NAME = ".matoi"


class GlobalConfig(BaseModel):
    """Global config (~/.matoi/config.json). Shared across all projects."""
    anthropic_api_key: str = ""


class ProjectConfig(BaseModel):
    """Project config (./matoi/config.json). Per-project settings."""
    team_name: str = ""
    pm: str = ""
    agents: list[str] = []
    project_name: str = ""
    project_description: str = ""


def get_global_dir() -> Path:
    GLOBAL_DIR.mkdir(exist_ok=True)
    return GLOBAL_DIR


def load_global_config() -> GlobalConfig:
    """Load global config, merging with env vars."""
    config = GlobalConfig()
    if GLOBAL_CONFIG_FILE.exists():
        data = json.loads(GLOBAL_CONFIG_FILE.read_text())
        config = GlobalConfig.model_validate(data)

    # Env var overrides file
    env_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if env_key:
        config.anthropic_api_key = env_key

    return config


def save_global_config(config: GlobalConfig) -> None:
    get_global_dir()
    GLOBAL_CONFIG_FILE.write_text(config.model_dump_json(indent=2))


def get_project_dir(cwd: Path | None = None) -> Path:
    """Return ./matoi/ in current working directory."""
    base = cwd or Path.cwd()
    return base / PROJECT_DIR_NAME


def load_project_config(cwd: Path | None = None) -> ProjectConfig | None:
    """Load project config or None if not initialized."""
    project_dir = get_project_dir(cwd)
    config_path = project_dir / "config.json"
    if not config_path.exists():
        return None
    return ProjectConfig.model_validate_json(config_path.read_text())


def save_project_config(config: ProjectConfig, cwd: Path | None = None) -> None:
    project_dir = get_project_dir(cwd)
    project_dir.mkdir(exist_ok=True)
    (project_dir / "config.json").write_text(config.model_dump_json(indent=2))


def ensure_project_structure(cwd: Path | None = None) -> Path:
    """Create matoi/ directory structure in project. Returns project dir."""
    project_dir = get_project_dir(cwd)
    project_dir.mkdir(exist_ok=True)
    (project_dir / "memory").mkdir(exist_ok=True)
    (project_dir / "artifacts").mkdir(exist_ok=True)
    return project_dir


def require_api_key() -> str:
    """Get API key from global config or env, or raise."""
    config = load_global_config()
    if config.anthropic_api_key:
        # Also set in env so Anthropic SDK picks it up
        os.environ["ANTHROPIC_API_KEY"] = config.anthropic_api_key
        return config.anthropic_api_key
    return ""
