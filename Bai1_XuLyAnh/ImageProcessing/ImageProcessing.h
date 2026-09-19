// ImageProcessing.h : tệp tiêu đề chính của chương trình
//
// THỰC HÀNH XỬ LÝ ẢNH - Bài thực hành số 1
// Đọc và hiển thị ảnh Bitmap 256 màu (mở rộng cho ảnh 24 bit màu)

#pragma once

#ifndef __AFXWIN_H__
	#error "Phải include 'stdafx.h' trước tệp này"
#endif

#include "resource.h"		// các ký hiệu tài nguyên

class CImageProcessingApp : public CWinApp
{
public:
	CImageProcessingApp();

	// TRUE: chỉ chấp nhận mở ảnh Bitmap 256 màu (đúng yêu cầu của bài thực hành)
	// FALSE: cho phép mở thêm ảnh Bitmap 24 bit màu
	BOOL m_bOnly256Colors;

// Overrides
public:
	virtual BOOL InitInstance();
	virtual int  ExitInstance();

// Implementation
	afx_msg void OnAppAbout();
	afx_msg void OnOptOnly256();
	afx_msg void OnUpdateOptOnly256(CCmdUI* pCmdUI);
	DECLARE_MESSAGE_MAP()
};

extern CImageProcessingApp theApp;
