# Bài thực hành số 1 — Đọc và hiển thị ảnh Bitmap

Chương trình `ImageProcessing` viết bằng **VC++ / MFC** (SDI, lớp View kế thừa `CScrollView`),
đọc ảnh **Bitmap 256 màu** (mở rộng cho ảnh **24 bit màu**), lưu lại toàn bộ dữ liệu ảnh
để dùng cho các bài thực hành tiếp theo, và hiển thị ảnh bằng cả hai hàm
`::SetDIBitsToDevice` và `CDC::StretchBlt`.

## 1. Cách mở và biên dịch

1. Mở tệp **`ImageProcessing.sln`** bằng Visual Studio (project để ở bộ công cụ **v120 / VS2013**;
   nếu dùng VS mới hơn, khi được hỏi hãy chọn **Retarget / Nâng cấp** — hoặc chuột phải vào
   project → *Properties* → *General* → đổi *Platform Toolset* sang bản đang có).
   > Cần cài **thành phần MFC** của Visual Studio (Visual Studio Installer →
   > *Desktop development with C++* → tích **MFC / ATL**).
2. Chọn cấu hình **Debug | Win32** rồi bấm **F7** để biên dịch, **F5** để chạy.
3. Vào menu **Tệp → Mở ảnh Bitmap…**, chọn một tệp trong thư mục **`Images`**.

## 2. Các tệp trong bài

```
Bai1_XuLyAnh/
├── ImageProcessing.sln              Solution
├── ImageProcessing/
│   ├── ImageProcessing.vcxproj      Project (v120, Win32, MFC Shared DLL, Unicode)
│   ├── ImageProcessing.h/.cpp       Lớp ứng dụng + hộp thoại Giới thiệu + tuỳ chọn 256 màu
│   ├── MainFrm.h/.cpp               Cửa sổ chính + thanh trạng thái
│   ├── ImageProcessingDoc.h/.cpp    ĐỌC ẢNH và LƯU DỮ LIỆU ẢNH  (phần chính)
│   ├── ImageProcessingView.h/.cpp   HIỂN THỊ ẢNH (CScrollView)  (phần chính)
│   ├── ImageProcessing.rc           Tài nguyên: menu, hộp thoại, bảng chuỗi
│   ├── Resource.h, stdafx.*, targetver.h
│   └── res/ImageProcessing.ico
├── Images/                          Ảnh mẫu (xem mục 5)
├── TRA_LOI_CAU_HOI.md               Trả lời 5 câu hỏi của bài thực hành
└── README.md
```

## 3. Đối chiếu với yêu cầu của bài

| Yêu cầu | Thực hiện ở đâu |
|---|---|
| **1. Mở một tệp ảnh bitmap** | `CImageProcessingDoc::OnOpenDocument()`; bộ lọc `*.bmp` khai báo trong chuỗi `IDR_MAINFRAME` |
| **2. Đọc nội dung ảnh, lưu lại để xử lý sau** | `ReadBmpByCFile()` (đọc tuần tự bằng `CFile`) và `ReadBmpByLoadImage()` (dùng `::LoadImage` + `::GetDIBits`). Dữ liệu giữ trong `m_bmfHeader`, `m_pBMI` (tiêu đề + bảng màu), `m_pDibBits` (vùng điểm ảnh), `m_bmBitmap`, `m_palLogical` |
| **3. Hiển thị ảnh vừa đọc** | `CImageProcessingView::OnDraw()` — chọn `::SetDIBitsToDevice` hoặc `CDC::StretchBlt` trong menu **Hiển thị** |
| **4. Xử lý ngoại lệ (chỉ ảnh bitmap, chỉ BMP 256 màu)** | Kiểm tra phần mở rộng, chữ ký `"BM"`, `biCompression`, `biBitCount` trong `ReadBmpByCFile()` và `ValidateBitmap()`; bắt `CFileException` / `CMemoryException` |
| **Mở rộng cho ảnh Bitmap 24 bit** | Bỏ dấu chọn ở menu **Tuỳ chọn → Chỉ nhận ảnh Bitmap 256 màu** |
| **Câu hỏi 1–5** | Tệp `TRA_LOI_CAU_HOI.md`, kèm chức năng minh hoạ trong menu **Xử lý** |

## 4. Các chức năng của chương trình

- **Tệp**: Mở ảnh Bitmap, Ghi ảnh, Ghi ảnh thành… (ghi ra tệp `.bmp` đúng chuẩn sau khi xử lý).
- **Đọc ảnh**: chọn 1 trong 2 cách đọc — *đọc tuần tự bằng `CFile`* hoặc *dùng hàm API `::LoadImage`*.
- **Hiển thị**: `::SetDIBitsToDevice` / `CDC::StretchBlt` / *Vừa cửa sổ* (co giãn giữ nguyên tỉ lệ).
- **Xử lý** (minh hoạ cho câu hỏi 3, 4, 5):
  - *Thông tin ảnh*: kích thước, số bit/pixel, số byte một dòng, số phần tử bảng màu và **số màu thực sự được dùng**;
  - *Lật ảnh theo chiều ngang*, *Ảnh âm bản*, *Chuyển ảnh xám* — thao tác vùng dữ liệu;
  - *Xoay vòng bảng màu*, *Đảo ngược bảng màu* — thao tác bảng màu;
  - *Tạo bản sao của ảnh*, *Khôi phục từ bản sao*.
- **Tuỳ chọn**: bật/tắt ràng buộc chỉ nhận ảnh 256 màu (ghi nhớ trong Registry).
- Di chuột trên ảnh: thanh trạng thái hiện **toạ độ, chỉ số bảng màu và màu RGB** của điểm ảnh.

## 5. Ảnh mẫu trong thư mục `Images`

| Tệp | Mô tả | Kết quả mong đợi |
|---|---|---|
| `Lena_256mau.bmp` | BMP 8 bit, 512×512, bảng màu 256 phần tử | Mở bình thường |
| `Baboon_256mau.bmp` | BMP 8 bit, 384×384 | Mở bình thường |
| `Lena_xam_256mau.bmp` | BMP 8 bit, bảng màu chỉ có **219** phần tử (`biClrUsed` ≠ 0) | Mở bình thường — thử chức năng *Thông tin ảnh* |
| `Lena_24bit.bmp` | BMP 24 bit | Bị **từ chối** khi đang bật "chỉ nhận 256 màu"; mở được sau khi tắt tuỳ chọn |
| `Test_2mau_1bit.bmp` | BMP 1 bit (2 màu) | Bị **từ chối**: "ảnh 1 bit/pixel" |
| `Test_hong_khong_phai_bitmap.bmp` | Tệp văn bản đổi đuôi thành `.bmp` | Bị **từ chối**: 2 byte đầu không phải `"BM"` |
| `Test_khong_phai_bmp.png` | Ảnh PNG | Bị **từ chối** ngay từ phần mở rộng |

## 6. Hai điểm dễ sai khi làm bài (đã xử lý trong chương trình)

1. **Mỗi dòng ảnh được làm tròn lên bội số 4 byte** — dùng `((w * bpp + 31) / 32) * 4`,
   không phải `w * bpp / 8`.
2. **Ảnh BMP lưu lộn ngược** — dòng đầu trong bộ nhớ là dòng dưới cùng của ảnh
   (xem hàm `GetLinePtr`).

Ngoài ra, mã mẫu trong tài liệu hướng dẫn có hai lỗi đánh máy cần lưu ý:
`if (pDoc->m_bmBitmap.m_hObject = = NULL)` là **phép gán**, phải viết `==`;
và biến khai báo là `m_bmBimap` nhưng lúc dùng lại viết `m_bmBitmap`.
