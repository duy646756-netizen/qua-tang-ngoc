// ImageProcessingDoc.cpp : cài đặt lớp CImageProcessingDoc
//
// Bài thực hành số 1 - Đọc và hiển thị ảnh Bitmap

#include "stdafx.h"
#include "ImageProcessing.h"
#include "ImageProcessingDoc.h"
#include "MainFrm.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#endif

// Kích thước bộ đệm dùng cho BITMAPINFO: tiêu đề ảnh + bảng màu đủ 256 phần tử
#define BMI_BUFFER_SIZE (sizeof(BITMAPINFOHEADER) + 256 * sizeof(RGBQUAD))

// Tính số byte của một dòng ảnh: LUÔN được làm tròn lên bội số của 4 byte
static int CalcRowBytes(int nWidth, int nBitCount)
{
	return ((nWidth * nBitCount + 31) / 32) * 4;
}

// ============================================================================
IMPLEMENT_DYNCREATE(CImageProcessingDoc, CDocument)

BEGIN_MESSAGE_MAP(CImageProcessingDoc, CDocument)
END_MESSAGE_MAP()

CImageProcessingDoc::CImageProcessingDoc()
{
	ZeroMemory(&m_bmfHeader, sizeof(m_bmfHeader));
	m_pBMI          = NULL;
	m_pDibBits      = NULL;
	m_dwImageSize   = 0;
	m_nRowBytes     = 0;
	m_hBitmap       = NULL;
	m_nReadMode     = READ_BY_CFILE;

	m_pBackupBMI    = NULL;
	m_pBackupBits   = NULL;
	m_hBitmapBackup = NULL;

	// Theo tài liệu: quản số của lớp CBitmap phải được đặt NULL khi khởi tạo
	m_bmBitmap.m_hObject = NULL;
	m_bmBackup.m_hObject = NULL;
	m_palLogical.m_hObject = NULL;
}

CImageProcessingDoc::~CImageProcessingDoc()
{
	ReleaseImage();
	ReleaseBackup();
}

BOOL CImageProcessingDoc::OnNewDocument()
{
	if (!CDocument::OnNewDocument())
		return FALSE;
	return TRUE;
}

// DeleteContents được khung MFC gọi trước mỗi lần mở tài liệu mới
void CImageProcessingDoc::DeleteContents()
{
	ReleaseImage();
	ReleaseBackup();
	ZeroMemory(&m_bmfHeader, sizeof(m_bmfHeader));
	m_strFilePath.Empty();
	CDocument::DeleteContents();
}

void CImageProcessingDoc::Serialize(CArchive& ar)
{
	// Ảnh Bitmap được đọc/ghi trực tiếp theo cấu trúc tệp trong
	// OnOpenDocument / OnSaveDocument nên không dùng cơ chế serialize.
	UNREFERENCED_PARAMETER(ar);
}

// ============================================================================
// GIẢI PHÓNG DỮ LIỆU
// ============================================================================
void CImageProcessingDoc::ReleaseImage()
{
	// Chú ý: m_pDibBits KHÔNG được delete vì nó trỏ vào vùng nhớ của DIB Section,
	// vùng nhớ này được Windows giải phóng khi xoá đối tượng bitmap.
	if (m_bmBitmap.m_hObject != NULL)
		m_bmBitmap.DeleteObject();
	else if (m_hBitmap != NULL)
		::DeleteObject(m_hBitmap);
	m_hBitmap  = NULL;
	m_pDibBits = NULL;

	if (m_palLogical.m_hObject != NULL)
		m_palLogical.DeleteObject();

	if (m_pBMI != NULL)
	{
		delete[] (BYTE*)m_pBMI;
		m_pBMI = NULL;
	}
	// Chú ý: KHÔNG xoá m_bmfHeader ở đây, vì hàm CreateGdiObjects gọi ReleaseImage()
	// sau khi phần đọc tệp đã điền xong tiêu đề tệp.
	m_dwImageSize = 0;
	m_nRowBytes   = 0;
}

void CImageProcessingDoc::ReleaseBackup()
{
	if (m_bmBackup.m_hObject != NULL)
		m_bmBackup.DeleteObject();
	else if (m_hBitmapBackup != NULL)
		::DeleteObject(m_hBitmapBackup);
	m_hBitmapBackup = NULL;

	if (m_pBackupBMI != NULL)
	{
		delete[] (BYTE*)m_pBackupBMI;
		m_pBackupBMI = NULL;
	}
	if (m_pBackupBits != NULL)
	{
		delete[] m_pBackupBits;
		m_pBackupBits = NULL;
	}
}

// ============================================================================
// MỞ ẢNH - Yêu cầu 1, 2 và 4 của bài thực hành
// ============================================================================
BOOL CImageProcessingDoc::OnOpenDocument(LPCTSTR lpszPathName)
{
	// Gọi lớp cơ sở: kiểm tra tệp có tồn tại không và gọi DeleteContents()
	if (!CDocument::OnOpenDocument(lpszPathName))
		return FALSE;

	CString strError;
	BITMAPINFO* pBMI  = NULL;	// bộ đệm tạm chứa tiêu đề ảnh + bảng màu
	BYTE*       pBits = NULL;	// bộ đệm tạm chứa vùng dữ liệu điểm ảnh
	DWORD       dwSize = 0;

	// ---- BƯỚC 1: đọc nội dung tệp ảnh (2 cách, chọn trong menu "Đọc ảnh") ----
	BOOL bOK = (m_nReadMode == READ_BY_LOADIMAGE)
		? ReadBmpByLoadImage(lpszPathName, strError, pBMI, pBits, dwSize)
		: ReadBmpByCFile(lpszPathName, strError, pBMI, pBits, dwSize);

	if (!bOK)
	{
		// ---- Xử lý ngoại lệ: thông báo lỗi và KHÔNG mở tài liệu ----
		if (pBMI  != NULL) delete[] (BYTE*)pBMI;
		if (pBits != NULL) delete[] pBits;
		AfxMessageBox(strError, MB_OK | MB_ICONEXCLAMATION);
		return FALSE;
	}

	// ---- BƯỚC 2: tạo CBitmap + CPalette từ dữ liệu vừa đọc ----
	// (CreateGdiObjects nhận quyền quản lý pBMI; pBits chỉ được sao chép)
	if (!CreateGdiObjects(pBMI, pBits, dwSize, strError))
	{
		delete[] pBits;
		AfxMessageBox(strError, MB_OK | MB_ICONEXCLAMATION);
		return FALSE;
	}
	delete[] pBits;		// dữ liệu đã được sao vào DIB Section

	m_strFilePath = lpszPathName;

	// ---- BƯỚC 3: tạo sẵn một bản sao dự phòng (câu hỏi 5) ----
	CString strTmp;
	MakeBackup(strTmp);

	SetModifiedFlag(FALSE);
	return TRUE;
}

// ============================================================================
// CÁCH 1: ĐỌC TUẦN TỰ THEO CẤU TRÚC TỆP BMP BẰNG CFile
// Cấu trúc tệp: [BITMAPFILEHEADER][BITMAPINFOHEADER][bảng màu][dữ liệu điểm ảnh]
// ============================================================================
BOOL CImageProcessingDoc::ReadBmpByCFile(LPCTSTR lpszPathName, CString& strError,
                                         BITMAPINFO*& pBMI, BYTE*& pBits, DWORD& dwSize)
{
	pBMI = NULL; pBits = NULL; dwSize = 0;

	// ---- Ngoại lệ 1: phần mở rộng của tệp phải là .BMP ----
	CString strPath(lpszPathName);
	int nDot = strPath.ReverseFind(_T('.'));
	CString strExt = (nDot >= 0) ? strPath.Mid(nDot + 1) : _T("");
	if (strExt.CompareNoCase(_T("bmp")) != 0 && strExt.CompareNoCase(_T("dib")) != 0)
	{
		strError.Format(_T("Tệp \"%s\" không phải là ảnh Bitmap.\n")
			_T("Chương trình chỉ mở được tệp ảnh Bitmap (*.bmp, *.dib)."), strPath);
		return FALSE;
	}

	CFile file;
	CFileException fe;
	// ---- Ngoại lệ 2: không mở được tệp ----
	if (!file.Open(strPath, CFile::modeRead | CFile::shareDenyWrite | CFile::typeBinary, &fe))
	{
		TCHAR szCause[255] = { 0 };
		fe.GetErrorMessage(szCause, 255);
		strError.Format(_T("Không mở được tệp:\n%s\n%s"), strPath, szCause);
		return FALSE;
	}

	BITMAPFILEHEADER bmfh;
	BITMAPINFOHEADER bih;
	ZeroMemory(&bmfh, sizeof(bmfh));
	ZeroMemory(&bih,  sizeof(bih));

	try
	{
		// ---- Đọc 14 byte BITMAPFILEHEADER ----
		if (file.Read(&bmfh, sizeof(BITMAPFILEHEADER)) != sizeof(BITMAPFILEHEADER))
		{
			strError = _T("Tệp quá ngắn: không đọc được BITMAPFILEHEADER.");
			file.Close();
			return FALSE;
		}

		// ---- Ngoại lệ 3: 2 byte đầu tiên phải là chữ "BM" (0x4D42) ----
		if (bmfh.bfType != 0x4D42)
		{
			strError.Format(_T("Tệp \"%s\" KHÔNG phải là ảnh Bitmap.\n")
				_T("Hai byte đầu của tệp là 0x%04X, trong khi ảnh BMP phải là 0x4D42 (\"BM\")."),
				strPath, bmfh.bfType);
			file.Close();
			return FALSE;
		}

		// ---- Đọc 40 byte BITMAPINFOHEADER ----
		if (file.Read(&bih, sizeof(BITMAPINFOHEADER)) != sizeof(BITMAPINFOHEADER))
		{
			strError = _T("Tệp hỏng: không đọc được BITMAPINFOHEADER.");
			file.Close();
			return FALSE;
		}

		// ---- Ngoại lệ 4: kiểm tra số bit/pixel, cách nén, kích thước ----
		if (!ValidateBitmap(&bih, strError))
		{
			file.Close();
			return FALSE;
		}

		// Nếu tiêu đề dài hơn 40 byte (BITMAPV4/V5HEADER) thì bỏ qua phần dư
		if (bih.biSize > sizeof(BITMAPINFOHEADER))
			file.Seek(bih.biSize - sizeof(BITMAPINFOHEADER), CFile::current);

		// ---- Cấp phát bộ đệm cho BITMAPINFOHEADER + bảng màu ----
		pBMI = (BITMAPINFO*) new BYTE[BMI_BUFFER_SIZE];
		ZeroMemory(pBMI, BMI_BUFFER_SIZE);
		pBMI->bmiHeader = bih;
		pBMI->bmiHeader.biSize = sizeof(BITMAPINFOHEADER);

		// ---- Đọc BẢNG MÀU (chỉ ảnh <= 8 bit/pixel mới có bảng màu) ----
		int nColors = 0;
		if (bih.biBitCount <= 8)
		{
			nColors = (bih.biClrUsed != 0) ? (int)bih.biClrUsed : (1 << bih.biBitCount);
			if (nColors > 256) nColors = 256;
			UINT nNeed = (UINT)(nColors * sizeof(RGBQUAD));
			if (file.Read(pBMI->bmiColors, nNeed) != nNeed)
			{
				strError = _T("Tệp hỏng: không đọc được bảng màu (palette).");
				file.Close();
				return FALSE;
			}
		}
		pBMI->bmiHeader.biClrUsed = (DWORD)nColors;

		// ---- Nhảy tới vùng dữ liệu điểm ảnh theo bfOffBits ----
		if (bmfh.bfOffBits != 0)
			file.Seek(bmfh.bfOffBits, CFile::begin);

		int nWidth   = (int)bih.biWidth;
		BOOL bTopDown = (bih.biHeight < 0);	// biHeight < 0 => ảnh lưu xuôi (top-down)
		int nHeight  = bTopDown ? -(int)bih.biHeight : (int)bih.biHeight;
		int nRowBytes = CalcRowBytes(nWidth, bih.biBitCount);
		dwSize = (DWORD)nRowBytes * nHeight;

		// ---- Đọc VÙNG DỮ LIỆU ĐIỂM ẢNH ----
		pBits = new BYTE[dwSize];
		ZeroMemory(pBits, dwSize);
		UINT nRead = file.Read(pBits, dwSize);
		if (nRead < dwSize)
		{
			strError.Format(_T("Tệp ảnh bị cắt cụt: cần %lu byte dữ liệu nhưng chỉ đọc được %u byte."),
				dwSize, nRead);
			file.Close();
			return FALSE;
		}
		file.Close();

		// ---- Chuẩn hoá: luôn lưu theo kiểu bottom-up (lộn ngược) ----
		if (bTopDown)
		{
			BYTE* pTmp = new BYTE[nRowBytes];
			for (int y = 0; y < nHeight / 2; y++)
			{
				BYTE* p1 = pBits + (DWORD)y * nRowBytes;
				BYTE* p2 = pBits + (DWORD)(nHeight - 1 - y) * nRowBytes;
				memcpy(pTmp, p1, nRowBytes);
				memcpy(p1, p2, nRowBytes);
				memcpy(p2, pTmp, nRowBytes);
			}
			delete[] pTmp;
		}

		pBMI->bmiHeader.biHeight      = nHeight;	// luôn dương
		pBMI->bmiHeader.biSizeImage   = dwSize;
		pBMI->bmiHeader.biCompression = BI_RGB;
		m_bmfHeader = bmfh;
	}
	catch (CFileException* pEx)
	{
		TCHAR szCause[255] = { 0 };
		pEx->GetErrorMessage(szCause, 255);
		strError.Format(_T("Lỗi khi đọc tệp ảnh:\n%s"), szCause);
		pEx->Delete();
		return FALSE;
	}
	catch (CMemoryException* pEx)
	{
		strError = _T("Không đủ bộ nhớ để đọc ảnh.");
		pEx->Delete();
		return FALSE;
	}
	return TRUE;
}

// ============================================================================
// KIỂM TRA TÍNH HỢP LỆ CỦA ẢNH - phần XỬ LÝ NGOẠI LỆ (yêu cầu 4)
// ============================================================================
BOOL CImageProcessingDoc::ValidateBitmap(const BITMAPINFOHEADER* pbih, CString& strError) const
{
	if (pbih->biSize < sizeof(BITMAPINFOHEADER))
	{
		strError = _T("Ảnh dùng tiêu đề kiểu OS/2 (BITMAPCOREHEADER) - chương trình không hỗ trợ.");
		return FALSE;
	}
	if (pbih->biWidth <= 0 || pbih->biHeight == 0)
	{
		strError = _T("Kích thước ảnh không hợp lệ.");
		return FALSE;
	}
	if (pbih->biCompression != BI_RGB)
	{
		strError.Format(_T("Ảnh BMP đang ở dạng NÉN (biCompression = %lu).\n")
			_T("Chương trình chỉ xử lý ảnh BMP không nén (BI_RGB)."), pbih->biCompression);
		return FALSE;
	}

	int nBits = pbih->biBitCount;

	// Yêu cầu của bài: CHỈ thao tác với ảnh BMP 256 màu (8 bit/pixel).
	// Có thể tắt ràng buộc này trong menu "Tuỳ chọn" để mở rộng cho ảnh 24 bit.
	if (theApp.m_bOnly256Colors)
	{
		if (nBits != 8)
		{
			strError.Format(
				_T("Ảnh này là ảnh %d bit/pixel (%s).\n\n")
				_T("Chương trình đang đặt ở chế độ CHỈ NHẬN ảnh Bitmap 256 màu (8 bit/pixel).\n")
				_T("Vào menu \"Tuỳ chọn / Chỉ nhận ảnh 256 màu\" để bỏ ràng buộc này ")
				_T("nếu muốn mở thêm ảnh 24 bit."),
				nBits,
				(nBits == 1) ? _T("ảnh đen trắng") :
				(nBits == 4) ? _T("16 màu") :
				(nBits == 16) ? _T("65536 màu") :
				(nBits == 24) ? _T("16 triệu màu") : _T("true color"));
			return FALSE;
		}
	}
	else if (nBits != 8 && nBits != 24)
	{
		strError.Format(_T("Chương trình chỉ hỗ trợ ảnh BMP 256 màu (8 bit/pixel) ")
			_T("và ảnh BMP 24 bit màu.\nẢnh đang mở là ảnh %d bit/pixel."), nBits);
		return FALSE;
	}
	return TRUE;
}

// ============================================================================
// CÁCH 2: ĐỌC ẢNH BẰNG HÀM API ::LoadImage (đúng như tài liệu hướng dẫn)
// Sau đó dùng ::GetDIBColorTable và ::GetDIBits để lấy bảng màu + vùng dữ liệu
// ============================================================================
BOOL CImageProcessingDoc::ReadBmpByLoadImage(LPCTSTR lpszPathName, CString& strError,
                                             BITMAPINFO*& pBMI, BYTE*& pBits, DWORD& dwSize)
{
	pBMI = NULL; pBits = NULL; dwSize = 0;

	// ---- Ngoại lệ 1: phần mở rộng phải là .BMP ----
	CString strPath(lpszPathName);
	int nDot = strPath.ReverseFind(_T('.'));
	CString strExt = (nDot >= 0) ? strPath.Mid(nDot + 1) : _T("");
	if (strExt.CompareNoCase(_T("bmp")) != 0 && strExt.CompareNoCase(_T("dib")) != 0)
	{
		strError.Format(_T("Tệp \"%s\" không phải là ảnh Bitmap.\n")
			_T("Chương trình chỉ mở được tệp ảnh Bitmap (*.bmp, *.dib)."), strPath);
		return FALSE;
	}

	// ---- Nạp ảnh từ tệp, chuyển thành quản số bitmap ----
	HBITMAP hBmp = (HBITMAP)::LoadImage(AfxGetInstanceHandle(),
	                                    lpszPathName,
	                                    IMAGE_BITMAP, 0, 0,
	                                    LR_LOADFROMFILE | LR_CREATEDIBSECTION);
	// ---- Ngoại lệ 2: LoadImage trả về NULL nếu tệp không phải BMP hợp lệ ----
	if (hBmp == NULL)
	{
		strError.Format(_T("Hàm ::LoadImage không đọc được tệp \"%s\".\n")
			_T("Tệp không phải ảnh Bitmap hợp lệ hoặc đã bị hỏng."), strPath);
		return FALSE;
	}

	// ---- Lấy thông tin ảnh: dùng cấu trúc BITMAP ----
	BITMAP bm;
	ZeroMemory(&bm, sizeof(bm));
	if (::GetObject(hBmp, sizeof(BITMAP), &bm) == 0)
	{
		::DeleteObject(hBmp);
		strError = _T("Không lấy được thông tin BITMAP của ảnh.");
		return FALSE;
	}

	pBMI = (BITMAPINFO*) new BYTE[BMI_BUFFER_SIZE];
	ZeroMemory(pBMI, BMI_BUFFER_SIZE);
	BITMAPINFOHEADER& bih = pBMI->bmiHeader;
	bih.biSize        = sizeof(BITMAPINFOHEADER);
	bih.biWidth       = bm.bmWidth;
	bih.biHeight      = bm.bmHeight;
	bih.biPlanes      = 1;
	bih.biBitCount    = bm.bmBitsPixel;
	bih.biCompression = BI_RGB;

	// ---- Ngoại lệ 3: kiểm tra số bit/pixel (chỉ nhận ảnh 256 màu) ----
	if (!ValidateBitmap(&bih, strError))
	{
		::DeleteObject(hBmp);
		delete[] (BYTE*)pBMI;
		pBMI = NULL;
		return FALSE;
	}

	HDC hdcMem = ::CreateCompatibleDC(NULL);
	int nColors = (bm.bmBitsPixel <= 8) ? (1 << bm.bmBitsPixel) : 0;
	if (nColors > 0)
	{
		// Muốn đọc BẢNG MÀU thì bitmap phải đang được gắn vào ngữ cảnh thiết bị
		HGDIOBJ hOld = ::SelectObject(hdcMem, hBmp);
		::GetDIBColorTable(hdcMem, 0, nColors, pBMI->bmiColors);
		::SelectObject(hdcMem, hOld);	// phải gỡ ra trước khi gọi GetDIBits
	}

	int nRowBytes = CalcRowBytes(bm.bmWidth, bm.bmBitsPixel);
	dwSize = (DWORD)nRowBytes * bm.bmHeight;
	bih.biSizeImage = dwSize;
	bih.biClrUsed   = (DWORD)nColors;

	pBits = new BYTE[dwSize];
	ZeroMemory(pBits, dwSize);

	// ---- Lấy VÙNG DỮ LIỆU điểm ảnh ra bộ đệm của chương trình ----
	int nLines = ::GetDIBits(hdcMem, hBmp, 0, bm.bmHeight, pBits, pBMI, DIB_RGB_COLORS);
	::DeleteDC(hdcMem);
	::DeleteObject(hBmp);	// đã lấy xong dữ liệu, không cần quản số này nữa

	if (nLines == 0)
	{
		strError = _T("Hàm ::GetDIBits không lấy được vùng dữ liệu của ảnh.");
		return FALSE;
	}

	// GetDIBits có thể sửa lại các trường của tiêu đề -> đặt lại cho chắc chắn
	bih.biSize        = sizeof(BITMAPINFOHEADER);
	bih.biHeight      = bm.bmHeight;
	bih.biCompression = BI_RGB;
	bih.biSizeImage   = dwSize;
	bih.biClrUsed     = (DWORD)nColors;

	// Dựng lại BITMAPFILEHEADER cho đồng bộ với cách đọc bằng CFile
	ZeroMemory(&m_bmfHeader, sizeof(m_bmfHeader));
	m_bmfHeader.bfType    = 0x4D42;
	m_bmfHeader.bfOffBits = (DWORD)(sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER)
	                      + nColors * sizeof(RGBQUAD));
	m_bmfHeader.bfSize    = m_bmfHeader.bfOffBits + dwSize;
	return TRUE;
}

// ============================================================================
// TẠO CBitmap (DIB Section) VÀ CPalette TỪ DỮ LIỆU VỪA ĐỌC
// Dùng DIB Section để m_pDibBits trỏ THẲNG vào vùng nhớ của bitmap: mọi thay
// đổi trên vùng dữ liệu đều hiển thị ngay, không phải sao chép qua lại.
// ============================================================================
BOOL CImageProcessingDoc::CreateGdiObjects(BITMAPINFO* pBMI, BYTE* pBits,
                                           DWORD dwSize, CString& strError)
{
	ReleaseImage();
	m_pBMI = pBMI;			// từ đây lớp Document quản lý bộ đệm này

	m_nRowBytes   = CalcRowBytes(GetWidth(), GetBitCount());
	m_dwImageSize = dwSize;

	BYTE* pSectionBits = NULL;
	HDC hdcScreen = ::GetDC(NULL);
	m_hBitmap = ::CreateDIBSection(hdcScreen, m_pBMI, DIB_RGB_COLORS,
	                               (void**)&pSectionBits, NULL, 0);
	::ReleaseDC(NULL, hdcScreen);

	if (m_hBitmap == NULL || pSectionBits == NULL)
	{
		strError = _T("Không tạo được đối tượng Bitmap trong bộ nhớ (CreateDIBSection thất bại).");
		ReleaseImage();
		return FALSE;
	}

	memcpy(pSectionBits, pBits, dwSize);
	m_pDibBits = pSectionBits;

	// Gắn quản số bitmap cho lớp CBitmap của MFC
	m_bmBitmap.Attach(m_hBitmap);

	// Tạo bảng màu logic (chỉ có tác dụng khi màn hình đang ở chế độ 256 màu)
	RebuildLogicalPalette();
	return TRUE;
}

// Tạo lại bảng màu logic CPalette từ bảng màu của ảnh
void CImageProcessingDoc::RebuildLogicalPalette()
{
	if (m_palLogical.m_hObject != NULL)
		m_palLogical.DeleteObject();

	int n = GetPaletteEntries();
	if (n <= 0 || GetPalette() == NULL)
		return;

	BYTE* pBuf = new BYTE[sizeof(LOGPALETTE) + n * sizeof(PALETTEENTRY)];
	LOGPALETTE* pLP = (LOGPALETTE*)pBuf;
	pLP->palVersion    = 0x300;
	pLP->palNumEntries = (WORD)n;
	RGBQUAD* pRGB = GetPalette();
	for (int i = 0; i < n; i++)
	{
		pLP->palPalEntry[i].peRed   = pRGB[i].rgbRed;
		pLP->palPalEntry[i].peGreen = pRGB[i].rgbGreen;
		pLP->palPalEntry[i].peBlue  = pRGB[i].rgbBlue;
		pLP->palPalEntry[i].peFlags = 0;
	}
	m_palLogical.CreatePalette(pLP);
	delete[] pBuf;
}

// Sau khi sửa bảng màu trong m_pBMI phải cập nhật lại cho DIB Section
void CImageProcessingDoc::ApplyPaletteToBitmap()
{
	if (m_hBitmap == NULL || GetBitCount() > 8 || GetPaletteEntries() <= 0)
		return;
	HDC hdcMem = ::CreateCompatibleDC(NULL);
	HGDIOBJ hOld = ::SelectObject(hdcMem, m_hBitmap);
	::SetDIBColorTable(hdcMem, 0, GetPaletteEntries(), GetPalette());
	::SelectObject(hdcMem, hOld);
	::DeleteDC(hdcMem);
	RebuildLogicalPalette();
}

// ============================================================================
// GHI ẢNH (đã xử lý) RA TỆP .BMP
// ============================================================================
BOOL CImageProcessingDoc::OnSaveDocument(LPCTSTR lpszPathName)
{
	if (!HasImage())
	{
		AfxMessageBox(_T("Chưa có ảnh nào để ghi."), MB_OK | MB_ICONINFORMATION);
		return FALSE;
	}
	CString strError;
	if (!WriteBmpFile(lpszPathName, strError))
	{
		AfxMessageBox(strError, MB_OK | MB_ICONEXCLAMATION);
		return FALSE;
	}
	m_strFilePath = lpszPathName;
	SetModifiedFlag(FALSE);
	return TRUE;
}

BOOL CImageProcessingDoc::WriteBmpFile(LPCTSTR lpszPathName, CString& strError)
{
	CFile file;
	CFileException fe;
	if (!file.Open(lpszPathName, CFile::modeCreate | CFile::modeWrite | CFile::typeBinary, &fe))
	{
		TCHAR szCause[255] = { 0 };
		fe.GetErrorMessage(szCause, 255);
		strError.Format(_T("Không ghi được tệp:\n%s\n%s"), lpszPathName, szCause);
		return FALSE;
	}
	try
	{
		int nColors = GetPaletteEntries();
		BITMAPFILEHEADER bmfh;
		ZeroMemory(&bmfh, sizeof(bmfh));
		bmfh.bfType    = 0x4D42;	// "BM"
		bmfh.bfOffBits = (DWORD)(sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER)
		               + nColors * sizeof(RGBQUAD));
		bmfh.bfSize    = bmfh.bfOffBits + m_dwImageSize;

		file.Write(&bmfh, sizeof(BITMAPFILEHEADER));
		file.Write(&m_pBMI->bmiHeader, sizeof(BITMAPINFOHEADER));
		if (nColors > 0)
			file.Write(m_pBMI->bmiColors, (UINT)(nColors * sizeof(RGBQUAD)));
		file.Write(m_pDibBits, m_dwImageSize);
		file.Close();
		m_bmfHeader = bmfh;
	}
	catch (CFileException* pEx)
	{
		TCHAR szCause[255] = { 0 };
		pEx->GetErrorMessage(szCause, 255);
		strError.Format(_T("Lỗi khi ghi tệp ảnh:\n%s"), szCause);
		pEx->Delete();
		return FALSE;
	}
	return TRUE;
}

// ============================================================================
// TRUY CẬP VÙNG DỮ LIỆU ĐIỂM ẢNH (trả lời câu hỏi 4)
// Ảnh BMP được lưu LỘN NGƯỢC: dòng đầu tiên trong bộ nhớ là dòng DƯỚI CÙNG.
// Mỗi dòng ảnh chiếm m_nRowBytes byte (đã làm tròn lên bội số của 4).
// ============================================================================
BYTE* CImageProcessingDoc::GetLinePtr(int y) const
{
	if (!HasImage() || y < 0 || y >= GetHeight())
		return NULL;
	return m_pDibBits + (DWORD)(GetHeight() - 1 - y) * m_nRowBytes;
}

BOOL CImageProcessingDoc::GetPixelInfo(int x, int y, int& nIndex, COLORREF& rgb) const
{
	nIndex = -1;
	rgb = 0;
	if (!HasImage() || x < 0 || x >= GetWidth() || y < 0 || y >= GetHeight())
		return FALSE;

	BYTE* pLine = GetLinePtr(y);
	if (pLine == NULL) return FALSE;

	if (GetBitCount() == 8)
	{
		nIndex = pLine[x];				// giá trị điểm ảnh = CHỈ SỐ trong bảng màu
		RGBQUAD* p = GetPalette();
		if (p != NULL && nIndex < GetPaletteEntries())
			rgb = RGB(p[nIndex].rgbRed, p[nIndex].rgbGreen, p[nIndex].rgbBlue);
	}
	else if (GetBitCount() == 24)
	{
		BYTE* p = pLine + x * 3;		// thứ tự byte trong BMP là B, G, R
		rgb = RGB(p[2], p[1], p[0]);
	}
	return TRUE;
}

// Đếm số màu THỰC SỰ được dùng trong ảnh (trả lời câu hỏi 3)
int CImageProcessingDoc::CountUsedColors() const
{
	if (!HasImage()) return 0;

	if (GetBitCount() == 8)
	{
		// Ảnh 256 màu: đếm số chỉ số bảng màu thực sự xuất hiện
		bool bUsed[256] = { false };
		for (int y = 0; y < GetHeight(); y++)
		{
			BYTE* pLine = GetLinePtr(y);
			for (int x = 0; x < GetWidth(); x++)
				bUsed[pLine[x]] = true;
		}
		int n = 0;
		for (int i = 0; i < 256; i++) if (bUsed[i]) n++;
		return n;
	}
	else if (GetBitCount() == 24)
	{
		std::set<DWORD> setColors;
		for (int y = 0; y < GetHeight(); y++)
		{
			BYTE* pLine = GetLinePtr(y);
			for (int x = 0; x < GetWidth(); x++)
			{
				BYTE* p = pLine + x * 3;
				setColors.insert(((DWORD)p[2] << 16) | ((DWORD)p[1] << 8) | p[0]);
			}
		}
		return (int)setColors.size();
	}
	return 0;
}

CString CImageProcessingDoc::GetImageInfoString() const
{
	CString s;
	if (!HasImage())
		return CString(_T("Chưa mở ảnh nào."));

	int nBits = GetBitCount();
	CString strLoai;
	if (nBits == 8)       strLoai = _T("Bitmap 256 màu (có bảng màu)");
	else if (nBits == 24) strLoai = _T("Bitmap 24 bit màu (không có bảng màu)");
	else                  strLoai.Format(_T("Bitmap %d bit/pixel"), nBits);

	s.Format(
		_T("TỆP ẢNH\n")
		_T("    Đường dẫn        : %s\n")
		_T("    Cách đọc         : %s\n\n")
		_T("BITMAPFILEHEADER\n")
		_T("    bfType           : 0x%04X (\"BM\")\n")
		_T("    bfSize           : %lu byte\n")
		_T("    bfOffBits        : %lu (vị trí bắt đầu vùng dữ liệu)\n\n")
		_T("BITMAPINFOHEADER\n")
		_T("    biWidth          : %d pixel\n")
		_T("    biHeight         : %d pixel\n")
		_T("    biBitCount       : %d bit/pixel  ->  %s\n")
		_T("    biCompression    : %lu (0 = BI_RGB, không nén)\n")
		_T("    biClrUsed        : %d phần tử bảng màu\n\n")
		_T("VÙNG DỮ LIỆU\n")
		_T("    Số byte một dòng : %d byte (đã làm tròn bội số 4)\n")
		_T("    Tổng dữ liệu     : %lu byte\n\n")
		_T("SỐ MÀU\n")
		_T("    Số màu tối đa    : %d màu (= 2^%d)\n")
		_T("    Số màu thực dùng : %d màu"),
		m_strFilePath,
		(m_nReadMode == READ_BY_LOADIMAGE) ? _T("Hàm API ::LoadImage") : _T("Đọc tuần tự bằng CFile"),
		m_bmfHeader.bfType, m_bmfHeader.bfSize, m_bmfHeader.bfOffBits,
		GetWidth(), GetHeight(), nBits, strLoai,
		m_pBMI->bmiHeader.biCompression, GetPaletteEntries(),
		m_nRowBytes, m_dwImageSize,
		(nBits >= 24) ? 16777216 : (1 << nBits), nBits,
		CountUsedColors());
	return s;
}

// ============================================================================
// BẢN SAO CỦA ẢNH (trả lời câu hỏi 5)
// ============================================================================
BOOL CImageProcessingDoc::MakeBackup(CString& strError)
{
	if (!HasImage())
	{
		strError = _T("Chưa có ảnh để tạo bản sao.");
		return FALSE;
	}
	ReleaseBackup();

	// --- Cách A: sao chép thẳng vùng dữ liệu + bảng màu sang bộ đệm riêng ---
	m_pBackupBMI = (BITMAPINFO*) new BYTE[BMI_BUFFER_SIZE];
	memcpy(m_pBackupBMI, m_pBMI, BMI_BUFFER_SIZE);
	m_pBackupBits = new BYTE[m_dwImageSize];
	memcpy(m_pBackupBits, m_pDibBits, m_dwImageSize);

	// --- Cách B: tạo một HBITMAP hoàn toàn độc lập bằng hàm API ::CopyImage,
	//     rồi gắn cho một lớp CBitmap khác. (Không được gán m_bmB = m_bmBitmap
	//     vì như thế hai lớp cùng dùng CHUNG một quản số!)
	m_hBitmapBackup = (HBITMAP)::CopyImage(m_hBitmap, IMAGE_BITMAP, 0, 0, LR_CREATEDIBSECTION);
	if (m_hBitmapBackup != NULL)
		m_bmBackup.Attach(m_hBitmapBackup);

	return TRUE;
}

BOOL CImageProcessingDoc::RestoreFromBackup()
{
	if (!HasImage() || !HasBackup())
		return FALSE;
	memcpy(m_pBMI, m_pBackupBMI, BMI_BUFFER_SIZE);
	memcpy(m_pDibBits, m_pBackupBits, m_dwImageSize);
	ApplyPaletteToBitmap();
	SetModifiedFlag(TRUE);
	UpdateAllViews(NULL);
	return TRUE;
}

// ============================================================================
// CÁC PHÉP XỬ LÝ MINH HOẠ
// ============================================================================

// Lật ảnh theo chiều ngang - thao tác TRỰC TIẾP trên vùng dữ liệu điểm ảnh
void CImageProcessingDoc::ProcessFlipHorizontal()
{
	if (!HasImage()) return;
	int w = GetWidth(), h = GetHeight();

	if (GetBitCount() == 8)
	{
		for (int y = 0; y < h; y++)
		{
			BYTE* pLine = GetLinePtr(y);
			for (int x = 0; x < w / 2; x++)
			{
				BYTE t = pLine[x];
				pLine[x] = pLine[w - 1 - x];
				pLine[w - 1 - x] = t;
			}
		}
	}
	else if (GetBitCount() == 24)
	{
		for (int y = 0; y < h; y++)
		{
			BYTE* pLine = GetLinePtr(y);
			for (int x = 0; x < w / 2; x++)
			{
				BYTE* p1 = pLine + x * 3;
				BYTE* p2 = pLine + (w - 1 - x) * 3;
				for (int k = 0; k < 3; k++)
				{
					BYTE t = p1[k]; p1[k] = p2[k]; p2[k] = t;
				}
			}
		}
	}
	SetModifiedFlag(TRUE);
	UpdateAllViews(NULL);
}

// Ảnh âm bản
void CImageProcessingDoc::ProcessNegative()
{
	if (!HasImage()) return;

	if (GetBitCount() == 8)
	{
		// Ảnh 256 màu: giá trị điểm ảnh chỉ là CHỈ SỐ, muốn đảo màu thì
		// phải đảo các màu trong BẢNG MÀU chứ không phải đảo chỉ số.
		RGBQUAD* p = GetPalette();
		for (int i = 0; i < GetPaletteEntries(); i++)
		{
			p[i].rgbRed   = 255 - p[i].rgbRed;
			p[i].rgbGreen = 255 - p[i].rgbGreen;
			p[i].rgbBlue  = 255 - p[i].rgbBlue;
		}
		ApplyPaletteToBitmap();
	}
	else if (GetBitCount() == 24)
	{
		for (int y = 0; y < GetHeight(); y++)
		{
			BYTE* pLine = GetLinePtr(y);
			for (int x = 0; x < GetWidth() * 3; x++)
				pLine[x] = 255 - pLine[x];
		}
	}
	SetModifiedFlag(TRUE);
	UpdateAllViews(NULL);
}

// Chuyển sang ảnh xám theo công thức Y = 0.299R + 0.587G + 0.114B
void CImageProcessingDoc::ProcessGray()
{
	if (!HasImage()) return;

	if (GetBitCount() == 8)
	{
		RGBQUAD* p = GetPalette();
		for (int i = 0; i < GetPaletteEntries(); i++)
		{
			BYTE g = (BYTE)((299 * p[i].rgbRed + 587 * p[i].rgbGreen + 114 * p[i].rgbBlue) / 1000);
			p[i].rgbRed = p[i].rgbGreen = p[i].rgbBlue = g;
		}
		ApplyPaletteToBitmap();
	}
	else if (GetBitCount() == 24)
	{
		for (int y = 0; y < GetHeight(); y++)
		{
			BYTE* pLine = GetLinePtr(y);
			for (int x = 0; x < GetWidth(); x++)
			{
				BYTE* p = pLine + x * 3;	// B, G, R
				BYTE g = (BYTE)((299 * p[2] + 587 * p[1] + 114 * p[0]) / 1000);
				p[0] = p[1] = p[2] = g;
			}
		}
	}
	SetModifiedFlag(TRUE);
	UpdateAllViews(NULL);
}

// Xoay vòng bảng màu - minh hoạ thao tác với BẢNG MÀU (câu hỏi 4)
void CImageProcessingDoc::PaletteRotate(int nStep)
{
	if (!HasImage() || GetPaletteEntries() <= 0) return;
	int n = GetPaletteEntries();
	RGBQUAD* p = GetPalette();
	RGBQUAD* pTmp = new RGBQUAD[n];
	for (int i = 0; i < n; i++)
		pTmp[(i + nStep + n) % n] = p[i];
	memcpy(p, pTmp, n * sizeof(RGBQUAD));
	delete[] pTmp;
	ApplyPaletteToBitmap();
	SetModifiedFlag(TRUE);
	UpdateAllViews(NULL);
}

// Đảo ngược thứ tự bảng màu
void CImageProcessingDoc::PaletteReverse()
{
	if (!HasImage() || GetPaletteEntries() <= 0) return;
	int n = GetPaletteEntries();
	RGBQUAD* p = GetPalette();
	for (int i = 0; i < n / 2; i++)
	{
		RGBQUAD t = p[i];
		p[i] = p[n - 1 - i];
		p[n - 1 - i] = t;
	}
	ApplyPaletteToBitmap();
	SetModifiedFlag(TRUE);
	UpdateAllViews(NULL);
}

// ============================================================================
#ifdef _DEBUG
void CImageProcessingDoc::AssertValid() const
{
	CDocument::AssertValid();
}

void CImageProcessingDoc::Dump(CDumpContext& dc) const
{
	CDocument::Dump(dc);
}
#endif //_DEBUG
