"""Make the home-screen app icons in pwa/: the dragon surveyor from the book
cover (images/cover.jpg) with a Piedmont Pine "370" band across the bottom.

Run from the repo root, then commit pwa/*.png:
    python3 scripts/make-icons.py path/to/AtkinsonHyperlegibleNext-ExtraBold.ttf
Needs Pillow. The font is Atkinson Hyperlegible Next (weight 800) from
Google Fonts, the site's own font. If the cover changes, adjust CROP.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

COVER = Path("images/cover.jpg")
OUT = Path("pwa")
# Square around the dragon and the surveying instrument, in cover pixels
# (left, top, right, bottom); the cover is 1792 x 2400.
CROP = (510, 915, 1410, 1815)
PINE = (0x00, 0x6D, 0x6A)      # UNC Piedmont Pine
GINKGO = (0xFF, 0xD3, 0x40)    # UNC Ginkgo
WHITE = (255, 255, 255)
SIZE = 1024


def centered(draw, text, font, cx, cy, fill):
    box = draw.textbbox((0, 0), text, font=font)
    w, h = box[2] - box[0], box[3] - box[1]
    draw.text((cx - w / 2 - box[0], cy - h / 2 - box[1]), text, font=font, fill=fill)


def icon(font_path, scale=1.0):
    """scale < 1 keeps everything inside Android's maskable safe circle."""
    # The maskable icon zooms out (a bigger square of the cover) so the
    # dragon and band stay inside the safe circle while the art fills the edges.
    left, top, right, bottom = CROP
    grow = (right - left) * (1 / scale - 1) / 2
    box = (round(left - grow), round(top - grow), round(right + grow), round(bottom + grow))
    im = Image.open(COVER).convert("RGB").crop(box).resize((SIZE, SIZE), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    c = SIZE / 2
    if scale == 1.0:
        band_h = 230
        band_top = SIZE - band_h
        d.rectangle([0, band_top, SIZE, SIZE], fill=PINE)
        d.rectangle([0, band_top, SIZE, band_top + 14], fill=GINKGO)
        centered(d, "370", ImageFont.truetype(font_path, 190), c, band_top + band_h / 2 + 7, WHITE)
    else:
        # A pill well inside the safe circle (radius 40% of the icon).
        half_w, band_h, mid = 200, 184, c + 250
        d.rounded_rectangle([c - half_w, mid - band_h / 2, c + half_w, mid + band_h / 2],
                            radius=band_h / 2, fill=PINE)
        centered(d, "370", ImageFont.truetype(font_path, 150), c, mid, WHITE)
    return im


def main():
    font = sys.argv[1]
    full, safe = icon(font), icon(font, 0.80)
    for name, img, px in [("icon-192.png", full, 192), ("icon-512.png", full, 512),
                          ("apple-touch-icon.png", full, 180), ("favicon-32.png", full, 32),
                          ("icon-maskable-512.png", safe, 512)]:
        img.resize((px, px), Image.LANCZOS).save(OUT / name, optimize=True)
    print("Wrote icons to", OUT)


if __name__ == "__main__":
    main()
