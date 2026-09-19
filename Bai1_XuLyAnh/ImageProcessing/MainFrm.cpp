// MainFrm.cpp : cài đặt lớp CMainFrame

#include "stdafx.h"
#include "ImageProcessing.h"
#include "MainFrm.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#endif

IMPLEMENT_DYNCREATE(CMainFrame, CFrameWnd)

BEGIN_MESSAGE_MAP(CMainFrame, CFrameWnd)
	ON_WM_CREATE()
END_MESSAGE_MAP()

// Các ô (pane) của thanh trạng thái
static UINT indicators[] =
{
	ID_SEPARATOR,				// ô hiện dòng thông báo
	IDS_INDICATOR_IMGINFO,		// ô hiện thông tin ảnh
};

CMainFrame::CMainFrame()
{
}

CMainFrame::~CMainFrame()
{
}

int CMainFrame::OnCreate(LPCREATESTRUCT lpCreateStruct)
{
	if (CFrameWnd::OnCreate(lpCreateStruct) == -1)
		return -1;

	if (!m_wndStatusBar.Create(this) ||
		!m_wndStatusBar.SetIndicators(indicators, sizeof(indicators) / sizeof(UINT)))
	{
		TRACE0("Khong tao duoc thanh trang thai\n");
		return -1;
	}
	// Đặt độ rộng cố định cho ô thông tin ảnh
	m_wndStatusBar.SetPaneInfo(1, IDS_INDICATOR_IMGINFO, SBPS_NORMAL, 520);
	return 0;
}

BOOL CMainFrame::PreCreateWindow(CREATESTRUCT& cs)
{
	if (!CFrameWnd::PreCreateWindow(cs))
		return FALSE;
	cs.cx = 900;
	cs.cy = 650;
	return TRUE;
}

void CMainFrame::SetImageInfo(LPCTSTR lpszText)
{
	if (m_wndStatusBar.GetSafeHwnd() != NULL)
		m_wndStatusBar.SetPaneText(1, lpszText);
}

#ifdef _DEBUG
void CMainFrame::AssertValid() const
{
	CFrameWnd::AssertValid();
}

void CMainFrame::Dump(CDumpContext& dc) const
{
	CFrameWnd::Dump(dc);
}
#endif //_DEBUG
