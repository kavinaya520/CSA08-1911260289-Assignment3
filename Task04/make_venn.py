"""Draws the Venn diagrams of Q4 (needs matplotlib: pip install matplotlib). Output: venn.png"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

xs, ys = np.meshgrid(np.linspace(-3, 3, 500), np.linspace(-1.8, 1.8, 300))
A = (xs + 0.8) ** 2 + ys ** 2 < 1.3 ** 2
B = (xs - 0.8) ** 2 + ys ** 2 < 1.3 ** 2
panels = [("AI and OT (clash): A & B", A & B), ("A or B (any elective): A | B", A | B), ("only AI: A - B", A & ~B),
          ("only OT: B - A", B & ~A), ("exactly one: A ^ B", A ^ B), ("neither: U - (A | B)", ~(A | B))]
fig, axes = plt.subplots(2, 3, figsize=(10, 5))
for ax, (title, mask) in zip(axes.flat, panels):
    ax.imshow(np.where(mask, 1.0, np.nan), extent=(-3, 3, -1.8, 1.8), origin="lower", cmap="Blues", vmin=0, vmax=1.6)
    for cx, name in ((-0.8, "AI (A)"), (0.8, "OT (B)")):
        ax.add_patch(plt.Circle((cx, 0), 1.3, fill=False, lw=1.5))
        ax.text(cx * 1.9, 1.5, name, ha="center", fontsize=8)
    ax.add_patch(plt.Rectangle((-3, -1.8), 6, 3.6, fill=False, lw=1))
    ax.set_title(title, fontsize=9); ax.set_xlim(-3, 3); ax.set_ylim(-1.8, 1.8); ax.set_aspect("equal"); ax.axis("off")
fig.suptitle("Venn diagrams (shaded = result, rectangle = all students)", fontsize=10)
fig.tight_layout(); fig.savefig("venn.png", dpi=130)
