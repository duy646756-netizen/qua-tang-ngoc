# -*- coding: utf-8 -*-
"""
nhan_dien.py — Phần lõi của phần mềm NHẬN DIỆN ĐỒ NỘI THẤT.

Tách riêng khỏi giao diện để app.py, detect_image.py và evaluate.py dùng chung
một bộ mã, đồng thời kiểm thử được phần xử lý mà không cần mở cửa sổ.

Điểm quan trọng: chương trình CHỈ nhận diện đồ nội thất. Việc lọc được làm hai
lớp — lọc ngay khi gọi mô hình (tham số classes) và lọc lại theo tên lớp sau khi
có kết quả — nên không có vật thể nào ngoài danh mục lọt ra ngoài.
"""

from __future__ import annotations

import os
import time
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ============================================================================
# 1. DANH MỤC ĐỒ NỘI THẤT
# ============================================================================
# Khoá là tên lớp của mô hình (viết thường). Giá trị là tên tiếng Việt.
# Gộp cả tên của hai bộ dữ liệu:
#   * COCO            - 80 lớp, nhận diện rất chính xác nhưng KHÔNG có tủ, kệ,
#                       bàn làm việc, ngăn kéo…
#   * Open Images V7  - 601 lớp, có đầy đủ tủ quần áo, tủ bếp, kệ sách, ngăn kéo,
#                       bàn trà, bàn làm việc, tủ đầu giường…

# --- Nhóm 1: ĐỒ NỘI THẤT (luôn luôn nhận diện) ---------------------------
NHOM_NOI_THAT: Dict[str, str] = {
    # Bàn
    "table": "bàn",
    "desk": "bàn làm việc",
    "coffee table": "bàn trà",
    "kitchen & dining room table": "bàn ăn",
    "dining table": "bàn ăn",
    # Ghế
    "chair": "ghế",
    "stool": "ghế đẩu",
    "bench": "ghế băng",
    "couch": "ghế sofa",
    "loveseat": "ghế sofa đôi",
    "studio couch": "ghế sofa dài",
    "sofa bed": "ghế sofa giường",
    # Giường
    "bed": "giường",
    "infant bed": "giường cũi em bé",
    # Tủ
    "wardrobe": "tủ quần áo",
    "cabinetry": "tủ",
    "cupboard": "tủ",
    "bathroom cabinet": "tủ phòng tắm",
    "chest of drawers": "tủ ngăn kéo",
    "filing cabinet": "tủ hồ sơ",
    "nightstand": "tủ đầu giường",
    "drawer": "ngăn kéo",
    # Kệ
    "shelf": "kệ",
    "bookcase": "kệ sách",
    "wine rack": "kệ rượu",
}

# --- Nhóm 2: THIẾT BỊ VÀ ĐỒ TRANG TRÍ (tuỳ chọn, mặc định TẮT) -----------
NHOM_THIET_BI: Dict[str, str] = {
    "television": "tivi",
    "tv": "tivi",
    "refrigerator": "tủ lạnh",
    "oven": "lò nướng",
    "microwave oven": "lò vi sóng",
    "microwave": "lò vi sóng",
    "toaster": "máy nướng bánh mì",
    "sink": "bồn rửa",
    "toilet": "bồn cầu",
    "bathtub": "bồn tắm",
    "lamp": "đèn",
    "mirror": "gương",
    "curtain": "rèm cửa",
    "pillow": "gối",
    "vase": "bình hoa",
    "houseplant": "chậu cây",
    "potted plant": "chậu cây",
    "clock": "đồng hồ",
    "wall clock": "đồng hồ treo tường",
    "alarm clock": "đồng hồ báo thức",
    "ceiling fan": "quạt trần",
    "mechanical fan": "quạt",
}

# Lớp "Furniture" của Open Images là lớp cha chung chung, bật lên sẽ vẽ chồng
# khung lên mọi món đồ nên cố ý KHÔNG đưa vào danh mục.


def bang_ten(kem_thiet_bi: bool = False) -> Dict[str, str]:
    """Danh mục đang áp dụng, tuỳ theo có kèm nhóm thiết bị/trang trí hay không."""
    bang = dict(NHOM_NOI_THAT)
    if kem_thiet_bi:
        bang.update(NHOM_THIET_BI)
    return bang


def ten_viet(ten_lop: str, kem_thiet_bi: bool = True) -> Optional[str]:
    """Trả về tên tiếng Việt, hoặc None nếu lớp đó không thuộc danh mục nội thất."""
    return bang_ten(kem_thiet_bi).get(ten_lop.strip().lower())


# ============================================================================
# 2. BẢNG MÀU
# ============================================================================
# Màu được chọn sẵn cho dễ nhìn và tương phản tốt với nền ảnh, thay vì sinh màu
# ngẫu nhiên. Mỗi tên vật thể luôn nhận đúng một màu cố định.
BANG_MAU: Sequence[tuple] = (
    (239, 68, 68), (59, 130, 246), (16, 185, 129), (245, 158, 11),
    (168, 85, 247), (236, 72, 153), (20, 184, 166), (249, 115, 22),
    (99, 102, 241), (132, 204, 22), (6, 182, 212), (217, 70, 239),
    (234, 179, 8), (14, 165, 233), (34, 197, 94), (244, 63, 94),
)


def mau_cua(ten: str) -> tuple:
    """Màu cố định cho một tên vật thể (cùng tên thì luôn cùng màu)."""
    tong = sum((i + 1) * ord(c) for i, c in enumerate(ten))
    return BANG_MAU[tong % len(BANG_MAU)]


# ============================================================================
# 3. PHÔNG CHỮ HỖ TRỢ TIẾNG VIỆT
# ============================================================================
CAC_PHONG_UNG_VIEN = (
    "C:/Windows/Fonts/segoeuib.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
)

_bo_nho_phong: dict = {}


def _tim_tep_phong() -> Optional[str]:
    for duong_dan in CAC_PHONG_UNG_VIEN:
        if os.path.isfile(duong_dan):
            return duong_dan
    return None


TEP_PHONG = _tim_tep_phong()


def lay_phong(co_chu: int):
    """Phông chữ theo cỡ, có nhớ đệm để không mở lại tệp mỗi lần vẽ."""
    if co_chu not in _bo_nho_phong:
        try:
            _bo_nho_phong[co_chu] = (
                ImageFont.truetype(TEP_PHONG, co_chu) if TEP_PHONG else ImageFont.load_default()
            )
        except Exception:
            _bo_nho_phong[co_chu] = ImageFont.load_default()
    return _bo_nho_phong[co_chu]


def co_chu_theo_anh(rong: int, cao: int) -> int:
    """Cỡ chữ tính theo cạnh lớn của ảnh, để nhãn không quá to cũng không quá bé."""
    return int(min(44, max(15, max(rong, cao) / 42)))


# ============================================================================
# 4. ĐỌC ẢNH AN TOÀN
# ============================================================================
def doc_anh(duong_dan: str) -> np.ndarray:
    """Đọc ảnh thành mảng BGR.

    Dùng np.fromfile + cv2.imdecode thay cho cv2.imread để mở được cả đường dẫn
    có dấu tiếng Việt trên Windows (cv2.imread thường trả về None trong trường
    hợp này).
    """
    if not os.path.isfile(duong_dan):
        raise FileNotFoundError(f"Không tìm thấy tệp ảnh:\n{duong_dan}")
    du_lieu = np.fromfile(duong_dan, dtype=np.uint8)
    if du_lieu.size == 0:
        raise ValueError(f"Tệp rỗng: {os.path.basename(duong_dan)}")
    anh = cv2.imdecode(du_lieu, cv2.IMREAD_COLOR)
    if anh is None:
        raise ValueError(
            f"Không đọc được ảnh «{os.path.basename(duong_dan)}».\n"
            "Tệp có thể bị hỏng hoặc không phải định dạng ảnh được hỗ trợ."
        )
    return anh


# ----------------------------------------------------------------------------
# Thêm viền quanh ảnh
# ----------------------------------------------------------------------------
# Ảnh chụp sản phẩm (tủ, bàn, ghế trên nền trơn) thường chiếm trọn khung hình.
# Mô hình lại được huấn luyện trên ảnh cảnh thật, nơi mỗi món chỉ chiếm một phần
# khung, nên gặp ảnh sản phẩm là nó lúng túng. Thêm một viền quanh ảnh để món đồ
# chỉ còn chiếm phần giữa khung giúp mô hình nhận ra tốt hơn hẳn.
#
# Đo trên ba ảnh sản phẩm thật (tủ quần áo, ghế sofa, bàn làm việc):
#   tủ quần áo  : không nhận ra gì  ->  tủ quần áo 48 %
#   bàn làm việc: không nhận ra gì  ->  tủ ngăn kéo 57 %
#   ghế sofa    : ghế sofa 88 %     ->  ghế sofa 95 %
# Hai mức viền: mức 25 % đủ cho phần lớn ảnh, thêm mức 50 % giúp gọi đúng tên
# những món bị chụp quá sát (ảnh tủ quần áo: "tủ chén 44 %" -> "tủ quần áo 48 %").
CAC_TI_LE_VIEN = (0.25, 0.50)


def them_vien(anh_bgr: np.ndarray, ti_le: float = 0.25):
    """Thêm viền quanh ảnh, lấy màu nền ở bốn góc cho tự nhiên.

    Trả về (ảnh mới, độ lệch x, độ lệch y) để quy toạ độ khung về ảnh gốc.
    """
    cao, rong = anh_bgr.shape[:2]
    day = int(max(cao, rong) * ti_le)
    if day <= 0:
        return anh_bgr, 0, 0
    o = max(2, min(cao, rong) // 40)
    bon_goc = np.concatenate([
        anh_bgr[:o, :o].reshape(-1, 3), anh_bgr[:o, -o:].reshape(-1, 3),
        anh_bgr[-o:, :o].reshape(-1, 3), anh_bgr[-o:, -o:].reshape(-1, 3),
    ])
    mau = [int(v) for v in np.median(bon_goc, axis=0)]
    anh_moi = cv2.copyMakeBorder(anh_bgr, day, day, day, day,
                                 cv2.BORDER_CONSTANT, value=mau)
    return anh_moi, day, day


# ============================================================================
# 5. KẾT QUẢ
# ============================================================================
@dataclass
class VatThe:
    ten_vi: str
    ten_en: str
    do_tin_cay: float
    hop: tuple            # (x1, y1, x2, y2)
    nguon: str = ""       # mô hình nào tìm ra

    @property
    def dien_tich(self) -> int:
        x1, y1, x2, y2 = self.hop
        return max(0, x2 - x1) * max(0, y2 - y1)

    @property
    def mau(self) -> tuple:
        return mau_cua(self.ten_vi)


@dataclass
class KetQua:
    anh_bgr: np.ndarray                       # ảnh gốc, chưa vẽ gì
    danh_sach: List[VatThe] = field(default_factory=list)
    giay_xu_ly: float = 0.0
    ten_tep: str = ""

    @property
    def thong_ke(self) -> Counter:
        return Counter(v.ten_vi for v in self.danh_sach)

    @property
    def do_tin_cay_tb(self) -> float:
        if not self.danh_sach:
            return 0.0
        return sum(v.do_tin_cay for v in self.danh_sach) / len(self.danh_sach)

    def tom_tat(self) -> str:
        if not self.danh_sach:
            return "Không tìm thấy đồ nội thất nào trong ảnh."
        phan = [f"{t} x{s}" if s > 1 else t for t, s in self.thong_ke.most_common()]
        return f"Tìm thấy {len(self.danh_sach)} món: " + ", ".join(phan)

    def ve(self, nhan_manh: Optional[int] = None) -> Image.Image:
        """Vẽ kết quả lên ảnh. nhan_manh là chỉ số vật thể cần làm nổi bật."""
        return ve_ket_qua(self.anh_bgr, self.danh_sach, nhan_manh)


# ============================================================================
# 6. VẼ KẾT QUẢ
# ============================================================================
def ve_ket_qua(anh_bgr: np.ndarray, danh_sach: List[VatThe],
               nhan_manh: Optional[int] = None) -> Image.Image:
    """Vẽ khung và nhãn tiếng Việt lên ảnh.

    Dùng PIL chứ không dùng cv2.putText vì cv2.putText không in được chữ có dấu.
    Khung được tô màu mờ bên trong, nhãn nằm trong một ô bo góc để dễ đọc trên
    mọi nền ảnh.
    """
    nen = Image.fromarray(cv2.cvtColor(anh_bgr, cv2.COLOR_BGR2RGB)).convert("RGBA")
    rong, cao = nen.size

    lop_ve = Image.new("RGBA", nen.size, (0, 0, 0, 0))
    ve = ImageDraw.Draw(lop_ve)

    co_chu = co_chu_theo_anh(rong, cao)
    phong = lay_phong(co_chu)
    day_vien = max(2, round(max(rong, cao) / 420))
    dem = max(4, co_chu // 4)

    for i, vat in enumerate(danh_sach):
        x1, y1, x2, y2 = vat.hop
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(rong, x2), min(cao, y2)
        if x2 <= x1 or y2 <= y1:
            continue

        noi_bat = (nhan_manh is None) or (i == nhan_manh)
        mau = vat.mau
        do_dam = 255 if noi_bat else 90
        ve.rectangle([x1, y1, x2, y2], fill=mau + (54 if noi_bat else 18,))
        ve.rectangle([x1, y1, x2, y2], outline=mau + (do_dam,),
                     width=day_vien * (2 if (nhan_manh is not None and noi_bat) else 1))

        if not noi_bat:
            continue

        nhan = f"{vat.ten_vi}  {vat.do_tin_cay:.0%}"
        khung = ve.textbbox((0, 0), nhan, font=phong)
        rong_chu, cao_chu = khung[2] - khung[0], khung[3] - khung[1]
        rong_o, cao_o = rong_chu + 2 * dem, cao_chu + 2 * dem

        # Nhãn nằm trên khung; chạm mép trên thì lật xuống, chạm mép phải thì dịch vào
        y_o = y1 - cao_o - 2 if y1 - cao_o - 2 >= 0 else y1 + 2
        x_o = min(x1, max(0, rong - rong_o))

        ve.rounded_rectangle([x_o, y_o, x_o + rong_o, y_o + cao_o],
                             radius=max(3, dem // 2), fill=mau + (235,))
        ve.text((x_o + dem - khung[0], y_o + dem - khung[1]), nhan,
                font=phong, fill=(255, 255, 255, 255))

    return Image.alpha_composite(nen, lop_ve).convert("RGB")


# ============================================================================
# 7. BỘ NHẬN DIỆN
# ============================================================================
# Mỗi chế độ là một danh sách mô hình sẽ chạy. Chế độ "ket_hop" chạy cả hai rồi
# gộp kết quả, cho số món tìm được nhiều nhất.
CHE_DO = {
    "oiv7": {
        "ten": "Đầy đủ đồ nội thất (Open Images V7)",
        "mo_ta": "Nhận được tủ quần áo, tủ bếp, kệ sách, ngăn kéo, bàn làm việc…",
        "models": ["yolov8m-oiv7.pt"],
    },
    "coco": {
        "ten": "Chính xác cao (COCO)",
        "mo_ta": "Rất chắc chắn với ghế, sofa, giường, bàn ăn — nhưng không biết tủ, kệ.",
        "models": ["yolov8m.pt"],
    },
    "ket_hop": {
        "ten": "Kết hợp cả hai (tốt nhất, chậm hơn)",
        "mo_ta": "Chạy lần lượt hai mô hình rồi gộp kết quả, tìm được nhiều món nhất.",
        "models": ["yolov8m-oiv7.pt", "yolov8m.pt"],
    },
    "tu_huan_luyen": {
        "ten": "Mô hình tự huấn luyện (models/best.pt)",
        "mo_ta": "Dùng sau khi đã chạy train.py trên bộ ảnh riêng.",
        "models": [os.path.join("models", "best.pt")],
    },
}
CHE_DO_MAC_DINH = "oiv7"


def _iou(a: tuple, b: tuple) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    x1, y1 = max(ax1, bx1), max(ay1, by1)
    x2, y2 = min(ax2, bx2), min(ay2, by2)
    giao = max(0, x2 - x1) * max(0, y2 - y1)
    if giao == 0:
        return 0.0
    dt_a = max(0, ax2 - ax1) * max(0, ay2 - ay1)
    dt_b = max(0, bx2 - bx1) * max(0, by2 - by1)
    return giao / float(dt_a + dt_b - giao)


def gop_trung_lap(danh_sach: List[VatThe]) -> List[VatThe]:
    """Bỏ các khung chỉ cùng một món đồ nhưng bị hai mô hình cùng tìm ra.

    Cùng tên  -> trùng nhau trên 50 % thì bỏ cái có độ tin cậy thấp hơn.
    Khác tên  -> phải trùng trên 80 % mới bỏ (ví dụ "bàn" và "bàn ăn").
    """
    con_lai: List[VatThe] = []
    for vat in sorted(danh_sach, key=lambda v: v.do_tin_cay, reverse=True):
        trung = False
        for da_giu in con_lai:
            nguong = 0.5 if da_giu.ten_vi == vat.ten_vi else 0.8
            if _iou(da_giu.hop, vat.hop) > nguong:
                trung = True
                break
        if not trung:
            con_lai.append(vat)
    return con_lai


class BoNhanDien:
    """Bọc một hoặc hai mô hình YOLO lại cho gọn. Mô hình chỉ nạp khi cần dùng."""

    def __init__(self, che_do: str = CHE_DO_MAC_DINH):
        self.che_do = che_do if che_do in CHE_DO else CHE_DO_MAC_DINH
        self._kho_model: dict = {}

    # ---- nạp mô hình ----
    def _lay_model(self, ten_tep: str):
        if ten_tep not in self._kho_model:
            from ultralytics import YOLO          # nhập muộn cho app mở nhanh
            self._kho_model[ten_tep] = YOLO(ten_tep)
        return self._kho_model[ten_tep]

    def doi_che_do(self, che_do: str) -> None:
        if che_do in CHE_DO:
            self.che_do = che_do

    def nap_truoc(self) -> None:
        """Nạp sẵn mô hình của chế độ hiện tại (dùng để hiện thông báo chờ)."""
        for ten_tep in CHE_DO[self.che_do]["models"]:
            self._lay_model(ten_tep)

    @staticmethod
    def _ids_noi_that(ten_lop: dict, bang: Dict[str, str]) -> Optional[List[int]]:
        """Tìm chỉ số các lớp thuộc danh mục nội thất trong một mô hình cụ thể.

        Lọc theo TÊN chứ không theo số thứ tự, nhờ vậy dùng được cho cả mô hình
        COCO (80 lớp), Open Images V7 (601 lớp) lẫn mô hình tự huấn luyện.
        """
        ids = [i for i, ten in ten_lop.items() if str(ten).strip().lower() in bang]
        return ids or None

    # ---- nhận diện ----
    def nhan_dien(
        self,
        duong_dan_anh: str,
        nguong_tin_cay: float = 0.40,
        kem_thiet_bi: bool = False,
        co_anh: int = 640,
        dung_tta: bool = False,
        them_vien_phu: bool = True,
    ) -> KetQua:
        bat_dau = time.perf_counter()
        anh_bgr = doc_anh(duong_dan_anh)
        bang = bang_ten(kem_thiet_bi)
        cao_goc, rong_goc = anh_bgr.shape[:2]

        # Mỗi lượt là một phiên bản của ảnh kèm độ lệch toạ độ của nó
        cac_luot = [(anh_bgr, 0, 0)]
        if them_vien_phu:
            cac_luot += [them_vien(anh_bgr, t) for t in CAC_TI_LE_VIEN]

        tat_ca: List[VatThe] = []
        for ten_tep in CHE_DO[self.che_do]["models"]:
            model = self._lay_model(ten_tep)
            ten_lop = model.names
            ids = self._ids_noi_that(ten_lop, bang)

            for anh_vao, lech_x, lech_y in cac_luot:
                ket_qua = model.predict(
                    source=anh_vao,
                    classes=ids,
                    conf=nguong_tin_cay,
                    iou=0.45,
                    imgsz=co_anh,
                    augment=dung_tta,
                    verbose=False,
                )[0]

                for hop in ket_qua.boxes:
                    ten_en = str(ten_lop[int(hop.cls[0])])
                    ten_vi = bang.get(ten_en.strip().lower())
                    if ten_vi is None:
                        continue          # lớp lọc thứ hai: không để lọt vật lạ
                    x1, y1, x2, y2 = (int(v) for v in hop.xyxy[0])
                    # Quy toạ độ về ảnh gốc rồi cắt cho nằm trong ảnh
                    x1, x2 = x1 - lech_x, x2 - lech_x
                    y1, y2 = y1 - lech_y, y2 - lech_y
                    dt_truoc = max(1, (x2 - x1) * (y2 - y1))
                    x1, y1 = max(0, x1), max(0, y1)
                    x2, y2 = min(rong_goc, x2), min(cao_goc, y2)
                    if x2 <= x1 or y2 <= y1:
                        continue
                    # Bỏ khung nằm chủ yếu ngoài ảnh gốc (do phần viền sinh ra)
                    if (x2 - x1) * (y2 - y1) < 0.5 * dt_truoc:
                        continue
                    tat_ca.append(
                        VatThe(
                            ten_vi=ten_vi,
                            ten_en=ten_en,
                            do_tin_cay=float(hop.conf[0]),
                            hop=(x1, y1, x2, y2),
                            nguon=os.path.basename(ten_tep),
                        )
                    )

        danh_sach = gop_trung_lap(tat_ca)
        danh_sach.sort(key=lambda v: v.do_tin_cay, reverse=True)

        return KetQua(
            anh_bgr=anh_bgr,
            danh_sach=danh_sach,
            giay_xu_ly=time.perf_counter() - bat_dau,
            ten_tep=os.path.basename(duong_dan_anh),
        )
