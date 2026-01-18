from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QMessageBox, QFrame, QSpacerItem, QSizePolicy
)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt

from toggle_switch import ToggleSwitch
from list_editor import ListEditorDialog
from effects import apply_mica_effect, apply_mica_visual, apply_mica_to_dialog
import strategies_db

class StrategyConstructorDialog(QDialog):
    def __init__(self, lists_dir: str, settings: dict = None, parent=None):
        super().__init__(parent)
        self.lists_dir = Path(lists_dir)
        self.user_settings = settings if settings is not None else {}
        self.setWindowTitle("Конструктор Стратегий")
        self.setMinimumSize(400, 450)
        
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAutoFillBackground(False)
        self.setStyleSheet("""
            QDialog { background: transparent; color: #E5E7EB; }
            QLabel { color: #E5E7EB; font-weight: 500; }
            QComboBox {
                background-color: rgba(30, 35, 55, 0.9);
                color: white;
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 6px;
                padding: 5px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background-color: #262C3F;
                color: white;
                selection-background-color: #3B82F6;
            }
        """)

        self.font_header = QFont("Segoe UI", 11, QFont.Bold)
        self.font_ui = QFont("Segoe UI", 10)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(self.create_label("Стратегия для YouTube:"))
        self.combo_youtube = QComboBox()
        self.combo_youtube.setFont(self.font_ui)
        self.combo_youtube.addItem("Нет")
        y_keys = sorted(strategies_db.YOUTUBE_STRATEGIES.keys())
        self.combo_youtube.addItems(y_keys)
        if "Yv02" in y_keys: 
            self.combo_youtube.setCurrentText("Yv02")
        layout.addWidget(self.combo_youtube)

        layout.addWidget(self.create_label("Общая стратегия:"))
        self.combo_general = QComboBox()
        self.combo_general.setFont(self.font_ui)
        self.combo_general.addItem("Нет")
        g_keys = sorted(strategies_db.GENERAL_STRATEGIES.keys())
        self.combo_general.addItems(g_keys)
        if "v7" in g_keys:
            self.combo_general.setCurrentText("v7")
        layout.addWidget(self.combo_general)

        disc_layout = QHBoxLayout()
        disc_lbl = self.create_label("Стратегия для Discord:")
        self.toggle_discord = ToggleSwitch()
        self.toggle_discord.setChecked(True)
        disc_layout.addWidget(disc_lbl)
        disc_layout.addStretch()
        disc_layout.addWidget(self.toggle_discord)
        layout.addLayout(disc_layout)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: rgba(255,255,255,0.1);")
        layout.addWidget(line)

        game_info = QLabel("Автоматически добавится Game стратегия (для корректной работы игрового режима)")
        game_info.setWordWrap(True)
        game_info.setStyleSheet("color: #9CA3AF; font-size: 11px;")
        layout.addWidget(game_info)

        layout.addStretch()

        btns_layout = QHBoxLayout()
        
        self.btn_manual = QPushButton("Редактор текста")
        self.btn_save = QPushButton("Применить и Сохранить")
        
        btn_style = """
        QPushButton {
            background-color: #262C3F; color: white;
            border: 1px solid #333A52; border-radius: 6px; padding: 8px;
        }
        QPushButton:hover { background-color: #2E364D; }
        """
        self.btn_manual.setStyleSheet(btn_style)
        self.btn_save.setStyleSheet(btn_style.replace("#262C3F", "#166534").replace("#2E364D", "#15803d"))

        self.btn_manual.clicked.connect(self.open_manual_editor)
        self.btn_save.clicked.connect(self.save_strategy)

        btns_layout.addWidget(self.btn_manual)
        btns_layout.addWidget(self.btn_save)
        layout.addLayout(btns_layout)
        last_yv = self.user_settings.get("last_yv", "Yv02")
        last_v = self.user_settings.get("last_v", "v7")
        last_discord = self.user_settings.get("last_discord", True)
        self.combo_youtube.setCurrentText(last_yv)
        self.combo_general.setCurrentText(last_v)
        self.toggle_discord.setChecked(last_discord)

        if last_yv in [self.combo_youtube.itemText(i) for i in range(self.combo_youtube.count())]:
            self.combo_youtube.setCurrentText(last_yv)
        
        if last_v in [self.combo_general.itemText(i) for i in range(self.combo_general.count())]:
            self.combo_general.setCurrentText(last_v)
            
        self.toggle_discord.setChecked(last_discord)

        apply_mica_effect(self)
        apply_mica_visual(self.btn_manual)
        apply_mica_visual(self.btn_save)

    def get_selected_settings(self):
        return {
            "last_yv": self.combo_youtube.currentText(),
            "last_v": self.combo_general.currentText(),
            "last_discord": self.toggle_discord.isChecked()
        }

    def create_label(self, text):
        lbl = QLabel(text)
        lbl.setFont(self.font_header)
        return lbl

    def open_manual_editor(self):
        editor = ListEditorDialog(
            str(self.lists_dir), 
            filename="custom_strategy.txt", 
            editor_type="strategy", 
            parent=self
        )
        apply_mica_to_dialog(editor, alt=True)
        editor.exec()

    def save_strategy(self):
        blocks = []

        y_sel = self.combo_youtube.currentText()
        if y_sel != "Нет" and y_sel in strategies_db.YOUTUBE_STRATEGIES:
            blocks.append("\n".join(strategies_db.YOUTUBE_STRATEGIES[y_sel]))

        g_sel = self.combo_general.currentText()
        if g_sel != "Нет" and g_sel in strategies_db.GENERAL_STRATEGIES:
            blocks.append("\n".join(strategies_db.GENERAL_STRATEGIES[g_sel]))

        if self.toggle_discord.isChecked():
            blocks.append("\n".join(strategies_db.DISCORD_STRATEGY))

        blocks.append("\n".join(strategies_db.GAME_STRATEGY))

        full_text = "\n--new\n".join(blocks)

        try:
            if not self.lists_dir.exists():
                self.lists_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = self.lists_dir / "custom_strategy.txt"
            file_path.write_text(full_text, encoding="utf-8")
            
            QMessageBox.information(self, "Успех", "Стратегия собрана и сохранена!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить:\n{e}")