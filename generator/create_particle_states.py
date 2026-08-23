from pathlib import Path
import json
import random

import cairosvg
import numpy as np
from PIL import Image


# =========================================================
# Configuration
# =========================================================

CANVAS_WIDTH = 300
CANVAS_HEIGHT = 340

PORTRAIT = Path("assets/portrait.svg")
JAVA = Path("assets/java.svg")
VERCEL = Path("assets/vercel.svg")

OUTPUT_DIR = Path("output/particles")

# Number of particles used by the animation.
PARTICLE_COUNT = 4500

# Seed keeps the generated states reproducible.
random.seed(42)


# =========================================================
# Utility: rasterize SVG
# =========================================================

def svg_to_image(svg_path, width, height):
    """
    Convert an SVG into a transparent PNG image.
    """

    png_data = cairosvg.svg2png(
        url=str(svg_path),
        output_width=width,
        output_height=height
    )

    temp_path = OUTPUT_DIR / f"{svg_path.stem}_temp.png"

    temp_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    temp_path.write_bytes(png_data)

    image = Image.open(temp_path).convert("RGBA")

    temp_path.unlink()

    return image


# =========================================================
# Extract coordinates from an image
# =========================================================

def image_to_points(image):
    """
    Convert visible pixels into particle coordinates.
    """

    rgba = np.array(image)

    alpha = rgba[:, :, 3]

    # Anything visible becomes a candidate point.
    mask = alpha > 30

    ys, xs = np.where(mask)

    points = []

    for x, y in zip(xs, ys):
        points.append({
            "x": float(x),
            "y": float(y)
        })

    return points


# =========================================================
# Resize point collection to desired particle count
# =========================================================

def normalize_points(points, count):
    """
    Convert arbitrary number of points into exactly
    PARTICLE_COUNT points.
    """

    if not points:
        raise ValueError("No visible points found.")

    # -----------------------------------------------------
    # Too many points
    # -----------------------------------------------------

    if len(points) > count:

        selected = random.sample(
            points,
            count
        )

        return selected

    # -----------------------------------------------------
    # Too few points
    # -----------------------------------------------------

    result = []

    for i in range(count):

        point = points[
            i % len(points)
        ]

        # Tiny deterministic jitter prevents identical
        # particles when we duplicate a point.
        jitter_x = random.uniform(-0.4, 0.4)
        jitter_y = random.uniform(-0.4, 0.4)

        result.append({
            "x": point["x"] + jitter_x,
            "y": point["y"] + jitter_y
        })

    return result


# =========================================================
# Center an image
# =========================================================

def center_image(image, target_width, target_height):
    """
    Scale an image to fit inside the canvas while preserving
    its aspect ratio, then center it.
    """

    image = image.copy()

    image.thumbnail(
        (
            target_width,
            target_height
        ),
        Image.Resampling.LANCZOS
    )

    canvas = Image.new(
        "RGBA",
        (
            target_width,
            target_height
        ),
        (0, 0, 0, 0)
    )

    x = (
        target_width - image.width
    ) // 2

    y = (
        target_height - image.height
    ) // 2

    canvas.alpha_composite(
        image,
        (
            x,
            y
        )
    )

    return canvas


# =========================================================
# Generate a logo state
# =========================================================

def create_logo_state(svg_path, state_name):

    print(
        f"Generating {state_name} state..."
    )

    image = svg_to_image(
        svg_path,
        CANVAS_WIDTH,
        CANVAS_HEIGHT
    )

    image = center_image(
        image,
        CANVAS_WIDTH,
        CANVAS_HEIGHT
    )

    points = image_to_points(image)

    print(
        f"  Visible pixels: {len(points):,}"
    )

    points = normalize_points(
        points,
        PARTICLE_COUNT
    )

    output = OUTPUT_DIR / f"{state_name}.json"

    output.write_text(
        json.dumps(
            {
                "width": CANVAS_WIDTH,
                "height": CANVAS_HEIGHT,
                "particles": points
            },
            indent=2
        ),
        encoding="utf-8"
    )

    print(
        f"  Saved: {output}"
    )


# =========================================================
# Portrait state
# =========================================================

def create_portrait_state():

    print("Generating portrait state...")

    image = Image.open(
        PORTRAIT
    ) if PORTRAIT.suffix.lower() != ".svg" else svg_to_image(
        PORTRAIT,
        CANVAS_WIDTH,
        CANVAS_HEIGHT
    )

    points = image_to_points(
        image
    )

    print(
        f"  Visible pixels: {len(points):,}"
    )

    points = normalize_points(
        points,
        PARTICLE_COUNT
    )

    output = OUTPUT_DIR / "portrait.json"

    output.write_text(
        json.dumps(
            {
                "width": CANVAS_WIDTH,
                "height": CANVAS_HEIGHT,
                "particles": points
            },
            indent=2
        ),
        encoding="utf-8"
    )

    print(
        f"  Saved: {output}"
    )


# =========================================================
# Main
# =========================================================

def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print()
    print("=" * 50)
    print("Creating particle states")
    print("=" * 50)
    print()

    create_portrait_state()

    create_logo_state(
        JAVA,
        "java"
    )

    create_logo_state(
        VERCEL,
        "vercel"
    )

    print()
    print("=" * 50)
    print("Particle states generated successfully")
    print("=" * 50)


if __name__ == "__main__":
    main()