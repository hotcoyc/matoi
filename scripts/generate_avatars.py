"""Generate pixel-art Braille avatars for PM agents.

Each avatar is drawn on a PIL Image as 1-bit pixel art,
then converted to Unicode Braille characters.

Usage: python scripts/generate_avatars.py
"""

from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("pip install Pillow")
    raise SystemExit(1)

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets" / "avatars"

# Braille Unicode: each char is a 2x4 dot grid
# Dot positions:  1 4
#                 2 5
#                 3 6
#                 7 8
# Codepoint: 0x2800 + sum of bit values for active dots
BRAILLE_DOTS = [
    (0, 0, 0x01),  # dot 1
    (0, 1, 0x02),  # dot 2
    (0, 2, 0x04),  # dot 3
    (1, 0, 0x08),  # dot 4
    (1, 1, 0x10),  # dot 5
    (1, 2, 0x20),  # dot 6
    (0, 3, 0x40),  # dot 7
    (1, 3, 0x80),  # dot 8
]


def image_to_braille(img: Image.Image) -> str:
    """Convert a 1-bit image to a Braille Unicode string."""
    pixels = img.load()
    w, h = img.size
    lines = []

    for y in range(0, h, 4):
        line = ""
        for x in range(0, w, 2):
            code = 0x2800
            for dx, dy, bit in BRAILLE_DOTS:
                px, py = x + dx, y + dy
                if px < w and py < h:
                    # pixel is "on" if it's dark (0)
                    if pixels[px, py] == 0:
                        code |= bit
            line += chr(code)
        lines.append(line)

    return "\n".join(lines)


def draw_startup_pm() -> Image.Image:
    """Young, spiky hair, confident smirk."""
    img = Image.new("1", (28, 32), 1)  # white background
    d = ImageDraw.Draw(img)

    # Hair - spiky, messy
    d.rectangle([7, 0, 20, 3], fill=0)
    d.rectangle([5, 2, 22, 5], fill=0)
    d.rectangle([9, 0, 11, 0], fill=1)  # spike gap
    d.rectangle([15, 0, 17, 0], fill=1)  # spike gap
    d.point([(6, 1), (21, 1), (5, 3), (22, 3)], fill=0)  # spikes

    # Head outline
    d.rectangle([6, 5, 21, 22], fill=0)
    d.rectangle([8, 6, 19, 21], fill=1)  # face interior

    # Eyes - confident, slightly narrow
    d.rectangle([9, 10, 12, 12], fill=0)   # left eye
    d.rectangle([15, 10, 18, 12], fill=0)  # right eye
    d.rectangle([10, 11, 11, 11], fill=1)  # left pupil highlight
    d.rectangle([16, 11, 17, 11], fill=1)  # right pupil highlight

    # Eyebrows - angled, confident
    d.line([(9, 8), (12, 9)], fill=0)   # left brow
    d.line([(15, 9), (18, 8)], fill=0)  # right brow

    # Nose
    d.point([(14, 15)], fill=0)

    # Mouth - smirk
    d.line([(11, 18), (16, 18)], fill=0)
    d.point([(17, 17)], fill=0)  # smirk up

    # Neck
    d.rectangle([11, 23, 16, 25], fill=0)
    d.rectangle([12, 23, 15, 24], fill=1)

    # Collar - casual t-shirt
    d.rectangle([7, 25, 20, 31], fill=0)
    d.rectangle([9, 26, 18, 31], fill=1)
    d.polygon([(11, 25), (14, 28), (17, 25)], fill=1)  # v-neck

    return img


def draw_delivery_pm() -> Image.Image:
    """Serious, glasses, neat parted hair."""
    img = Image.new("1", (28, 32), 1)
    d = ImageDraw.Draw(img)

    # Hair - neat, parted
    d.rectangle([7, 1, 20, 6], fill=0)
    d.rectangle([6, 3, 21, 6], fill=0)
    d.line([(13, 1), (13, 4)], fill=1)  # part line

    # Head outline
    d.rectangle([6, 6, 21, 23], fill=0)
    d.rectangle([8, 7, 19, 22], fill=1)

    # Glasses - rectangular, serious
    d.rectangle([8, 11, 13, 14], fill=0)   # left lens
    d.rectangle([9, 12, 12, 13], fill=1)   # left lens interior
    d.rectangle([14, 11, 19, 14], fill=0)  # right lens
    d.rectangle([15, 12, 18, 13], fill=1)  # right lens interior
    d.line([(13, 12), (14, 12)], fill=0)   # bridge

    # Eyes behind glasses
    d.rectangle([10, 12, 11, 13], fill=0)  # left eye
    d.rectangle([16, 12, 17, 13], fill=0)  # right eye

    # Nose
    d.line([(13, 15), (14, 17)], fill=0)

    # Mouth - straight, neutral
    d.line([(11, 19), (16, 19)], fill=0)

    # Neck
    d.rectangle([11, 24, 16, 26], fill=0)
    d.rectangle([12, 24, 15, 25], fill=1)

    # Collar - button-up shirt
    d.rectangle([6, 26, 21, 31], fill=0)
    d.rectangle([8, 27, 19, 31], fill=1)
    d.line([(13, 26), (13, 31)], fill=0)  # shirt center line
    d.point([(13, 28), (13, 30)], fill=0)  # buttons

    return img


def draw_enterprise_pm() -> Image.Image:
    """Stern, square jaw, tie, slicked back hair."""
    img = Image.new("1", (28, 32), 1)
    d = ImageDraw.Draw(img)

    # Hair - slicked back, corporate
    d.rectangle([6, 0, 21, 5], fill=0)
    d.rectangle([5, 2, 22, 5], fill=0)
    d.line([(8, 1), (19, 1)], fill=0)  # slick top

    # Head - wider, square jaw
    d.rectangle([5, 5, 22, 23], fill=0)
    d.rectangle([7, 6, 20, 22], fill=1)

    # Eyes - stern, narrow
    d.rectangle([8, 11, 12, 12], fill=0)   # left eye
    d.rectangle([15, 11, 19, 12], fill=0)  # right eye
    d.point([(9, 11), (10, 11)], fill=1)   # left highlight
    d.point([(16, 11), (17, 11)], fill=1)  # right highlight

    # Eyebrows - thick, straight
    d.rectangle([8, 9, 12, 9], fill=0)
    d.rectangle([15, 9, 19, 9], fill=0)

    # Nose
    d.line([(13, 14), (14, 16)], fill=0)
    d.point([(12, 16)], fill=0)

    # Mouth - firm line
    d.line([(10, 19), (17, 19)], fill=0)
    d.line([(10, 20), (17, 20)], fill=0)

    # Neck - thick
    d.rectangle([10, 24, 17, 26], fill=0)
    d.rectangle([11, 24, 16, 25], fill=1)

    # Suit and tie
    d.rectangle([4, 26, 23, 31], fill=0)
    d.rectangle([6, 27, 11, 31], fill=1)   # left lapel
    d.rectangle([16, 27, 21, 31], fill=1)  # right lapel
    # Tie
    d.rectangle([13, 26, 14, 31], fill=0)
    d.polygon([(12, 27), (14, 29), (15, 27)], fill=0)  # tie knot

    return img


def draw_product_strategist_pm() -> Image.Image:
    """Thoughtful, side-swept hair, soft features."""
    img = Image.new("1", (28, 32), 1)
    d = ImageDraw.Draw(img)

    # Hair - side-swept, flowing
    d.rectangle([6, 1, 21, 6], fill=0)
    d.rectangle([4, 2, 8, 7], fill=0)   # side sweep left
    d.rectangle([5, 3, 7, 8], fill=0)   # longer on left side
    d.point([(4, 5), (4, 6)], fill=0)

    # Head - slightly rounder
    d.ellipse([6, 5, 21, 23], fill=0)
    d.ellipse([8, 7, 19, 22], fill=1)

    # Eyes - wider, thoughtful
    d.rectangle([9, 11, 12, 13], fill=0)   # left eye
    d.rectangle([15, 11, 18, 13], fill=0)  # right eye
    d.point([(10, 12)], fill=1)            # left highlight
    d.point([(16, 12)], fill=1)            # right highlight

    # Eyebrows - slightly raised, curious
    d.line([(9, 9), (12, 10)], fill=0)
    d.line([(15, 10), (18, 9)], fill=0)

    # Nose - small
    d.point([(13, 15), (14, 15)], fill=0)

    # Mouth - slight smile, thinking
    d.line([(11, 18), (16, 18)], fill=0)
    d.point([(11, 17), (16, 17)], fill=0)  # dimples/smile

    # Neck
    d.rectangle([11, 23, 16, 25], fill=0)
    d.rectangle([12, 23, 15, 24], fill=1)

    # Collar - turtleneck/casual
    d.rectangle([7, 25, 20, 31], fill=0)
    d.rectangle([9, 27, 18, 31], fill=1)
    d.rectangle([10, 25, 17, 27], fill=0)  # turtleneck
    d.rectangle([11, 25, 16, 26], fill=1)  # turtleneck interior

    return img


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    avatars = {
        "startup-pm": (draw_startup_pm, "🚀"),
        "delivery-pm": (draw_delivery_pm, "📋"),
        "enterprise-pm": (draw_enterprise_pm, "🏢"),
        "product-strategist-pm": (draw_product_strategist_pm, "🎯"),
    }

    for slug, (draw_fn, emoji) in avatars.items():
        img = draw_fn()

        # Also save as PNG for reference
        png_path = ASSETS_DIR / f"{slug}.png"
        img.save(png_path)

        # Convert to Braille
        braille = image_to_braille(img)
        txt_path = ASSETS_DIR / f"{slug}.txt"
        txt_path.write_text(braille)

        print(f"Generated {slug}:")
        print(braille)
        print()


if __name__ == "__main__":
    main()
