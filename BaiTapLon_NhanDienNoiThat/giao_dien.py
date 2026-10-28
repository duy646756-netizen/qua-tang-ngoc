# -*- coding: utf-8 -*-
"""
giao_dien.py — Bảng màu, phông chữ và các ô điều khiển dùng chung cho app.py.
Tách riêng để app.py chỉ còn phần luồng xử lý, dễ đọc.
"""

from __future__ import annotations

import sys
import tkinter as tk
from tkinter import ttk

# ============================================================================
# BẢNG MÀU
# ============================================================================
NEN        = "#f1f4f9"   # nền chung
THE        = "#ffffff"   # nền các thẻ nội dung
VIEN       = "#dfe5ee"   # đường viền
HEADER     = "#111c33"   # thanh tiêu đề
HEADER_PHU = "#8fa3c4"   # chữ phụ trên thanh tiêu đề
CHU        = "#17202f"   # chữ chính
CHU_MO     = "#6b7686"   # chữ phụ
CHINH      = "#2f6df6"   # màu nhấn
CHINH_DAM  = "#1f54cc"
CHINH_NHAT = "#eaf0fe"
XANH       = "#0e9f6e"
CAM        = "#d97706"
DO         = "#dc2626"
VUNG_ANH   = "#e9edf4"   # nền khu vực xem ảnh


def ho_phong() -> str:
    """Chọn phông chữ hợp với hệ điều hành đang chạy."""
    if sys.platform.startswith("win"):
        return "Segoe UI"
    if sys.platform == "darwin":
        return "Helvetica Neue"
    return "DejaVu Sans"


PH = ho_phong()
F_TIEU_DE   = (PH, 17, "bold")
F_PHU_DE    = (PH, 10)
F_MUC       = (PH, 10, "bold")
F_THUONG    = (PH, 10)
F_NHO       = (PH, 9)
F_SO_LIEU   = (PH, 20, "bold")
F_NUT       = (PH, 11, "bold")


# ============================================================================
# THIẾT LẬP KIỂU CHO CÁC Ô ttk
# ============================================================================
def ap_dung_kieu(goc: tk.Misc) -> ttk.Style:
    kieu = ttk.Style(goc)
    try:
        kieu.theme_use("clam")
    except tk.TclError:
        pass

    kieu.configure(".", background=THE, foreground=CHU, font=F_THUONG)
    kieu.configure("TFrame", background=THE)
    kieu.configure("Nen.TFrame", background=NEN)
    kieu.configure("TLabel", background=THE, foreground=CHU, font=F_THUONG)
    kieu.configure("Mo.TLabel", background=THE, foreground=CHU_MO, font=F_NHO)
    kieu.configure("Muc.TLabel", background=THE, foreground=CHU, font=F_MUC)

    kieu.configure("TCheckbutton", background=THE, foreground=CHU, font=F_THUONG)
    kieu.map("TCheckbutton", background=[("active", THE)])

    kieu.configure("TCombobox", fieldbackground="#ffffff", background="#ffffff",
                   bordercolor=VIEN, arrowcolor=CHINH, padding=5)
    kieu.map("TCombobox", fieldbackground=[("readonly", "#ffffff")],
             bordercolor=[("focus", CHINH)])

    kieu.configure("TScale", background=THE, troughcolor="#dde4ef",
                   bordercolor=THE, lightcolor=CHINH, darkcolor=CHINH)

    kieu.configure("TProgressbar", background=CHINH, troughcolor="#dde4ef",
                   bordercolor=THE, lightcolor=CHINH, darkcolor=CHINH, thickness=6)

    # Bảng kết quả
    kieu.configure("Treeview",
                   background="#ffffff", fieldbackground="#ffffff",
                   foreground=CHU, rowheight=30, font=F_THUONG, borderwidth=0)
    kieu.configure("Treeview.Heading",
                   background="#f3f6fb", foreground=CHU_MO,
                   font=(PH, 9, "bold"), relief="flat", padding=(8, 7))
    kieu.map("Treeview.Heading", background=[("active", "#e8eefa")])
    kieu.map("Treeview",
             background=[("selected", CHINH_NHAT)],
             foreground=[("selected", CHU)])
    return kieu


# ============================================================================
# CÁC Ô GIAO DIỆN TỰ DỰNG
# ============================================================================
class The(tk.Frame):
    """Một thẻ nội dung nền trắng, có viền mảnh và tiêu đề nhỏ."""

    def __init__(self, cha: tk.Misc, tieu_de: str = "", **kw):
        super().__init__(cha, bg=VIEN, padx=1, pady=1, **kw)
        self.than = tk.Frame(self, bg=THE)
        self.than.pack(fill="both", expand=True)
        if tieu_de:
            tk.Label(self.than, text=tieu_de.upper(), bg=THE, fg=CHU_MO,
                     font=(PH, 9, "bold"), anchor="w").pack(
                fill="x", padx=14, pady=(12, 6))


class Nut(tk.Label):
    """Nút bấm phẳng, đổi màu khi rê chuột — tk.Button mặc định trông rất cũ."""

    def __init__(self, cha: tk.Misc, chu: str, lenh, chinh: bool = True, **kw):
        self.mau_nen = CHINH if chinh else "#eef2f8"
        self.mau_nen_hover = CHINH_DAM if chinh else "#e2e8f2"
        self.mau_chu = "#ffffff" if chinh else CHU
        self.lenh = lenh
        self._bat = True
        super().__init__(cha, text=chu, bg=self.mau_nen, fg=self.mau_chu,
                         font=F_NUT, padx=14, pady=11, cursor="hand2", **kw)
        self.bind("<Enter>", self._vao)
        self.bind("<Leave>", self._ra)
        self.bind("<Button-1>", self._bam)

    def _vao(self, _=None):
        if self._bat:
            self.config(bg=self.mau_nen_hover)

    def _ra(self, _=None):
        if self._bat:
            self.config(bg=self.mau_nen)

    def _bam(self, _=None):
        if self._bat and callable(self.lenh):
            self.lenh()

    def dat_trang_thai(self, bat: bool) -> None:
        self._bat = bat
        if bat:
            self.config(bg=self.mau_nen, fg=self.mau_chu, cursor="hand2")
        else:
            self.config(bg="#e8ecf3", fg="#a7b0be", cursor="arrow")


class ONhan(tk.Label):
    """Ô nhãn nhỏ nhiều màu, dùng để hiện thống kê 'ghế x3', 'tủ x1'…"""

    def __init__(self, cha: tk.Misc, chu: str, mau_rgb: tuple):
        mau = "#%02x%02x%02x" % mau_rgb
        super().__init__(cha, text=f" {chu} ", bg=mau, fg="#ffffff",
                         font=(PH, 9, "bold"), padx=6, pady=3)


# ============================================================================
# CÁC Ô GIAO DIỆN NÂNG CAO
# ============================================================================
class NutDoan(tk.Frame):
    """Dải nút chọn một trong nhiều mức (kiểu segmented control)."""

    def __init__(self, cha: tk.Misc, cac_muc, chi_so_mac_dinh: int = 1, khi_doi=None):
        super().__init__(cha, bg=VIEN, padx=1, pady=1)
        self.khi_doi = khi_doi
        self.gia_tri = cac_muc[chi_so_mac_dinh][1]
        self._nut = []
        trong = tk.Frame(self, bg="#eef2f8")
        trong.pack(fill="x")
        for i, (nhan, gia_tri) in enumerate(cac_muc):
            o = tk.Label(trong, text=nhan, font=(PH, 9, "bold"), padx=10, pady=7,
                         cursor="hand2", bg="#eef2f8", fg=CHU_MO)
            o.pack(side="left", expand=True, fill="x")
            o.bind("<Button-1>", lambda _e, k=i: self.chon(k))
            self._nut.append((o, gia_tri))
        self.chon(chi_so_mac_dinh, bao=False)

    def chon(self, chi_so: int, bao: bool = True) -> None:
        for i, (o, gia_tri) in enumerate(self._nut):
            if i == chi_so:
                o.config(bg=CHINH, fg="#ffffff")
                self.gia_tri = gia_tri
            else:
                o.config(bg="#eef2f8", fg=CHU_MO)
        if bao and callable(self.khi_doi):
            self.khi_doi(self.gia_tri)


class OAnhNho(tk.Frame):
    """Một dòng trong danh sách ảnh: ảnh thu nhỏ + tên tệp + số món tìm được."""

    def __init__(self, cha: tk.Misc, anh_tk, ten: str, khi_bam):
        super().__init__(cha, bg=THE, padx=6, pady=5, cursor="hand2")
        self.vien = tk.Frame(self, bg=THE, padx=2, pady=2)
        self.vien.pack(fill="x")
        trong = tk.Frame(self.vien, bg="#f6f8fc")
        trong.pack(fill="x")

        self.o_anh = tk.Label(trong, image=anh_tk, bg="#f6f8fc")
        self.o_anh.image = anh_tk
        self.o_anh.pack(side="left", padx=6, pady=6)

        giua = tk.Frame(trong, bg="#f6f8fc")
        giua.pack(side="left", fill="both", expand=True, padx=(2, 6))
        self.o_ten = tk.Label(giua, text=ten, bg="#f6f8fc", fg=CHU,
                              font=(PH, 9, "bold"), anchor="w")
        self.o_ten.pack(fill="x")
        self.o_trang_thai = tk.Label(giua, text="đang chờ…", bg="#f6f8fc",
                                     fg=CHU_MO, font=(PH, 8), anchor="w")
        self.o_trang_thai.pack(fill="x")

        for o in (self, self.vien, trong, self.o_anh, giua, self.o_ten, self.o_trang_thai):
            o.bind("<Button-1>", lambda _e: khi_bam())

    def dat_trang_thai(self, chu: str, mau: str = CHU_MO) -> None:
        self.o_trang_thai.config(text=chu, fg=mau)

    def dat_chon(self, dang_chon: bool) -> None:
        self.vien.config(bg=CHINH if dang_chon else THE)
