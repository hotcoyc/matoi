"""Shared CLI utilities."""

from pathlib import Path

from matoi.agents.registry import AgentRegistry

# Project root — walk up from this file to find agents/ directory
_CLI_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _CLI_DIR.parent.parent.parent  # src/matoi/cli -> project root


def get_project_root() -> Path:
    """Return the project root (where agents/, teams/, assets/ live)."""
    return _PROJECT_ROOT


def get_registry() -> AgentRegistry:
    """Load and return the agent registry."""
    agents_dir = get_project_root() / "agents"
    registry = AgentRegistry(agents_dir)
    registry.load_all()
    return registry


def load_avatar(slug: str) -> str | None:
    """Load Braille-art avatar for an agent, or None if not found."""
    avatar_path = get_project_root() / "assets" / "avatars" / f"{slug}.txt"
    if avatar_path.exists():
        return avatar_path.read_text()
    return None
