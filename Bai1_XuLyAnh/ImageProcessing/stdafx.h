// stdafx.h : tep tieu de dung chung, it thay doi -> duoc bien dich truoc (PCH)

#pragma once

#ifndef VC_EXTRALEAN
#define VC_EXTRALEAN            // Loai bot cac thanh phan it dung cua Windows
#endif

#include "targetver.h"

#define _ATL_CSTRING_EXPLICIT_CONSTRUCTORS  // Ham tao cua CString la explicit

// Tat cac canh bao an cua MFC ve cac ham bi coi la khong an toan
#ifndef _AFX_NO_MFC_CONTROLS_IN_DIALOGS
#define _AFX_NO_MFC_CONTROLS_IN_DIALOGS
#endif

#include <afxwin.h>         // Thanh phan loi va chuan cua MFC
#include <afxext.h>         // Phan mo rong cua MFC (CScrollView, CStatusBar...)
#include <afxdisp.h>        // Ho tro Automation

#ifndef _AFX_NO_AFXCMN_SUPPORT
#include <afxcmn.h>         // Ho tro cac control chung cua Windows
#endif

#include <set>              // dung de dem so mau thuc su co trong anh
