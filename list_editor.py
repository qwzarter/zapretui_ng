from pathlib import Path
import re
import time
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QMessageBox, QSizePolicy
)
from PySide6.QtGui import QFont, QTextCursor, QTextCharFormat, QColor, QPalette
from PySide6.QtCore import Qt
from effects import apply_mica_effect, apply_mica_visual, apply_mica_to_dialog

BUTTON_STYLE_DARK = """
QPushButton {
    background-color: #262C3F;
    color: #E5E7EB;
    border: 1px solid #333A52;
    border-radius: 8px;
    padding: 6px 14px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #2E364D;
}
QPushButton:pressed {
    background-color: #1E2333;
}
QPushButton:disabled {
    background-color: #3C3F4A;
    color: #9CA3AF;
    border: 1px solid #4B5563;
}
"""

DIALOG_STYLE = """
QDialog {
    background-color: transparent;
    color: #E5E7EB;
}
QLabel {
    color: #E5E7EB;
}
QTextEdit {
    background-color: rgba(30, 35, 55, 0.85);
    color: #F3F4F6;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px;
    padding: 6px;
}
"""

DOMAIN_RE = re.compile(
    r"^(?:[A-Za-z0-9](?:[A-Za-z0-9\-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,}$"
)


class ListEditorDialog(QDialog):
    def __init__(self, lists_dir: str, filename: str = "list-general.txt", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактор списков — list-general.txt")
        self.setMinimumSize(650, 500)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAutoFillBackground(False)

        pal = self.palette()
        pal.setColor(QPalette.Window, QColor(0, 0, 0, 0))
        self.setPalette(pal)

        self.setStyleSheet(DIALOG_STYLE)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)

        self.lists_dir = Path(lists_dir)
        self.filename = filename
        self.filepath = self.lists_dir / self.filename

        self.font_default = QFont("Segoe UI", 11)

        layout = QVBoxLayout(self)

        info = QLabel(
            "Один домен на строку (пример: example.com)\n"
            "Перед сохранением создаётся резервная копия файла."
        )
        info.setFont(self.font_default)
        layout.addWidget(info)

        self.text = QTextEdit()
        self.text.setFont(self.font_default)
        self.text.setAcceptRichText(False)
        layout.addWidget(self.text)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.validate_btn = QPushButton("Проверить")
        self.save_btn = QPushButton("Сохранить")
        self.reload_btn = QPushButton("Перезагрузить")

        for b in (self.validate_btn, self.save_btn, self.reload_btn):
            b.setStyleSheet(BUTTON_STYLE_DARK)
            b.setMinimumWidth(120)
            b.setMinimumHeight(38)
            b.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            b.setFont(self.font_default)
            b.setCursor(Qt.PointingHandCursor)

        self.validate_btn.clicked.connect(self.validate_highlight)
        self.save_btn.clicked.connect(self.save_file)
        self.reload_btn.clicked.connect(self.load_file)

        btn_layout.addWidget(self.validate_btn)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.reload_btn)
        layout.addLayout(btn_layout)
        self.load_file()
        apply_mica_effect(self)
        apply_mica_visual(self.text, alt=True)
        apply_mica_visual(self.validate_btn, alt=True)
        apply_mica_visual(self.save_btn, alt=True)
        apply_mica_visual(self.reload_btn, alt=True)

    def load_file(self):
        try:
            if not self.lists_dir.exists():
                self.lists_dir.mkdir(parents=True, exist_ok=True)
            if not self.filepath.exists():
                self.filepath.write_text("", encoding="utf-8")
            text = self.filepath.read_text(encoding="utf-8").replace("\r\n", "\n")
            self.text.setPlainText(text)
            self.clear_highlight()
        except Exception as e:
            self.show_message("Ошибка", f"Не удалось загрузить файл:\n{e}", error=True)

    def validate_highlight(self):
        content = self.text.toPlainText()
        lines = content.splitlines()
        self.clear_highlight()

        invalid_lines = []
        cursor = self.text.textCursor()
        fmt_invalid = QTextCharFormat()
        fmt_invalid.setBackground(QColor(220, 38, 38, 80))

        pos = 0
        for i, raw in enumerate(lines):
            line = raw.strip()
            line_len = len(raw)
            if line and not DOMAIN_RE.match(line):
                invalid_lines.append((i + 1, line))
                cursor.setPosition(pos)
                cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
                cursor.mergeCharFormat(fmt_invalid)
            pos += line_len + 1

        if invalid_lines:
            msg = "Найдены некорректные строки:\n" + "\n".join(
                f"{ln}: {val}" for ln, val in invalid_lines
            )
            self.show_message("Проверка", msg)
        else:
            self.show_message("Проверка", "Ошибок не найдено.")

    def clear_highlight(self):
        cursor = self.text.textCursor()
        cursor.select(QTextCursor.Document)
        fmt = QTextCharFormat()
        fmt.setBackground(QColor(0, 0, 0, 0))
        cursor.mergeCharFormat(fmt)
        cursor.clearSelection()
        self.text.setTextCursor(cursor)

    def save_file(self):
        try:
            raw = self.text.toPlainText()
            lines = [ln.strip() for ln in raw.splitlines()]
            seen = set()
            cleaned = []
            for ln in lines:
                if ln and ln not in seen:
                    seen.add(ln)
                    cleaned.append(ln)

            bad = [ln for ln in cleaned if not DOMAIN_RE.match(ln)]
            if bad:
                reply = self.ask_question(
                    "Некорректные строки",
                    "Найдены строки, которые не выглядят как домены:\n\n"
                    + "\n".join(bad[:20])
                    + ("\n\n(Показаны первые 20)" if len(bad) > 20 else "")
                    + "\n\nСохранить файл несмотря на это?",
                )
                if not reply:
                    return

            if self.filepath.exists():
                ts = time.strftime("%Y%m%d-%H%M%S")
                bak = self.filepath.with_name(self.filepath.name + f".bak.{ts}")
                self.filepath.replace(bak)
                self.filepath.write_text(
                    "\n".join(cleaned) + ("\n" if cleaned else ""), encoding="utf-8"
                )
                self.show_message("Сохранено", f"Файл сохранён. Резервная копия: {bak.name}")
            else:
                self.filepath.write_text(
                    "\n".join(cleaned) + ("\n" if cleaned else ""), encoding="utf-8"
                )
                self.show_message("Сохранено", "Файл сохранён.")
            self.load_file()
        except Exception as e:
            self.show_message("Ошибка", f"Не удалось сохранить файл:\n{e}", error=True)

    def show_message(self, title: str, text: str, error=False):
        box = QMessageBox(self)
        box.setWindowTitle(title)
        box.setText(text)
        box.setIcon(QMessageBox.Critical if error else QMessageBox.Information)
        apply_mica_to_dialog(box, alt=None if error else False)
        box.exec()


    def ask_question(self, title: str, text: str):
        box = QMessageBox(self)
        box.setWindowTitle(title)
        box.setText(text)
        box.setIcon(QMessageBox.Question)
        box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        apply_mica_to_dialog(box, alt=True)
        return box.exec() == QMessageBox.Yes