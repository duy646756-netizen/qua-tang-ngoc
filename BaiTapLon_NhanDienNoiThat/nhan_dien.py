# -*- coding: utf-8 -*-
"""
nhan_dien.py — Phần lõi của chương trình nhận diện đồ nội thất.

Tách riêng khỏi giao diện để:
  * app.py (giao diện Tkinter), detect_image.py (dòng lệnh) và evaluate.py
    dùng chung một bộ mã, không viết trùng;
  * có thể kiểm thử phần lõi mà không cần mở cửa sổ.
"""

from __future__ import annotations

import os
from collections import Counter
from dataclasses import dataclass, field
from typing import List, Optional

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ============================================================================
# 1. DANH MỤC ĐỒ NỘI THẤT
# ============================================================================
# ID lớp theo bộ dữ liệu COCO mà mô hình YOLO được huấn luyện sẵn.
# Chỉ giữ lại những lớp thuộc nhóm đồ đạc trong nhà.
CLASS_NOI_THAT: List[int] = [
    13,  # bench         - ghế băng
    56,  # chair         - ghế
    57,  # couch         - ghế sofa
    58,  # potted plant  - chậu cây
    59,  # bed           - giường
    60,  # dining table  - bàn ăn
    61,  # toilet        - bồn cầu
    62,  # tv            - tivi
    68,  # microwave     - lò vi sóng
    69,  # oven          - lò nướng
    70,  # toaster       - máy nướng bánh mì
    71,  # sink          - bồn rửa
    72,  # refrigerator  - tủ lạnh
    73,  # book          - sách
    74,  # clock         - đồng hồ
    75,  # vase          - bình hoa
]

TEN_TIENG_VIET = {
    "bench": "ghế băng",
    "chair": "ghế",
    "couch": "ghế sofa",
    "potted plant": "chậu cây",
    "bed": "giường",
    "dining table": "bàn ăn",
    "toilet": "bồn cầu",
    "tv": "tivi",
    "microwave": "lò vi sóng",
    "oven": "lò nướng",
    "toaster": "máy nướng bánh mì",
    "sink": "bồn rửa",
    "refrigerator": "tủ lạnh",
    "book": "sách",
    "clock": "đồng hồ",
    "vase": "bình hoa",
    # Các lớp tự huấn luyện thêm (nếu có) đặt tiếp ở đây
    "wardrobe": "tủ quần áo",
    "desk": "bàn làm việc",
    "lamp": "đèn",
    "shelf": "kệ",
    "mirror": "gương",
    "curtain": "rèm cửa",
    "carpet": "thảm",
}


def dich_nhan(ten_tieng_anh: str) -> str:
    """Dịch tên lớp sang tiếng Việt; không có trong từ điển thì giữ nguyên."""
    return TEN_TIENG_VIET.get(ten_tieng_anh.lower(), ten_tieng_anh)


# ============================================================================
# 2. PHÔNG CHỮ HỖ TRỢ TIẾNG VIỆT
# ============================================================================
# LỖI CŨ: chỉ trỏ cứng vào "C:/Windows/Fonts/arial.ttf"; máy khác không có thì
# rơi về ImageFont.load_default() — phông này KHÔNG vẽ được dấu tiếng Việt.
# CÁCH SỬA: dò lần lượt các phông Unicode thông dụng của Windows / macOS / Linux.
CAC_PHONG_UNG_VIEN = [
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/segoeui.ttf",
    "C:/Windows/Fonts/tahoma.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
]

_bo_nho_phong: dict = {}       # cache theo cỡ chữ, tránh mở lại tệp phông mỗi lần vẽ


def _tim_tep_phong() -> Optional[str]:
    for duong_dan in CAC_PHONG_UNG_VIEN:
        if os.path.isfile(duong_dan):
            return duong_dan
    return None


TEP_PHONG = _tim_tep_phong()


def lay_phong(co_chu: int) -> ImageFont.ImageFont:
    """Trả về phông chữ theo cỡ, có nhớ đệm. Không tìm được phông Unicode nào
    thì dùng phông mặc định (chấp nhận mất dấu) để chương trình vẫn chạy."""
    if co_chu in _bo_nho_phong:
        return _bo_nho_phong[co_chu]
    try:
        phong = ImageFont.truetype(TEP_PHONG, co_chu) if TEP_PHONG else ImageFont.load_default()
    except Exception:
        phong = ImageFont.load_default()
    _bo_nho_phong[co_chu] = phong
    return phong


def co_chu_theo_anh(chieu_rong: int, chieu_cao: int) -> int:
    """LỖI CŨ: cỡ chữ cố định 28px nên ảnh lớn thì chữ li ti, ảnh nhỏ thì chữ
    che kín vật thể. CÁCH SỬA: tính cỡ chữ theo cạnh lớn của ảnh."""
    canh_lon = max(chieu_rong, chieu_cao)
    return int(min(48, max(14, canh_lon / 38)))


def mau_theo_class(cls_id: int) -> tuple:
    """Sinh màu RGB riêng, cố định cho từng lớp (dùng tỉ lệ vàng để màu tản đều)."""
    import colorsys
    hue = (cls_id * 0.61803398875) % 1.0
    r, g, b = colorsys.hsv_to_rgb(hue, 0.85, 0.95)
    return (int(r * 255), int(g * 255), int(b * 255))


# ============================================================================
# 3. ĐỌC ẢNH AN TOÀN
# ============================================================================
def doc_anh(duong_dan: str) -> np.ndarray:
    """Đọc ảnh trả về mảng BGR.

    Dùng np.fromfile + cv2.imdecode thay cho cv2.imread để đọc được cả đường dẫn
    có dấu tiếng Việt hoặc khoảng trắng trên Windows (cv2.imread hay trả về None
    trong những trường hợp này).
    """
    if not os.path.isfile(duong_dan):
        raise FileNotFoundError(f"Không tìm thấy tệp ảnh: {duong_dan}")
    try:
        du_lieu = np.fromfile(duong_dan, dtype=np.uint8)
    except OSError as loi:
        raise OSError(f"Không đọc được tệp: {duong_dan}") from loi
    if du_lieu.size == 0:
        raise ValueError(f"Tệp rỗng: {duong_dan}")
    anh = cv2.imdecode(du_lieu, cv2.IMREAD_COLOR)
    if anh is None:
        raise ValueError(
            f"Tệp không phải ảnh hợp lệ hoặc định dạng không hỗ trợ: {os.path.basename(duong_dan)}"
        )
    return anh


# ============================================================================
# 4. KẾT QUẢ NHẬN DIỆN
# ============================================================================
@dataclass
class VatThe:
    ten_en: str
    ten_vi: str
    do_tin_cay: float
    hop: tuple          # (x1, y1, x2, y2)
    cls_id: int


@dataclass
class KetQua:
    anh_da_ve: Image.Image
    danh_sach: List[VatThe] = field(default_factory=list)

    @property
    def thong_ke(self) -> Counter:
        """Đếm số lượng theo từng loại đồ vật."""
        return Counter(v.ten_vi for v in self.danh_sach)

    def tom_tat(self) -> str:
        if not self.danh_sach:
            return "Không phát hiện đồ nội thất nào trong ảnh."
        phan = [f"{ten} x{sl}" if sl > 1 else ten for ten, sl in self.thong_ke.most_common()]
        return f"Phát hiện {len(self.danh_sach)} vật thể: " + ", ".join(phan)


# ============================================================================
# 5. VẼ KHUNG VÀ NHÃN TIẾNG VIỆT
# ============================================================================
def ve_ket_qua(anh_bgr: np.ndarray, danh_sach: List[VatThe]) -> Image.Image:
    """Vẽ khung chữ nhật và nhãn tiếng Việt lên ảnh bằng PIL.

    Dùng PIL chứ không dùng cv2.putText vì cv2.putText không in được chữ có dấu.
    """
    anh_pil = Image.fromarray(cv2.cvtColor(anh_bgr, cv2.COLOR_BGR2RGB))
    ve = ImageDraw.Draw(anh_pil)

    rong, cao = anh_pil.size
    co_chu = co_chu_theo_anh(rong, cao)
    phong = lay_phong(co_chu)
    do_day_vien = max(2, round(max(rong, cao) / 500))
    dem = max(3, co_chu // 5)

    for vat in danh_sach:
        x1, y1, x2, y2 = vat.hop
        mau = mau_theo_class(vat.cls_id)
        nhan = f"{vat.ten_vi} {vat.do_tin_cay:.0%}"

        ve.rectangle([x1, y1, x2, y2], outline=mau, width=do_day_vien)

        khung_chu = ve.textbbox((0, 0), nhan, font=phong)
        rong_chu = khung_chu[2] - khung_chu[0]
        cao_chu = khung_chu[3] - khung_chu[1]

        # Nhãn mặc định nằm phía trên khung; nếu chạm mép trên thì lật xuống dưới
        if y1 - cao_chu - 2 * dem >= 0:
            y_nen = y1 - cao_chu - 2 * dem
        else:
            y_nen = y1
        # Không để nhãn tràn ra khỏi mép phải
        x_nen = min(x1, max(0, rong - rong_chu - 2 * dem))

        ve.rectangle(
            [x_nen, y_nen, x_nen + rong_chu + 2 * dem, y_nen + cao_chu + 2 * dem],
            fill=mau,
        )
        ve.text((x_nen + dem, y_nen + dem - khung_chu[1]), nhan, font=phong, fill=(255, 255, 255))

    return anh_pil


# ============================================================================
# 6. BỘ NHẬN DIỆN
# ============================================================================
class BoNhanDien:
    """Bọc mô hình YOLO lại cho gọn. Mô hình chỉ được nạp khi dùng lần đầu."""

    def __init__(self, ten_model: str = "yolov8m.pt"):
        self.ten_model = ten_model
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from ultralytics import YOLO      # nhập muộn để mở app nhanh hơn
            self._model = YOLO(self.ten_model)
        return self._model

    def doi_model(self, ten_model: str) -> None:
        if ten_model != self.ten_model:
            self.ten_model = ten_model
            self._model = None

    @property
    def danh_sach_lop(self) -> dict:
        return self.model.names

    def _loc_lop(self) -> Optional[List[int]]:
        """Chỉ lọc theo danh sách COCO khi mô hình đúng là mô hình 80 lớp của COCO.
        Mô hình tự huấn luyện có bộ lớp riêng nên không áp dụng bộ lọc này."""
        ten = self.danh_sach_lop
        if len(ten) == 80 and ten.get(56) == "chair":
            return CLASS_NOI_THAT
        return None

    def nhan_dien(
        self,
        duong_dan_anh: str,
        nguong_tin_cay: float = 0.5,
        nguong_iou: float = 0.45,
        co_anh: int = 960,
        dung_tta: bool = False,
    ) -> KetQua:
        """Nhận diện đồ nội thất trong một ảnh.

        nguong_tin_cay : chỉ giữ vật thể có độ tin cậy từ mức này trở lên
        nguong_iou     : ngưỡng gộp các khung trùng nhau (NMS)
        co_anh         : kích thước đưa vào mạng; lớn hơn = bắt vật nhỏ tốt hơn
        dung_tta       : bật tăng cường lúc dự đoán, chính xác hơn nhưng chậm hơn
        """
        anh_bgr = doc_anh(duong_dan_anh)

        ket_qua_yolo = self.model.predict(
            source=anh_bgr,
            classes=self._loc_lop(),
            conf=nguong_tin_cay,
            iou=nguong_iou,
            imgsz=co_anh,
            augment=dung_tta,
            verbose=False,
        )[0]

        danh_sach: List[VatThe] = []
        ten_lop = self.danh_sach_lop
        for hop in ket_qua_yolo.boxes:
            cls_id = int(hop.cls[0])
            ten_en = ten_lop[cls_id]
            danh_sach.append(
                VatThe(
                    ten_en=ten_en,
                    ten_vi=dich_nhan(ten_en),
                    do_tin_cay=float(hop.conf[0]),
                    hop=tuple(int(v) for v in hop.xyxy[0]),
                    cls_id=cls_id,
                )
            )

        # Sắp xếp theo độ tin cậy giảm dần cho dễ đọc
        danh_sach.sort(key=lambda v: v.do_tin_cay, reverse=True)

        return KetQua(anh_da_ve=ve_ket_qua(anh_bgr, danh_sach), danh_sach=danh_sach)
