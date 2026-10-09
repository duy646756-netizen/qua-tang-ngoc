# -*- coding: utf-8 -*-
"""
detect_image.py — Nhận diện bằng dòng lệnh, cho một ảnh hoặc cả thư mục ảnh.

Ví dụ:
    python detect_image.py anh/phong_khach.jpg
    python detect_image.py anh/ --out ket_qua/ --conf 0.6
    python detect_image.py anh/bep.jpg --model yolov8l.pt --tta
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import Counter

from nhan_dien import BoNhanDien

DUOI_ANH = (".jpg", ".jpeg", ".png", ".bmp", ".webp")


def lay_danh_sach_anh(duong_dan: str) -> list:
    """LỖI CŨ: tên tệp bị ghi cứng là "image.jpg", không có tệp đó là chết chương
    trình. CÁCH SỬA: nhận đường dẫn từ dòng lệnh, chấp nhận cả thư mục."""
    if os.path.isfile(duong_dan):
        return [duong_dan]
    if os.path.isdir(duong_dan):
        return sorted(
            os.path.join(duong_dan, ten)
            for ten in os.listdir(duong_dan)
            if ten.lower().endswith(DUOI_ANH)
        )
    raise FileNotFoundError(f"Không tìm thấy: {duong_dan}")


def main() -> int:
    bo_doc = argparse.ArgumentParser(
        description="Nhận diện đồ nội thất trong ảnh bằng YOLOv8",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    bo_doc.add_argument("duong_dan", help="đường dẫn tới một ảnh hoặc một thư mục ảnh")
    bo_doc.add_argument("--model", default="yolov8m.pt", help="tệp mô hình YOLO")
    bo_doc.add_argument("--conf", type=float, default=0.5, help="ngưỡng tin cậy (0–1)")
    bo_doc.add_argument("--imgsz", type=int, default=960, help="kích thước ảnh đưa vào mạng")
    bo_doc.add_argument("--out", default="ket_qua", help="thư mục ghi ảnh kết quả")
    bo_doc.add_argument("--tta", action="store_true", help="bật chế độ chính xác cao (chậm hơn)")
    tham_so = bo_doc.parse_args()

    try:
        cac_anh = lay_danh_sach_anh(tham_so.duong_dan)
    except FileNotFoundError as loi:
        print(f"Lỗi: {loi}", file=sys.stderr)
        return 1

    if not cac_anh:
        print("Không có tệp ảnh nào trong thư mục.", file=sys.stderr)
        return 1

    os.makedirs(tham_so.out, exist_ok=True)
    bo_nhan_dien = BoNhanDien(tham_so.model)
    tong_ket = Counter()
    so_loi = 0

    for duong_dan in cac_anh:
        ten_tep = os.path.basename(duong_dan)
        print(f"\n=== {ten_tep} " + "=" * max(0, 60 - len(ten_tep)))
        try:
            ket_qua = bo_nhan_dien.nhan_dien(
                duong_dan,
                nguong_tin_cay=tham_so.conf,
                co_anh=tham_so.imgsz,
                dung_tta=tham_so.tta,
            )
        except Exception as loi:                      # noqa: BLE001
            print(f"  BỎ QUA — {loi}", file=sys.stderr)
            so_loi += 1
            continue

        if not ket_qua.danh_sach:
            print("  Không phát hiện đồ nội thất nào.")
        else:
            print(f"  {'Vật thể':<24}{'Độ tin cậy':>12}   Vị trí khung")
            print("  " + "-" * 68)
            for vat in ket_qua.danh_sach:
                x1, y1, x2, y2 = vat.hop
                print(f"  {vat.ten_vi:<24}{vat.do_tin_cay:>11.1%}   ({x1}, {y1}) – ({x2}, {y2})")
            tong_ket.update(ket_qua.thong_ke)

        tep_ra = os.path.join(tham_so.out, f"ketqua_{os.path.splitext(ten_tep)[0]}.jpg")
        ket_qua.anh_da_ve.convert("RGB").save(tep_ra)
        print(f"  -> đã ghi: {tep_ra}")

    if len(cac_anh) > 1:
        print("\n===== TỔNG KẾT " + "=" * 55)
        print(f"  Số ảnh xử lý thành công : {len(cac_anh) - so_loi}/{len(cac_anh)}")
        for ten, so_luong in tong_ket.most_common():
            print(f"  {ten:<24}{so_luong:>5}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
