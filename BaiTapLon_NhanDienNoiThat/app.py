# -*- coding: utf-8 -*-
"""
app.py — Phần mềm NHẬN DIỆN ĐỒ NỘI THẤT trong ảnh.

Chạy: bấm đúp tệp chay.bat, hoặc gõ  python app.py
Phần xử lý ảnh ở nhan_dien.py, phần màu sắc giao diện ở giao_dien.py.
"""

from __future__ import annotations

import os
import threading
import tkinter as tk
import traceback
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

import giao_dien as gd
from nhan_dien import BoNhanDien, KetQua, mau_cua

KHUNG_ANH = (820, 470)        # vùng xem ảnh
CO_ANH_NHO = (74, 56)         # ảnh thu nhỏ trong danh sách

# Ba mức độ nhạy, thay cho thanh trượt dễ kéo nhầm lên 90 % rồi không ra gì
CAC_MUC_NHAY = (
    ("Nhạy", 0.25),           # bắt được nhiều món, chấp nhận vài món sai
    ("Cân bằng", 0.40),
    ("Chắc chắn", 0.60),      # chỉ báo khi thật sự chắc
)


class UngDung:
    def __init__(self, cua_so: tk.Tk):
        self.cua_so = cua_so
        # Bên trong luôn chạy cả hai mô hình rồi gộp kết quả cho chính xác nhất.
        # Người dùng không phải chọn gì cả.
        self.bo_nhan_dien = BoNhanDien("ket_hop")

        self.cac_anh: list[dict] = []     # [{duong_dan, ten, o_danh_sach, ket_qua}]
        self.chi_so_dang_xem: int | None = None
        self._anh_tk = None
        self._dang_chay = False
        self._nguong = 0.40

        cua_so.title("Nhận diện đồ nội thất trong ảnh")
        cua_so.geometry("1380x900")
        cua_so.minsize(1180, 800)
        cua_so.configure(bg=gd.NEN)

        gd.ap_dung_kieu(cua_so)
        self._dung_tieu_de()
        self._dung_trang_thai()
        self._dung_than()

        # Nạp sẵn mô hình ngay khi mở chương trình. Nếu đợi đến lúc người dùng
        # chọn ảnh mới nạp thì ảnh đầu tiên phải chờ thêm khoảng 10 giây.
        self.san_sang = False
        threading.Thread(target=self._nap_mo_hinh, daemon=True).start()

    # ================================================================== #
    # DỰNG GIAO DIỆN
    # ================================================================== #
    def _dung_tieu_de(self) -> None:
        thanh = tk.Frame(self.cua_so, bg=gd.HEADER, height=80)
        thanh.pack(fill="x")
        thanh.pack_propagate(False)

        trai = tk.Frame(thanh, bg=gd.HEADER)
        trai.pack(side="left", padx=26, pady=15)
        tk.Label(trai, text="NHẬN DIỆN ĐỒ NỘI THẤT", bg=gd.HEADER, fg="#ffffff",
                 font=(gd.PH, 18, "bold")).pack(anchor="w")
        tk.Label(trai, text="Chọn một hoặc nhiều ảnh — chương trình tự tìm bàn, ghế, tủ, giường, kệ…",
                 bg=gd.HEADER, fg=gd.HEADER_PHU, font=(gd.PH, 10)).pack(anchor="w")

        phai = tk.Frame(thanh, bg=gd.HEADER)
        phai.pack(side="right", padx=26)
        o = tk.Label(phai, text="  YOLOv8  ", bg=gd.CHINH, fg="#ffffff",
                     font=(gd.PH, 10, "bold"), padx=6, pady=3)
        o.pack(anchor="e", pady=(4, 4))
        tk.Label(phai, text="Chỉ nhận diện đồ nội thất", bg=gd.HEADER,
                 fg=gd.HEADER_PHU, font=(gd.PH, 9)).pack(anchor="e")

    def _dung_trang_thai(self) -> None:
        thanh = tk.Frame(self.cua_so, bg="#e8edf5", height=36)
        thanh.pack(fill="x", side="bottom")
        thanh.pack_propagate(False)
        self.o_trang_thai = tk.Label(
            thanh, text="Sẵn sàng. Lần chạy đầu tiên cần mạng để tải mô hình về.",
            bg="#e8edf5", fg=gd.CHU_MO, font=(gd.PH, 9), anchor="w")
        self.o_trang_thai.pack(side="left", padx=18)
        self.o_tien_do = tk.Label(thanh, text="", bg="#e8edf5", fg=gd.CHINH,
                                  font=(gd.PH, 9, "bold"))
        self.o_tien_do.pack(side="right", padx=18)

    def _dung_than(self) -> None:
        than = tk.Frame(self.cua_so, bg=gd.NEN)
        than.pack(fill="both", expand=True, padx=16, pady=14)
        than.columnconfigure(1, weight=1)
        than.rowconfigure(0, weight=1)

        self._cot_trai(than)
        self._cot_giua(than)
        self._cot_phai(than)

    # ---------------------------------------------------------------- #
    def _cot_trai(self, cha: tk.Frame) -> None:
        cot = tk.Frame(cha, bg=gd.NEN, width=300)
        cot.grid(row=0, column=0, sticky="ns", padx=(0, 14))
        cot.grid_propagate(False)

        the1 = gd.The(cot, "Chọn ảnh")
        the1.pack(fill="x")
        self.nut_chon = gd.Nut(the1.than, "Chọn ảnh để nhận diện", self.chon_anh)
        self.nut_chon.pack(fill="x", padx=14, pady=(2, 6))
        tk.Label(the1.than, text="Giữ Ctrl để chọn nhiều ảnh cùng lúc",
                 bg=gd.THE, fg=gd.CHU_MO, font=(gd.PH, 8)).pack(padx=14, anchor="w")
        self.nut_luu = gd.Nut(the1.than, "Lưu ảnh đang xem", self.luu_anh, chinh=False)
        self.nut_luu.pack(fill="x", padx=14, pady=(10, 4))
        self.nut_luu_tat = gd.Nut(the1.than, "Lưu tất cả kết quả", self.luu_tat_ca, chinh=False)
        self.nut_luu_tat.pack(fill="x", padx=14, pady=(0, 14))
        self.nut_luu.dat_trang_thai(False)
        self.nut_luu_tat.dat_trang_thai(False)

        the2 = gd.The(cot, "Độ nhạy")
        the2.pack(fill="x", pady=(14, 0))
        self.chon_nhay = gd.NutDoan(the2.than, CAC_MUC_NHAY, 1, self._doi_nhay)
        self.chon_nhay.pack(fill="x", padx=14, pady=(2, 6))
        self.o_giai_thich = tk.Label(
            the2.than, text="Mức thường dùng. Bỏ sót ít mà cũng ít báo nhầm.",
            bg=gd.THE, fg=gd.CHU_MO, font=(gd.PH, 9), wraplength=250,
            justify="left", anchor="w")
        self.o_giai_thich.pack(fill="x", padx=14, pady=(0, 14))

        the3 = gd.The(cot, "Tổng quan")
        the3.pack(fill="both", expand=True, pady=(14, 0))
        hang = tk.Frame(the3.than, bg=gd.THE)
        hang.pack(fill="x", padx=14, pady=(2, 10))
        self.o_so_mon = self._o_so(hang, "Số món", "0", gd.CHINH)
        self.o_tin_cay = self._o_so(hang, "Tin cậy TB", "–", gd.XANH)
        self.o_thoi_gian = self._o_so(hang, "Thời gian", "–", gd.CAM)

        tk.Label(the3.than, text="THỐNG KÊ THEO LOẠI", bg=gd.THE, fg=gd.CHU_MO,
                 font=(gd.PH, 9, "bold"), anchor="w").pack(fill="x", padx=14)
        self.khung_nhan = tk.Frame(the3.than, bg=gd.THE)
        self.khung_nhan.pack(fill="both", expand=True, padx=14, pady=(6, 14))
        tk.Label(self.khung_nhan, text="(chưa có dữ liệu)", bg=gd.THE,
                 fg=gd.CHU_MO, font=(gd.PH, 9)).pack(anchor="w")

    @staticmethod
    def _o_so(cha, nhan, gia_tri, mau):
        o = tk.Frame(cha, bg=gd.THE)
        o.pack(side="left", expand=True, fill="x")
        gt = tk.Label(o, text=gia_tri, bg=gd.THE, fg=mau, font=(gd.PH, 19, "bold"))
        gt.pack(anchor="w")
        tk.Label(o, text=nhan, bg=gd.THE, fg=gd.CHU_MO, font=(gd.PH, 9)).pack(anchor="w")
        return gt

    # ---------------------------------------------------------------- #
    def _cot_giua(self, cha: tk.Frame) -> None:
        cot = tk.Frame(cha, bg=gd.NEN)
        cot.grid(row=0, column=1, sticky="nsew")
        cot.rowconfigure(0, weight=3)
        cot.rowconfigure(1, weight=2)
        cot.columnconfigure(0, weight=1)

        the_anh = gd.The(cot)
        the_anh.grid(row=0, column=0, sticky="nsew")
        vung = tk.Frame(the_anh.than, bg=gd.VUNG_ANH)
        vung.pack(fill="both", expand=True, padx=10, pady=10)
        self.o_anh = tk.Label(
            vung, bg=gd.VUNG_ANH, fg=gd.CHU_MO, font=(gd.PH, 11), justify="center",
            text="Chưa có ảnh\n\nBấm « Chọn ảnh để nhận diện »")
        self.o_anh.pack(fill="both", expand=True)
        self.thanh_chay = ttk.Progressbar(the_anh.than, mode="determinate")

        the_bang = gd.The(cot, "Danh sách món đồ trong ảnh đang xem")
        the_bang.grid(row=1, column=0, sticky="nsew", pady=(14, 0))
        tk.Label(the_bang.than, text="Bấm một dòng để làm nổi bật món đó trên ảnh.",
                 bg=gd.THE, fg=gd.CHU_MO, font=(gd.PH, 9)).pack(anchor="w", padx=14)

        khung = tk.Frame(the_bang.than, bg=gd.THE)
        khung.pack(fill="both", expand=True, padx=14, pady=(6, 14))
        self.bang = ttk.Treeview(khung, columns=("stt", "ten", "tin_cay", "kt", "vt"),
                                 show="headings", height=6)
        for ma, td, rong, canh in (("stt", "#", 44, "center"), ("ten", "Món đồ", 230, "w"),
                                   ("tin_cay", "Độ tin cậy", 110, "center"),
                                   ("kt", "Kích thước (px)", 140, "center"),
                                   ("vt", "Vị trí khung", 210, "center")):
            self.bang.heading(ma, text=td)
            self.bang.column(ma, width=rong, anchor=canh, stretch=(ma == "ten"))
        self.bang.tag_configure("le", background="#ffffff")
        self.bang.tag_configure("chan", background="#f7f9fd")
        self.bang.bind("<<TreeviewSelect>>", self._chon_dong)
        cuon = ttk.Scrollbar(khung, orient="vertical", command=self.bang.yview)
        self.bang.configure(yscrollcommand=cuon.set)
        self.bang.pack(side="left", fill="both", expand=True)
        cuon.pack(side="right", fill="y")

    # ---------------------------------------------------------------- #
    def _cot_phai(self, cha: tk.Frame) -> None:
        cot = tk.Frame(cha, bg=gd.NEN, width=250)
        cot.grid(row=0, column=2, sticky="ns", padx=(14, 0))
        cot.grid_propagate(False)

        the = gd.The(cot, "Danh sách ảnh")
        the.pack(fill="both", expand=True)

        ngoai = tk.Frame(the.than, bg=gd.THE)
        ngoai.pack(fill="both", expand=True, padx=8, pady=(0, 10))
        self.khung_cuon = tk.Canvas(ngoai, bg=gd.THE, highlightthickness=0, width=215)
        cuon = ttk.Scrollbar(ngoai, orient="vertical", command=self.khung_cuon.yview)
        self.khung_cuon.configure(yscrollcommand=cuon.set)
        self.khung_cuon.pack(side="left", fill="both", expand=True)
        cuon.pack(side="right", fill="y")

        self.khung_ds = tk.Frame(self.khung_cuon, bg=gd.THE)
        self.khung_cuon.create_window((0, 0), window=self.khung_ds, anchor="nw", width=213)
        self.khung_ds.bind(
            "<Configure>",
            lambda _e: self.khung_cuon.configure(scrollregion=self.khung_cuon.bbox("all")))

        self.o_ds_trong = tk.Label(self.khung_ds, text="Chưa chọn ảnh nào",
                                   bg=gd.THE, fg=gd.CHU_MO, font=(gd.PH, 9))
        self.o_ds_trong.pack(pady=14)

    # ================================================================== #
    # CHUẨN BỊ MÔ HÌNH
    # ================================================================== #
    def _nap_mo_hinh(self) -> None:
        self.cua_so.after(0, lambda: self._bao(
            "Đang chuẩn bị mô hình nhận diện… (lần đầu cần mạng để tải về)", gd.CHU))
        try:
            self.bo_nhan_dien.nap_truoc()
            self.cua_so.after(0, lambda: self._bao(
                "Sẵn sàng. Bấm « Chọn ảnh để nhận diện » để bắt đầu.", gd.XANH))
        except Exception as loi:                            # noqa: BLE001
            traceback.print_exc()
            tb = str(loi)
            self.cua_so.after(0, lambda: self._bao(
                "Chưa tải được mô hình: " + tb[:90], gd.DO))
        finally:
            self.san_sang = True

    # ================================================================== #
    # SỰ KIỆN
    # ================================================================== #
    def _doi_nhay(self, gia_tri: float) -> None:
        self._nguong = gia_tri
        self.o_giai_thich.config(text={
            0.25: "Bắt được nhiều món nhất, đổi lại có thể báo nhầm đôi chút.",
            0.40: "Mức thường dùng. Bỏ sót ít mà cũng ít báo nhầm.",
            0.60: "Chỉ báo những món thật sự chắc chắn. Có thể bỏ sót món khó thấy.",
        }[gia_tri])
        if self.cac_anh and not self._dang_chay:
            self._bat_dau_xu_ly()          # tự chạy lại với mức nhạy mới

    def _chon_dong(self, _=None) -> None:
        if self.chi_so_dang_xem is None:
            return
        chon = self.bang.selection()
        self._ve_anh(self.bang.index(chon[0]) if chon else None, hieu_ung=False)

    # ================================================================== #
    # CHỌN VÀ XỬ LÝ ẢNH
    # ================================================================== #
    def chon_anh(self) -> None:
        if self._dang_chay:
            return
        cac_tep = filedialog.askopenfilenames(
            title="Chọn một hoặc nhiều ảnh (giữ Ctrl để chọn nhiều)",
            filetypes=[("Tệp ảnh", "*.jpg *.jpeg *.png *.bmp *.webp"),
                       ("Tất cả tệp", "*.*")])
        if not cac_tep:
            return

        for o in self.khung_ds.winfo_children():
            o.destroy()
        self.cac_anh.clear()
        self.chi_so_dang_xem = None

        for duong_dan in cac_tep:
            muc = {"duong_dan": duong_dan, "ten": os.path.basename(duong_dan),
                   "ket_qua": None, "o": None}
            muc["o"] = self._them_vao_danh_sach(muc, len(self.cac_anh))
            self.cac_anh.append(muc)

        self._bat_dau_xu_ly()

    def _them_vao_danh_sach(self, muc: dict, chi_so: int):
        try:
            anh = Image.open(muc["duong_dan"])
            anh.thumbnail(CO_ANH_NHO, Image.LANCZOS)
            anh_tk = ImageTk.PhotoImage(anh.convert("RGB"))
        except Exception:
            anh_tk = ImageTk.PhotoImage(Image.new("RGB", CO_ANH_NHO, "#dfe5ee"))
        ten = muc["ten"]
        o = gd.OAnhNho(self.khung_ds, anh_tk,
                       ten if len(ten) <= 22 else ten[:19] + "…",
                       lambda k=chi_so: self.xem_anh(k))
        o.pack(fill="x")
        return o

    def _bat_dau_xu_ly(self) -> None:
        self._khoa("Đang nhận diện… (lần đầu phải tải mô hình, có thể mất vài phút)")
        self.thanh_chay.config(maximum=len(self.cac_anh), value=0)
        self.thanh_chay.pack(fill="x", padx=10, pady=(0, 10))
        for muc in self.cac_anh:
            muc["ket_qua"] = None
            muc["o"].dat_trang_thai("đang chờ…", gd.CHU_MO)
        threading.Thread(target=self._chay_tat_ca, args=(self._nguong,), daemon=True).start()

    def _chay_tat_ca(self, nguong: float) -> None:
        """Chạy trong luồng phụ. Mọi lỗi của từng ảnh được bắt riêng nên một ảnh
        hỏng không làm dừng cả loạt, và giao diện không bao giờ bị treo."""
        tong = len(self.cac_anh)
        for i, muc in enumerate(self.cac_anh):
            self.cua_so.after(0, lambda k=i, t=tong: self._bao_tien_do(k, t))
            try:
                kq = self.bo_nhan_dien.nhan_dien(
                    muc["duong_dan"], nguong_tin_cay=nguong, kem_thiet_bi=False)
                self.cua_so.after(0, lambda k=i, r=kq: self._xong_mot_anh(k, r))
            except Exception as loi:                        # noqa: BLE001
                traceback.print_exc()
                self.cua_so.after(0, lambda k=i, e=str(loi): self._loi_mot_anh(k, e))
        self.cua_so.after(0, self._xong_tat_ca)

    def _bao_tien_do(self, chi_so: int, tong: int) -> None:
        self.o_tien_do.config(text=f"Đang xử lý {chi_so + 1}/{tong}")
        if chi_so < len(self.cac_anh):
            self.cac_anh[chi_so]["o"].dat_trang_thai("đang nhận diện…", gd.CHINH)

    def _xong_mot_anh(self, chi_so: int, kq: KetQua) -> None:
        muc = self.cac_anh[chi_so]
        muc["ket_qua"] = kq
        so = len(kq.danh_sach)
        muc["o"].dat_trang_thai(f"tìm thấy {so} món" if so else "không có món nào",
                                gd.XANH if so else gd.CHU_MO)
        self.thanh_chay.config(value=chi_so + 1)
        if self.chi_so_dang_xem is None:
            self.xem_anh(chi_so)

    def _loi_mot_anh(self, chi_so: int, thong_bao: str) -> None:
        self.cac_anh[chi_so]["o"].dat_trang_thai("lỗi: " + thong_bao[:28], gd.DO)
        self.thanh_chay.config(value=chi_so + 1)

    def _xong_tat_ca(self) -> None:
        self.thanh_chay.pack_forget()
        self.o_tien_do.config(text="")
        self._mo_khoa()
        xong = [m for m in self.cac_anh if m["ket_qua"] is not None]
        tong_mon = sum(len(m["ket_qua"].danh_sach) for m in xong)
        if len(self.cac_anh) > 1:
            self._bao(f"Đã xử lý {len(xong)}/{len(self.cac_anh)} ảnh — "
                      f"tổng cộng {tong_mon} món đồ.", gd.CHU)
        self.nut_luu_tat.dat_trang_thai(tong_mon > 0)

    # ================================================================== #
    # HIỂN THỊ
    # ================================================================== #
    def xem_anh(self, chi_so: int) -> None:
        if not (0 <= chi_so < len(self.cac_anh)):
            return
        self.chi_so_dang_xem = chi_so
        for i, muc in enumerate(self.cac_anh):
            muc["o"].dat_chon(i == chi_so)

        kq = self.cac_anh[chi_so]["ket_qua"]
        if kq is None:
            self.o_anh.config(image="", text="Ảnh này chưa xử lý xong…")
            return

        self._ve_anh(None, hieu_ung=True)
        self.bang.delete(*self.bang.get_children())
        for i, vat in enumerate(kq.danh_sach, start=1):
            x1, y1, x2, y2 = vat.hop
            self.bang.insert("", "end",
                             values=(i, vat.ten_vi, f"{vat.do_tin_cay:.1%}",
                                     f"{x2 - x1} × {y2 - y1}",
                                     f"({x1}, {y1}) – ({x2}, {y2})"),
                             tags=("le" if i % 2 else "chan",))

        self.o_so_mon.config(text=str(len(kq.danh_sach)))
        self.o_tin_cay.config(text=f"{kq.do_tin_cay_tb:.0%}" if kq.danh_sach else "–")
        self.o_thoi_gian.config(text=f"{kq.giay_xu_ly:.1f}s")

        for o in self.khung_nhan.winfo_children():
            o.destroy()
        if kq.danh_sach:
            self._xep_nhan(kq.thong_ke.most_common())
        else:
            tk.Label(self.khung_nhan, text="(không có món nào)", bg=gd.THE,
                     fg=gd.CHU_MO, font=(gd.PH, 9)).pack(anchor="w")

        self._bao(f"{kq.ten_tep} — {kq.tom_tat()}", gd.CHU)
        self.nut_luu.dat_trang_thai(bool(kq.danh_sach))

    def _xep_nhan(self, cac_muc) -> None:
        BE_NGANG, hang, da_dung = 268, None, 0
        for ten, so_luong in cac_muc:
            chu = f"{ten} ×{so_luong}"
            rong = len(chu) * 7 + 22
            if hang is None or (da_dung and da_dung + rong > BE_NGANG):
                hang = tk.Frame(self.khung_nhan, bg=gd.THE)
                hang.pack(fill="x", anchor="w")
                da_dung = 0
            gd.ONhan(hang, chu, mau_cua(ten)).pack(side="left", padx=(0, 4), pady=2)
            da_dung += rong

    def _ve_anh(self, nhan_manh: int | None, hieu_ung: bool = False) -> None:
        if self.chi_so_dang_xem is None:
            return
        kq = self.cac_anh[self.chi_so_dang_xem]["ket_qua"]
        if kq is None:
            return
        anh = kq.ve(nhan_manh)
        anh.thumbnail(KHUNG_ANH, Image.LANCZOS)
        if hieu_ung:
            self._hien_dan(anh)
        else:
            self._dat_anh(anh)

    def _dat_anh(self, anh: Image.Image) -> None:
        self._anh_tk = ImageTk.PhotoImage(anh)
        self.o_anh.config(image=self._anh_tk, text="")

    def _hien_dan(self, anh: Image.Image, buoc: int = 0) -> None:
        """Hiệu ứng ảnh hiện dần cho mượt mắt (5 bước, khoảng 1/8 giây)."""
        tong_buoc = 5
        if buoc >= tong_buoc:
            self._dat_anh(anh)
            return
        nen = Image.new("RGB", anh.size, gd.VUNG_ANH)
        self._dat_anh(Image.blend(nen, anh, (buoc + 1) / tong_buoc))
        self.cua_so.after(25, lambda: self._hien_dan(anh, buoc + 1))

    # ================================================================== #
    # LƯU
    # ================================================================== #
    def luu_anh(self) -> None:
        if self.chi_so_dang_xem is None:
            return
        kq = self.cac_anh[self.chi_so_dang_xem]["ket_qua"]
        if kq is None or not kq.danh_sach:
            return
        goc = os.path.splitext(kq.ten_tep)[0]
        duong_dan = filedialog.asksaveasfilename(
            title="Lưu ảnh kết quả", defaultextension=".jpg",
            initialfile=f"ketqua_{goc}.jpg",
            filetypes=[("Ảnh JPEG", "*.jpg"), ("Ảnh PNG", "*.png")])
        if not duong_dan:
            return
        try:
            kq.ve().convert("RGB").save(duong_dan, quality=95)
            self._bao(f"Đã lưu: {duong_dan}", gd.XANH)
        except Exception as loi:                            # noqa: BLE001
            messagebox.showerror("Không lưu được", str(loi))

    def luu_tat_ca(self) -> None:
        co = [m for m in self.cac_anh if m["ket_qua"] and m["ket_qua"].danh_sach]
        if not co:
            return
        thu_muc = filedialog.askdirectory(title="Chọn thư mục để lưu tất cả kết quả")
        if not thu_muc:
            return
        da_luu, loi = 0, 0
        for muc in co:
            try:
                goc = os.path.splitext(muc["ten"])[0]
                muc["ket_qua"].ve().convert("RGB").save(
                    os.path.join(thu_muc, f"ketqua_{goc}.jpg"), quality=95)
                da_luu += 1
            except Exception:                               # noqa: BLE001
                loi += 1
        self._bao(f"Đã lưu {da_luu} ảnh vào {thu_muc}"
                  + (f" ({loi} ảnh lỗi)" if loi else ""), gd.XANH)

    # ================================================================== #
    def _bao(self, chu: str, mau: str) -> None:
        self.o_trang_thai.config(text=chu, fg=mau)

    def _khoa(self, thong_bao: str) -> None:
        self._dang_chay = True
        self.nut_chon.dat_trang_thai(False)
        self.nut_luu.dat_trang_thai(False)
        self.nut_luu_tat.dat_trang_thai(False)
        self._bao(thong_bao, gd.CHU)

    def _mo_khoa(self) -> None:
        self._dang_chay = False
        self.nut_chon.dat_trang_thai(True)


def main() -> None:
    cua_so = tk.Tk()
    UngDung(cua_so)
    cua_so.mainloop()
    # Thoát dứt khoát: các thư viện tính toán còn giữ luồng nền, nếu để Python
    # tự dọn thì cửa sổ đã đóng mà tiến trình vẫn báo lỗi lằng nhằng.
    os._exit(0)


if __name__ == "__main__":
    main()
