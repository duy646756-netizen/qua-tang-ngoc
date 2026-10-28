# HUẤN LUYỆN MÔ HÌNH RIÊNG BẰNG GOOGLE COLAB (miễn phí, có GPU)

Mô hình đang dùng sẵn nhận đúng phần lớn trường hợp, nhưng vẫn gọi nhầm tên một
số món — ví dụ **bàn làm việc có hộc tủ bị gọi là "tủ ngăn kéo"**. Muốn sửa dứt
điểm thì phải huấn luyện bằng ảnh thật.

Huấn luyện cần **GPU**. Máy tính thường chỉ có CPU, chạy sẽ mất vài ngày.
Google Colab cho dùng GPU miễn phí — làm theo các bước dưới đây mất khoảng
**1–3 tiếng**, trong đó phần lớn là thời gian máy tự chạy.

---

## Bước 1 — Mở Colab và bật GPU

1. Vào `colab.research.google.com` → **New notebook**.
2. Menu **Runtime → Change runtime type → Hardware accelerator: T4 GPU** → **Save**.

## Bước 2 — Cài thư viện

Dán vào ô lệnh đầu tiên rồi bấm chạy:

```python
!pip install -q ultralytics fiftyone
import torch; print("GPU:", torch.cuda.get_device_name(0))
```

Phải in ra tên GPU, ví dụ `Tesla T4`. Không in ra thì quay lại bước 1.

## Bước 3 — Tải ảnh nội thất đã có sẵn nhãn

Bộ **Open Images V7** của Google có sẵn hàng trăm nghìn ảnh nội thất **đã được
gán nhãn**, tải về dùng luôn, không phải ngồi khoanh tay.

```python
import fiftyone as fo
import fiftyone.zoo as foz

LOP = ["Table", "Desk", "Chair", "Couch", "Bed", "Wardrobe", "Cabinetry",
       "Cupboard", "Shelf", "Bookcase", "Drawer", "Chest of drawers",
       "Nightstand", "Stool", "Bench", "Coffee table",
       "Kitchen & dining room table", "Filing cabinet"]

train = foz.load_zoo_dataset("open-images-v7", split="train",
                             label_types=["detections"], classes=LOP,
                             max_samples=6000, dataset_name="nt_train")
val   = foz.load_zoo_dataset("open-images-v7", split="validation",
                             label_types=["detections"], classes=LOP,
                             max_samples=1200, dataset_name="nt_val")

for bo, ten in ((train, "train"), (val, "val")):
    bo.export(export_dir="/content/noi_that", dataset_type=fo.types.YOLOv5Dataset,
              label_field="ground_truth", split=ten, classes=LOP)
print("Xong. Ảnh đã nằm ở /content/noi_that")
```

Bước này tải khoảng 3–6 GB, mất 20–40 phút. **Muốn mô hình giỏi hơn nữa thì
tăng `max_samples`** (ví dụ 15000), đổi lại tải và huấn luyện lâu hơn.

## Bước 4 — Huấn luyện

```python
from ultralytics import YOLO

model = YOLO("yolov8m.pt")          # máy yếu thì đổi thành yolov8s.pt
model.train(
    data="/content/noi_that/dataset.yaml",
    epochs=60, imgsz=640, batch=16, patience=15,
    degrees=10, translate=0.1, scale=0.5, fliplr=0.5, mosaic=1.0,
    name="noi_that",
)
```

Mất khoảng 1–2 tiếng với 6000 ảnh trên GPU T4. **Để tab Colab mở**, không là nó
tự ngắt.

## Bước 5 — Xem kết quả và tải mô hình về

```python
from ultralytics import YOLO
m = YOLO("runs/detect/noi_that/weights/best.pt")
kq = m.val(data="/content/noi_that/dataset.yaml")
print("mAP@50     :", round(kq.box.map50, 4))
print("mAP@50-95  :", round(kq.box.map, 4))
print("Precision  :", round(kq.box.mp, 4))
print("Recall     :", round(kq.box.mr, 4))

from google.colab import files
files.download("runs/detect/noi_that/weights/best.pt")
```

Chép bốn con số này vào báo cáo. **mAP@50 trên 0,70 là khá, trên 0,85 là tốt.**

## Bước 6 — Đưa mô hình vào phần mềm

1. Chép tệp `best.pt` vừa tải về vào thư mục **`models`** của phần mềm.
2. Mở tệp `nhan_dien.py`, tìm dòng:

```python
CHE_DO_MAC_DINH = "oiv7"
```

đổi thành:

```python
CHE_DO_MAC_DINH = "tu_huan_luyen"
```

3. Chạy lại `chay.bat`. Từ giờ phần mềm dùng mô hình bạn tự huấn luyện.

---

## Lưu ý trung thực

- **Không có mô hình nào đúng 100 %.** Kể cả huấn luyện tốt, vẫn sẽ có ảnh bị
  sai — ảnh ngược sáng, món bị che khuất, góc chụp lạ.
- Muốn mô hình giỏi với **ảnh của riêng bạn** (ví dụ ảnh chụp trong cửa hàng của
  bạn) thì cách tốt nhất là chụp và gán nhãn chính ảnh đó, trộn thêm vào bộ dữ
  liệu ở bước 3. Dùng [LabelImg](https://github.com/HumanSignal/labelImg) hoặc
  [Roboflow](https://roboflow.com), xuất ở định dạng YOLO.
- Số ảnh càng nhiều, mô hình càng chắc. 6000 ảnh là mức tối thiểu cho kết quả
  dùng được.
