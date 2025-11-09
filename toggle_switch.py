from PySide6.QtCore import Qt, Property, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QColor, QBrush
from PySide6.QtWidgets import QCheckBox


class ToggleSwitch(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(50, 28)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)

        self._handle_x = 3
        self._anim = QPropertyAnimation(self, b"handle_position")
        self._anim.setDuration(150)
        self._anim.setEasingCurve(QEasingCurve.InOutQuad)

        self._locked = False

        self.stateChanged.connect(self.start_animation)

    def setLocked(self, locked: bool):
        self._locked = bool(locked)
        self.update()

    def get_handle_position(self):
        return self._handle_x

    def set_handle_position(self, x):
        self._handle_x = x
        self.update()

    handle_position = Property(float, get_handle_position, set_handle_position)

    def mousePressEvent(self, event):
        if self._locked:
            event.ignore()
            return
        if event.button() == Qt.LeftButton:
            self.toggle()
        else:
            super().mousePressEvent(event)

    def start_animation(self, state):
        start = 25 if not self.isChecked() else 3
        end = 3 if not self.isChecked() else 25
        self._anim.stop()
        self._anim.setStartValue(start)
        self._anim.setEndValue(end)
        self._anim.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.isChecked():
            base_color = QColor("#16A34A")
        else:
            base_color = QColor("#4B5563")

        if self._locked:
            base_color = base_color.lighter(60)

        painter.setBrush(base_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, 50, 28, 14, 14)

        knob_color = QColor("#FFFFFF")
        if self._locked:
            knob_color = QColor(180, 180, 180)
        painter.setBrush(QBrush(knob_color))
        painter.drawEllipse(self._handle_x, 3, 22, 22)

        if self._locked:
            painter.setBrush(QColor(0, 0, 0, 60))
            painter.drawRoundedRect(0, 0, 50, 28, 14, 14)