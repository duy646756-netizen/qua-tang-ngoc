# -*- coding: utf-8 -*-
from assets_lib import *
import numpy as np
from matplotlib.patches import Polygon, Circle, FancyBboxPatch, Rectangle, Wedge

# ---------------------------------------------------------------- 1. NEN BIA
def bg_title():
    W, H = 1600, 900
    fig, ax = canvas(W, H, dpi=150, bg=RED)
    g = np.linspace(0, 1, 512).reshape(-1, 1)
    grad = np.zeros((512, 512, 3))
    c1 = np.array([0.42, 0.04, 0.07]); c2 = np.array([0.62, 0.09, 0.11])
    for i in range(3):
        grad[:, :, i] = c1[i] + (c2[i] - c1[i]) * (1 - g)
    ax.imshow(grad, extent=[0, W, 0, H], zorder=-9, aspect="auto")
    # tia sang toa tu goc phai tren
    for a in np.linspace(-8, 96, 15):
        L = 2100
        x2 = 1290 + L * np.cos(np.deg2rad(a + 138)); y2 = 730 + L * np.sin(np.deg2rad(a + 138))
        ax.add_patch(Polygon([(1290, 730), (x2, y2),
                              (x2 + 60, y2 + 60)], closed=True, fc=GOLD, alpha=0.045, zorder=-8))
    star(ax, 1290, 730, 250, color=GOLD, alpha=0.16, z=-7)
    star(ax, 1290, 730, 120, color=GOLD, alpha=0.95, z=2)
    ax.add_patch(Rectangle((0, 0), W, 14, color=GOLD, zorder=6))
    save(fig, "bg_title.png", transparent=False)

# ------------------------------------------------- 2. LO TRINH (MUC LUC)
def fig_roadmap():
    W, H = 1360, 250
    fig, ax = canvas(W, H)
    ax.plot([90, W - 90], [125, 125], color=GOLD, lw=6, zorder=1, solid_capstyle="round")
    labels = ["Khái niệm\n& định nghĩa", "Nội hàm\nkhái niệm",
              "Quá trình nhận thức\ncủa Đảng", "Nhận xét\n& thảo luận"]
    xs = np.linspace(170, W - 170, 4)
    for i, (x, lb) in enumerate(zip(xs, labels)):
        bubble(ax, x, 125, 62, fc=RED, z=4)
        bubble(ax, x, 125, 62, fc="none", ec=GOLD, lw=5, z=5)
        txt(ax, x, 125, ["I", "II", "III", "IV"][i], size=30, color=GOLD, weight="bold", z=6)
    save(fig, "fig_roadmap.png")

# ------------------------------------------- 3. KHAI NIEM TU TUONG (dong tam)
def fig_tutuong():
    W, H = 960, 760
    fig, ax = canvas(W, H)
    cx, cy = 480, 380
    bubble(ax, cx, cy, 330, fc=RED_L, ec=RED2, lw=3, z=1)
    bubble(ax, cx, cy, 225, fc=GOLD_L, ec=GOLD, lw=3, z=2)
    bubble(ax, cx, cy, 128, fc=RED, z=3)
    txt(ax, cx, cy + 14, "NHÀ", size=19, color=GOLD, weight="bold", z=6)
    txt(ax, cx, cy - 24, "TƯ TƯỞNG", size=19, color=GOLD, weight="bold", z=6)
    txt(ax, cx, cy + 178, "HỆ TƯ TƯỞNG", size=18, color="#8A6A12", weight="bold", z=6)
    txt(ax, cx, cy + 282, "TƯ TƯỞNG", size=19, color=RED, weight="bold", z=6)
    txt(ax, cx, cy - 272, wrap("người sáng tạo hệ thống quan điểm dẫn dắt thời đại", 24),
        size=12, color=GRAY, z=6)
    star(ax, cx, cy + 96, 26, color=GOLD, z=6)
    save(fig, "fig_tutuong.png")

# ----------------------------------------------- 4. TRANG TRI TRICH DAN
def fig_quote():
    W, H = 420, 420
    fig, ax = canvas(W, H)
    bubble(ax, 210, 210, 190, fc=RED_L, z=1)
    txt(ax, 210, 150, "“", size=200, color=RED2, weight="bold", z=4)
    star(ax, 210, 318, 44, color=GOLD, z=5)
    save(fig, "fig_quote.png")

# ------------------------------------- 5. BANH XE HE THONG QUAN DIEM
def fig_hethong():
    W = H = 980
    fig, ax = canvas(W, H)
    cx, cy, R = 490, 490, 320
    items = ["Giải phóng dân tộc,\ngiai cấp, con người",
             "Độc lập dân tộc\ngắn với CNXH",
             "Đảng Cộng sản\nViệt Nam",
             "Đại đoàn kết\ntoàn dân tộc",
             "Nhà nước của dân,\ndo dân, vì dân",
             "Đoàn kết quốc tế",
             "Văn hoá, đạo đức,\ncon người",
             "Phương pháp\ncách mạng"]
    n = len(items)
    for i, it in enumerate(items):
        a0 = 90 + i * (360 / n) + 2
        a1 = 90 + (i + 1) * (360 / n) - 2
        fc = GOLD_L if i % 2 == 0 else RED_L
        ec = GOLD if i % 2 == 0 else RED2
        ax.add_patch(Wedge((cx, cy), R, a0, a1, width=150, fc=fc, ec=ec, lw=2, zorder=2))
        am = np.deg2rad((a0 + a1) / 2)
        ax.text(cx + 245 * np.cos(am), cy + 245 * np.sin(am), it, fontsize=12.9,
                color=INK, ha="center", va="center", zorder=6, linespacing=1.3)
    bubble(ax, cx, cy, 168, fc=RED, z=4)
    txt(ax, cx, cy + 54, "HỆ THỐNG", size=16, color=GOLD, weight="bold", z=7)
    txt(ax, cx, cy + 22, "QUAN ĐIỂM", size=16, color=GOLD, weight="bold", z=7)
    txt(ax, cx, cy - 16, "toàn diện & sâu sắc", size=11.5, color=WHITE, z=7)
    txt(ax, cx, cy - 44, "về những vấn đề cơ bản", size=11.5, color=WHITE, z=7)
    txt(ax, cx, cy - 72, "của cách mạng Việt Nam", size=11.5, color=WHITE, z=7)
    save(fig, "fig_hethong.png")

# ------------------------------------------------ 6. NGUON GOC (phieu -> 1)
def fig_nguongoc():
    W, H = 1180, 760
    fig, ax = canvas(W, H)
    src = [("CHỦ NGHĨA\nMÁC – LÊNIN", "Cơ sở thế giới quan\nvà phương pháp luận", RED),
           ("GIÁ TRỊ TRUYỀN THỐNG\nTỐT ĐẸP CỦA DÂN TỘC", "Yêu nước, nhân nghĩa,\nđoàn kết, cần cù", "#A8761A"),
           ("TINH HOA VĂN HOÁ\nNHÂN LOẠI", "Phương Đông và\nphương Tây", "#7A4B12")]
    xs = [200, 590, 980]
    for x, (t, s, c) in zip(xs, src):
        card(ax, x - 175, 545, 350, 185, fc=WHITE, ec=c, lw=3, r=18, z=2)
        txt(ax, x, 672, t, size=13.2, color=c, weight="bold", z=6)
        txt(ax, x, 594, s, size=11.4, color=GRAY, z=6)
        arrow(ax, (x, 540), (x if x == 590 else (590 + (x - 590) * 0.42), 420),
              color=GOLD, lw=4, ms=18)
    ax.add_patch(Polygon([(250, 415), (930, 415), (720, 300), (460, 300)],
                         closed=True, fc=GOLD_L, ec=GOLD, lw=2.5, zorder=2))
    txt(ax, 590, 357, "TÀI NĂNG, PHẨM CHẤT & HOẠT ĐỘNG THỰC TIỄN CỦA HỒ CHÍ MINH",
        size=11.6, color="#7A5A10", weight="bold", z=6)
    arrow(ax, (590, 296), (590, 232), color=GOLD, lw=4, ms=18)
    card(ax, 285, 80, 610, 150, fc=RED, ec=RED, r=22, z=3)
    txt(ax, 590, 175, "TƯ TƯỞNG HỒ CHÍ MINH", size=21, color=GOLD, weight="bold", z=7)
    txt(ax, 590, 125, "Vận dụng và phát triển sáng tạo vào điều kiện cụ thể của nước ta",
        size=11.6, color=WHITE, z=7)
    star(ax, 340, 155, 22, color=GOLD, z=7); star(ax, 840, 155, 22, color=GOLD, z=7)
    save(fig, "fig_nguongoc.png")

# --------------------------------------------------- 7. GIA TRI: SOI DUONG
def fig_giatri():
    W, H = 1080, 700
    fig, ax = canvas(W, H)
    for i, a in enumerate(np.linspace(28, 152, 9)):
        L = 900
        ax.add_patch(Polygon([(240, 470),
                              (240 + L * np.cos(np.deg2rad(a)), 470 + L * np.sin(np.deg2rad(a))),
                              (240 + L * np.cos(np.deg2rad(a + 7)), 470 + L * np.sin(np.deg2rad(a + 7)))],
                             closed=True, fc=GOLD, alpha=0.20, zorder=1))
    ax.add_patch(Polygon([(180, 70), (300, 70), (280, 430), (200, 430)],
                         closed=True, fc=RED, zorder=3))
    ax.add_patch(Rectangle((188, 430), 104, 46, fc=RED2, zorder=4))
    star(ax, 240, 512, 52, color=GOLD, z=5)
    ax.plot([60, 1020], [70, 70], color="#D9CEC2", lw=5, zorder=2)
    miles = [(470, "1930\nCương lĩnh\nđầu tiên"), (640, "1945\nCách mạng\nTháng Tám"),
             (810, "1975\nThống nhất\nđất nước"), (975, "1986 – nay\nĐổi mới &\nhội nhập")]
    for x, lb in miles:
        bubble(ax, x, 70, 17, fc=GOLD, z=5)
        bubble(ax, x, 70, 17, fc="none", ec=RED, lw=3, z=6)
        txt(ax, x, 175, lb, size=11.5, color=INK, weight="bold", z=6)
    txt(ax, 640, 560, "“… mãi mãi soi đường cho sự nghiệp cách mạng\ncủa nhân dân ta giành thắng lợi”",
        size=14.5, color=RED, weight="bold", style="italic", z=7)
    save(fig, "fig_giatri.png")

# ----------------------------------------- 8–11. TIMELINE (5 bien the)
STAGES = [("1930 – 1969", "Vận dụng trong\nthực tiễn cách mạng"),
          ("1969 – 1986", "Học tập tư tưởng,\nđạo đức, tác phong"),
          ("1986 – 1991", "Bước ngoặt:\nkhẳng định khái niệm"),
          ("1991 – nay", "Hoàn thiện, bổ sung\nvà phát triển")]

def fig_timeline(active=None, name="fig_timeline.png", W=1420, H=248):
    fig, ax = canvas(W, H)
    y = 122
    ax.plot([95, W - 95], [y, y], color="#E2D7CB", lw=7, zorder=1, solid_capstyle="round")
    xs = np.linspace(200, W - 200, 4)
    if active is not None:
        ax.plot([95, xs[active]], [y, y], color=GOLD, lw=7, zorder=2, solid_capstyle="round")
    for i, (x, (yr, lb)) in enumerate(zip(xs, STAGES)):
        on = (active == i)
        bubble(ax, x, y, 42 if on else 30, fc=RED if on else WHITE,
               ec=RED if on else "#CDBFB1", lw=4, z=4)
        if on:
            star(ax, x, y, 20, color=GOLD, z=6)
        else:
            txt(ax, x, y, str(i + 1), size=15, color=GRAY, weight="bold", z=6)
        txt(ax, x, y + 78, yr, size=14.5, color=RED if on else INK, weight="bold", z=6)
        txt(ax, x, y - 80, lb, size=11, color=INK if on else GRAY,
            weight="bold" if on else "normal", z=6)
    save(fig, name)

def fig_star():
    fig, ax = canvas(300, 300)
    star(ax, 150, 150, 140, color=GOLD, z=5)
    save(fig, "star_gold.png")

# -------------------------------------------------- 12. BAC THANG NHAN THUC
def fig_nhanxet():
    W, H = 1060, 700
    fig, ax = canvas(W, H)
    steps = [("1930–1969", "Vận dụng\ntrong thực tiễn"), ("1969–1986", "Học tập\ntư tưởng, đạo đức"),
             ("1986–1991", "Khẳng định\nnền tảng tư tưởng"), ("1991–nay", "Hoàn thiện,\nphát triển sáng tạo")]
    bw, bh0, gap = 225, 118, 8
    for i, (yr, lb) in enumerate(steps):
        x = 40 + i * (bw + gap); h = bh0 + i * 108
        fc = [RED_L, GOLD_L, "#F6DFC0", RED][i]
        ec = [RED2, GOLD, "#C98A1E", RED][i]
        tc = [INK, INK, INK, GOLD][i]
        card(ax, x, 60, bw, h, fc=fc, ec=ec, lw=3, r=16, z=2)
        txt(ax, x + bw / 2, 60 + h - 42, yr, size=14.5,
            color=GOLD if i == 3 else RED, weight="bold", z=6)
        txt(ax, x + bw / 2, 60 + h - 100, lb, size=12, color=tc, z=6)
    arrow(ax, (70, 566), (1000, 606), color=GOLD, lw=5, ms=22, rad=-0.08)
    txt(ax, 520, 665, "NHẬN THỨC NGÀY CÀNG ĐẦY ĐỦ, TOÀN DIỆN VÀ SÂU SẮC HƠN",
        size=13.5, color=RED, weight="bold", z=8)
    save(fig, "fig_nhanxet.png")

# ------------------------------------------------------ 13. THAO LUAN
def fig_thaoluan():
    W, H = 1020, 470
    fig, ax = canvas(W, H)
    for cx, cy, r, fc, ec, q, tc in [(285, 265, 175, GOLD, GOLD, "?", RED),
                                     (735, 205, 175, GOLD_L, GOLD, "?", RED)]:
        bubble(ax, cx, cy, r, fc=fc, ec=ec, lw=4, z=3)
        ax.add_patch(Polygon([(cx - 55, cy - r + 22), (cx - 5, cy - r + 22),
                              (cx - 30, cy - r - 58)], closed=True, fc=fc, ec=ec, lw=4, zorder=2))
        txt(ax, cx, cy + 6, q, size=112, color=tc, weight="bold", z=6)
    star(ax, 512, 400, 40, color=GOLD, z=7)
    save(fig, "fig_thaoluan.png")

if __name__ == "__main__":
    bg_title(); fig_roadmap(); fig_tutuong(); fig_quote(); fig_hethong()
    fig_nguongoc(); fig_giatri(); fig_nhanxet(); fig_thaoluan(); fig_star()
    fig_timeline(None, "fig_timeline.png")
    for i in range(4):
        fig_timeline(i, f"fig_tl{i+1}.png")
