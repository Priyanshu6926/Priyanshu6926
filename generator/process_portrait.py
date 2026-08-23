from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageOps


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

INPUT = Path("assets/portrait-original.png")
OUTPUT = Path("output/portrait-dither.png")

WIDTH = 300
HEIGHT = 340


# ---------------------------------------------------------
# Floyd-Steinberg dithering
# ---------------------------------------------------------

def floyd_steinberg(image):
    """
    Convert a grayscale image into a black/white
    Floyd-Steinberg dithered image.
    """

    pixels = np.array(image, dtype=np.float32)

    height, width = pixels.shape

    for y in range(height):
        for x in range(width):

            old_pixel = pixels[y, x]

            # Threshold
            new_pixel = 255 if old_pixel >= 128 else 0

            pixels[y, x] = new_pixel

            error = old_pixel - new_pixel

            # Right
            if x + 1 < width:
                pixels[y, x + 1] += error * 7 / 16

            # Bottom-left
            if y + 1 < height and x > 0:
                pixels[y + 1, x - 1] += error * 3 / 16

            # Bottom
            if y + 1 < height:
                pixels[y + 1, x] += error * 5 / 16

            # Bottom-right
            if y + 1 < height and x + 1 < width:
                pixels[y + 1, x + 1] += error * 1 / 16

    pixels = np.clip(pixels, 0, 255)

    return Image.fromarray(pixels.astype(np.uint8))


# ---------------------------------------------------------
# Main processing
# ---------------------------------------------------------

def main():

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    print("Loading portrait...")

    image = Image.open(INPUT).convert("RGB")

    print(f"Original size: {image.size}")

    # -----------------------------------------------------
    # Crop to a portrait-oriented composition
    # -----------------------------------------------------

    # The source image is square.
    # We create a slightly taller composition centered
    # around the subject.
    crop_width = int(image.width * 0.82)
    crop_height = image.height

    left = (image.width - crop_width) // 2
    top = 0

    image = image.crop(
        (
            left,
            top,
            left + crop_width,
            crop_height,
        )
    )

    print(f"Cropped size: {image.size}")

    # -----------------------------------------------------
    # Resize to our processing grid
    # -----------------------------------------------------

    image = image.resize(
        (WIDTH, HEIGHT),
        Image.Resampling.LANCZOS,
    )

    # -----------------------------------------------------
    # Grayscale
    # -----------------------------------------------------

    image = ImageOps.grayscale(image)

    # -----------------------------------------------------
    # Increase contrast
    # -----------------------------------------------------

    image = ImageEnhance.Contrast(image).enhance(1.35)

    # -----------------------------------------------------
    # Floyd-Steinberg dithering
    # -----------------------------------------------------

    print("Applying Floyd-Steinberg dithering...")

    dithered = floyd_steinberg(image)

    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    dithered.save(OUTPUT)

    print()
    print("Done!")
    print(f"Output: {OUTPUT}")
    print(f"Size: {dithered.size}")


if __name__ == "__main__":
    main()