# -*- coding: utf-8 -*-
"""
train.py — Huấn luyện tinh chỉnh (fine-tune) mô hình trên bộ ảnh nội thất riêng.

Đây là phần làm nên "bài tập lớn": thay vì chỉ gọi mô hình có sẵn, ta dạy thêm
cho nó những món đồ mà bộ COCO không có (tủ quần áo, kệ sách, đèn bàn, rèm…).

Chuẩn bị dữ liệu trước khi chạy (xem README mục 6):
    data/
      images/train/*.jpg   labels/train/*.txt
      images/val/*.jpg     labels/val/*.txt
      furniture.yaml

Chạy:
    python train.py --epochs 100
    python train.py --model yolov8s.pt --epochs 150 --batch 8
"""

from __future__ import annotations

import argparse
import os
import shutil


def main() -> int:
    bo_doc = argparse.ArgumentParser(
        description="Huấn luyện tinh chỉnh YOLOv8 cho bài toán nhận diện đồ nội thất",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    bo_doc.add_argument("--data", default=os.path.join("data", "furniture.yaml"),
                        help="tệp cấu hình bộ dữ liệu")
    bo_doc.add_argument("--model", default="yolov8m.pt", help="mô hình khởi đầu")
    bo_doc.add_argument("--epochs", type=int, default=100, help="số vòng huấn luyện")
    bo_doc.add_argument("--imgsz", type=int, default=640, help="kích thước ảnh huấn luyện")
    bo_doc.add_argument("--batch", type=int, default=16, help="số ảnh mỗi lô")
    bo_doc.add_argument("--patience", type=int, default=25,
                        help="dừng sớm nếu sau bấy nhiêu vòng không khá hơn")
    bo_doc.add_argument("--device", default=None, help="'0' dùng GPU, 'cpu' dùng CPU")
    bo_doc.add_argument("--ten", default="noi_that", help="tên lần chạy")
    tham_so = bo_doc.parse_args()

    if not os.path.isfile(tham_so.data):
        print(f"Lỗi: không tìm thấy tệp cấu hình dữ liệu '{tham_so.data}'.")
        print("Hãy đọc README mục 6 để chuẩn bị bộ dữ liệu trước.")
        return 1

    from ultralytics import YOLO

    model = YOLO(tham_so.model)
    ket_qua = model.train(
        data=tham_so.data,
        epochs=tham_so.epochs,
        imgsz=tham_so.imgsz,
        batch=tham_so.batch,
        patience=tham_so.patience,
        device=tham_so.device,
        name=tham_so.ten,
        # Tăng cường dữ liệu: giúp mô hình chịu được ảnh chụp nghiêng, thiếu sáng
        hsv_h=0.015, hsv_s=0.7, hsv_v=0.4,
        degrees=10.0, translate=0.1, scale=0.5, fliplr=0.5,
        mosaic=1.0, mixup=0.1,
    )

    # Chép mô hình tốt nhất ra models/best.pt để app.py dùng được ngay
    thu_muc_luu = getattr(ket_qua, "save_dir", None)
    if thu_muc_luu:
        nguon = os.path.join(str(thu_muc_luu), "weights", "best.pt")
        if os.path.isfile(nguon):
            os.makedirs("models", exist_ok=True)
            dich = os.path.join("models", "best.pt")
            shutil.copy2(nguon, dich)
            print(f"\nĐã chép mô hình tốt nhất sang: {dich}")
            print("Mở app.py, chọn mục 'Mô hình tự huấn luyện' để dùng.")
            print("Chạy tiếp 'python evaluate.py' để đo độ chính xác.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
