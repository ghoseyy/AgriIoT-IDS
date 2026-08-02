"""Graphical abstract per the journal's spec: image 531 x 1328 pixels (h x w)
or proportionally more, readable at 5 x 13 cm. Summarizes the paper's actual
pipeline and real results -- no invented numbers.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# 1328 x 531 px at 200 dpi -> figsize in inches = px / dpi
DPI = 200
W_PX, H_PX = 1328, 531
FIGSIZE = (W_PX / DPI, H_PX / DPI)

COLOR_NODE = "#3B5169"      # slate blue -- constrained device
COLOR_DETECT = "#2E7D5B"    # green -- detection tier
COLOR_RECOVER = "#B5541A"   # burnt orange -- recovery tier
COLOR_RESULT = "#1F4E8C"    # deep blue -- headline result
COLOR_TEXT = "#1A1A1A"
COLOR_BG = "#FFFFFF"


def box(ax, xy, w, h, text, facecolor, fontsize=7.2, textcolor="white", weight="bold"):
    x, y = xy
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.012,rounding_size=0.02",
        linewidth=0, facecolor=facecolor, alpha=0.95,
        mutation_aspect=1,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
             fontsize=fontsize, color=textcolor, weight=weight,
             family="sans-serif", linespacing=1.35)
    return patch


def arrow(ax, start, end, color="#555555", lw=1.6):
    a = FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=12,
                          color=color, linewidth=lw, shrinkA=2, shrinkB=2)
    ax.add_patch(a)


def main():
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 40)
    ax.axis("off")
    fig.patch.set_facecolor(COLOR_BG)

    # Title strip
    ax.text(50, 36.5, "Beyond Detection: Autonomous Intrusion Recovery for Resource-Constrained AgriIoT",
            ha="center", va="center", fontsize=8.6, weight="bold", color=COLOR_TEXT, family="sans-serif")
    ax.plot([4, 96], [33.3, 33.3], color="#CCCCCC", linewidth=0.8)

    # Stage 1: constrained AgriIoT node
    box(ax, (1.5, 8), 15, 22, "AgriIoT\nnode\n\ncompute +\nconnectivity\nlimited",
        COLOR_NODE, fontsize=7.2)

    # Stage 2: two-tier detection
    box(ax, (19, 19), 17, 11, "Tier 1\nRandom Forest\nF1 = 0.9965", COLOR_DETECT, fontsize=7.0)
    box(ax, (19, 6), 17, 11, "Tier 2\nAutoencoder\n(low-confidence flows)", COLOR_DETECT, fontsize=6.8)
    ax.text(27.5, 18.1, "confident ↓", ha="center", fontsize=5.6, color="#444444", style="italic")

    # merge arrows into detection result badge
    detect_badge_x = 39
    box(ax, (detect_badge_x, 9.5), 15, 13, "FPR:\n0.082% → 0.069%\n(McNemar p<1e-45)",
        "#E8F3EE", fontsize=6.6, textcolor=COLOR_DETECT, weight="bold")

    # Stage 3: recovery
    box(ax, (57, 6), 19, 20, "Tier 3\nQ-learning recovery\nisolate / rollback / reroute\n(grounded confidence)",
        COLOR_RECOVER, fontsize=6.1)

    # Stage 4: headline result
    box(ax, (79, 6), 19, 20, "68.3% faster\nrecovery (MTTR)\n\n62.2% less\ndowntime",
        COLOR_RESULT, fontsize=7.4)

    # Arrows connecting main flow
    arrow(ax, (16.5, 17), (19, 22))
    arrow(ax, (36, 24.5), (39, 19))
    arrow(ax, (36, 11.5), (39, 15))
    arrow(ax, (54, 16), (57, 16))
    arrow(ax, (76, 16), (79, 16))

    # Bottom validation strip
    ax.plot([4, 96], [4.6, 4.6], color="#CCCCCC", linewidth=0.8)
    ax.text(50, 2.2,
            "Validated on CICIDS2017 and Farm-flow (real AgriIoT traffic)  •  "
            "INT8 quantization: -70% model size, no retraining",
            ha="center", va="center", fontsize=6.8, color="#333333", family="sans-serif")

    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    for path in ("arxiv_final/graphical_abstract.png", "cee_submission/graphical_abstract.png"):
        plt.savefig(path, dpi=DPI, facecolor=COLOR_BG)
    plt.close()
    print("Saved graphical_abstract.png (1328x531 px target) to both submission bundles")


if __name__ == "__main__":
    main()
