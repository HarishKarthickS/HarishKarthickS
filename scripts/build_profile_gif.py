"""Build the animated header used by the GitHub profile README."""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


WIDTH = 1200
HEIGHT = 360
FRAMES = 40
FRAME_MS = 100

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "profile-hero.gif"

NAVY = (14, 22, 32)
NAVY_LIGHT = (23, 36, 50)
CREAM = (244, 239, 225)
MUTED = (185, 199, 207)
TEAL = (86, 199, 187)
CORAL = (255, 158, 105)
GOLD = (255, 216, 138)


def load_font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    """Load a suitable local font, with portable fallbacks."""

    candidates: list[Path]
    if mono:
        candidates = [
            Path("C:/Windows/Fonts/consola.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
        ]
    elif bold:
        candidates = [
            Path("C:/Windows/Fonts/georgiab.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"),
        ]
    else:
        candidates = [
            Path("C:/Windows/Fonts/georgia.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"),
        ]

    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)

    return ImageFont.load_default()


DISPLAY = load_font(56, bold=True)
BODY = load_font(22)
MONO = load_font(16, mono=True)
MONO_SMALL = load_font(13, mono=True)


def lerp(a: int, b: int, amount: float) -> int:
    return round(a + (b - a) * amount)


def build_background() -> Image.Image:
    """Create the static editorial backdrop."""

    image = Image.new("RGB", (WIDTH, HEIGHT), NAVY)
    pixels = image.load()

    for y in range(HEIGHT):
        for x in range(WIDTH):
            amount = (x / WIDTH * 0.55) + (y / HEIGHT * 0.45)
            pixels[x, y] = tuple(
                lerp(NAVY[channel], NAVY_LIGHT[channel], amount)
                for channel in range(3)
            )

    draw = ImageDraw.Draw(image, "RGBA")
    random.seed(42)
    for _ in range(145):
        x = random.randrange(WIDTH)
        y = random.randrange(HEIGHT)
        opacity = random.randrange(8, 24)
        draw.point((x, y), fill=(255, 255, 255, opacity))

    draw.rounded_rectangle(
        (1, 1, WIDTH - 2, HEIGHT - 2),
        radius=26,
        outline=(101, 127, 145, 90),
        width=2,
    )
    return image


def draw_spark(draw: ImageDraw.ImageDraw, x: float, y: float, size: float, color: tuple[int, ...]) -> None:
    points = [
        (x, y - size),
        (x + size * 0.28, y - size * 0.28),
        (x + size, y),
        (x + size * 0.28, y + size * 0.28),
        (x, y + size),
        (x - size * 0.28, y + size * 0.28),
        (x - size, y),
        (x - size * 0.28, y - size * 0.28),
    ]
    draw.polygon(points, fill=color)


def draw_frame(background: Image.Image, frame_index: int) -> Image.Image:
    phase = frame_index / FRAMES
    angle = phase * math.tau
    frame = background.copy().convert("RGBA")
    draw = ImageDraw.Draw(frame, "RGBA")

    # Left-side editorial typography.
    draw.text((76, 62), "HELLO, I'M", font=MONO, fill=TEAL, stroke_width=0)
    draw.text((72, 105), "Harish Karthick S", font=DISPLAY, fill=CREAM)
    draw.text((76, 178), "software engineer / curious builder", font=MONO, fill=MUTED)
    draw.line((76, 222, 573, 222), fill=(66, 88, 104, 190), width=1)
    draw.text((76, 247), "Useful software, made with care.", font=BODY, fill=CREAM)
    draw.rounded_rectangle((76, 306, 132, 309), radius=2, fill=CORAL)
    draw.rounded_rectangle((141, 306, 166, 309), radius=2, fill=GOLD)

    # A softly glowing "idea" and its orbit.
    glow = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow, "RGBA")
    glow_draw.ellipse((918, 65, 1128, 275), fill=(86, 199, 187, 28))
    glow = glow.filter(ImageFilter.GaussianBlur(22))
    frame = Image.alpha_composite(frame, glow)
    draw = ImageDraw.Draw(frame, "RGBA")

    center_x, center_y = 1021, 170
    draw.ellipse(
        (center_x - 79, center_y - 79, center_x + 79, center_y + 79),
        outline=(86, 199, 187, 115),
        width=2,
    )
    draw.ellipse(
        (center_x - 43, center_y - 43, center_x + 43, center_y + 43),
        fill=GOLD,
        outline=(255, 238, 194, 220),
        width=2,
    )

    # Orbital marker moves continuously for a seamless loop.
    marker_x = center_x + math.cos(angle) * 79
    marker_y = center_y + math.sin(angle) * 79
    draw.ellipse(
        (marker_x - 8, marker_y - 8, marker_x + 8, marker_y + 8),
        fill=CORAL,
        outline=CREAM,
        width=2,
    )

    # Gentle wave lines suggest an idea becoming a real system.
    wave_shift = math.sin(angle) * 5
    draw.arc((885, 198 + wave_shift, 1156, 286 + wave_shift), 195, 342, fill=(244, 239, 225, 150), width=2)
    draw.arc((897, 213 - wave_shift, 1140, 297 - wave_shift), 195, 342, fill=(86, 199, 187, 130), width=2)

    # Three stages pulse one at a time.
    labels = ("SKETCH", "BUILD", "SHIP")
    stage = int((phase * 3) % 3)
    for index, label in enumerate(labels):
        left = 887 + index * 92
        active = index == stage
        fill = (255, 158, 105, 230) if active else (39, 57, 72, 210)
        text_fill = NAVY if active else MUTED
        draw.rounded_rectangle((left, 306, left + 78, 332), radius=13, fill=fill)
        text_box = draw.textbbox((0, 0), label, font=MONO_SMALL)
        text_width = text_box[2] - text_box[0]
        draw.text((left + (78 - text_width) / 2, 312), label, font=MONO_SMALL, fill=text_fill)

    # Twinkles have independent, sinusoidal opacity.
    twinkles = [(893, 83, GOLD, 10), (1126, 101, TEAL, 8), (1094, 270, CORAL, 9)]
    for index, (x, y, color, size) in enumerate(twinkles):
        opacity = int(95 + 150 * ((math.sin(angle + index * 2.1) + 1) / 2))
        draw_spark(draw, x, y, size, (*color, opacity))

    return frame.convert("RGB")


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    background = build_background()
    frames = [draw_frame(background, index) for index in range(FRAMES)]

    # A shared palette keeps colors steady and substantially reduces the file size.
    palette = frames[0].quantize(colors=80, method=Image.Quantize.MEDIANCUT)
    indexed_frames = [
        frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames
    ]
    indexed_frames[0].save(
        OUTPUT,
        save_all=True,
        append_images=indexed_frames[1:],
        duration=FRAME_MS,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(f"Wrote {OUTPUT} ({OUTPUT.stat().st_size / 1024:.1f} KiB)")


if __name__ == "__main__":
    main()
