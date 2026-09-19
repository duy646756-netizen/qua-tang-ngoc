// MainFrm.h : lớp cửa sổ chính (SDI)

#pragma once

class CMainFrame : public CFrameWnd
{
protected: // chỉ được tạo từ serialization
	CMainFrame();
	DECLARE_DYNCREATE(CMainFrame)

// Attributes
public:
	CStatusBar m_wndStatusBar;

	// Hiện thông tin ảnh lên ô thứ hai của thanh trạng thái
	void SetImageInfo(LPCTSTR lpszText);

// Overrides
public:
	virtual BOOL PreCreateWindow(CREATESTRUCT& cs);

// Implementation
public:
	virtual ~CMainFrame();
#ifdef _DEBUG
	virtual void AssertValid() const;
	virtual void Dump(CDumpContext& dc) const;
#endif

protected:
	afx_msg int OnCreate(LPCREATESTRUCT lpCreateStruct);
	DECLARE_MESSAGE_MAP()
};
