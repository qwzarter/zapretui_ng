import platform
import ctypes
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QPushButton, QComboBox
from PySide6.QtCore import QTimer, Qt

# Режим отладки — форсировать тип эффекта:
# None     → использовать по версии Windows
# "mica"   → принудительно включить Mica
# "mica_alt"   → принудительно включить Mica Alt
# "mica+"  → принудительно включить Mica+ (авто)
# "acrylic"   → принудительно включить Acrylic (Win10)
# "aero"   → принудительно включить Aero
# "solid" или "fallback"   → использовать обычный цветной фон
FORCE_EFFECT_MODE = None


def apply_mica_effect(widget, alt=None):
    hwnd = int(widget.winId())
    try:
        winver = int(platform.release())
    except ValueError:
        winver = 8

    if FORCE_EFFECT_MODE:
        mode = FORCE_EFFECT_MODE.lower()
        if mode == "mica":
            winver = 11
            alt = False
        elif mode == "mica_alt":
            winver = 11
            alt = True
        elif mode == "mica+":
            winver = 11
            alt = None
        elif mode == "acrylic":
            winver = 10
        elif mode == "aero":
            winver = 7
        elif mode in ("solid", "fallback"):
            winver = 6

    if winver >= 11:
        # Mica / Mica Alt / Mica+ (Windows 11)
        DWMWA_SYSTEMBACKDROP_TYPE = 38
        DWMSBT_MAINWINDOW = 2     # Mica
        DWMSBT_TABBEDWINDOW = 3   # Mica Alt
        DWMSBT_DESKTOPWINDOW = 4  # Mica+

        if alt is True:
            backdrop = DWMSBT_TABBEDWINDOW
        elif alt is False:
            backdrop = DWMSBT_MAINWINDOW
        else:
            backdrop = DWMSBT_DESKTOPWINDOW

        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_SYSTEMBACKDROP_TYPE,
            ctypes.byref(ctypes.c_int(backdrop)),
            ctypes.sizeof(ctypes.c_int)
        )

        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(ctypes.c_int(1)),
            ctypes.sizeof(ctypes.c_int)
        )

        try:
            class MARGINS(ctypes.Structure):
                _fields_ = [
                    ("cxLeftWidth", ctypes.c_int),
                    ("cxRightWidth", ctypes.c_int),
                    ("cyTopHeight", ctypes.c_int),
                    ("cyBottomHeight", ctypes.c_int),
                ]
            ctypes.windll.dwmapi.DwmExtendFrameIntoClientArea(
                hwnd, ctypes.byref(MARGINS(-1, -1, -1, -1))
            )
        except Exception:
            pass

    elif winver == 10:
        # Acrylic (Windows 10)
        class ACCENTPOLICY(ctypes.Structure):
            _fields_ = [
                ("AccentState", ctypes.c_int),
                ("AccentFlags", ctypes.c_int),
                ("GradientColor", ctypes.c_int),
                ("AnimationId", ctypes.c_int),
            ]

        class WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):
            _fields_ = [
                ("Attribute", ctypes.c_int),
                ("Data", ctypes.c_void_p),
                ("SizeOfData", ctypes.c_size_t),
            ]

        accent = ACCENTPOLICY()
        accent.AccentState = 4  # Blur
        accent.GradientColor = 0xAA252839 if alt else 0xAA1E2030
        data = WINDOWCOMPOSITIONATTRIBDATA()
        data.Attribute = 19
        data.Data = ctypes.addressof(accent)
        data.SizeOfData = ctypes.sizeof(accent)
        ctypes.windll.user32.SetWindowCompositionAttribute(hwnd, ctypes.byref(data))

    elif winver in (7, 8):
        # Aero Glass / DWM BlurBehind (Windows 7–8)
        class DWM_BLURBEHIND(ctypes.Structure):
            _fields_ = [
                ("dwFlags", ctypes.c_uint),
                ("fEnable", ctypes.c_bool),
                ("hRgnBlur", ctypes.c_void_p),
                ("fTransitionOnMaximized", ctypes.c_bool),
            ]

        DWM_BB_ENABLE = 0x00000001

        bb = DWM_BLURBEHIND()
        bb.dwFlags = DWM_BB_ENABLE
        bb.fEnable = True
        bb.hRgnBlur = None
        bb.fTransitionOnMaximized = False

        try:
            is_enabled = ctypes.c_bool()
            ctypes.windll.dwmapi.DwmIsCompositionEnabled(ctypes.byref(is_enabled))
            if is_enabled.value:
                ctypes.windll.dwmapi.DwmEnableBlurBehindWindow(hwnd, ctypes.byref(bb))
            else:
                color = "#2B3045" if alt else "#1E2030"
                widget.setStyleSheet(f"background-color: {color}; color: white; border-radius: 8px;")
        except Exception:
            color = "#2B3045" if alt else "#1E2030"
            widget.setStyleSheet(f"background-color: {color}; color: white; border-radius: 8px;")

    else:
        # Fallback для старых систем
        color = "#2B3045" if alt else "#1E2030"
        widget.setStyleSheet(f"background-color: {color}; color: white; border-radius: 8px;")

    pal = widget.palette()
    pal.setColor(QPalette.Window, QColor(0, 0, 0, 1))
    widget.setPalette(pal)


def apply_mica_visual(widget, alt=None):
    if alt is True:
        opacity = "0.25"
        border_opacity = "0.22"
    elif alt is False:
        opacity = "0.15"
        border_opacity = "0.15"
    else:
        opacity = "0.18"
        border_opacity = "0.18"

    base = widget.styleSheet() or ""

    if isinstance(widget, QPushButton):
        extra = f"""
QPushButton {{
    background-color: rgba(36, 40, 55, {opacity});
    border: 1px solid rgba(255,255,255,{border_opacity});
    border-radius: 8px;
    color: #E6E9F0;
}}
QPushButton:hover {{
    background-color: rgba(255,255,255,0.12);
}}
"""
        widget.setStyleSheet(base + "\n" + extra)
        return

    if isinstance(widget, QComboBox):
        extra = f"""
QComboBox {{
    background-color: rgba(36, 40, 55, {opacity});
    border: 1px solid rgba(255,255,255,{border_opacity});
}}
QComboBox::drop-down {{
    background-color: rgba(255,255,255,0.05);
}}
QComboBox QAbstractItemView {{
    background-color: rgba(36, 40, 55, {opacity});
    border: 1px solid rgba(255,255,255,{border_opacity});
}}
QScrollBar:vertical {{
    background: rgba(30,33,45,0.95);
    width: 10px;
    border-radius: 5px;
}}
QScrollBar::handle:vertical {{
    background: rgba(255,255,255,0.25);
    border-radius: 5px;
}}
"""
        widget.setStyleSheet(base + "\n" + extra)
        return

    extra = f"""
{widget.__class__.__name__} {{
    background-color: rgba(36, 40, 55, {opacity});
    border: 1px solid rgba(255,255,255,{border_opacity});
    border-radius: 8px;
}}
"""
    widget.setStyleSheet(base + "\n" + extra)


def apply_mica_to_dialog(dialog, alt=None):
    dialog.setAttribute(Qt.WA_TranslucentBackground, True)
    dialog.setAutoFillBackground(False)

    pal = dialog.palette()
    pal.setColor(QPalette.Window, QColor(0, 0, 0, 1))
    dialog.setPalette(pal)

    if alt is True:
        dialog.setStyleSheet("""
            QMessageBox, QDialog {
                background-color: rgba(36, 40, 55, 0.92);
                color: #E6E9F0;
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 10px;
            }
            QLabel {
                color: #E6E9F0;
                font-size: 13px;
            }
            QPushButton {
                background-color: rgba(255,255,255,0.07);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px;
                color: #E6E9F0;
                padding: 6px 16px;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.14);
            }
        """)
    elif alt is False:
        dialog.setStyleSheet("""
            QMessageBox, QDialog {
                background-color: rgba(30, 33, 45, 0.92);
                color: #E6E9F0;
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 10px;
            }
            QLabel {
                color: #E6E9F0;
                font-size: 13px;
            }
            QPushButton {
                background-color: rgba(36, 40, 55, 0.7);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 8px;
                color: #E6E9F0;
                padding: 6px 16px;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.12);
            }
        """)
    else:
        dialog.setStyleSheet("""
            QMessageBox, QDialog {
                background-color: rgba(33, 36, 50, 0.94);
                color: #E6E9F0;
                border: 1px solid rgba(255,255,255,0.07);
                border-radius: 10px;
            }
            QLabel {
                color: #E6E9F0;
                font-size: 13px;
            }
            QPushButton {
                background-color: rgba(40, 45, 60, 0.8);
                border: 1px solid rgba(255,255,255,0.09);
                border-radius: 8px;
                color: #E6E9F0;
                padding: 6px 16px;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.14);
            }
        """)

    def _apply_mica_delayed():
        try:
            apply_mica_effect(dialog, alt=alt)
        except Exception:
            pass

    QTimer.singleShot(0, _apply_mica_delayed)
