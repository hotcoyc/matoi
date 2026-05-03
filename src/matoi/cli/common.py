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


def load_avatar(slug: str, width_chars: int = 30) -> str | None:
    """Load avatar as Braille art from PNG, resized to fit terminal panel.

    Each Braille char = 2x4 pixels, so width_chars=30 means 60px wide.
    Falls back to .txt if PNG not found or Pillow not installed.
    """
    png_path = get_project_root() / "assets" / "avatars" / f"{slug}.png"
    if png_path.exists():
        try:
            return _png_to_braille(png_path, width_chars)
        except Exception:
            pass

    txt_path = get_project_root() / "assets" / "avatars" / f"{slug}.txt"
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
