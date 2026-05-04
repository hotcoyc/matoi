"""Shared CLI utilities."""

from pathlib import Path

from matoi.agents.registry import AgentRegistry

# Package directory — where bundled_agents/, bundled_assets/ live inside installed package
_CLI_DIR = Path(__file__).resolve().parent
_PACKAGE_DIR = _CLI_DIR.parent  # src/matoi/cli -> src/matoi
_REPO_ROOT = _PACKAGE_DIR.parent.parent  # src/matoi -> repo root (for dev mode)


def _find_agents_dir() -> Path:
    """Find agents directory: bundled (pip install) or repo (dev mode)."""
    # 1. Bundled inside package (pip install / pipx)
    bundled = _PACKAGE_DIR / "bundled_agents"
    if bundled.exists():
        return bundled
    # 2. Repo root (editable install / dev)
    repo = _REPO_ROOT / "agents"
    if repo.exists():
        return repo
    # 3. Fallback
    return bundled


def _find_assets_dir() -> Path:
    """Find assets directory: bundled (pip install) or repo (dev mode)."""
    bundled = _PACKAGE_DIR / "bundled_assets"
    if bundled.exists():
        return bundled
    repo = _REPO_ROOT / "assets"
    if repo.exists():
        return repo
    return bundled


def get_package_root() -> Path:
    """Return the matoi package root."""
    return _PACKAGE_DIR


def get_project_root() -> Path:
    """Return the repo root (backward compat for dev mode)."""
    return _REPO_ROOT


def get_registry() -> AgentRegistry:
    """Load and return the agent registry."""
    agents_dir = _find_agents_dir()
    registry = AgentRegistry(agents_dir)
    registry.load_all()
    return registry


def load_avatar(slug: str, width_chars: int = 30) -> str | None:
    """Load avatar as Braille art from PNG, resized to fit terminal panel."""
    assets_dir = _find_assets_dir()

    png_path = assets_dir / "avatars" / f"{slug}.png"
    if png_path.exists():
        try:
            return _png_to_braille(png_path, width_chars)
        except Exception:
            pass

    txt_path = assets_dir / "avatars" / f"{slug}.txt"
    if txt_path.exists():
        return txt_path.read_text()
    return None


def _png_to_braille(path: Path, width_chars: int = 30) -> str:
    """Convert PNG to Braille Unicode string, resized to fit."""
    from PIL import Image

    img = Image.open(path)

    # Target pixel dimensions: each Braille char = 2px wide, 4px tall
    target_w = width_chars * 2
    ratio = target_w / img.width
    target_h = int(img.height * ratio)
    # Round up to multiple of 4 for clean Braille rows
    target_h = ((target_h + 3) // 4) * 4

    img = img.resize((target_w, target_h), Image.NEAREST)
    bw = img.convert("L").point(lambda x: 0 if x < 128 else 255, "1")
    pixels = bw.load()
    w, h = bw.size

    braille_dots = [
        (0, 0, 0x01), (0, 1, 0x02), (0, 2, 0x04),
        (1, 0, 0x08), (1, 1, 0x10), (1, 2, 0x20),
        (0, 3, 0x40), (1, 3, 0x80),
    ]

    lines = []
    for y in range(0, h, 4):
        line = ""
        for x in range(0, w, 2):
            code = 0x2800
            for dx, dy, bit in braille_dots:
                px, py = x + dx, y + dy
                if px < w and py < h and pixels[px, py] == 0:
                    code |= bit
            line += chr(code)
        lines.append(line)
    return "\n".join(lines)
