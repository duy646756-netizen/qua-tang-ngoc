# -*- coding: utf-8 -*-
"""
app.py — Giao diện chương trình NHẬN DIỆN ĐỒ NỘI THẤT trong ảnh.

Chạy:  python app.py
Phần lõi nhận diện nằm ở nhan_dien.py.
"""

from __future__ import annotations

import os
import threading
import tkinter as tk
import traceback
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

from nhan_dien import BoNhanDien, KetQua

# Các mô hình cho người dùng chọn: càng xuống dưới càng chính xác, càng chậm.
# Mô hình tự huấn luyện (nếu đã chạy train.py) nằm ở models/best.pt
CAC_MODEL = [
    ("YOLOv8n — nhanh nhất, kém chính xác nhất", "yolov8n.pt"),
    ("YOLOv8s — cân bằng", "yolov8s.pt"),
    ("YOLOv8m — chính xác cao (khuyên dùng)", "yolov8m.pt"),
    ("YOLOv8l — chính xác nhất, chậm", "yolov8l.pt"),
    ("Mô hình tự huấn luyện (models/best.pt)", os.path.join("models", "best.pt")),
]

KICH_THUOC_XEM = (760, 500)      # khung hiển thị ảnh kết quả


class UngDung:
    def __init__(self, cua_so: tk.Tk):
        self.cua_so = cua_so
        self.bo_nhan_dien = BoNhanDien("yolov8m.pt")
        self.ket_qua: KetQua | None = None      # giữ ảnh gốc độ phân giải đầy đủ để lưu
        self._anh_hien_thi = None               # giữ tham chiếu, tránh bị thu gom rác

        cua_so.title("Nhận diện đồ nội thất bằng ảnh — YOLOv8")
        cua_so.geometry("980x860")
        cua_so.minsize(820, 700)

        self._dung_giao_dien()

    # ------------------------------------------------------------------ #
    # Dựng giao diện
    # ------------------------------------------------------------------ #
    def _dung_giao_dien(self) -> None:
        tk.Label(
            self.cua_so,
            text="PHẦN MỀM NHẬN DIỆN ĐỒ NỘI THẤT",
            font=("Arial", 20, "bold"),
        ).pack(pady=(16, 4))
        tk.Label(
            self.cua_so,
            text="Chọn một ảnh phòng khách, phòng bếp, phòng ngủ… chương trình sẽ khoanh vùng và gọi tên từng món đồ.",
            font=("Arial", 10),
            fg="#555555",
        ).pack()

        # ---- Hàng tuỳ chọn ----
        khung_tuy_chon = ttk.LabelFrame(self.cua_so, text="Tuỳ chọn nhận diện")
        khung_tuy_chon.pack(fill="x", padx=18, pady=12)

        ttk.Label(khung_tuy_chon, text="Mô hình:").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        self.bien_model = tk.StringVar(value=CAC_MODEL[2][0])
        hop_model = ttk.Combobox(
            khung_tuy_chon,
            textvariable=self.bien_model,
            values=[ten for ten, _ in CAC_MODEL],
            state="readonly",
            width=42,
        )
        hop_model.grid(row=0, column=1, sticky="w", pady=8)

        ttk.Label(khung_tuy_chon, text="Ngưỡng tin cậy:").grid(row=0, column=2, sticky="e", padx=(24, 8))
        self.bien_nguong = tk.DoubleVar(value=0.50)
        thanh_truot = ttk.Scale(
            khung_tuy_chon, from_=0.10, to=0.95, variable=self.bien_nguong,
            orient="horizontal", length=170, command=self._cap_nhat_nhan_nguong,
        )
        thanh_truot.grid(row=0, column=3, pady=8)
        self.nhan_nguong = ttk.Label(khung_tuy_chon, text="50%", width=5)
        self.nhan_nguong.grid(row=0, column=4, padx=(6, 8))

        self.bien_tta = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            khung_tuy_chon,
            text="Chế độ chính xác cao (chậm hơn 2–3 lần)",
            variable=self.bien_tta,
        ).grid(row=1, column=1, columnspan=3, sticky="w", pady=(0, 10))

        # ---- Hàng nút bấm ----
        khung_nut = tk.Frame(self.cua_so)
        khung_nut.pack(pady=4)
        self.nut_chon_anh = tk.Button(
            khung_nut, text="  Chọn ảnh để nhận diện  ", font=("Arial", 12, "bold"),
            command=self.chon_anh, cursor="hand2",
        )
        self.nut_chon_anh.pack(side="left", padx=6)
        self.nut_luu = tk.Button(
            khung_nut, text="  Lưu ảnh kết quả  ", font=("Arial", 12),
            command=self.luu_ket_qua, state="disabled", cursor="hand2",
        )
        self.nut_luu.pack(side="left", padx=6)

        self.thanh_tien_trinh = ttk.Progressbar(self.cua_so, mode="indeterminate")

        # ---- Vùng ảnh ----
        self.nhan_anh = tk.Label(
            self.cua_so, text="(chưa có ảnh)", width=96, height=22,
            relief="groove", bg="#fafafa", fg="#999999",
        )
        self.nhan_anh.pack(pady=10, padx=18)

        # ---- Bảng kết quả ----
        khung_bang = ttk.LabelFrame(self.cua_so, text="Danh sách vật thể phát hiện được")
        khung_bang.pack(fill="both", expand=True, padx=18, pady=(0, 6))

        self.bang = ttk.Treeview(
            khung_bang, columns=("stt", "ten", "tin_cay", "vi_tri"),
            show="headings", height=6,
        )
        for cot, tieu_de, rong, canh in (
            ("stt", "STT", 60, "center"),
            ("ten", "Tên vật thể", 260, "w"),
            ("tin_cay", "Độ tin cậy", 120, "center"),
            ("vi_tri", "Vị trí khung (x1, y1, x2, y2)", 300, "center"),
        ):
            self.bang.heading(cot, text=tieu_de)
            self.bang.column(cot, width=rong, anchor=canh)
        thanh_cuon = ttk.Scrollbar(khung_bang, orient="vertical", command=self.bang.yview)
        self.bang.configure(yscrollcommand=thanh_cuon.set)
        self.bang.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=6)
        thanh_cuon.pack(side="right", fill="y", pady=6)

        # ---- Dòng trạng thái ----
        self.nhan_trang_thai = tk.Label(
            self.cua_so, text="Sẵn sàng. Lần chạy đầu tiên chương trình sẽ tự tải mô hình về (cần mạng).",
            font=("Arial", 11), wraplength=940, anchor="w", justify="left",
        )
        self.nhan_trang_thai.pack(fill="x", padx=18, pady=(0, 14))

    def _cap_nhat_nhan_nguong(self, _=None) -> None:
        self.nhan_nguong.config(text=f"{self.bien_nguong.get():.0%}")

    # ------------------------------------------------------------------ #
    # Xử lý
    # ------------------------------------------------------------------ #
    def chon_anh(self) -> None:
        duong_dan = filedialog.askopenfilename(
            title="Chọn ảnh cần nhận diện",
            filetypes=[("Tệp ảnh", "*.jpg *.jpeg *.png *.bmp *.webp"), ("Tất cả tệp", "*.*")],
        )
        if not duong_dan:
            return

        ten_model = dict(CAC_MODEL)[self.bien_model.get()]
        if ten_model.startswith("models") and not os.path.isfile(ten_model):
            messagebox.showwarning(
                "Chưa có mô hình tự huấn luyện",
                "Không tìm thấy tệp models/best.pt.\n"
                "Hãy chạy train.py để huấn luyện trước, hoặc chọn một mô hình YOLOv8 có sẵn.",
            )
            return

        self._khoa_giao_dien("Đang nhận diện, vui lòng chờ…")
        threading.Thread(
            target=self._chay_nhan_dien,
            args=(duong_dan, ten_model, float(self.bien_nguong.get()), bool(self.bien_tta.get())),
            daemon=True,
        ).start()

    def _chay_nhan_dien(self, duong_dan: str, ten_model: str, nguong: float, tta: bool) -> None:
        """Chạy trong luồng phụ để giao diện không bị đơ.

        Toàn bộ thân hàm nằm trong try/except: dù lỗi gì xảy ra, giao diện vẫn
        luôn được mở khoá trở lại (lỗi cũ: thiếu try/except nên khi mô hình ném
        lỗi, thanh tiến trình quay mãi và nút bấm xám vĩnh viễn).
        """
        try:
            self.bo_nhan_dien.doi_model(ten_model)
            ket_qua = self.bo_nhan_dien.nhan_dien(
                duong_dan, nguong_tin_cay=nguong, dung_tta=tta
            )
            self.cua_so.after(0, lambda: self._hien_ket_qua(ket_qua, os.path.basename(duong_dan)))
        except Exception as loi:                       # noqa: BLE001 - cần bắt mọi lỗi
            traceback.print_exc()
            thong_bao = str(loi) or loi.__class__.__name__
            self.cua_so.after(0, lambda: self._bao_loi(thong_bao))

    def _hien_ket_qua(self, ket_qua: KetQua, ten_tep: str) -> None:
        self.ket_qua = ket_qua

        anh_xem = ket_qua.anh_da_ve.copy()
        anh_xem.thumbnail(KICH_THUOC_XEM, Image.LANCZOS)
        self._anh_hien_thi = ImageTk.PhotoImage(anh_xem)
        self.nhan_anh.config(image=self._anh_hien_thi, text="", width=0, height=0)

        self.bang.delete(*self.bang.get_children())
        for i, vat in enumerate(ket_qua.danh_sach, start=1):
            x1, y1, x2, y2 = vat.hop
            self.bang.insert(
                "", "end",
                values=(i, vat.ten_vi, f"{vat.do_tin_cay:.1%}", f"({x1}, {y1}) – ({x2}, {y2})"),
            )

        self.nhan_trang_thai.config(text=f"{ten_tep} — {ket_qua.tom_tat()}", fg="black")
        self.nut_luu.config(state="normal" if ket_qua.danh_sach else "disabled")
        self._mo_khoa_giao_dien()

    def _bao_loi(self, thong_bao: str) -> None:
        self.nhan_trang_thai.config(text=f"Lỗi: {thong_bao}", fg="#b00020")
        self._mo_khoa_giao_dien()
        messagebox.showerror("Không nhận diện được", thong_bao)

    def luu_ket_qua(self) -> None:
        if self.ket_qua is None:
            return
        duong_dan = filedialog.asksaveasfilename(
            title="Lưu ảnh kết quả",
            defaultextension=".jpg",
            initialfile="ket_qua.jpg",
            filetypes=[("Ảnh JPEG", "*.jpg"), ("Ảnh PNG", "*.png")],
        )
        if not duong_dan:
            return
        try:
            anh = self.ket_qua.anh_da_ve
            if duong_dan.lower().endswith((".jpg", ".jpeg")):
                anh = anh.convert("RGB")
            anh.save(duong_dan)                     # PIL ghi được đường dẫn có dấu
            self.nhan_trang_thai.config(text=f"Đã lưu ảnh kết quả: {duong_dan}", fg="#1b5e20")
        except Exception as loi:                    # noqa: BLE001
            messagebox.showerror("Không lưu được", str(loi))

    # ------------------------------------------------------------------ #
    def _khoa_giao_dien(self, thong_bao: str) -> None:
        self.nut_chon_anh.config(state="disabled")
        self.nut_luu.config(state="disabled")
        self.nhan_trang_thai.config(text=thong_bao, fg="black")
        self.thanh_tien_trinh.pack(fill="x", padx=60, pady=(0, 6))
        self.thanh_tien_trinh.start(12)

    def _mo_khoa_giao_dien(self) -> None:
        self.thanh_tien_trinh.stop()
        self.thanh_tien_trinh.pack_forget()
        self.nut_chon_anh.config(state="normal")


def main() -> None:
    cua_so = tk.Tk()
    UngDung(cua_so)
    cua_so.mainloop()


if __name__ == "__main__":
    main()
