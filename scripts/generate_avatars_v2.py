"""Generate larger pixel-art avatars with color for terminal display.

Creates 48x56 pixel faces, saved as PNG + Braille txt.
Use `chafa` for colored terminal display.

Usage: python scripts/generate_avatars_v2.py
"""

from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("pip install Pillow")
    raise SystemExit(1)

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets" / "avatars"

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SKIN = (255, 220, 185)
SKIN_SHADOW = (230, 190, 150)
HAIR_DARK = (40, 30, 25)
HAIR_BROWN = (80, 55, 35)
RED = (220, 60, 60)
BLUE = (60, 80, 160)
GRAY = (80, 80, 80)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (180, 180, 180)
GREEN = (60, 140, 80)
TEAL = (50, 120, 130)
GLASS = (180, 210, 230)
BG = (30, 30, 40)


def draw_startup_pm() -> Image.Image:
    """Young, spiky hair, confident smirk, hoodie."""
    img = Image.new("RGB", (48, 56), BG)
    d = ImageDraw.Draw(img)

    # Hair - spiky, messy
    for x, y in [(14, 2), (18, 0), (22, 1), (26, 0), (30, 2)]:
        d.rectangle([x, y, x + 3, y + 8], fill=HAIR_DARK)
    d.rectangle([12, 4, 35, 14], fill=HAIR_DARK)
    d.rectangle([10, 8, 37, 14], fill=HAIR_DARK)

    # Head
    d.rectangle([12, 12, 35, 38], fill=SKIN)
    d.rectangle([14, 13, 33, 37], fill=SKIN)

    # Eyes - confident
    d.rectangle([16, 20, 21, 24], fill=WHITE)
    d.rectangle([26, 20, 31, 24], fill=WHITE)
    d.rectangle([18, 21, 20, 23], fill=BLACK)
    d.rectangle([28, 21, 30, 23], fill=BLACK)
    d.point([(19, 21)], fill=WHITE)  # highlight
    d.point([(29, 21)], fill=WHITE)

    # Eyebrows - angled
    d.line([(16, 18), (21, 19)], fill=HAIR_DARK, width=2)
    d.line([(26, 19), (31, 18)], fill=HAIR_DARK, width=2)

    # Nose
    d.rectangle([23, 27, 24, 30], fill=SKIN_SHADOW)

    # Smirk
    d.line([(19, 33), (28, 33)], fill=(180, 80, 80), width=1)
    d.line([(28, 33), (30, 31)], fill=(180, 80, 80), width=1)

    # Neck
    d.rectangle([20, 38, 27, 42], fill=SKIN)

    # Hoodie - red
    d.rectangle([8, 42, 39, 55], fill=RED)
    d.rectangle([12, 43, 35, 55], fill=(190, 50, 50))
    # Hood strings
    d.line([(21, 42), (21, 48)], fill=WHITE, width=1)
    d.line([(27, 42), (27, 48)], fill=WHITE, width=1)
    # V-neck
    d.polygon([(20, 42), (24, 48), (28, 42)], fill=SKIN)

    return img


def draw_delivery_pm() -> Image.Image:
    """Serious, glasses, neat parted hair, button shirt."""
    img = Image.new("RGB", (48, 56), BG)
    d = ImageDraw.Draw(img)

    # Hair - neat, parted
    d.rectangle([12, 4, 35, 14], fill=HAIR_BROWN)
    d.rectangle([10, 8, 37, 14], fill=HAIR_BROWN)
    d.rectangle([10, 6, 14, 14], fill=HAIR_BROWN)  # left side
    d.rectangle([33, 6, 37, 14], fill=HAIR_BROWN)
    # Part
    d.line([(22, 4), (22, 10)], fill=SKIN, width=2)

    # Head
    d.rectangle([12, 12, 35, 38], fill=SKIN)
    d.rectangle([14, 13, 33, 37], fill=SKIN)

    # Glasses
    d.rectangle([14, 20, 22, 26], fill=BLACK)
    d.rectangle([15, 21, 21, 25], fill=GLASS)
    d.rectangle([25, 20, 33, 26], fill=BLACK)
    d.rectangle([26, 21, 32, 25], fill=GLASS)
    d.line([(22, 22), (25, 22)], fill=BLACK, width=1)

    # Eyes behind glasses
    d.rectangle([17, 22, 19, 24], fill=BLACK)
    d.rectangle([28, 22, 30, 24], fill=BLACK)

    # Nose
    d.rectangle([23, 27, 24, 31], fill=SKIN_SHADOW)
    d.point([(22, 31)], fill=SKIN_SHADOW)

    # Mouth - straight
    d.line([(19, 33), (28, 33)], fill=(180, 100, 100), width=1)

    # Neck
    d.rectangle([20, 38, 27, 42], fill=SKIN)

    # Button shirt - blue
    d.rectangle([8, 42, 39, 55], fill=BLUE)
    d.rectangle([10, 43, 37, 55], fill=(50, 70, 140))
    # Collar
    d.polygon([(18, 42), (14, 46), (20, 46)], fill=WHITE)
    d.polygon([(30, 42), (34, 46), (28, 46)], fill=WHITE)
    # Buttons
    d.line([(24, 42), (24, 55)], fill=(40, 60, 120), width=1)
    for y in [45, 49, 53]:
        d.rectangle([23, y, 25, y + 1], fill=WHITE)

    return img


def draw_enterprise_pm() -> Image.Image:
    """Stern, square jaw, slicked back, suit and tie."""
    img = Image.new("RGB", (48, 56), BG)
    d = ImageDraw.Draw(img)

    # Hair - slicked back
    d.rectangle([10, 2, 37, 12], fill=HAIR_DARK)
    d.rectangle([8, 6, 39, 12], fill=HAIR_DARK)

    # Head - wider, square
    d.rectangle([10, 10, 37, 40], fill=SKIN)
    d.rectangle([12, 11, 35, 39], fill=SKIN)

    # Eyes - stern, narrow
    d.rectangle([14, 21, 20, 24], fill=WHITE)
    d.rectangle([27, 21, 33, 24], fill=WHITE)
    d.rectangle([16, 22, 19, 23], fill=BLACK)
    d.rectangle([29, 22, 32, 23], fill=BLACK)

    # Eyebrows - thick, straight
    d.rectangle([14, 18, 20, 20], fill=HAIR_DARK)
    d.rectangle([27, 18, 33, 20], fill=HAIR_DARK)

    # Nose
    d.rectangle([23, 26, 24, 31], fill=SKIN_SHADOW)
    d.rectangle([22, 30, 25, 31], fill=SKIN_SHADOW)

    # Mouth - firm
    d.line([(18, 34), (29, 34)], fill=(160, 80, 80), width=2)

    # Neck - thick
    d.rectangle([18, 40, 29, 44], fill=SKIN)

    # Suit - dark gray
    d.rectangle([4, 44, 43, 55], fill=DARK_GRAY)
    # Lapels
    d.polygon([(4, 44), (20, 44), (16, 55)], fill=GRAY)
    d.polygon([(43, 44), (28, 44), (32, 55)], fill=GRAY)
    # White shirt
    d.rectangle([20, 44, 28, 55], fill=WHITE)
    # Tie
    d.polygon([(22, 44), (24, 48), (26, 44)], fill=RED)
    d.rectangle([23, 48, 25, 55], fill=RED)

    return img


def draw_product_strategist_pm() -> Image.Image:
    """Thoughtful, side-swept hair, soft features, turtleneck."""
    img = Image.new("RGB", (48, 56), BG)
    d = ImageDraw.Draw(img)

    # Hair - side-swept, flowing
    d.rectangle([12, 4, 35, 14], fill=HAIR_BROWN)
    d.rectangle([10, 6, 37, 14], fill=HAIR_BROWN)
    # Long sweep to left
    d.rectangle([6, 6, 14, 18], fill=HAIR_BROWN)
    d.rectangle([4, 8, 12, 20], fill=HAIR_BROWN)
    d.rectangle([6, 10, 10, 16], fill=HAIR_BROWN)

    # Head - slightly rounder
    d.ellipse([12, 12, 35, 38], fill=SKIN)

    # Eyes - wider, thoughtful
    d.rectangle([16, 20, 21, 25], fill=WHITE)
    d.rectangle([26, 20, 31, 25], fill=WHITE)
    d.rectangle([17, 21, 19, 24], fill=(60, 100, 60))  # green eyes
    d.rectangle([27, 21, 29, 24], fill=(60, 100, 60))
    d.rectangle([18, 22, 19, 23], fill=BLACK)  # pupils
    d.rectangle([28, 22, 29, 23], fill=BLACK)
    d.point([(18, 21)], fill=WHITE)
    d.point([(28, 21)], fill=WHITE)

    # Eyebrows - slightly raised
    d.line([(16, 18), (21, 19)], fill=HAIR_BROWN, width=1)
    d.line([(26, 19), (31, 18)], fill=HAIR_BROWN, width=1)

    # Nose
    d.rectangle([23, 27, 24, 30], fill=SKIN_SHADOW)

    # Slight smile
    d.line([(20, 33), (27, 33)], fill=(180, 100, 100), width=1)
    d.point([(19, 32), (28, 32)], fill=SKIN_SHADOW)

    # Neck
    d.rectangle([20, 38, 27, 42], fill=SKIN)

    # Turtleneck - teal
    d.rectangle([8, 42, 39, 55], fill=TEAL)
    d.rectangle([10, 44, 37, 55], fill=(40, 105, 115))
    # Turtleneck collar
    d.rectangle([18, 40, 29, 44], fill=TEAL)
    d.rectangle([20, 41, 27, 43], fill=(40, 105, 115))

    return img


# Braille converter for txt fallback
BRAILLE_DOTS = [
    (0, 0, 0x01), (0, 1, 0x02), (0, 2, 0x04),
    (1, 0, 0x08), (1, 1, 0x10), (1, 2, 0x20),
    (0, 3, 0x40), (1, 3, 0x80),
]


def image_to_braille(img: Image.Image) -> str:
    bw = img.convert("1")
    pixels = bw.load()
    w, h = bw.size
    lines = []
    for y in range(0, h, 4):
        line = ""
        for x in range(0, w, 2):
            code = 0x2800
            for dx, dy, bit in BRAILLE_DOTS:
                px, py = x + dx, y + dy
                if px < w and py < h and pixels[px, py] == 0:
                    code |= bit
            line += chr(code)
        lines.append(line)
    return "\n".join(lines)


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    avatars = {
        "startup-pm": draw_startup_pm,
        "delivery-pm": draw_delivery_pm,
        "enterprise-pm": draw_enterprise_pm,
        "product-strategist-pm": draw_product_strategist_pm,
    }

    for slug, draw_fn in avatars.items():
        img = draw_fn()

        # Save PNG (for chafa color display)
        png_path = ASSETS_DIR / f"{slug}.png"
        img.save(png_path)

        # Save Braille fallback
        braille = image_to_braille(img)
        txt_path = ASSETS_DIR / f"{slug}.txt"
        txt_path.write_text(braille)

        print(f"=== {slug} ===")
        print(braille)
        print()

    print("Done! Use `chafa --size=20 assets/avatars/<name>.png` for color display.")


if __name__ == "__main__":
    main()
