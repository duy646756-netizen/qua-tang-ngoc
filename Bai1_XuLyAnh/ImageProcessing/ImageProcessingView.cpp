// ImageProcessingView.cpp : cài đặt lớp CImageProcessingView
//
// Bài thực hành số 1 - phần HIỂN THỊ ẢNH (yêu cầu 3)

#include "stdafx.h"
#include "ImageProcessing.h"
#include "ImageProcessingDoc.h"
#include "ImageProcessingView.h"
#include "MainFrm.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#endif

IMPLEMENT_DYNCREATE(CImageProcessingView, CScrollView)

BEGIN_MESSAGE_MAP(CImageProcessingView, CScrollView)
	ON_WM_SIZE()
	ON_WM_MOUSEMOVE()

	ON_COMMAND(ID_READ_BY_CFILE,     &CImageProcessingView::OnReadByCFile)
	ON_UPDATE_COMMAND_UI(ID_READ_BY_CFILE, &CImageProcessingView::OnUpdateReadByCFile)
	ON_COMMAND(ID_READ_BY_LOADIMAGE, &CImageProcessingView::OnReadByLoadImage)
	ON_UPDATE_COMMAND_UI(ID_READ_BY_LOADIMAGE, &CImageProcessingView::OnUpdateReadByLoadImage)

	ON_COMMAND(ID_DISP_SETDIBITS,  &CImageProcessingView::OnDispSetDIBits)
	ON_UPDATE_COMMAND_UI(ID_DISP_SETDIBITS, &CImageProcessingView::OnUpdateDispSetDIBits)
	ON_COMMAND(ID_DISP_STRETCHBLT, &CImageProcessingView::OnDispStretchBlt)
	ON_UPDATE_COMMAND_UI(ID_DISP_STRETCHBLT, &CImageProcessingView::OnUpdateDispStretchBlt)
	ON_COMMAND(ID_DISP_FITWINDOW,  &CImageProcessingView::OnDispFitWindow)
	ON_UPDATE_COMMAND_UI(ID_DISP_FITWINDOW, &CImageProcessingView::OnUpdateDispFitWindow)

	ON_COMMAND(ID_IMG_INFO,     &CImageProcessingView::OnImgInfo)
	ON_COMMAND(ID_IMG_FLIPH,    &CImageProcessingView::OnImgFlipH)
	ON_COMMAND(ID_IMG_NEGATIVE, &CImageProcessingView::OnImgNegative)
	ON_COMMAND(ID_IMG_GRAY,     &CImageProcessingView::OnImgGray)
	ON_COMMAND(ID_PAL_ROTATE,   &CImageProcessingView::OnPalRotate)
	ON_COMMAND(ID_PAL_REVERSE,  &CImageProcessingView::OnPalReverse)
	ON_COMMAND(ID_IMG_BACKUP,   &CImageProcessingView::OnImgBackup)
	ON_COMMAND(ID_IMG_RESTORE,  &CImageProcessingView::OnImgRestore)

	ON_UPDATE_COMMAND_UI(ID_IMG_INFO,     &CImageProcessingView::OnUpdateNeedImage)
	ON_UPDATE_COMMAND_UI(ID_IMG_FLIPH,    &CImageProcessingView::OnUpdateNeedImage)
	ON_UPDATE_COMMAND_UI(ID_IMG_NEGATIVE, &CImageProcessingView::OnUpdateNeedImage)
	ON_UPDATE_COMMAND_UI(ID_IMG_GRAY,     &CImageProcessingView::OnUpdateNeedImage)
	ON_UPDATE_COMMAND_UI(ID_IMG_BACKUP,   &CImageProcessingView::OnUpdateNeedImage)
	ON_UPDATE_COMMAND_UI(ID_PAL_ROTATE,   &CImageProcessingView::OnUpdateNeedPalette)
	ON_UPDATE_COMMAND_UI(ID_PAL_REVERSE,  &CImageProcessingView::OnUpdateNeedPalette)
	ON_UPDATE_COMMAND_UI(ID_IMG_RESTORE,  &CImageProcessingView::OnUpdateNeedBackup)
END_MESSAGE_MAP()

// ============================================================================
CImageProcessingView::CImageProcessingView()
{
	m_nDisplayMode = DISP_SETDIBITS;
	m_bFitWindow   = FALSE;
}

CImageProcessingView::~CImageProcessingView()
{
}

void CImageProcessingView::OnInitialUpdate()
{
	CScrollView::OnInitialUpdate();
	UpdateScrollSizes();
}

void CImageProcessingView::OnUpdate(CView* pSender, LPARAM lHint, CObject* pHint)
{
	UNREFERENCED_PARAMETER(pSender);
	UNREFERENCED_PARAMETER(lHint);
	UNREFERENCED_PARAMETER(pHint);

	UpdateScrollSizes();
	Invalidate(TRUE);

	// Hiện kích thước ảnh lên thanh trạng thái
	CImageProcessingDoc* pDoc = GetDocument();
	CString s;
	if (pDoc != NULL && pDoc->HasImage())
		s.Format(_T("%d x %d pixel - %d bit/pixel - %d màu trong bảng màu"),
			pDoc->GetWidth(), pDoc->GetHeight(), pDoc->GetBitCount(), pDoc->GetPaletteEntries());
	else
		s = _T("Chưa mở ảnh");
	ShowImageInfoOnStatusBar(s);
}

// Đặt kích thước vùng cuộn đúng bằng kích thước ảnh
void CImageProcessingView::UpdateScrollSizes()
{
	CImageProcessingDoc* pDoc = GetDocument();
	CSize sizeTotal(0, 0);
	if (!m_bFitWindow && pDoc != NULL && pDoc->HasImage())
		sizeTotal = CSize(pDoc->GetWidth(), pDoc->GetHeight());
	SetScrollSizes(MM_TEXT, sizeTotal);
}

void CImageProcessingView::ShowImageInfoOnStatusBar(LPCTSTR lpszText)
{
	CMainFrame* pFrame = DYNAMIC_DOWNCAST(CMainFrame, AfxGetMainWnd());
	if (pFrame != NULL)
		pFrame->SetImageInfo(lpszText);
}

// ============================================================================
// HIỂN THỊ ẢNH - yêu cầu 3 của bài thực hành
// ============================================================================
void CImageProcessingView::OnDraw(CDC* pDC)
{
	CImageProcessingDoc* pDoc = GetDocument();
	ASSERT_VALID(pDoc);
	if (pDoc == NULL)
		return;

	// ---- Chưa có ảnh: hiện dòng hướng dẫn ----
	if (pDoc->m_bmBitmap.m_hObject == NULL || !pDoc->HasImage())
	{
		CRect rc;
		GetClientRect(&rc);
		pDC->SetBkMode(TRANSPARENT);
		pDC->DrawText(_T("Vào menu \"Tệp / Mở ảnh...\" để mở một ảnh Bitmap 256 màu (*.bmp)"),
			-1, &rc, DT_CENTER | DT_VCENTER | DT_SINGLELINE);
		return;
	}

	int w = pDoc->GetWidth();
	int h = pDoc->GetHeight();

	// ---- Chọn bảng màu vào ngữ cảnh thiết bị (cần khi màn hình ở chế độ 256 màu) ----
	CPalette* pOldPal = NULL;
	if (pDoc->m_palLogical.m_hObject != NULL)
	{
		pOldPal = pDC->SelectPalette(&pDoc->m_palLogical, FALSE);
		pDC->RealizePalette();
	}

	// ---- Vùng đích: cả cửa sổ nếu đang ở chế độ "vừa cửa sổ" ----
	CRect rcDest(0, 0, w, h);
	if (m_bFitWindow)
	{
		CRect rcClient;
		GetClientRect(&rcClient);
		// giữ nguyên tỉ lệ khung hình của ảnh
		double dScale = min((double)rcClient.Width() / w, (double)rcClient.Height() / h);
		int nW = (int)(w * dScale);
		int nH = (int)(h * dScale);
		rcDest.SetRect(0, 0, nW, nH);
	}

	if (m_nDisplayMode == DISP_SETDIBITS && !m_bFitWindow)
	{
		// ---- CÁCH 1: hiển thị thẳng từ vùng dữ liệu DIB ----
		// Không cần tạo ngữ cảnh thiết bị trung gian, vẽ trực tiếp từ bộ nhớ ảnh.
		::SetDIBitsToDevice(
			pDC->GetSafeHdc(),		// quản số ngữ cảnh thiết bị đích
			0, 0,					// toạ độ trái - trên nơi cần hiển thị
			w, h,					// chiều rộng, chiều cao ảnh
			0, 0,					// toạ độ trái - dưới của ảnh nguồn
			0,						// dòng quét bắt đầu
			h,						// số dòng quét
			pDoc->GetDibBits(),		// con trỏ vùng dữ liệu ảnh
			pDoc->GetBitmapInfo(),	// con trỏ vùng thông tin ảnh (header + bảng màu)
			DIB_RGB_COLORS);		// bảng màu chứa giá trị RGB thật
	}
	else
	{
		// ---- CÁCH 2: hiển thị qua ngữ cảnh thiết bị trong bộ nhớ + StretchBlt ----
		CDC dcMem;
		dcMem.CreateCompatibleDC(pDC);		// tạo ngữ cảnh thiết bị tương thích
		CBitmap* pOldBmp = dcMem.SelectObject(&pDoc->m_bmBitmap);	// gắn bitmap vào
		if (pDoc->m_palLogical.m_hObject != NULL)
		{
			dcMem.SelectPalette(&pDoc->m_palLogical, FALSE);
			dcMem.RealizePalette();
		}
		pDC->SetStretchBltMode(COLORONCOLOR);
		pDC->StretchBlt(rcDest.left, rcDest.top, rcDest.Width(), rcDest.Height(),
		                &dcMem, 0, 0, w, h, SRCCOPY);
		dcMem.SelectObject(pOldBmp);		// trả lại bitmap cũ trước khi xoá DC
		dcMem.DeleteDC();
	}

	if (pOldPal != NULL)
		pDC->SelectPalette(pOldPal, FALSE);
}

void CImageProcessingView::OnSize(UINT nType, int cx, int cy)
{
	CScrollView::OnSize(nType, cx, cy);
	if (m_bFitWindow)
		Invalidate(TRUE);
}

// Di chuột trên ảnh -> hiện toạ độ, chỉ số bảng màu và màu của điểm ảnh
void CImageProcessingView::OnMouseMove(UINT nFlags, CPoint point)
{
	CImageProcessingDoc* pDoc = GetDocument();
	if (pDoc != NULL && pDoc->HasImage())
	{
		CPoint pt = point;
		if (m_bFitWindow)
		{
			CRect rcClient;
			GetClientRect(&rcClient);
			double dScale = min((double)rcClient.Width() / pDoc->GetWidth(),
			                    (double)rcClient.Height() / pDoc->GetHeight());
			if (dScale > 0)
			{
				pt.x = (int)(pt.x / dScale);
				pt.y = (int)(pt.y / dScale);
			}
		}
		else
		{
			pt += GetScrollPosition();	// đổi sang toạ độ ảnh khi đang cuộn
		}

		int nIndex = -1;
		COLORREF rgb = 0;
		CString s;
		if (pDoc->GetPixelInfo(pt.x, pt.y, nIndex, rgb))
		{
			if (nIndex >= 0)
				s.Format(_T("(%d, %d)  chỉ số bảng màu = %d  ->  RGB(%d, %d, %d)"),
					pt.x, pt.y, nIndex, GetRValue(rgb), GetGValue(rgb), GetBValue(rgb));
			else
				s.Format(_T("(%d, %d)  RGB(%d, %d, %d)"),
					pt.x, pt.y, GetRValue(rgb), GetGValue(rgb), GetBValue(rgb));
			ShowImageInfoOnStatusBar(s);
		}
	}
	CScrollView::OnMouseMove(nFlags, point);
}

// ============================================================================
// CÁC LỆNH TRÊN MENU
// ============================================================================
void CImageProcessingView::OnReadByCFile()
{
	GetDocument()->m_nReadMode = READ_BY_CFILE;
}
void CImageProcessingView::OnUpdateReadByCFile(CCmdUI* pCmdUI)
{
	pCmdUI->SetRadio(GetDocument()->m_nReadMode == READ_BY_CFILE);
}
void CImageProcessingView::OnReadByLoadImage()
{
	GetDocument()->m_nReadMode = READ_BY_LOADIMAGE;
}
void CImageProcessingView::OnUpdateReadByLoadImage(CCmdUI* pCmdUI)
{
	pCmdUI->SetRadio(GetDocument()->m_nReadMode == READ_BY_LOADIMAGE);
}

void CImageProcessingView::OnDispSetDIBits()
{
	m_nDisplayMode = DISP_SETDIBITS;
	Invalidate(TRUE);
}
void CImageProcessingView::OnUpdateDispSetDIBits(CCmdUI* pCmdUI)
{
	pCmdUI->SetRadio(m_nDisplayMode == DISP_SETDIBITS);
}
void CImageProcessingView::OnDispStretchBlt()
{
	m_nDisplayMode = DISP_STRETCHBLT;
	Invalidate(TRUE);
}
void CImageProcessingView::OnUpdateDispStretchBlt(CCmdUI* pCmdUI)
{
	pCmdUI->SetRadio(m_nDisplayMode == DISP_STRETCHBLT);
}
void CImageProcessingView::OnDispFitWindow()
{
	m_bFitWindow = !m_bFitWindow;
	UpdateScrollSizes();
	Invalidate(TRUE);
}
void CImageProcessingView::OnUpdateDispFitWindow(CCmdUI* pCmdUI)
{
	pCmdUI->SetCheck(m_bFitWindow);
}

void CImageProcessingView::OnImgInfo()
{
	CWaitCursor wait;
	AfxMessageBox(GetDocument()->GetImageInfoString(), MB_OK | MB_ICONINFORMATION);
}

void CImageProcessingView::OnImgFlipH()
{
	CWaitCursor wait;
	GetDocument()->ProcessFlipHorizontal();
}

void CImageProcessingView::OnImgNegative()
{
	CWaitCursor wait;
	GetDocument()->ProcessNegative();
}

void CImageProcessingView::OnImgGray()
{
	CWaitCursor wait;
	GetDocument()->ProcessGray();
}

void CImageProcessingView::OnPalRotate()
{
	GetDocument()->PaletteRotate(16);
}

void CImageProcessingView::OnPalReverse()
{
	GetDocument()->PaletteReverse();
}

void CImageProcessingView::OnImgBackup()
{
	CString strError;
	if (GetDocument()->MakeBackup(strError))
		AfxMessageBox(_T("Đã tạo xong một bản sao độc lập của ảnh trong bộ nhớ.\n")
			_T("Có thể xử lý thoải mái rồi dùng lệnh \"Khôi phục từ bản sao\" để lấy lại ảnh gốc."),
			MB_OK | MB_ICONINFORMATION);
	else
		AfxMessageBox(strError, MB_OK | MB_ICONEXCLAMATION);
}

void CImageProcessingView::OnImgRestore()
{
	if (!GetDocument()->RestoreFromBackup())
		AfxMessageBox(_T("Chưa có bản sao nào."), MB_OK | MB_ICONEXCLAMATION);
}

void CImageProcessingView::OnUpdateNeedImage(CCmdUI* pCmdUI)
{
	pCmdUI->Enable(GetDocument() != NULL && GetDocument()->HasImage());
}

void CImageProcessingView::OnUpdateNeedPalette(CCmdUI* pCmdUI)
{
	CImageProcessingDoc* pDoc = GetDocument();
	pCmdUI->Enable(pDoc != NULL && pDoc->HasImage() && pDoc->GetPaletteEntries() > 0);
}

void CImageProcessingView::OnUpdateNeedBackup(CCmdUI* pCmdUI)
{
	CImageProcessingDoc* pDoc = GetDocument();
	pCmdUI->Enable(pDoc != NULL && pDoc->HasImage() && pDoc->HasBackup());
}

// ============================================================================
#ifdef _DEBUG
void CImageProcessingView::AssertValid() const
{
	CScrollView::AssertValid();
}

void CImageProcessingView::Dump(CDumpContext& dc) const
{
	CScrollView::Dump(dc);
}

CImageProcessingDoc* CImageProcessingView::GetDocument() const // bản không gỡ lỗi dùng hàm inline
{
	ASSERT(m_pDocument->IsKindOf(RUNTIME_CLASS(CImageProcessingDoc)));
	return (CImageProcessingDoc*)m_pDocument;
}
#endif //_DEBUG
