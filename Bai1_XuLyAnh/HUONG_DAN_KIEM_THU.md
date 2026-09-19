# HƯỚNG DẪN SỬ DỤNG VÀ KIỂM THỬ CHƯƠNG TRÌNH

## 1. Biên dịch và chạy

1. Giải nén, mở tệp **`ImageProcessing.sln`** bằng Visual Studio.
   Nếu Visual Studio hỏi nâng cấp bộ công cụ (project đang để **v120 / VS2013**) thì chọn
   **Retarget / Nâng cấp**; hoặc chuột phải project → *Properties* → *General* →
   *Platform Toolset* → chọn bản đang có.
2. Máy phải cài **thành phần MFC**: mở *Visual Studio Installer* → *Modify* →
   *Desktop development with C++* → tích **MFC/ATL support**.
3. Chọn cấu hình **Debug | Win32** → bấm **F7** (Build) → bấm **F5** (chạy).
4. Vào **Tệp → Mở ảnh Bitmap…** rồi chọn ảnh trong thư mục **`Images`**.

## 2. Ý nghĩa các menu

| Menu | Lệnh | Tác dụng |
|---|---|---|
| **Tệp** | Mở ảnh Bitmap… `Ctrl+O` | Mở tệp ảnh, hộp thoại chỉ lọc `*.bmp` |
| | Ghi ảnh `Ctrl+S` / Ghi ảnh thành… | Ghi ảnh (kể cả ảnh đã xử lý) ra tệp `.bmp` đúng chuẩn |
| **Đọc ảnh** | Cách 1: đọc tuần tự bằng `CFile` | Đọc từng phần theo cấu trúc tệp BMP (mặc định) |
| | Cách 2: đọc bằng hàm API `::LoadImage` | Nạp bằng `::LoadImage` rồi lấy dữ liệu bằng `::GetDIBits` |
| **Hiển thị** | Dùng hàm `::SetDIBitsToDevice` | Vẽ thẳng từ vùng dữ liệu DIB (mặc định) |
| | Dùng hàm `CDC::StretchBlt` | Vẽ qua ngữ cảnh thiết bị trong bộ nhớ |
| | Vừa cửa sổ (co giãn ảnh) | Co giãn ảnh cho vừa cửa sổ, giữ nguyên tỉ lệ |
| **Xử lý** | Thông tin ảnh… | Kích thước, số bit/pixel, số byte một dòng, số phần tử bảng màu, **số màu thực sự dùng** |
| | Lật ảnh ngang / Âm bản / Chuyển xám | Minh hoạ thao tác **vùng dữ liệu** điểm ảnh |
| | Xoay vòng bảng màu / Đảo ngược bảng màu | Minh hoạ thao tác **bảng màu** |
| | Tạo bản sao / Khôi phục từ bản sao | Minh hoạ cách tạo bản sao của `m_bmBitmap` |
| **Tuỳ chọn** | Chỉ nhận ảnh Bitmap 256 màu | Bật: chỉ mở được ảnh 8 bit (đúng yêu cầu bài). Tắt: mở thêm được ảnh 24 bit |

> Di chuột trên ảnh: thanh trạng thái hiện **toạ độ, chỉ số bảng màu và màu RGB** của điểm ảnh
> đang trỏ tới — dùng để chứng minh chương trình đã thực sự lưu được vùng dữ liệu ảnh.

## 3. Kịch bản kiểm thử theo từng yêu cầu của bài

### Yêu cầu 1 + 2 — Mở tệp, đọc nội dung và lưu lại

| TT | Thao tác | Kết quả mong đợi |
|---|---|---|
| 1.1 | **Tệp → Mở ảnh Bitmap…** | Hộp thoại chỉ hiện các tệp `*.bmp` |
| 1.2 | Chọn `Images\Lena_256mau.bmp` | Ảnh hiện ra; thanh trạng thái ghi `512 x 512 pixel - 8 bit/pixel - 256 màu trong bảng màu` |
| 1.3 | **Xử lý → Thông tin ảnh…** | `bfType = 0x4D42`, `biWidth = 512`, `biHeight = 512`, `biBitCount = 8`, `biCompression = 0`, số byte một dòng `512`, tổng dữ liệu `262144` byte |
| 1.4 | Rê chuột lên ảnh | Thanh trạng thái đổi liên tục theo điểm ảnh: `(x, y) chỉ số bảng màu = … -> RGB(…)` ⇒ **đã lưu được cả vùng dữ liệu lẫn bảng màu** |
| 1.5 | **Đọc ảnh → Cách 2: `::LoadImage`**, rồi mở lại chính ảnh đó | Ảnh hiện y hệt; *Thông tin ảnh* ghi `Cách đọc: Hàm API ::LoadImage` ⇒ hai cách đọc cho cùng kết quả |
| 1.6 | Mở `Images\Lena_xam_256mau.bmp` → *Thông tin ảnh* | `biClrUsed = 219` (bảng màu **không đủ 256** phần tử) mà ảnh vẫn hiện đúng ⇒ đọc bảng màu theo `biClrUsed`, không cố định 1024 byte |

### Yêu cầu 3 — Hiển thị ảnh

| TT | Thao tác | Kết quả mong đợi |
|---|---|---|
| 2.1 | **Hiển thị → Dùng hàm `::SetDIBitsToDevice`** | Ảnh hiện đúng màu, đúng chiều (không bị lộn ngược) |
| 2.2 | **Hiển thị → Dùng hàm `CDC::StretchBlt`** | Ảnh hiện **giống hệt** cách trên ⇒ cài đặt đúng cả hai hàm |
| 2.3 | Thu nhỏ cửa sổ cho nhỏ hơn ảnh | Xuất hiện **thanh cuộn**; kéo cuộn thì ảnh dịch đúng, không bị vẽ sai (nhờ `CScrollView`) |
| 2.4 | Che cửa sổ bằng cửa sổ khác rồi hiện lại | Ảnh **được vẽ lại đầy đủ** ⇒ vẽ trong `OnDraw` là đúng |
| 2.5 | **Hiển thị → Vừa cửa sổ**, rồi thay đổi kích thước cửa sổ | Ảnh co giãn theo cửa sổ, **giữ nguyên tỉ lệ** (đây là ưu điểm của `StretchBlt` so với `SetDIBitsToDevice`) |

### Yêu cầu 4 — Xử lý ngoại lệ (phần hay bị hỏi nhất)

| TT | Mở tệp | Thông báo mong đợi |
|---|---|---|
| 3.1 | `Images\Test_khong_phai_bmp.png` (gõ tay tên tệp, hoặc chọn *All Files*) | *"Tệp … không phải là ảnh Bitmap. Chương trình chỉ mở được tệp ảnh Bitmap (\*.bmp, \*.dib)."* — chặn ở bước kiểm tra **phần mở rộng** |
| 3.2 | `Images\Test_hong_khong_phai_bitmap.bmp` | *"Tệp … KHÔNG phải là ảnh Bitmap. Hai byte đầu của tệp là 0x…, trong khi ảnh BMP phải là 0x4D42 (\"BM\")."* — chặn ở bước kiểm tra **chữ ký tệp** (đuôi `.bmp` đúng nhưng nội dung sai) |
| 3.3 | `Images\Test_2mau_1bit.bmp` | *"Ảnh này là ảnh 1 bit/pixel (ảnh đen trắng)… chương trình đang đặt ở chế độ CHỈ NHẬN ảnh Bitmap 256 màu."* |
| 3.4 | `Images\Lena_24bit.bmp` | Bị từ chối với thông báo *"Ảnh này là ảnh 24 bit/pixel (16 triệu màu)…"* |
| 3.5 | Sau mỗi lần bị từ chối, nhìn lên cửa sổ | **Ảnh cũ vẫn còn nguyên**, chương trình **không bị treo/thoát** ⇒ `OnOpenDocument` trả về `FALSE` đúng cách |

### Phần mở rộng — ảnh Bitmap 24 bit màu

| TT | Thao tác | Kết quả mong đợi |
|---|---|---|
| 4.1 | **Tuỳ chọn → Chỉ nhận ảnh Bitmap 256 màu** (bỏ dấu chọn) | Hiện thông báo: từ nay mở được cả ảnh 256 màu và 24 bit |
| 4.2 | Mở lại `Images\Lena_24bit.bmp` | Ảnh hiện đúng màu; *Thông tin ảnh* ghi `biBitCount = 24`, `biClrUsed = 0` (**không có bảng màu**), số byte một dòng `1536` |
| 4.3 | Mở `Images\Test_2mau_1bit.bmp` | Vẫn bị từ chối: chỉ hỗ trợ 8 và 24 bit |
| 4.4 | Thoát chương trình rồi mở lại | Tuỳ chọn được **ghi nhớ** (lưu trong Registry) |

### Kiểm thử phần trả lời câu hỏi 3, 4, 5

| TT | Thao tác | Kết quả mong đợi — chứng minh điều gì |
|---|---|---|
| 5.1 | Mở `Lena_256mau.bmp` → **Xử lý → Thông tin ảnh…** | Mục *SỐ MÀU*: *số màu tối đa* = 256 (= 2^8) còn *số màu thực dùng* thường **nhỏ hơn** ⇒ **câu 3** |
| 5.2 | **Xử lý → Lật ảnh theo chiều ngang** | Ảnh lật gương ngay lập tức ⇒ thao tác được trên **vùng dữ liệu** (câu 4) |
| 5.3 | **Xử lý → Chuyển ảnh xám** | Ảnh thành xám ⇒ với ảnh 8 bit chỉ cần sửa **bảng màu** (câu 4) |
| 5.4 | **Xử lý → Đảo ngược bảng màu** | Màu ảnh đổi hẳn trong khi **vùng dữ liệu không đổi** ⇒ chứng minh giá trị điểm ảnh chỉ là **chỉ số** trỏ vào bảng màu |
| 5.5 | Mở ảnh 24 bit rồi xem menu **Xử lý** | Hai lệnh về bảng màu bị **làm mờ** ⇒ ảnh 24 bit không có bảng màu |
| 5.6 | Sau khi đã lật + xám + đảo màu → **Xử lý → Khôi phục từ bản sao** | Ảnh trở lại **y hệt ảnh gốc** (cả dữ liệu lẫn bảng màu) ⇒ **câu 5** |
| 5.7 | **Tệp → Ghi ảnh thành…** → đặt tên mới → mở lại tệp vừa ghi | Ảnh mở lại đúng ⇒ tệp `.bmp` ghi ra đúng chuẩn, dữ liệu dùng được cho các bài sau |

## 4. Bảng tự kiểm trước khi nộp

- [ ] Build không lỗi ở cấu hình **Debug | Win32**.
- [ ] Mở được ảnh BMP 256 màu và hiển thị đúng (không lộn ngược, không lệch màu).
- [ ] Chạy được **cả hai** cách đọc và **cả hai** hàm hiển thị.
- [ ] Bốn ca ngoại lệ (mục 3.1 → 3.4) đều hiện thông báo rõ ràng, chương trình không chết.
- [ ] Giải thích được: vì sao dòng ảnh phải **làm tròn bội số 4 byte**.
- [ ] Giải thích được: vì sao ảnh BMP **lưu lộn ngược** và code xử lý ở đâu (`GetLinePtr`).
- [ ] Giải thích được ý nghĩa **từng tham số** của `::SetDIBitsToDevice` và `StretchBlt`.
- [ ] Giải thích được vì sao **không được** viết `CBitmap bmCopy = m_bmBitmap;`.
