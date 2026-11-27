"""Shared look for the book's diagrams: Inter type and UNC colors."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

NAVY = "#13294B"
PINE = "#006D6A"
BLUE = "#4B9CD3"
BASIN = "#5B6670"
CORNER = "#CFD3D5"
FOG = "#ECEDED"
CLAY = "#E95550"
POPLAR = "#FF9E1B"
GINKGO = "#FFD340"
SAND = "#FFEEC2"
DOGWOOD = "#B6DDC0"
BERRY = "#9F237E"
DUSK = "#4E3C98"
LAND = "#C9DDB8"
WATER = "#DCEBF5"

plt.rcParams.update({
    "font.family": "Inter",
    "font.size": 11,
    "text.color": NAVY,
    "axes.labelcolor": NAVY,
    "axes.edgecolor": NAVY,
    "xtick.color": NAVY,
    "ytick.color": NAVY,
    "axes.titleweight": "bold",
    "axes.titlesize": 13,
    "axes.titlecolor": NAVY,
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.1,
    "savefig.facecolor": "white",
})


def save(fig, path):
    fig.savefig(path)
    plt.close(fig)
    print("wrote", path)
