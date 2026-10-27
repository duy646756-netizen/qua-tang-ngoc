# -*- coding: utf-8 -*-
"""
app.py — Phần mềm NHẬN DIỆN ĐỒ NỘI THẤT trong ảnh.

Chạy:  python app.py
Phần xử lý ảnh nằm ở nhan_dien.py, phần màu sắc giao diện ở giao_dien.py.
"""

from __future__ import annotations

import os
import threading
import tkinter as tk
import traceback
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

import giao_dien as gd
from nhan_dien import CHE_DO, CHE_DO_MAC_DINH, BoNhanDien, KetQua

KHUNG_ANH = (860, 540)          # kích thước tối đa của vùng xem ảnh


class UngDung:
    def __init__(self, cua_so: tk.Tk):
        self.cua_so = cua_so
        self.bo_nhan_dien = BoNhanDien(CHE_DO_MAC_DINH)
        self.ket_qua: KetQua | None = None
        self._anh_tk = None                  # giữ tham chiếu kẻo bị thu gom rác
        self._dang_chay = False

        cua_so.title("Nhận diện đồ nội thất trong ảnh")
        cua_so.geometry("1240x880")
        cua_so.minsize(1100, 780)
        cua_so.configure(bg=gd.NEN)

        gd.ap_dung_kieu(cua_so)
        self._dung_thanh_tieu_de()
        # Thanh trạng thái phải được đặt trước phần thân: phần thân dùng
        # expand=True nên nếu đặt sau sẽ chiếm hết chỗ và đẩy thanh này ra ngoài.
        self._dung_thanh_trang_thai()
        self._dung_than()

    # ================================================================== #
    # DỰNG GIAO DIỆN
    # ================================================================== #
    def _dung_thanh_tieu_de(self) -> None:
        thanh = tk.Frame(self.cua_so, bg=gd.HEADER, height=78)
        thanh.pack(fill="x")
        thanh.pack_propagate(False)

        trai = tk.Frame(thanh, bg=gd.HEADER)
        trai.pack(side="left", padx=24, pady=14)
        tk.Label(trai, text="NHẬN DIỆN ĐỒ NỘI THẤT", bg=gd.HEADER, fg="#ffffff",
                 font=(gd.PH, 17, "bold")).pack(anchor="w")
        tk.Label(trai, text="Phát hiện bàn, ghế, tủ, giường, kệ… trong ảnh chụp nội thất",
                 bg=gd.HEADER, fg=gd.HEADER_PHU, font=(gd.PH, 10)).pack(anchor="w")

        phai = tk.Frame(thanh, bg=gd.HEADER)
        phai.pack(side="right", padx=24)
        tk.Label(phai, text="YOLOv8", bg=gd.HEADER, fg="#ffffff",
                 font=(gd.PH, 12, "bold")).pack(anchor="e")
        tk.Label(phai, text="Bài tập lớn môn Xử lý ảnh", bg=gd.HEADER,
                 fg=gd.HEADER_PHU, font=(gd.PH, 9)).pack(anchor="e")

    def _dung_than(self) -> None:
        than = tk.Frame(self.cua_so, bg=gd.NEN)
        than.pack(fill="both", expand=True, padx=18, pady=16)
        than.columnconfigure(1, weight=1)
        than.rowconfigure(0, weight=1)

        self._dung_cot_trai(than)
        self._dung_cot_phai(than)

    # ---------------------------------------------------------------- #
    def _dung_cot_trai(self, cha: tk.Frame) -> None:
        cot = tk.Frame(cha, bg=gd.NEN, width=330)
        cot.grid(row=0, column=0, sticky="ns", padx=(0, 16))
        cot.grid_propagate(False)

        # ---- Thẻ 1: thao tác ----
        the1 = gd.The(cot, "Bước 1 · Chọn ảnh")
        the1.pack(fill="x")
        self.nut_chon = gd.Nut(the1.than, "Chọn ảnh để nhận diện", self.chon_anh, chinh=True)
        self.nut_chon.pack(fill="x", padx=14, pady=(2, 8))
        self.nut_luu = gd.Nut(the1.than, "Lưu ảnh kết quả", self.luu_anh, chinh=False)
        self.nut_luu.pack(fill="x", padx=14, pady=(0, 14))
        self.nut_luu.dat_trang_thai(False)

        # ---- Thẻ 2: tuỳ chọn ----
        the2 = gd.The(cot, "Bước 2 · Tuỳ chọn")
        the2.pack(fill="x", pady=(14, 0))
        than2 = the2.than

        ttk.Label(than2, text="Bộ nhận diện", style="Muc.TLabel").pack(
            anchor="w", padx=14, pady=(2, 4))
        self.ten_che_do = {CHE_DO[k]["ten"]: k for k in CHE_DO}
        self.bien_che_do = tk.StringVar(value=CHE_DO[CHE_DO_MAC_DINH]["ten"])
        hop = ttk.Combobox(than2, textvariable=self.bien_che_do, state="readonly",
                           values=list(self.ten_che_do.keys()), font=gd.F_NHO)
        hop.pack(fill="x", padx=14)
        hop.bind("<<ComboboxSelected>>", self._doi_che_do)

        self.nhan_mo_ta = ttk.Label(than2, text=CHE_DO[CHE_DO_MAC_DINH]["mo_ta"],
                                    style="Mo.TLabel", wraplength=280, justify="left")
        self.nhan_mo_ta.pack(anchor="w", padx=14, pady=(6, 12))

        hang = tk.Frame(than2, bg=gd.THE)
        hang.pack(fill="x", padx=14)
        ttk.Label(hang, text="Ngưỡng tin cậy", style="Muc.TLabel").pack(side="left")
        self.nhan_nguong = ttk.Label(hang, text="40%", style="Muc.TLabel", foreground=gd.CHINH)
        self.nhan_nguong.pack(side="right")
        self.bien_nguong = tk.DoubleVar(value=0.40)
        ttk.Scale(than2, from_=0.10, to=0.90, variable=self.bien_nguong,
                  orient="horizontal", command=self._doi_nguong).pack(
            fill="x", padx=14, pady=(4, 2))
        ttk.Label(than2, text="Càng cao càng ít báo nhầm, nhưng dễ bỏ sót món khó thấy.",
                  style="Mo.TLabel", wraplength=280, justify="left").pack(
            anchor="w", padx=14, pady=(0, 12))

        self.bien_thiet_bi = tk.BooleanVar(value=False)
        ttk.Checkbutton(than2, text="Kèm thiết bị và đồ trang trí",
                        variable=self.bien_thiet_bi).pack(anchor="w", padx=12)
        ttk.Label(than2, text="Tivi, tủ lạnh, đèn, gương, rèm, chậu cây…",
                  style="Mo.TLabel", wraplength=280, justify="left").pack(
            anchor="w", padx=34, pady=(0, 8))

        self.bien_tta = tk.BooleanVar(value=False)
        ttk.Checkbutton(than2, text="Chế độ chính xác cao (chậm hơn)",
                        variable=self.bien_tta).pack(anchor="w", padx=12, pady=(0, 14))

        # ---- Thẻ 3: tổng quan ----
        the3 = gd.The(cot, "Bước 3 · Tổng quan")
        the3.pack(fill="both", expand=True, pady=(14, 0))
        than3 = the3.than

        hang_so = tk.Frame(than3, bg=gd.THE)
        hang_so.pack(fill="x", padx=14, pady=(2, 10))
        self.o_so_mon = self._o_so_lieu(hang_so, "Số món", "0", gd.CHINH)
        self.o_tin_cay = self._o_so_lieu(hang_so, "Tin cậy TB", "–", gd.XANH)
        self.o_thoi_gian = self._o_so_lieu(hang_so, "Thời gian", "–", gd.CAM)

        ttk.Label(than3, text="Thống kê theo loại", style="Muc.TLabel").pack(
            anchor="w", padx=14, pady=(2, 6))
        self.khung_nhan = tk.Frame(than3, bg=gd.THE)
        self.khung_nhan.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        self.nhan_trong = ttk.Label(self.khung_nhan, text="(chưa có dữ liệu)", style="Mo.TLabel")
        self.nhan_trong.pack(anchor="w")

    @staticmethod
    def _o_so_lieu(cha: tk.Frame, nhan: str, gia_tri: str, mau: str) -> tk.Label:
        o = tk.Frame(cha, bg=gd.THE)
        o.pack(side="left", expand=True, fill="x")
        nhan_gt = tk.Label(o, text=gia_tri, bg=gd.THE, fg=mau, font=(gd.PH, 19, "bold"))
        nhan_gt.pack(anchor="w")
        tk.Label(o, text=nhan, bg=gd.THE, fg=gd.CHU_MO, font=(gd.PH, 9)).pack(anchor="w")
        return nhan_gt

    # ---------------------------------------------------------------- #
    def _dung_cot_phai(self, cha: tk.Frame) -> None:
        cot = tk.Frame(cha, bg=gd.NEN)
        cot.grid(row=0, column=1, sticky="nsew")
        cot.rowconfigure(0, weight=3)
        cot.rowconfigure(1, weight=2)
        cot.columnconfigure(0, weight=1)

        # ---- Vùng xem ảnh ----
        the_anh = gd.The(cot)
        the_anh.grid(row=0, column=0, sticky="nsew")
        vung = tk.Frame(the_anh.than, bg=gd.VUNG_ANH)
        vung.pack(fill="both", expand=True, padx=10, pady=10)
        self.nhan_anh = tk.Label(
            vung, bg=gd.VUNG_ANH, fg=gd.CHU_MO, font=(gd.PH, 11),
            text="Chưa có ảnh\n\nBấm « Chọn ảnh để nhận diện » ở cột bên trái",
            justify="center",
        )
        self.nhan_anh.pack(fill="both", expand=True)

        self.thanh_tien_trinh = ttk.Progressbar(the_anh.than, mode="indeterminate")

        # ---- Bảng kết quả ----
        the_bang = gd.The(cot, "Danh sách món đồ phát hiện được")
        the_bang.grid(row=1, column=0, sticky="nsew", pady=(16, 0))

        ttk.Label(the_bang.than,
                  text="Bấm vào một dòng để làm nổi bật món đó trên ảnh.",
                  style="Mo.TLabel").pack(anchor="w", padx=14, pady=(0, 6))

        khung = tk.Frame(the_bang.than, bg=gd.THE)
        khung.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        cot_bang = ("stt", "ten", "tin_cay", "kich_thuoc", "vi_tri")
        self.bang = ttk.Treeview(khung, columns=cot_bang, show="headings", height=7)
        for ma, tieu_de, rong, canh in (
            ("stt", "#", 46, "center"),
            ("ten", "Món đồ", 240, "w"),
            ("tin_cay", "Độ tin cậy", 120, "center"),
            ("kich_thuoc", "Kích thước (px)", 150, "center"),
            ("vi_tri", "Vị trí khung", 220, "center"),
        ):
            self.bang.heading(ma, text=tieu_de)
            self.bang.column(ma, width=rong, anchor=canh, stretch=(ma == "ten"))
        self.bang.tag_configure("le", background="#ffffff")
        self.bang.tag_configure("chan", background="#f7f9fd")
        self.bang.bind("<<TreeviewSelect>>", self._chon_dong)

        cuon = ttk.Scrollbar(khung, orient="vertical", command=self.bang.yview)
        self.bang.configure(yscrollcommand=cuon.set)
        self.bang.pack(side="left", fill="both", expand=True)
        cuon.pack(side="right", fill="y")

    def _dung_thanh_trang_thai(self) -> None:
        thanh = tk.Frame(self.cua_so, bg="#e8edf5", height=34)
        thanh.pack(fill="x", side="bottom")
        thanh.pack_propagate(False)
        self.nhan_trang_thai = tk.Label(
            thanh,
            text="Sẵn sàng. Lần chạy đầu tiên chương trình sẽ tự tải mô hình về (cần mạng).",
            bg="#e8edf5", fg=gd.CHU_MO, font=(gd.PH, 9), anchor="w",
        )
        self.nhan_trang_thai.pack(side="left", padx=18)

    # ================================================================== #
    # SỰ KIỆN
    # ================================================================== #
    def _doi_nguong(self, _=None) -> None:
        self.nhan_nguong.config(text=f"{self.bien_nguong.get():.0%}")

    def _doi_che_do(self, _=None) -> None:
        ma = self.ten_che_do[self.bien_che_do.get()]
        self.nhan_mo_ta.config(text=CHE_DO[ma]["mo_ta"])

    def _chon_dong(self, _=None) -> None:
        if self.ket_qua is None:
            return
        chon = self.bang.selection()
        chi_so = self.bang.index(chon[0]) if chon else None
        self._ve_anh(chi_so)

    # ================================================================== #
    # NHẬN DIỆN
    # ================================================================== #
    def chon_anh(self) -> None:
        if self._dang_chay:
            return
        duong_dan = filedialog.askopenfilename(
            title="Chọn ảnh nội thất cần nhận diện",
            filetypes=[("Tệp ảnh", "*.jpg *.jpeg *.png *.bmp *.webp"),
                       ("Tất cả tệp", "*.*")],
        )
        if not duong_dan:
            return

        ma_che_do = self.ten_che_do[self.bien_che_do.get()]
        tep_model = CHE_DO[ma_che_do]["models"][0]
        if ma_che_do == "tu_huan_luyen" and not os.path.isfile(tep_model):
            messagebox.showwarning(
                "Chưa có mô hình tự huấn luyện",
                "Không tìm thấy tệp models/best.pt.\n\n"
                "Hãy chạy train.py để huấn luyện trước, hoặc chọn một bộ nhận diện khác.",
            )
            return

        self._khoa("Đang nhận diện…  (lần đầu phải tải mô hình, có thể mất vài phút)")
        threading.Thread(
            target=self._chay,
            args=(duong_dan, ma_che_do, float(self.bien_nguong.get()),
                  bool(self.bien_thiet_bi.get()), bool(self.bien_tta.get())),
            daemon=True,
        ).start()

    def _chay(self, duong_dan: str, ma_che_do: str, nguong: float,
              kem_thiet_bi: bool, tta: bool) -> None:
        """Chạy trong luồng phụ để cửa sổ không bị đơ.

        Toàn bộ thân hàm nằm trong try/except: dù lỗi gì xảy ra thì giao diện
        cũng luôn được mở khoá trở lại, không bao giờ treo.
        """
        try:
            self.bo_nhan_dien.doi_che_do(ma_che_do)
            ket_qua = self.bo_nhan_dien.nhan_dien(
                duong_dan, nguong_tin_cay=nguong,
                kem_thiet_bi=kem_thiet_bi, dung_tta=tta,
            )
            self.cua_so.after(0, lambda: self._hien(ket_qua))
        except Exception as loi:                      # noqa: BLE001
            traceback.print_exc()
            thong_bao = str(loi) or loi.__class__.__name__
            self.cua_so.after(0, lambda: self._bao_loi(thong_bao))

    def _hien(self, ket_qua: KetQua) -> None:
        self.ket_qua = ket_qua
        self._ve_anh(None)

        # Bảng
        self.bang.delete(*self.bang.get_children())
        for i, vat in enumerate(ket_qua.danh_sach, start=1):
            x1, y1, x2, y2 = vat.hop
            self.bang.insert(
                "", "end",
                values=(i, vat.ten_vi, f"{vat.do_tin_cay:.1%}",
                        f"{x2 - x1} × {y2 - y1}", f"({x1}, {y1}) – ({x2}, {y2})"),
                tags=("le" if i % 2 else "chan",),
            )

        # Số liệu tổng quan
        self.o_so_mon.config(text=str(len(ket_qua.danh_sach)))
        self.o_tin_cay.config(
            text=f"{ket_qua.do_tin_cay_tb:.0%}" if ket_qua.danh_sach else "–")
        self.o_thoi_gian.config(text=f"{ket_qua.giay_xu_ly:.1f}s")

        # Các ô nhãn thống kê
        for o in self.khung_nhan.winfo_children():
            o.destroy()
        if ket_qua.danh_sach:
            self._xep_nhan(ket_qua.thong_ke.most_common())
        else:
            ttk.Label(self.khung_nhan, text="(không có món nào)",
                      style="Mo.TLabel").pack(anchor="w")

        self._dat_trang_thai(f"{ket_qua.ten_tep} — {ket_qua.tom_tat()}", gd.CHU)
        self.nut_luu.dat_trang_thai(bool(ket_qua.danh_sach))
        self._mo_khoa()

    def _xep_nhan(self, cac_muc) -> None:
        """Xếp các ô nhãn thống kê thành nhiều hàng, tự xuống dòng khi hết bề ngang."""
        from nhan_dien import mau_cua

        BE_NGANG = 300                      # bề ngang khả dụng của cột trái (điểm ảnh)
        hang = tk.Frame(self.khung_nhan, bg=gd.THE)
        hang.pack(fill="x", anchor="w")
        da_dung = 0
        for ten, so_luong in cac_muc:
            chu = f"{ten} ×{so_luong}"
            rong = len(chu) * 7 + 22        # ước lượng bề ngang của ô nhãn
            if da_dung and da_dung + rong > BE_NGANG:
                hang = tk.Frame(self.khung_nhan, bg=gd.THE)
                hang.pack(fill="x", anchor="w")
                da_dung = 0
            gd.ONhan(hang, chu, mau_cua(ten)).pack(side="left", padx=(0, 4), pady=2)
            da_dung += rong

    def _ve_anh(self, nhan_manh: int | None) -> None:
        if self.ket_qua is None:
            return
        anh = self.ket_qua.ve(nhan_manh)
        anh.thumbnail(KHUNG_ANH, Image.LANCZOS)
        self._anh_tk = ImageTk.PhotoImage(anh)
        self.nhan_anh.config(image=self._anh_tk, text="")

    def _bao_loi(self, thong_bao: str) -> None:
        self._dat_trang_thai(f"Lỗi: {thong_bao}", gd.DO)
        self._mo_khoa()
        messagebox.showerror("Không nhận diện được", thong_bao)

    def luu_anh(self) -> None:
        if self.ket_qua is None or not self.ket_qua.danh_sach:
            return
        goc = os.path.splitext(self.ket_qua.ten_tep)[0]
        duong_dan = filedialog.asksaveasfilename(
            title="Lưu ảnh kết quả", defaultextension=".jpg",
            initialfile=f"ketqua_{goc}.jpg",
            filetypes=[("Ảnh JPEG", "*.jpg"), ("Ảnh PNG", "*.png")],
        )
        if not duong_dan:
            return
        try:
            anh = self.ket_qua.ve(None)
            if duong_dan.lower().endswith((".jpg", ".jpeg")):
                anh = anh.convert("RGB")
            anh.save(duong_dan, quality=95)
            self._dat_trang_thai(f"Đã lưu: {duong_dan}", gd.XANH)
        except Exception as loi:                      # noqa: BLE001
            messagebox.showerror("Không lưu được", str(loi))

    # ================================================================== #
    def _dat_trang_thai(self, chu: str, mau: str) -> None:
        self.nhan_trang_thai.config(text=chu, fg=mau)

    def _khoa(self, thong_bao: str) -> None:
        self._dang_chay = True
        self.nut_chon.dat_trang_thai(False)
        self.nut_luu.dat_trang_thai(False)
        self._dat_trang_thai(thong_bao, gd.CHU)
        self.thanh_tien_trinh.pack(fill="x", padx=10, pady=(0, 10))
        self.thanh_tien_trinh.start(12)

    def _mo_khoa(self) -> None:
        self._dang_chay = False
        self.thanh_tien_trinh.stop()
        self.thanh_tien_trinh.pack_forget()
        self.nut_chon.dat_trang_thai(True)


def main() -> None:
    cua_so = tk.Tk()
    UngDung(cua_so)
    cua_so.mainloop()


if __name__ == "__main__":
    main()
