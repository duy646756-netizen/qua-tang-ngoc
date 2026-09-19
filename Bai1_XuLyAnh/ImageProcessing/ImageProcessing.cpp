// ImageProcessing.cpp : cài đặt lớp ứng dụng

#include "stdafx.h"
#include "ImageProcessing.h"
#include "MainFrm.h"
#include "ImageProcessingDoc.h"
#include "ImageProcessingView.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#endif

BEGIN_MESSAGE_MAP(CImageProcessingApp, CWinApp)
	ON_COMMAND(ID_APP_ABOUT, &CImageProcessingApp::OnAppAbout)
	ON_COMMAND(ID_FILE_OPEN, &CWinApp::OnFileOpen)
	ON_COMMAND(ID_OPT_ONLY256, &CImageProcessingApp::OnOptOnly256)
	ON_UPDATE_COMMAND_UI(ID_OPT_ONLY256, &CImageProcessingApp::OnUpdateOptOnly256)
END_MESSAGE_MAP()

// Đối tượng ứng dụng duy nhất
CImageProcessingApp theApp;

CImageProcessingApp::CImageProcessingApp()
{
	m_bOnly256Colors = TRUE;
}

BOOL CImageProcessingApp::InitInstance()
{
	// Khởi tạo các control chung của Windows
	INITCOMMONCONTROLSEX InitCtrls;
	InitCtrls.dwSize = sizeof(InitCtrls);
	InitCtrls.dwICC  = ICC_WIN95_CLASSES;
	InitCommonControlsEx(&InitCtrls);

	CWinApp::InitInstance();
	AfxEnableControlContainer();

	// Nơi lưu các tuỳ chọn của chương trình trong Registry
	SetRegistryKey(_T("ThucHanhXuLyAnh"));
	m_bOnly256Colors = (GetProfileInt(_T("TuyChon"), _T("ChiNhan256Mau"), 1) != 0);

	// Khai báo mẫu tài liệu SDI: Document - Frame - View
	CSingleDocTemplate* pDocTemplate = new CSingleDocTemplate(
		IDR_MAINFRAME,
		RUNTIME_CLASS(CImageProcessingDoc),
		RUNTIME_CLASS(CMainFrame),			// cửa sổ chính SDI
		RUNTIME_CLASS(CImageProcessingView));
	if (!pDocTemplate)
		return FALSE;
	AddDocTemplate(pDocTemplate);

	// Phân tích dòng lệnh (cho phép mở ảnh bằng cách kéo thả vào biểu tượng)
	CCommandLineInfo cmdInfo;
	ParseCommandLine(cmdInfo);
	if (!ProcessShellCommand(cmdInfo))
		return FALSE;

	m_pMainWnd->ShowWindow(SW_SHOW);
	m_pMainWnd->UpdateWindow();
	return TRUE;
}

int CImageProcessingApp::ExitInstance()
{
	WriteProfileInt(_T("TuyChon"), _T("ChiNhan256Mau"), m_bOnly256Colors ? 1 : 0);
	return CWinApp::ExitInstance();
}

// Bật/tắt ràng buộc "chỉ nhận ảnh 256 màu"
void CImageProcessingApp::OnOptOnly256()
{
	m_bOnly256Colors = !m_bOnly256Colors;
	if (m_bOnly256Colors)
		AfxMessageBox(_T("Từ bây giờ chương trình CHỈ mở ảnh Bitmap 256 màu (8 bit/pixel)."),
			MB_OK | MB_ICONINFORMATION);
	else
		AfxMessageBox(_T("Từ bây giờ chương trình mở được cả ảnh Bitmap 256 màu và 24 bit màu."),
			MB_OK | MB_ICONINFORMATION);
}

void CImageProcessingApp::OnUpdateOptOnly256(CCmdUI* pCmdUI)
{
	pCmdUI->SetCheck(m_bOnly256Colors);
}

// ============================================================================
// Hộp thoại "Giới thiệu"
// ============================================================================
class CAboutDlg : public CDialog
{
public:
	CAboutDlg();
	enum { IDD = IDD_ABOUTBOX };

protected:
	virtual void DoDataExchange(CDataExchange* pDX);
	DECLARE_MESSAGE_MAP()
};

CAboutDlg::CAboutDlg() : CDialog(CAboutDlg::IDD)
{
}

void CAboutDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
}

BEGIN_MESSAGE_MAP(CAboutDlg, CDialog)
END_MESSAGE_MAP()

void CImageProcessingApp::OnAppAbout()
{
	CAboutDlg aboutDlg;
	aboutDlg.DoModal();
}
