"""Copy the QGIS screenshots into images/qgis/ and add numbered callouts.

Usage: python qgis_annotate.py <dir with screenshots from qgis_screenshots.py>
"""
import shutil, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SRC = Path(sys.argv[1])
OUT = Path(__file__).resolve().parents[2] / "images" / "qgis"
OUT.mkdir(parents=True, exist_ok=True)
NAVY, CLAY = "#13294B", "#E95550"
FONT = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 22)

# (x, y) of each numbered badge on the 1440 x 900 screenshots.
CALLOUTS = {
    "qgis-interface": [(745, 28), (1290, 100), (95, 131), (75, 496), (720, 790), (1375, 131), (520, 884)],
    "qgis-digitize": [(320, 140), (437, 140), (676, 529), (1090, 219)],
}

def badge(draw, x, y, n, r=17):
    draw.ellipse([x - r - 3, y - r - 3, x + r + 3, y + r + 3], fill="white")
    draw.ellipse([x - r, y - r, x + r, y + r], fill=CLAY)
    draw.text((x, y + 1), str(n), fill="white", font=FONT, anchor="mm")

for png in sorted(SRC.glob("qgis-*.png")):
    name = png.stem
    if name in CALLOUTS:
        im = Image.open(png).convert("RGB")
        d = ImageDraw.Draw(im)
        for i, (x, y) in enumerate(CALLOUTS[name], 1):
            badge(d, x, y, i)
        im.save(OUT / png.name, optimize=True)
    else:
        shutil.copy(png, OUT / png.name)
    print("wrote", OUT / png.name)
