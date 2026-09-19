# BÀI THỰC HÀNH SỐ 1 — ĐỌC VÀ HIỂN THỊ ẢNH BITMAP
## Phần trả lời các câu hỏi

---

## Câu 1. Tóm tắt các bước đọc và hiển thị ảnh. Giải thích tại sao phải dùng các hàm tương ứng và ý nghĩa các tham số

### 1.1. Cấu trúc một tệp ảnh Bitmap

Một tệp `.BMP` không nén gồm 4 phần nối tiếp nhau:

| Phần | Kích thước | Nội dung |
|---|---|---|
| `BITMAPFILEHEADER` | 14 byte | `bfType` = 0x4D42 ("BM"), `bfSize` = cỡ cả tệp, `bfOffBits` = vị trí bắt đầu vùng dữ liệu |
| `BITMAPINFOHEADER` | 40 byte | `biWidth`, `biHeight`, `biBitCount` (số bit/pixel), `biCompression`, `biClrUsed`… |
| Bảng màu (palette) | `n × 4` byte | `n` phần tử `RGBQUAD` (chỉ có ở ảnh ≤ 8 bit/pixel). Ảnh 256 màu ⇒ `n` = 256 ⇒ 1024 byte |
| Vùng dữ liệu điểm ảnh | `biSizeImage` byte | Với ảnh 8 bit: **mỗi byte là một CHỈ SỐ trỏ vào bảng màu**, không phải màu thật |

Hai điều **bắt buộc phải nhớ** khi xử lý vùng dữ liệu:

1. **Mỗi dòng ảnh luôn được làm tròn lên bội số của 4 byte.**
   `rowBytes = ((biWidth × biBitCount + 31) / 32) × 4`
   Ví dụ ảnh 8 bit rộng 253 pixel thì một dòng chiếm 256 byte, thừa 3 byte rác.
   → Trong chương trình: hàm `CalcRowBytes()` trong `ImageProcessingDoc.cpp`.
2. **Ảnh được lưu lộn ngược (bottom-up):** dòng đầu tiên trong bộ nhớ là dòng **dưới cùng** của ảnh (trừ khi `biHeight < 0`).
   → Trong chương trình: hàm `GetLinePtr(y)` đổi chỉ số dòng: `m_pDibBits + (height - 1 - y) * rowBytes`.

### 1.2. Các bước ĐỌC ảnh

**Cách 1 — đọc tuần tự theo cấu trúc tệp** (hàm `CImageProcessingDoc::ReadBmpByCFile`):

| Bước | Hàm dùng | Tại sao |
|---|---|---|
| 1 | `CFile::Open(đường dẫn, CFile::modeRead \| CFile::shareDenyWrite \| CFile::typeBinary, &fe)` | Phải mở ở chế độ **nhị phân** (`typeBinary`), nếu mở kiểu văn bản thì byte 0x0D/0x0A bị biến đổi làm hỏng dữ liệu ảnh. Tham số cuối `CFileException*` để lấy nguyên nhân lỗi khi mở thất bại |
| 2 | `file.Read(&bmfh, sizeof(BITMAPFILEHEADER))` | Đọc đúng 14 byte đầu để kiểm tra chữ ký "BM" |
| 3 | `file.Read(&bih, sizeof(BITMAPINFOHEADER))` | Lấy kích thước ảnh và **số bit/pixel** — dựa vào đó mới biết có bảng màu hay không |
| 4 | `file.Read(pBMI->bmiColors, n × sizeof(RGBQUAD))` | Đọc bảng màu (chỉ với ảnh ≤ 8 bit) |
| 5 | `file.Seek(bfOffBits, CFile::begin)` | Nhảy thẳng tới vùng dữ liệu. Dùng `bfOffBits` chứ **không** tự cộng 14+40+1024, vì một số tệp có tiêu đề mở rộng (BITMAPV4/V5HEADER) |
| 6 | `file.Read(pBits, rowBytes × height)` | Đọc toàn bộ vùng dữ liệu điểm ảnh vào bộ nhớ **và giữ lại** để các bài sau dùng |

`Read(void* lpBuf, UINT nCount)` trả về **số byte thực sự đọc được**; nếu nhỏ hơn `nCount` nghĩa là tệp bị cắt cụt → báo lỗi.

**Cách 2 — dùng hàm API `::LoadImage`** (hàm `CImageProcessingDoc::ReadBmpByLoadImage`):

```cpp
hBitmap = (HBITMAP)::LoadImage(AfxGetInstanceHandle(),  // quản số thể hiện chương trình
                               lpszPathName,            // đường dẫn tệp ảnh
                               IMAGE_BITMAP,            // loại tài nguyên cần nạp
                               0, 0,                    // 0,0 = giữ nguyên kích thước gốc
                               LR_LOADFROMFILE |        // nạp từ TỆP (không phải từ tài nguyên)
                               LR_CREATEDIBSECTION);    // tạo DIB Section -> giữ nguyên dạng DIB,
                                                        // truy cập được vùng dữ liệu điểm ảnh
```

Vì sao phải có `LR_CREATEDIBSECTION`? Nếu không có cờ này, Windows chuyển ảnh thành **DDB** (bitmap phụ thuộc thiết bị) — mất bảng màu gốc, không lấy được vùng dữ liệu thô để xử lý.
Hàm trả về `NULL` nếu tệp không phải ảnh Bitmap hợp lệ → đây cũng là một cách bắt ngoại lệ.

Sau đó lấy dữ liệu ra:
- `::GetObject(hBmp, sizeof(BITMAP), &bm)` → cấu trúc `BITMAP`: `bmWidth`, `bmHeight`, `bmWidthBytes`, `bmBitsPixel`, `bmBits`.
- `::GetDIBColorTable(hdcMem, 0, n, pRGB)` → lấy **bảng màu** (bitmap phải đang được gắn vào ngữ cảnh thiết bị).
- `::GetDIBits(hdcMem, hBmp, 0, h, pBits, pBMI, DIB_RGB_COLORS)` → lấy **vùng dữ liệu** (bitmap phải **không** đang gắn trong DC nào).

Cuối cùng gắn quản số cho lớp MFC:
```cpp
if (m_bmBitmap.m_hObject != NULL) m_bmBitmap.DeleteObject();  // xoá ảnh cũ, tránh rò rỉ bộ nhớ
m_bmBitmap.Attach(hBitmap);   // gắn quản số HBITMAP cho lớp CBitmap
```

### 1.3. Các bước HIỂN THỊ ảnh

Việc vẽ được làm trong `CImageProcessingView::OnDraw(CDC* pDC)` vì:
- MFC gọi `OnDraw` mỗi khi cửa sổ cần vẽ lại (thu nhỏ/phóng to, bị che rồi hiện lại, cuộn…). Nếu vẽ ở chỗ khác thì ảnh sẽ **mất** khi cửa sổ được vẽ lại.
- `pDC` là ngữ cảnh thiết bị đã được MFC chuẩn bị sẵn (kể cả khi in ấn).

**Cách A — `::SetDIBitsToDevice` (vẽ thẳng từ vùng dữ liệu DIB):**

```cpp
::SetDIBitsToDevice(pDC->GetSafeHdc(), // quản số ngữ cảnh thiết bị đích
                    0, 0,              // XDest, YDest: toạ độ trái-trên nơi hiển thị
                    w, h,              // dwWidth, dwHeight: bề rộng/cao vùng cần vẽ
                    0, 0,              // XSrc, YSrc: toạ độ trái-DƯỚI của ảnh nguồn
                    0,                 // uStartScan: dòng quét bắt đầu
                    h,                 // cScanLines: số dòng quét đưa lên màn hình
                    pDibBits,          // lpvBits: con trỏ vùng dữ liệu ảnh
                    pBMI,              // lpbmi: con trỏ BITMAPINFO (tiêu đề + bảng màu)
                    DIB_RGB_COLORS);   // fuColorUse: bảng màu chứa giá trị RGB thật
```
Ưu điểm: vẽ trực tiếp từ bộ nhớ, **không cần** tạo ngữ cảnh thiết bị trung gian; rất hợp với các bài xử lý ảnh vì chỉ cần sửa mảng dữ liệu rồi vẽ lại. Nhược điểm: không co giãn được ảnh.

**Cách B — `CDC::StretchBlt` (chép qua ngữ cảnh thiết bị trong bộ nhớ):**

```cpp
CDC dcMem;
dcMem.CreateCompatibleDC(pDC);              // tạo DC trong bộ nhớ, tương thích với màn hình
CBitmap* pOld = dcMem.SelectObject(&m_bmBitmap); // gắn bitmap vào DC đó
pDC->StretchBlt(0, 0, nWidth, nHeight,      // vị trí và kích thước NƠI HIỂN THỊ
                &dcMem,                     // ngữ cảnh thiết bị NGUỒN
                0, 0, bm.bmWidth, bm.bmHeight, // vị trí và kích thước vùng NGUỒN
                SRCCOPY);                   // phép toán raster: chép nguyên xi
dcMem.SelectObject(pOld);                   // trả lại bitmap cũ trước khi huỷ DC
```
Vì sao phải có `dcMem`? Vì một bitmap **không thể vẽ trực tiếp** lên màn hình — nó phải được "gắn" (SelectObject) vào một ngữ cảnh thiết bị trước, rồi mới sao chép từ DC đó sang DC màn hình.
Ưu điểm: **co giãn được** ảnh (kích thước đích khác kích thước nguồn) → dùng cho chức năng "Vừa cửa sổ" trong chương trình. Nếu không cần co giãn thì `BitBlt` nhanh hơn.

> Chương trình cài đặt **cả hai cách**, chọn trong menu **Hiển thị**, để so sánh trực tiếp.

### 1.4. Vì sao lớp View kế thừa `CScrollView`?
Ảnh thường lớn hơn cửa sổ. `CScrollView` tự sinh thanh cuộn khi ta khai báo kích thước vùng làm việc:
```cpp
SetScrollSizes(MM_TEXT, CSize(pDoc->GetWidth(), pDoc->GetHeight()));
```
và tự dịch gốc toạ độ của `pDC` theo vị trí cuộn (trong `OnPrepareDC`), nên trong `OnDraw` ta cứ vẽ ảnh ở toạ độ (0,0) là đúng.

---

## Câu 2. Thiết lập xử lý ngoại lệ: chỉ đọc ảnh bitmap, nếu không phải thì thông báo. Giải thích cách làm

Chương trình kiểm tra theo **5 lớp bảo vệ**, đặt trong `ReadBmpByCFile()` và `ValidateBitmap()`:

**(1) Lọc ngay từ hộp thoại mở tệp.** Chuỗi mẫu tài liệu trong bảng chuỗi (`IDR_MAINFRAME`) khai báo bộ lọc `Ảnh Bitmap 256 màu (*.bmp)` và phần mở rộng mặc định `.bmp`, nên hộp thoại Open chỉ liệt kê tệp `.bmp`.

**(2) Kiểm tra phần mở rộng** (phòng khi người dùng gõ tay tên tệp):
```cpp
CString strExt = strPath.Mid(strPath.ReverseFind(_T('.')) + 1);
if (strExt.CompareNoCase(_T("bmp")) != 0 && strExt.CompareNoCase(_T("dib")) != 0)
    → báo lỗi "Chương trình chỉ mở được tệp ảnh Bitmap (*.bmp)"
```

**(3) Kiểm tra CHỮ KÝ của tệp — quan trọng nhất.** Phần mở rộng có thể bị đổi tên, chỉ có 2 byte đầu mới nói lên sự thật:
```cpp
if (bmfh.bfType != 0x4D42)   // 0x4D42 = 'B' + 'M' (little-endian)
    → "Tệp KHÔNG phải là ảnh Bitmap"
```
(Tệp `Images\Test_hong_khong_phai_bitmap.bmp` được tạo sẵn để thử trường hợp này.)

**(4) Kiểm tra khuôn dạng ảnh** — trong hàm `ValidateBitmap()`:
- `biSize < 40` → tiêu đề kiểu OS/2 (BITMAPCOREHEADER) → từ chối;
- `biCompression != BI_RGB` → ảnh nén RLE → từ chối;
- `biWidth <= 0 || biHeight == 0` → kích thước sai → từ chối;
- **`biBitCount != 8` → từ chối, vì bài yêu cầu chỉ thao tác với ảnh BMP 256 màu.**
  Thông báo nêu rõ ảnh đang mở là bao nhiêu bit/pixel. Muốn mở rộng cho ảnh 24 bit thì bỏ dấu chọn ở menu **Tuỳ chọn → Chỉ nhận ảnh Bitmap 256 màu** (tuỳ chọn này được ghi vào Registry, nhớ cho lần chạy sau).

**(5) Bắt ngoại lệ vào/ra bằng `try … catch`:**
```cpp
try { ... file.Read(...) ... }
catch (CFileException* pEx)   { pEx->GetErrorMessage(szCause, 255); … pEx->Delete(); }
catch (CMemoryException* pEx) { AfxMessageBox(_T("Không đủ bộ nhớ…")); pEx->Delete(); }
```
Ngoài ra còn kiểm tra giá trị trả về của `Read`: nếu số byte đọc được nhỏ hơn số byte cần → tệp bị cắt cụt → báo lỗi.

**Cách báo lỗi và huỷ việc mở tệp:**
```cpp
AfxMessageBox(strError, MB_OK | MB_ICONEXCLAMATION);
return FALSE;   // OnOpenDocument trả về FALSE => MFC huỷ việc mở tài liệu,
                // giữ nguyên ảnh cũ trên màn hình, không làm chương trình chết
```

---

## Câu 3. Làm thế nào để biết ảnh đang hiển thị là ảnh bao nhiêu màu?

Có ba mức trả lời, chương trình cài đặt cả ba trong menu **Xử lý → Thông tin ảnh**:

**a) Số màu TỐI ĐA — đọc từ `biBitCount`:**

| `biBitCount` | Số màu tối đa | Bảng màu |
|---|---|---|
| 1 | 2 màu | có, 2 phần tử |
| 4 | 16 màu | có, 16 phần tử |
| **8** | **256 màu** | **có, 256 phần tử** |
| 16 | 65 536 màu | không |
| 24 | 16 777 216 màu | không |
| 32 | 16 777 216 màu + kênh alpha | không |

Công thức: *số màu tối đa = 2^biBitCount* (với ảnh ≤ 8 bit).

Lấy giá trị này bằng một trong hai cách:
```cpp
// Cách 1: đọc thẳng từ tiêu đề đã lưu
int nBits = m_pBMI->bmiHeader.biBitCount;

// Cách 2: từ đối tượng CBitmap
BITMAP bm;
m_bmBitmap.GetBitmap(&bm);
int nBits = bm.bmBitsPixel;      // số bit/pixel
```

**b) Số phần tử bảng màu thực tế — `biClrUsed`:**
Nếu `biClrUsed = 0` thì bảng màu có đủ `2^biBitCount` phần tử; nếu khác 0 thì đó chính là số phần tử. (Ảnh mẫu `Lena_xam_256mau.bmp` chỉ có 219 phần tử.)

**c) Số màu THỰC SỰ được dùng trong ảnh** — hàm `CountUsedColors()`:
- Ảnh 8 bit: duyệt toàn bộ vùng dữ liệu, đánh dấu những **chỉ số** xuất hiện vào mảng `bool bUsed[256]`, rồi đếm số phần tử `true`. Một ảnh khai báo 256 màu vẫn có thể chỉ dùng thực sự vài chục màu.
- Ảnh 24 bit: gom giá trị `RGB` của từng điểm ảnh vào một `std::set<DWORD>`, kích thước tập hợp là số màu khác nhau.

---

## Câu 4. Muốn thao tác với vùng dữ liệu của Bitmap thì làm thế nào? Muốn thao tác với bảng màu thì làm thế nào?

### 4.1. Thao tác với VÙNG DỮ LIỆU

**Cách 1 — dùng con trỏ của DIB Section (cách chương trình này dùng, nhanh nhất).**
Khi tạo bitmap bằng `::CreateDIBSection`, Windows trả về **con trỏ tới chính vùng nhớ chứa điểm ảnh**; sửa trên con trỏ đó là sửa luôn bitmap, không phải sao chép đi đâu cả:
```cpp
m_hBitmap = ::CreateDIBSection(hdc, m_pBMI, DIB_RGB_COLORS, (void**)&m_pDibBits, NULL, 0);
```
Truy cập một điểm ảnh (ảnh 8 bit), nhớ hai quy tắc ở câu 1:
```cpp
BYTE* pLine = m_pDibBits + (DWORD)(height - 1 - y) * m_nRowBytes; // dòng y tính từ TRÊN xuống
BYTE  value = pLine[x];            // = chỉ số trong bảng màu
pLine[x] = 128;                    // ghi giá trị mới
```
Với ảnh 24 bit, mỗi điểm ảnh chiếm 3 byte theo thứ tự **B, G, R** (ngược với tên gọi RGB):
```cpp
BYTE* p = pLine + x * 3;
BYTE blue = p[0], green = p[1], red = p[2];
```
> Minh hoạ trong chương trình: **Xử lý → Lật ảnh theo chiều ngang**, **Ảnh âm bản**, **Chuyển ảnh xám**;
> di chuột trên ảnh sẽ thấy toạ độ, chỉ số bảng màu và màu RGB của điểm ảnh hiện trên thanh trạng thái.

**Cách 2 — dùng `CBitmap::GetBitmapBits` / `SetBitmapBits` (theo tài liệu hướng dẫn):**
```cpp
BITMAP bm;
m_bmBitmap.GetBitmap(&bm);                       // lấy thông tin: bmWidthBytes, bmHeight…
DWORD  dwSize = bm.bmWidthBytes * bm.bmHeight;
BYTE*  pBuf   = new BYTE[dwSize];
m_bmBitmap.GetBitmapBits(dwSize, pBuf);          // LẤY vùng dữ liệu ra bộ đệm
/* … xử lý trên pBuf … */
m_bmBitmap.SetBitmapBits(dwSize, pBuf);          // ĐẶT lại vùng dữ liệu cho bitmap
delete[] pBuf;
```
Cách này phải sao chép dữ liệu hai lần (ra và vào) nên chậm hơn cách 1.

**Cách 3 — `::GetDIBits` / `::SetDIBits`:** lấy/đặt dữ liệu kèm cả bảng màu, dùng khi bitmap là DDB.

Sau khi sửa dữ liệu phải gọi `UpdateAllViews(NULL)` (hoặc `Invalidate()`) để khung nhìn vẽ lại.

### 4.2. Thao tác với BẢNG MÀU

Với ảnh 256 màu, **đổi màu hiển thị không cần đụng tới vùng dữ liệu** — chỉ cần sửa bảng màu (nhanh hơn rất nhiều: 256 phần tử so với hàng trăm nghìn điểm ảnh).

```cpp
// 1) Sửa bảng màu đang lưu trong BITMAPINFO
RGBQUAD* pPal = m_pBMI->bmiColors;
for (int i = 0; i < m_pBMI->bmiHeader.biClrUsed; i++)
{
    pPal[i].rgbRed   = 255 - pPal[i].rgbRed;      // ví dụ: đảo màu -> ảnh âm bản
    pPal[i].rgbGreen = 255 - pPal[i].rgbGreen;
    pPal[i].rgbBlue  = 255 - pPal[i].rgbBlue;
}

// 2) Cập nhật bảng màu cho đối tượng bitmap (hàm ApplyPaletteToBitmap)
HDC hdcMem = ::CreateCompatibleDC(NULL);
HGDIOBJ hOld = ::SelectObject(hdcMem, m_hBitmap);
::SetDIBColorTable(hdcMem, 0, nColors, pPal);     // đọc lại bằng ::GetDIBColorTable
::SelectObject(hdcMem, hOld);
::DeleteDC(hdcMem);
```

Ngoài ra còn **bảng màu logic** `CPalette`, cần khi màn hình chạy ở chế độ 256 màu (card đời cũ):
```cpp
BYTE* pBuf = new BYTE[sizeof(LOGPALETTE) + n * sizeof(PALETTEENTRY)];
LOGPALETTE* pLP = (LOGPALETTE*)pBuf;
pLP->palVersion = 0x300;  pLP->palNumEntries = n;
for (int i = 0; i < n; i++) { pLP->palPalEntry[i].peRed = pPal[i].rgbRed; /* … */ }
m_palLogical.CreatePalette(pLP);      // tạo bảng màu
// khi vẽ:
CPalette* pOld = pDC->SelectPalette(&m_palLogical, FALSE);
pDC->RealizePalette();                // ánh xạ bảng màu logic sang bảng màu hệ thống
```
> Minh hoạ trong chương trình: **Xử lý → Xoay vòng bảng màu**, **Đảo ngược bảng màu**.
> Với ảnh 24 bit các lệnh này bị làm mờ vì ảnh 24 bit **không có bảng màu**.

---

## Câu 5. Muốn có một BẢN SAO của `m_bmBitmap` để dùng sau này thì làm thế nào?

**Điều tuyệt đối không được làm:**
```cpp
CBitmap bmCopy = m_bmBitmap;     // SAI: hai lớp cùng dùng CHUNG một quản số HBITMAP
                                 // -> sửa cái này hỏng cái kia, và khi cả hai cùng bị huỷ
                                 //    sẽ xoá hai lần một đối tượng GDI -> lỗi chương trình
```
Một quản số GDI chỉ được một lớp `CBitmap` quản lý. Muốn có bản sao phải tạo ra **một đối tượng GDI mới**.

**Cách A — dùng `::CopyImage` (ngắn gọn nhất, chương trình đang dùng):**
```cpp
m_hBitmapBackup = (HBITMAP)::CopyImage(m_hBitmap, IMAGE_BITMAP, 0, 0, LR_CREATEDIBSECTION);
m_bmBackup.Attach(m_hBitmapBackup);     // gắn quản số mới cho một lớp CBitmap khác
```

**Cách B — sao chép vùng dữ liệu sang bộ đệm riêng (cách chắc chắn nhất cho xử lý ảnh):**
```cpp
m_pBackupBits = new BYTE[m_dwImageSize];
memcpy(m_pBackupBits, m_pDibBits, m_dwImageSize);   // sao vùng dữ liệu
memcpy(m_pBackupBMI, m_pBMI, BMI_BUFFER_SIZE);      // sao cả tiêu đề + BẢNG MÀU
```
Khôi phục chỉ việc `memcpy` ngược lại rồi `ApplyPaletteToBitmap()` + `UpdateAllViews(NULL)`.
**Lưu ý: phải sao cả bảng màu**, vì với ảnh 256 màu, chỉ sao vùng dữ liệu mà quên bảng màu thì ảnh khôi phục sẽ sai màu.

**Cách C — tạo bitmap mới rồi chép qua DC (dùng `GetBitmapBits`/`SetBitmapBits`):**
```cpp
BITMAP bm;  m_bmBitmap.GetBitmap(&bm);
CBitmap bmCopy;
bmCopy.CreateBitmapIndirect(&bm);
DWORD dwSize = bm.bmWidthBytes * bm.bmHeight;
BYTE* pBuf = new BYTE[dwSize];
m_bmBitmap.GetBitmapBits(dwSize, pBuf);
bmCopy.SetBitmapBits(dwSize, pBuf);
delete[] pBuf;
```

**Cách D — chép qua hai ngữ cảnh thiết bị:**
```cpp
CDC dcSrc, dcDst;  dcSrc.CreateCompatibleDC(NULL);  dcDst.CreateCompatibleDC(NULL);
CBitmap bmCopy;    bmCopy.CreateCompatibleBitmap(&dcSrc, bm.bmWidth, bm.bmHeight);
CBitmap* pOldS = dcSrc.SelectObject(&m_bmBitmap);
CBitmap* pOldD = dcDst.SelectObject(&bmCopy);
dcDst.BitBlt(0, 0, bm.bmWidth, bm.bmHeight, &dcSrc, 0, 0, SRCCOPY);
dcSrc.SelectObject(pOldS);  dcDst.SelectObject(pOldD);
```

> Trong chương trình: **Xử lý → Tạo bản sao của ảnh** và **Khôi phục từ bản sao**.
> Bản sao còn được tạo **tự động ngay sau khi mở ảnh**, nên lúc nào cũng quay lại được ảnh gốc
> sau khi đã lật / âm bản / chuyển xám.
