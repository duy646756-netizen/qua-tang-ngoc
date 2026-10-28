# PHẦN MỀM NHẬN DIỆN ĐỒ NỘI THẤT TRONG ẢNH

Bài tập lớn môn **Xử lý ảnh**. Chương trình nhận vào ảnh chụp trong nhà, tự động
khoanh vùng và gọi tên từng món **đồ nội thất** bằng tiếng Việt kèm độ tin cậy.

Mô hình: **YOLOv8** (Ultralytics) · Giao diện: **Tkinter**

> **Chỉ nhận diện đồ nội thất.** Người, xe cộ, thú nuôi, điện thoại, chai lọ…
> đều bị loại bỏ. Việc lọc làm **hai lớp**: lọc ngay khi gọi mô hình và lọc lại
> theo tên lớp sau khi có kết quả, nên không có vật thể lạ nào lọt ra.

---

## 1. Những món nhận diện được

**Nhóm chính — đồ nội thất (luôn bật):**

| Loại | Các món |
|---|---|
| Bàn | bàn, bàn làm việc, bàn trà, bàn ăn |
| Ghế | ghế, ghế đẩu, ghế băng, ghế sofa, ghế sofa đôi, ghế sofa dài, ghế sofa giường |
| Giường | giường, giường cũi em bé |
| Tủ | tủ quần áo, tủ, tủ chén, tủ phòng tắm, tủ ngăn kéo, tủ hồ sơ, tủ đầu giường, ngăn kéo |
| Kệ | kệ, kệ sách, kệ rượu |

**Nhóm phụ — thiết bị và đồ trang trí (tích chọn mới bật):**
tivi, tủ lạnh, lò nướng, lò vi sóng, máy nướng bánh mì, bồn rửa, bồn cầu, bồn tắm,
đèn, gương, rèm cửa, gối, bình hoa, chậu cây, đồng hồ, quạt trần.

## 2. Bốn bộ nhận diện để chọn

| Bộ | Ưu điểm | Hạn chế |
|---|---|---|
| **Đầy đủ đồ nội thất (Open Images V7)** — *mặc định* | Biết tủ quần áo, tủ bếp, kệ sách, ngăn kéo, bàn làm việc, tủ đầu giường… | Độ tin cậy trung bình thấp hơn COCO |
| **Chính xác cao (COCO)** | Rất chắc chắn với ghế, sofa, giường, bàn ăn | **Không biết** tủ, kệ, bàn làm việc |
| **Kết hợp cả hai** | Chạy lần lượt hai mô hình rồi gộp kết quả — tìm được nhiều món nhất | Chậm gấp đôi |
| **Mô hình tự huấn luyện** | Dùng sau khi chạy `train.py` trên bộ ảnh riêng | Phải tự gán nhãn dữ liệu trước |

Khi chạy chế độ *Kết hợp*, hai mô hình thường cùng tìm ra một món. Chương trình
tự gộp các khung chồng nhau (cùng tên trùng trên 50 %, khác tên trùng trên 80 %)
nên mỗi món chỉ còn một khung duy nhất.

## 3. Chức năng chính

- Chọn ảnh, khoanh khung màu và gán nhãn tiếng Việt kèm phần trăm tin cậy.
- **Thanh trượt ngưỡng tin cậy** 10–90 %: càng cao càng ít báo nhầm.
- **Chế độ chính xác cao (TTA)**: bắt thêm món khó thấy, đổi lại chậm hơn.
- **Bảng kết quả**: tên món, độ tin cậy, kích thước và toạ độ khung.
  Bấm một dòng để **làm nổi bật** đúng món đó trên ảnh, các món khác mờ đi.
- **Tổng quan**: số món, độ tin cậy trung bình, thời gian xử lý và thống kê
  theo từng loại.
- **Lưu ảnh kết quả** ra `.jpg` / `.png`.
- **Chạy dòng lệnh** cho một ảnh hoặc cả thư mục ảnh.
- **Huấn luyện** và **đánh giá** mô hình trên bộ dữ liệu riêng.

---

## 4. Cài đặt

```bash
python -m venv venv
venv\Scripts\activate            # Windows
source venv/bin/activate         # macOS / Linux

python -m pip install -r requirements.txt
```

Nếu `pip install -r requirements.txt` báo lỗi, cài trực tiếp:

```bash
python -m pip install ultralytics opencv-python pillow numpy
```

Trên Linux, nếu chạy `app.py` báo `No module named 'tkinter'`:
`sudo apt install python3-tk`

**Yêu cầu:** Python 3.9 trở lên · khoảng 3 GB ổ cứng (chủ yếu là PyTorch) ·
có mạng ở lần chạy đầu để tải mô hình (`yolov8m-oiv7.pt` ≈ 52 MB).
Không bắt buộc có card đồ hoạ; có GPU NVIDIA thì nhanh hơn khoảng 10–20 lần.

## 5. Cách chạy

### Giao diện

**Bấm đúp tệp `chay.bat`** — lần đầu nó tự cài thư viện rồi mở phần mềm.
Hoặc gõ `python app.py`.

Cách dùng: chọn mức **Độ nhạy** → bấm **Chọn ảnh để nhận diện**
(giữ **Ctrl** để chọn nhiều ảnh cùng lúc) → bấm từng ảnh ở cột phải để xem kết
quả → **Lưu ảnh đang xem** hoặc **Lưu tất cả kết quả**.

Ba mức độ nhạy:

| Mức | Ngưỡng | Khi nào dùng |
|---|---|---|
| Nhạy | 25 % | Muốn bắt được nhiều món nhất, chấp nhận vài món sai |
| Cân bằng | 40 % | Mức thường dùng |
| Chắc chắn | 60 % | Chỉ báo món thật sự chắc |

Không còn ô chọn mô hình hay ô tích nào khác: bên trong chương trình **luôn chạy
cả hai mô hình rồi gộp kết quả**, nên lúc nào cũng ở mức chính xác cao nhất.

### Dòng lệnh

```bash
python detect_image.py anh/phong_khach.jpg
python detect_image.py anh/ --out ket_qua/ --conf 0.5
python detect_image.py anh/bep.jpg --che-do ket_hop --kem-thiet-bi --tta
```

Xem đầy đủ tham số: `python detect_image.py --help`

## 6. Cấu trúc thư mục

```
BaiTapLon_NhanDienNoiThat/
├── app.py              Giao diện chính
├── giao_dien.py        Bảng màu, phông chữ, các ô giao diện dùng chung
├── nhan_dien.py        Phần lõi: danh mục nội thất, nạp mô hình, vẽ nhãn
├── detect_image.py     Chạy bằng dòng lệnh
├── train.py            Huấn luyện tinh chỉnh trên bộ dữ liệu riêng
├── evaluate.py         Đo Precision / Recall / mAP, xuất CSV
├── requirements.txt
├── data/furniture.yaml Cấu hình bộ dữ liệu huấn luyện (17 lớp nội thất)
└── models/best.pt      Mô hình tự huấn luyện (có sau khi chạy train.py)
```

Mọi phần xử lý nằm ở `nhan_dien.py`; `app.py` và `detect_image.py` đều gọi lại
mô-đun này nên không có đoạn mã nào bị viết trùng.

## 7. Huấn luyện trên bộ dữ liệu riêng

**Bước 1 — Thu thập ảnh:** khoảng 150–200 ảnh cho mỗi loại, nhiều góc chụp,
nhiều điều kiện ánh sáng.

**Bước 2 — Gán nhãn:** dùng [LabelImg](https://github.com/HumanSignal/labelImg)
hoặc [Roboflow](https://roboflow.com), xuất ở **định dạng YOLO**.

**Bước 3 — Sắp xếp thư mục:**

```
data/
├── images/train/  (80 % số ảnh)      labels/train/  (tệp .txt cùng tên)
└── images/val/    (20 % số ảnh)      labels/val/
```

**Bước 4 — Huấn luyện:**

```bash
python train.py --epochs 100 --batch 16
```

Mô hình tốt nhất được chép sang `models/best.pt`; mở `app.py` chọn
*"Mô hình tự huấn luyện"* là dùng được ngay. Tên lớp trong `data/furniture.yaml`
đã trùng với danh mục trong `nhan_dien.py` nên nhãn tiếng Việt hiện tự động.

## 8. Đánh giá độ chính xác

```bash
python evaluate.py --model yolov8m.pt         # mốc so sánh
python evaluate.py --model models/best.pt     # sau khi huấn luyện
```

Điền số đo được vào bảng này khi viết báo cáo:

| Mô hình | Precision | Recall | mAP@50 | mAP@50-95 |
|---|---|---|---|---|
| YOLOv8m (chưa huấn luyện thêm) | | | | |
| YOLOv8m sau khi tinh chỉnh | | | | |

- **Precision** — trong những món chương trình báo, bao nhiêu phần trăm là đúng.
- **Recall** — trong những món thật sự có, chương trình tìm ra bao nhiêu phần trăm.
- **mAP@50** — độ chính xác trung bình khi khung dự đoán trùng khung thật từ 50 %.
- **mAP@50-95** — chỉ số nghiêm khắc nhất, trung bình trên nhiều mức trùng khớp.

## 9. Mẹo cho kết quả tốt nhất

1. Huấn luyện tinh chỉnh trên ảnh thực tế (mục 7) — cải thiện nhiều nhất.
2. Chọn chế độ **Kết hợp cả hai**.
3. Ngưỡng tin cậy 0,45 – 0,60 để loại bớt dự đoán sai.
4. Bật **chế độ chính xác cao** khi cần kết quả tốt nhất.
5. Ảnh chụp toàn cảnh căn phòng, đủ sáng, không quá gần.

> **Lưu ý trung thực:** không có hệ thống nhận diện vật thể nào đạt **100 %**
> tuyệt đối, kể cả sản phẩm thương mại. Mục tiêu thực tế là đẩy **mAP@50** lên
> càng cao càng tốt (trên 0,85 đã là rất khá) và nêu rõ trong báo cáo những
> trường hợp mô hình còn sai.

## 10. Kết quả thử nghiệm thực tế

Thử trên ba ảnh sản phẩm nội thất chụp trên nền trơn, chế độ *Kết hợp cả hai*,
ngưỡng 40 %:

| Ảnh | Kết quả | Nhận xét |
|---|---|---|
| Tủ quần áo 3 cánh | **tủ quần áo 48 %** | Đúng, khung bao sát món đồ |
| Ghế sofa | **ghế sofa 95 %** | Đúng, độ tin cậy rất cao |
| Bàn làm việc có hộc tủ | **tủ ngăn kéo 57 %** | Khoanh đúng cả cái bàn nhưng **gọi sai tên** |

Nhận xét rút ra: chương trình **khoanh vùng chính xác cả 3/3 ảnh**, nhưng gọi
đúng tên 2/3. Cái bàn làm việc bị gọi là "tủ ngăn kéo" vì phần hộc tủ bên phải
chiếm tỉ trọng lớn, trong khi lớp *Desk* của bộ Open Images vốn yếu.

Đây chính là lý do cần **huấn luyện tinh chỉnh** (mục 7): dạy thêm cho mô hình
bằng ảnh bàn làm việc thật sẽ sửa được đúng loại lỗi này.

### Vì sao phải chạy thêm lượt có viền

Ảnh chụp sản phẩm thường để món đồ chiếm trọn khung hình, trong khi mô hình được
huấn luyện trên ảnh cảnh thật nơi mỗi món chỉ chiếm một phần. Chương trình vì vậy
chạy thêm hai lượt trên bản sao có thêm viền 25 % và 50 % rồi gộp kết quả:

| Ảnh | Chỉ ảnh gốc | Có thêm lượt viền |
|---|---|---|
| Tủ quần áo | không nhận ra gì | tủ quần áo 48 % |
| Bàn làm việc | không nhận ra gì | tủ ngăn kéo 57 % |
| Ghế sofa | ghế sofa 88 % | ghế sofa 95 % |

Đổi lại mỗi ảnh mất thêm khoảng 2–3 lần thời gian. Muốn nhanh hơn thì chạy dòng
lệnh với `--khong-them-vien`.

## 11. Hạn chế hiện tại

- Chỉ xử lý **ảnh tĩnh**, chưa làm video và webcam.
- Món bị che khuất nhiều, ảnh ngược sáng hoặc chụp quá gần vẫn dễ bị bỏ sót.
- Bộ Open Images V7 nhận được nhiều loại tủ kệ hơn nhưng độ tin cậy trung bình
  thấp hơn COCO, nên ngưỡng mặc định để ở mức 40 %.
- Chạy bằng CPU mất khoảng 1–3 giây mỗi ảnh (bật chế độ chính xác cao hoặc chế
  độ kết hợp thì lâu hơn).
- **Gọi tên chưa thật chuẩn với một số món:** bàn làm việc có hộc tủ dễ bị gọi là
  "tủ ngăn kéo", tủ quần áo đôi khi bị gọi là "tủ chén". Khắc phục bằng cách huấn
  luyện tinh chỉnh ở mục 7.
