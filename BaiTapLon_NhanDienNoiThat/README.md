# PHẦN MỀM NHẬN DIỆN ĐỒ NỘI THẤT TRONG ẢNH

Bài tập lớn môn **Xử lý ảnh**. Chương trình nhận vào một tấm ảnh chụp trong nhà,
tự động khoanh vùng và gọi tên từng món đồ nội thất bằng **tiếng Việt**, kèm độ
tin cậy của mỗi dự đoán.

Mô hình sử dụng: **YOLOv8** (Ultralytics). Giao diện: **Tkinter**.

---

## 1. Chức năng

| Chức năng | Mô tả |
|---|---|
| Nhận diện từ ảnh | Chọn ảnh `.jpg .jpeg .png .bmp .webp`, khoanh khung và gán nhãn tiếng Việt |
| Chọn mô hình | 4 mức YOLOv8 (n / s / m / l) + mô hình tự huấn luyện, đổi ngay trong giao diện |
| Chỉnh ngưỡng tin cậy | Thanh trượt 10 % – 95 %, lọc bỏ các dự đoán thiếu chắc chắn |
| Chế độ chính xác cao | Bật tăng cường lúc dự đoán (TTA) để bắt thêm vật khó, đánh đổi tốc độ |
| Bảng kết quả | Liệt kê từng vật thể: tên, độ tin cậy, toạ độ khung |
| Thống kê | Đếm số lượng theo loại, ví dụ *"Phát hiện 7 vật thể: ghế x4, bàn ăn, tivi, chậu cây"* |
| Lưu ảnh kết quả | Ghi ảnh đã vẽ khung ra tệp `.jpg` / `.png` |
| Chạy dòng lệnh | Xử lý một ảnh hoặc **cả thư mục ảnh**, in bảng kết quả và tổng kết |
| Huấn luyện | Tinh chỉnh mô hình trên bộ ảnh riêng để nhận thêm đồ COCO không có |
| Đánh giá | Đo Precision, Recall, mAP@50, mAP@50-95 và xuất ra tệp CSV |

Các loại đồ nhận diện được sẵn (16 lớp từ bộ COCO): ghế băng, ghế, ghế sofa,
chậu cây, giường, bàn ăn, bồn cầu, tivi, lò vi sóng, lò nướng, máy nướng bánh mì,
bồn rửa, tủ lạnh, sách, đồng hồ, bình hoa.

---

## 2. Yêu cầu hệ thống

- Python **3.9** trở lên
- Khoảng **3 GB** ổ cứng trống (phần lớn là thư viện PyTorch)
- Kết nối mạng ở **lần chạy đầu** để tự tải tệp mô hình về
- Không bắt buộc có card đồ hoạ. Có GPU NVIDIA thì nhanh hơn khoảng 10–20 lần

---

## 3. Cài đặt

```bash
# 1. Tạo môi trường ảo
python -m venv venv

# 2. Kích hoạt môi trường ảo
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux

# 3. Cài thư viện
pip install -r requirements.txt
```

> Trên Linux, nếu chạy `app.py` báo lỗi `No module named 'tkinter'`:
> `sudo apt install python3-tk`

---

## 4. Cách chạy

### 4.1. Giao diện đồ hoạ

```bash
python app.py
```

Các bước: chọn mô hình → kéo thanh **Ngưỡng tin cậy** → bấm **Chọn ảnh để nhận
diện** → xem kết quả → bấm **Lưu ảnh kết quả** nếu cần.

Lần chạy đầu tiên chương trình phải tải tệp mô hình (`yolov8m.pt` khoảng 50 MB)
nên hơi lâu; những lần sau dùng lại bản đã tải.

### 4.2. Dòng lệnh

```bash
python detect_image.py anh/phong_khach.jpg                 # một ảnh
python detect_image.py anh/ --out ket_qua/ --conf 0.6      # cả thư mục
python detect_image.py anh/bep.jpg --model yolov8l.pt --tta
```

Các tham số: `--model`, `--conf`, `--imgsz`, `--out`, `--tta`
(xem đầy đủ bằng `python detect_image.py --help`).

---

## 5. Cấu trúc thư mục

```
BaiTapLon_NhanDienNoiThat/
├── app.py              Giao diện Tkinter
├── nhan_dien.py        Phần lõi: nạp mô hình, nhận diện, vẽ nhãn tiếng Việt
├── detect_image.py     Chạy bằng dòng lệnh (một ảnh hoặc cả thư mục)
├── train.py            Huấn luyện tinh chỉnh trên bộ dữ liệu riêng
├── evaluate.py         Đo độ chính xác, xuất bảng CSV
├── requirements.txt    Danh sách thư viện
├── data/
│   └── furniture.yaml  Cấu hình bộ dữ liệu huấn luyện
└── models/
    └── best.pt         Mô hình tự huấn luyện (sinh ra sau khi chạy train.py)
```

Toàn bộ phần xử lý nằm ở `nhan_dien.py`; `app.py`, `detect_image.py` và
`evaluate.py` đều gọi lại mô-đun này nên không có đoạn mã nào bị viết trùng.

---

## 6. Huấn luyện trên bộ dữ liệu riêng

Bộ COCO chỉ có 16 lớp gần với đồ nội thất. Muốn nhận thêm **tủ quần áo, bàn làm
việc, đèn, kệ, gương, rèm cửa, thảm** thì phải tự gán nhãn và huấn luyện thêm.

**Bước 1 — Thu thập ảnh.** Khoảng 150–200 ảnh cho mỗi lớp mới, chụp nhiều góc,
nhiều điều kiện ánh sáng.

**Bước 2 — Gán nhãn.** Dùng [LabelImg](https://github.com/HumanSignal/labelImg)
hoặc [Roboflow](https://roboflow.com), xuất ở **định dạng YOLO**.

**Bước 3 — Sắp xếp thư mục** theo đúng cấu trúc:

```
data/
├── images/train/  (80 % số ảnh)      labels/train/  (tệp .txt cùng tên)
└── images/val/    (20 % số ảnh)      labels/val/
```

**Bước 4 — Huấn luyện:**

```bash
python train.py --epochs 100 --batch 16
```

Xong, mô hình tốt nhất được chép sang `models/best.pt`; mở `app.py` chọn mục
*"Mô hình tự huấn luyện"* là dùng được ngay.

---

## 7. Đánh giá độ chính xác

```bash
python evaluate.py --model yolov8m.pt        # mô hình gốc, để lấy mốc so sánh
python evaluate.py --model models/best.pt    # mô hình sau khi huấn luyện
```

Điền số đo được vào bảng dưới đây khi làm báo cáo:

| Mô hình | Precision | Recall | mAP@50 | mAP@50-95 |
|---|---|---|---|---|
| YOLOv8n (bản ban đầu) | | | | |
| YOLOv8m (chưa huấn luyện thêm) | | | | |
| YOLOv8m sau khi tinh chỉnh | | | | |

Ý nghĩa các chỉ số:

- **Precision** — trong những vật chương trình báo, bao nhiêu phần trăm là đúng.
- **Recall** — trong những vật thật sự có trong ảnh, chương trình tìm ra bao nhiêu phần trăm.
- **mAP@50** — độ chính xác trung bình khi khung dự đoán trùng khung thật từ 50 % trở lên.
- **mAP@50-95** — chỉ số nghiêm khắc nhất, lấy trung bình trên nhiều mức trùng khớp.

---

## 8. Làm sao cho kết quả chính xác nhất

Xếp theo mức hiệu quả:

1. **Huấn luyện tinh chỉnh trên ảnh thực tế** (mục 6) — cải thiện nhiều nhất.
2. **Dùng mô hình lớn hơn**: `yolov8m` hoặc `yolov8l` thay cho `yolov8n`.
3. **Nâng ngưỡng tin cậy** lên 0,5 – 0,6 để loại bớt dự đoán sai.
4. **Bật chế độ chính xác cao (TTA)** khi cần kết quả tốt nhất, chấp nhận chậm.
5. **Tăng `--imgsz`** lên 1280 nếu ảnh có nhiều vật thể nhỏ.
6. **Ảnh đầu vào rõ nét, đủ sáng, chụp toàn cảnh căn phòng.**

> **Lưu ý trung thực:** không có hệ thống nhận diện vật thể nào đạt **100 %** tuyệt
> đối — kể cả các sản phẩm thương mại. Mục tiêu thực tế của bài là đẩy
> **mAP@50** lên càng cao càng tốt (trên 0,85 đã là rất khá) và nêu rõ trong báo cáo
> những trường hợp mô hình còn sai.

---

## 9. Hạn chế hiện tại

- Chỉ xử lý **ảnh tĩnh**, chưa làm video và webcam.
- Vật bị che khuất nhiều, ảnh ngược sáng hoặc chụp quá gần vẫn dễ bị bỏ sót.
- Mô hình gốc không phân biệt được các kiểu ghế / bàn khác nhau, chỉ gọi chung.
- Chạy bằng CPU mất khoảng 1–3 giây mỗi ảnh (bật TTA thì lâu hơn 2–3 lần).
