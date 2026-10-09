# -*- coding: utf-8 -*-
"""
evaluate.py — Đo độ chính xác của mô hình trên tập kiểm thử (validation).

In ra các chỉ số chuẩn của bài toán phát hiện vật thể:
    Precision  - trong những vật mô hình báo, bao nhiêu phần trăm là đúng
    Recall     - trong những vật thật sự có, mô hình tìm ra được bao nhiêu phần trăm
    mAP@50     - độ chính xác trung bình khi khung dự đoán trùng khung thật từ 50%
    mAP@50-95  - chỉ số nghiêm khắc nhất, trung bình trên nhiều mức trùng khớp

Chạy:
    python evaluate.py                                   # đo mô hình tự huấn luyện
    python evaluate.py --model yolov8m.pt                # đo mô hình gốc để so sánh
    python evaluate.py --model models/best.pt --csv kq.csv
"""

from __future__ import annotations

import argparse
import csv
import os


def main() -> int:
    bo_doc = argparse.ArgumentParser(
        description="Đánh giá độ chính xác mô hình nhận diện đồ nội thất",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    bo_doc.add_argument("--model", default=os.path.join("models", "best.pt"), help="mô hình cần đo")
    bo_doc.add_argument("--data", default=os.path.join("data", "furniture.yaml"),
                        help="tệp cấu hình bộ dữ liệu")
    bo_doc.add_argument("--imgsz", type=int, default=640)
    bo_doc.add_argument("--conf", type=float, default=0.001,
                        help="ngưỡng tin cậy khi đo (để thấp để tính đúng mAP)")
    bo_doc.add_argument("--csv", default="ket_qua_danh_gia.csv", help="tệp CSV ghi kết quả")
    tham_so = bo_doc.parse_args()

    for tep, mo_ta in ((tham_so.model, "mô hình"), (tham_so.data, "tệp cấu hình dữ liệu")):
        if not os.path.isfile(tep):
            print(f"Lỗi: không tìm thấy {mo_ta} '{tep}'.")
            return 1

    from ultralytics import YOLO

    model = YOLO(tham_so.model)
    kq = model.val(data=tham_so.data, imgsz=tham_so.imgsz, conf=tham_so.conf, verbose=False)

    hop = kq.box
    print("\n" + "=" * 62)
    print(f"  KẾT QUẢ ĐÁNH GIÁ — {tham_so.model}")
    print("=" * 62)
    print(f"  Precision (độ chuẩn xác)      : {hop.mp:.4f}")
    print(f"  Recall    (độ bao phủ)        : {hop.mr:.4f}")
    print(f"  mAP@50                        : {hop.map50:.4f}")
    print(f"  mAP@50-95                     : {hop.map:.4f}")

    print("\n  Chi tiết theo từng lớp:")
    print(f"  {'Lớp':<22}{'Precision':>11}{'Recall':>10}{'mAP@50':>10}")
    print("  " + "-" * 53)
    cac_dong = []
    ten_lop = model.names
    for i, chi_so_lop in enumerate(getattr(kq, "ap_class_index", [])):
        ten = ten_lop[int(chi_so_lop)]
        p, r, ap50 = hop.p[i], hop.r[i], hop.ap50[i]
        print(f"  {ten:<22}{p:>11.4f}{r:>10.4f}{ap50:>10.4f}")
        cac_dong.append({"lop": ten, "precision": f"{p:.4f}",
                         "recall": f"{r:.4f}", "map50": f"{ap50:.4f}"})

    cac_dong.append({"lop": "TỔNG (trung bình)", "precision": f"{hop.mp:.4f}",
                     "recall": f"{hop.mr:.4f}", "map50": f"{hop.map50:.4f}"})
    with open(tham_so.csv, "w", newline="", encoding="utf-8-sig") as tep:
        bo_ghi = csv.DictWriter(tep, fieldnames=["lop", "precision", "recall", "map50"])
        bo_ghi.writeheader()
        bo_ghi.writerows(cac_dong)
    print(f"\n  Đã ghi bảng kết quả ra: {tham_so.csv}")
    print("  Chép bảng này vào báo cáo, kèm so sánh trước / sau khi huấn luyện.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
