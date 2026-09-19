// ImageProcessingDoc.h : lớp Document - nơi ĐỌC và LƯU TRỮ dữ liệu ảnh Bitmap
//
// Bài thực hành số 1 - Xử lý ảnh: Đọc và hiển thị ảnh Bitmap
//
// Toàn bộ dữ liệu của ảnh được giữ lại trong lớp này (tiêu đề tệp, tiêu đề ảnh,
// bảng màu và vùng dữ liệu điểm ảnh) để các bài thực hành sau (nâng cao chất
// lượng ảnh, phân đoạn - tìm biên, phép toán hình thái) có thể dùng lại ngay.

#pragma once

// Cách đọc ảnh (xem menu "Đọc ảnh")
enum EReadMode
{
	READ_BY_CFILE     = 0,	// đọc tuần tự theo cấu trúc tệp bằng CFile::Read
	READ_BY_LOADIMAGE = 1	// đọc bằng hàm API ::LoadImage
};

class CImageProcessingDoc : public CDocument
{
protected: // chỉ được tạo từ serialization
	CImageProcessingDoc();
	DECLARE_DYNCREATE(CImageProcessingDoc)

// ===================== DỮ LIỆU ẢNH ĐƯỢC LƯU LẠI =====================
public:
	BITMAPFILEHEADER m_bmfHeader;	// 14 byte tiêu đề của tệp .BMP
	BITMAPINFO*      m_pBMI;		// BITMAPINFOHEADER (40 byte) + bảng màu (tối đa 256 RGBQUAD)
	BYTE*            m_pDibBits;	// vùng dữ liệu điểm ảnh (trỏ thẳng vào DIB Section)
	DWORD            m_dwImageSize;	// kích thước vùng dữ liệu (byte)
	int              m_nRowBytes;	// số byte thực sự của một dòng ảnh (đã làm tròn bội số 4)

	HBITMAP  m_hBitmap;			// quản số (handle) của bitmap
	CBitmap  m_bmBitmap;		// lớp CBitmap của MFC, quản lý m_hBitmap
	CPalette m_palLogical;		// bảng màu logic, dùng khi màn hình ở chế độ 256 màu
	CString  m_strFilePath;		// đường dẫn đầy đủ của tệp ảnh đang mở
	int      m_nReadMode;		// EReadMode - cách đọc ảnh đang chọn

	// ---- Bản sao dự phòng (trả lời câu hỏi 5) ----
	BITMAPINFO* m_pBackupBMI;	// bản sao của tiêu đề + bảng màu
	BYTE*       m_pBackupBits;	// bản sao của vùng dữ liệu điểm ảnh
	HBITMAP     m_hBitmapBackup;// bản sao độc lập của bitmap (quản số riêng)
	CBitmap     m_bmBackup;		// lớp CBitmap quản lý bản sao

// ===================== CÁC HÀM TIỆN ÍCH =====================
public:
	BOOL  HasImage() const      { return (m_pDibBits != NULL && m_pBMI != NULL); }
	BOOL  HasBackup() const     { return (m_pBackupBits != NULL); }
	int   GetWidth() const      { return m_pBMI ? (int)m_pBMI->bmiHeader.biWidth  : 0; }
	int   GetHeight() const     { return m_pBMI ? (int)m_pBMI->bmiHeader.biHeight : 0; }
	int   GetBitCount() const   { return m_pBMI ? (int)m_pBMI->bmiHeader.biBitCount : 0; }
	int   GetRowBytes() const   { return m_nRowBytes; }
	// Số phần tử của bảng màu (0 nếu là ảnh 24 bit - ảnh 24 bit không có bảng màu)
	int   GetPaletteEntries() const { return m_pBMI ? (int)m_pBMI->bmiHeader.biClrUsed : 0; }
	RGBQUAD* GetPalette() const { return m_pBMI ? m_pBMI->bmiColors : NULL; }
	BITMAPINFO* GetBitmapInfo() const { return m_pBMI; }
	BYTE* GetDibBits() const    { return m_pDibBits; }

	// Con trỏ tới đầu dòng ảnh thứ y TÍNH TỪ TRÊN XUỐNG (y = 0 là dòng trên cùng).
	// Ảnh BMP được lưu lộn ngược (bottom-up) nên phải đổi chỉ số dòng.
	BYTE* GetLinePtr(int y) const;

	// Lấy giá trị một điểm ảnh: với ảnh 8 bit trả về chỉ số trong bảng màu,
	// đồng thời trả về màu RGB thật sự của điểm ảnh qua tham số rgb.
	BOOL  GetPixelInfo(int x, int y, int& nIndex, COLORREF& rgb) const;

	// Đếm số màu thực sự xuất hiện trong ảnh (trả lời câu hỏi 3)
	int   CountUsedColors() const;

// ===================== ĐỌC / GHI ẢNH =====================
public:
	// Cách 1: đọc tuần tự theo cấu trúc tệp BMP bằng CFile (kèm bắt ngoại lệ)
	BOOL ReadBmpByCFile(LPCTSTR lpszPathName, CString& strError,
	                    BITMAPINFO*& pBMI, BYTE*& pBits, DWORD& dwSize);
	// Cách 2: đọc bằng hàm API ::LoadImage rồi lấy dữ liệu ra bằng ::GetDIBits
	BOOL ReadBmpByLoadImage(LPCTSTR lpszPathName, CString& strError,
	                        BITMAPINFO*& pBMI, BYTE*& pBits, DWORD& dwSize);
	// Kiểm tra các điều kiện hợp lệ của ảnh (xử lý ngoại lệ - yêu cầu 4)
	BOOL ValidateBitmap(const BITMAPINFOHEADER* pbih, CString& strError) const;
	// Tạo CBitmap (DIB Section) + CPalette từ dữ liệu vừa đọc
	BOOL CreateGdiObjects(BITMAPINFO* pBMI, BYTE* pBits, DWORD dwSize, CString& strError);
	// Giải phóng toàn bộ dữ liệu ảnh
	void ReleaseImage();
	// Ghi ảnh (đã xử lý) ra tệp .BMP
	BOOL WriteBmpFile(LPCTSTR lpszPathName, CString& strError);

	// Cập nhật lại bảng màu của DIB Section sau khi sửa bảng màu trong m_pBMI
	void ApplyPaletteToBitmap();
	// Tạo lại bảng màu logic (CPalette) từ bảng màu của ảnh
	void RebuildLogicalPalette();

	// ---- Bản sao (câu hỏi 5) ----
	BOOL MakeBackup(CString& strError);
	BOOL RestoreFromBackup();
	void ReleaseBackup();

// ===================== CÁC PHÉP XỬ LÝ MINH HỌA =====================
public:
	void ProcessFlipHorizontal();	// thao tác trực tiếp trên VÙNG DỮ LIỆU
	void ProcessNegative();			// ảnh âm bản
	void ProcessGray();				// chuyển ảnh xám
	void PaletteRotate(int nStep);	// xoay vòng BẢNG MÀU
	void PaletteReverse();			// đảo ngược thứ tự BẢNG MÀU
	CString GetImageInfoString() const;

// Overrides
public:
	virtual BOOL OnNewDocument();
	virtual void Serialize(CArchive& ar);
	virtual BOOL OnOpenDocument(LPCTSTR lpszPathName);
	virtual BOOL OnSaveDocument(LPCTSTR lpszPathName);
	virtual void DeleteContents();

// Implementation
public:
	virtual ~CImageProcessingDoc();
#ifdef _DEBUG
	virtual void AssertValid() const;
	virtual void Dump(CDumpContext& dc) const;
#endif

protected:
	DECLARE_MESSAGE_MAP()
};
