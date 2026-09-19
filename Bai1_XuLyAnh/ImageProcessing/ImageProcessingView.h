// ImageProcessingView.h : lớp View - nơi HIỂN THỊ ảnh
//
// Lớp View được dẫn xuất từ CScrollView (theo đúng hướng dẫn của bài thực hành)
// để ảnh lớn hơn cửa sổ vẫn cuộn xem được.

#pragma once

#include "ImageProcessingDoc.h"

// Cách hiển thị ảnh
enum EDisplayMode
{
	DISP_SETDIBITS  = 0,	// dùng hàm ::SetDIBitsToDevice
	DISP_STRETCHBLT = 1		// dùng hàm CDC::StretchBlt
};

class CImageProcessingView : public CScrollView
{
protected: // chỉ được tạo từ serialization
	CImageProcessingView();
	DECLARE_DYNCREATE(CImageProcessingView)

public:
	CImageProcessingDoc* GetDocument() const;

	int  m_nDisplayMode;	// EDisplayMode
	BOOL m_bFitWindow;		// TRUE: co giãn ảnh cho vừa cửa sổ (dùng StretchBlt)

	void UpdateScrollSizes();
	void ShowImageInfoOnStatusBar(LPCTSTR lpszText);

// Overrides
public:
	virtual void OnDraw(CDC* pDC);
	virtual void OnInitialUpdate();
protected:
	virtual void OnUpdate(CView* pSender, LPARAM lHint, CObject* pHint);

// Implementation
public:
	virtual ~CImageProcessingView();
#ifdef _DEBUG
	virtual void AssertValid() const;
	virtual void Dump(CDumpContext& dc) const;
#endif

protected:
	afx_msg void OnSize(UINT nType, int cx, int cy);
	afx_msg void OnMouseMove(UINT nFlags, CPoint point);

	afx_msg void OnReadByCFile();
	afx_msg void OnUpdateReadByCFile(CCmdUI* pCmdUI);
	afx_msg void OnReadByLoadImage();
	afx_msg void OnUpdateReadByLoadImage(CCmdUI* pCmdUI);

	afx_msg void OnDispSetDIBits();
	afx_msg void OnUpdateDispSetDIBits(CCmdUI* pCmdUI);
	afx_msg void OnDispStretchBlt();
	afx_msg void OnUpdateDispStretchBlt(CCmdUI* pCmdUI);
	afx_msg void OnDispFitWindow();
	afx_msg void OnUpdateDispFitWindow(CCmdUI* pCmdUI);

	afx_msg void OnImgInfo();
	afx_msg void OnImgFlipH();
	afx_msg void OnImgNegative();
	afx_msg void OnImgGray();
	afx_msg void OnPalRotate();
	afx_msg void OnPalReverse();
	afx_msg void OnImgBackup();
	afx_msg void OnImgRestore();
	afx_msg void OnUpdateNeedImage(CCmdUI* pCmdUI);		// bật/tắt menu khi chưa có ảnh
	afx_msg void OnUpdateNeedPalette(CCmdUI* pCmdUI);	// chỉ bật khi ảnh có bảng màu
	afx_msg void OnUpdateNeedBackup(CCmdUI* pCmdUI);

	DECLARE_MESSAGE_MAP()
};

#ifndef _DEBUG  // bản gỡ lỗi dùng hàm trong ImageProcessingView.cpp
inline CImageProcessingDoc* CImageProcessingView::GetDocument() const
   { return reinterpret_cast<CImageProcessingDoc*>(m_pDocument); }
#endif
