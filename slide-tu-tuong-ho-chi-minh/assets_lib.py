# -*- coding: utf-8 -*-
"""Thu vien ve hinh minh hoa phang (flat infographic) cho bo slide TTHCM."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Polygon, FancyArrowPatch, Wedge, Rectangle
import numpy as np, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#8C0D14"
RED2  = "#B3181F"
RED_L = "#FBEDEC"
GOLD  = "#E8B02B"
GOLD_L= "#FBF1D8"
INK   = "#241A16"
GRAY  = "#6E6257"
WHITE = "#FFFFFF"

plt.rcParams["font.family"] = "DejaVu Sans"

def canvas(w, h, dpi=190, bg=None):
    fig = plt.figure(figsize=(w/100.0, h/100.0), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w); ax.set_ylim(0, h); ax.set_aspect("equal"); ax.axis("off")
    if bg:
        ax.add_patch(Rectangle((0, 0), w, h, color=bg, zorder=-10))
    else:
        fig.patch.set_alpha(0)
    return fig, ax

def save(fig, name, transparent=True):
    p = os.path.join(OUT, name)
    fig.savefig(p, transparent=transparent, pad_inches=0)
    plt.close(fig)
    print("wrote", p)
    return p

def star(ax, cx, cy, r, color=GOLD, ec=None, lw=0, alpha=1, z=5, rot=0):
    pts = []
    for i in range(10):
        ang = np.deg2rad(90 + rot + i * 36)
        rr = r if i % 2 == 0 else r * 0.382
        pts.append((cx + rr * np.cos(ang), cy + rr * np.sin(ang)))
    ax.add_patch(Polygon(pts, closed=True, fc=color, ec=ec or color,
                         lw=lw, alpha=alpha, zorder=z))

def card(ax, x, y, w, h, fc=WHITE, ec=None, lw=1.6, r=14, z=2, alpha=1):
    ax.add_patch(FancyBboxPatch((x + r, y + r), w - 2*r, h - 2*r,
                 boxstyle=f"round,pad={r}", fc=fc, ec=ec or fc, lw=lw,
                 zorder=z, alpha=alpha))

def bubble(ax, cx, cy, r, fc=RED, ec=None, lw=0, z=4, alpha=1):
    ax.add_patch(Circle((cx, cy), r, fc=fc, ec=ec or fc, lw=lw, zorder=z, alpha=alpha))

def txt(ax, x, y, s, size=15, color=INK, weight="normal", ha="center", va="center",
        z=8, style="normal", wrap_w=None, lh=1.28, family=None):
    ax.text(x, y, s, fontsize=size, color=color, fontweight=weight, ha=ha, va=va,
            zorder=z, style=style, linespacing=lh,
            family=family or plt.rcParams["font.family"])

def arrow(ax, p1, p2, color=GOLD, lw=3.2, z=3, style="-|>", ms=14, rad=0.0):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=ms,
                 lw=lw, color=color, zorder=z,
                 connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0))

def wrap(s, n):
    words, lines, cur = s.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= n:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur); cur = w
    if cur: lines.append(cur)
    return "\n".join(lines)
