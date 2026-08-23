from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

INPUT = Path("assets/portrait-original.png")
OUTPUT = Path("output/portrait.svg")

WIDTH = 300
HEIGHT = 340

# Distance between dots
STEP = 3

# Dot size
MIN_RADIUS = 0.10
MAX_RADIUS = 1.30

# Portrait color
PORTRAIT_COLOR = "#A78BFA"


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    print("Loading portrait...")

    image = Image.open(INPUT).convert("L")

    print(f"Original size: {image.size}")

    # -----------------------------------------------------
    # Crop to 300:340 aspect ratio
    # -----------------------------------------------------

    target_ratio = WIDTH / HEIGHT

    original_width, original_height = image.size
    original_ratio = original_width / original_height

    if original_ratio > target_ratio:

        crop_width = int(original_height * target_ratio)

        left = (original_width - crop_width) // 2

        image = image.crop(
            (
                left,
                0,
                left + crop_width,
                original_height
            )
        )

    else:

        crop_height = int(original_width / target_ratio)

        top = (original_height - crop_height) // 2

        image = image.crop(
            (
                0,
                top,
                original_width,
                top + crop_height
            )
        )

    # -----------------------------------------------------
    # Resize
    # -----------------------------------------------------

    image = image.resize(
        (WIDTH, HEIGHT),
        Image.Resampling.LANCZOS
    )

    # -----------------------------------------------------
    # Improve contrast
    # -----------------------------------------------------

    image = ImageEnhance.Contrast(image).enhance(1.20)

    pixels = np.asarray(image, dtype=np.float32)

    # -----------------------------------------------------
    # SVG
    # -----------------------------------------------------

    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" '
        f'width="{WIDTH}" height="{HEIGHT}">'
    ]

    dot_count = 0

    # -----------------------------------------------------
    # Halftone generation
    # -----------------------------------------------------

    for row, y in enumerate(range(0, HEIGHT, STEP)):

        # Stagger every second row.
        row_offset = STEP / 2 if row % 2 else 0

        for x in range(0, WIDTH, STEP):

            sample_x = min(
                WIDTH - 1,
                int(x + STEP / 2)
            )

            sample_y = min(
                HEIGHT - 1,
                int(y + STEP / 2)
            )

            brightness = pixels[sample_y, sample_x] / 255.0

            # Convert:
            # white  -> 0
            # black  -> 1
            darkness = 1.0 - brightness

            # Gamma adjustment makes facial details
            # easier to preserve.
            darkness = darkness ** 0.72

            # Almost-white background disappears.
            if darkness < 0.025:
                continue

            # Dot radius.
            radius = (
                MIN_RADIUS
                + darkness *
                (MAX_RADIUS - MIN_RADIUS)
            )

            cx = x + STEP / 2 + row_offset
            cy = y + STEP / 2

            # Don't allow dots outside the canvas.
            if cx > WIDTH:
                continue

            svg.append(
                f'<circle '
                f'cx="{cx:.2f}" '
                f'cy="{cy:.2f}" '
                f'r="{radius:.2f}" '
                f'fill="{PORTRAIT_COLOR}"/>'
            )

            dot_count += 1

    svg.append("</svg>")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT.write_text(
        "\n".join(svg),
        encoding="utf-8"
    )

    print()
    print("Portrait SVG generated!")
    print(f"Output: {OUTPUT}")
    print(f"Dots: {dot_count:,}")


if __name__ == "__main__":
    main()