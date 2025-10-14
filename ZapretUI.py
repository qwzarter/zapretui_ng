import sys
import os
import json
import ctypes
import time
import subprocess
from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal, QRectF, Property, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon, QFont, QPalette, QColor, QPainter, QBrush
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QMessageBox, QSizePolicy, QCheckBox,
    QGraphicsOpacityEffect, QGraphicsColorizeEffect, QGraphicsDropShadowEffect
)

class ToggleSwitch(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(50, 28)

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
        painter.drawRoundedRect(QRectF(0, 0, 50, 28), 14, 14)

        knob_color = QColor("#FFFFFF")
        if self._locked:
            knob_color = QColor(180, 180, 180)
        painter.setBrush(QBrush(knob_color))
        painter.drawEllipse(QRectF(self._handle_x, 3, 22, 22))

        if self._locked:
            painter.setBrush(QColor(0, 0, 0, 60))
            painter.drawRoundedRect(QRectF(0, 0, 50, 28), 14, 14)

class WorkerThread(QThread):
    output = Signal(str)
    finished = Signal()

    def __init__(self, cmd, cwd):
        super().__init__()
        self.cmd = cmd
        self.cwd = cwd
        self.process = None
        self.running = True

    def run(self):
        try:
            creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            self.process = subprocess.Popen(
                self.cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=creationflags,
                cwd=self.cwd
            )
            for line in iter(self.process.stdout.readline, ''):
                if not self.running:
                    break
                if line:
                    self.output.emit(line.rstrip())
            if self.process:
                self.process.wait()
        except Exception as e:
            self.output.emit(f"Ошибка: {e}")
        self.finished.emit()

    def stop(self):
        try:
            if self.process and self.process.poll() is None:
                try:
                    self.process.terminate()
                except Exception:
                    pass
                time.sleep(1)
                if self.process.poll() is None:
                    subprocess.run(["taskkill", "/f", "/im", "winws.exe"], capture_output=True)
        except Exception as e:
            self.output.emit(f"Ошибка остановки: {e}")
        finally:
            self.running = False
            self.finished.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zapret UI")
        self.setFixedSize(400, 480)

        self.script_dir = Path(__file__).parent
        self.settings_path = self.script_dir / "settings.json"
        self.bin_dir = self.script_dir / "bin"
        self.lists_dir = self.script_dir / "lists"
        self.winws_exe = self.bin_dir / "winws.exe"
        self.settings = self.load_settings()

        self.is_connected = False
        self.current_thread = None

        self.font_default = QFont("Segoe UI", 12)
        self.font_bold = QFont("Segoe UI", 14, QFont.Bold)
        self.font_title = QFont("Segoe UI Black", 40, QFont.Bold)

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignVCenter)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setAlignment(Qt.AlignTop)

        title_label = QLabel("Zapret UI")
        title_label.setFont(self.font_title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #3B82F6; letter-spacing: 1px;")
        content_layout.addWidget(title_label)

        self.combo = QComboBox()
        self.combo.setFont(self.font_default)
        self.combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.combo.setMinimumWidth(300)
        arrow_path = (self.script_dir / "arrow_down_white.svg").as_posix()
        self.combo.setStyleSheet(f"""
            QComboBox {{
                background-color: #1E2030;
                color: #E6E9F0;
                border: 1px solid #2B3A64;
                border-radius: 6px;
                height: 38px;
                padding: 0 36px 0 10px;
            }}

            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 36px;
                border-left: 1px solid #2B3A64;
                background-color: #2D5BE3;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
            }}

            QComboBox::down-arrow {{
                image: url({arrow_path});
                width: 30px;
                height: 30px;
                margin-right: 0px;
                margin-top: 0px;
            }}

            QComboBox QAbstractItemView {{
                background-color: #1A1F3A;
                border: 1px solid #2B3A64;
                selection-background-color: #2E4DB7;
                color: #E9ECF5;
                outline: none;
            }}

            QScrollBar:vertical {{
                border: none;
                background: #1E2030;
                width: 10px;
                margin: 2px 2px 2px 0;
                border-radius: 4px;
            }}

            QScrollBar::handle:vertical {{
                background: #2D5BE3;
                min-height: 20px;
                border-radius: 4px;
            }}

            QScrollBar::handle:vertical:hover {{
                background: #3B74FF;
            }}

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                background: none;
                height: 0px;
            }}

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)
        strategies = [
            "Стандартный", "ALT", "ALT2 (Рекомендуемый)", "ALT3", "ALT4",
            "ALT5", "ALT6", "ALT7", "ALT8",
            "FAKE TLS AUTO", "FAKE TLS AUTO ALT", "FAKE TLS AUTO ALT2",
            "FAKE TLS AUTO ALT3", "SIMPLE FAKE (MGTS)", "SIMPLE FAKE ALT (MGTS ALT)"
        ]
        self.combo.addItems(strategies)
        self.combo.setCurrentText(self.settings.get("selected_strategy", "ALT2 (Рекомендуемый)"))
        content_layout.addWidget(self.combo)

        self.connect_button = QPushButton("Подключить")
        self.connect_button.setFont(self.font_bold)
        self.connect_button.setStyleSheet(self.style_button_green())
        self.connect_button.clicked.connect(self.handle_connect_toggle)
        self.connect_button.setMinimumHeight(48)
        self.connect_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        content_layout.addWidget(self.connect_button)

        status_container = QWidget()
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(6)

        label_status = QLabel("Статус:")
        label_status.setFont(self.font_default)
        label_status.setStyleSheet("color: gray;")

        self.status_value = QLabel("Отключено")
        self.status_value.setFont(self.font_bold)
        self.status_value.setStyleSheet("color: gray;")

        status_layout.addStretch()
        status_layout.addWidget(label_status)
        status_layout.addWidget(self.status_value)
        status_layout.addStretch()

        content_layout.addWidget(status_container, alignment=Qt.AlignCenter)

        game_frame = QWidget()
        game_frame.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 10px 16px;
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(0, 0, 0, 80))
        game_frame.setGraphicsEffect(shadow)

        game_layout = QHBoxLayout(game_frame)
        game_layout.setContentsMargins(0, 5, 20, 5)
        game_layout.setSpacing(10)

        label_game = QLabel("Игровой режим:")
        label_game.setFont(self.font_default)
        label_game.setStyleSheet("color: white; background: transparent;")

        self.game_mode = ToggleSwitch()
        self.game_mode.setChecked(self.settings.get("game_mode", False))
        self.game_mode.stateChanged.connect(self.on_game_mode_toggle)

        game_layout.addWidget(label_game)
        game_layout.addStretch()
        game_layout.addWidget(self.game_mode)

        content_layout.addWidget(game_frame)

        main_layout.addWidget(content, alignment=Qt.AlignVCenter)

        content_layout.setStretch(0, 0)
        content_layout.setStretch(1, 1)
        content_layout.setStretch(2, 1)
        content_layout.setStretch(3, 1)
        content_layout.setStretch(4, 1)

        self.apply_dark_theme()

        if not self.is_admin():
            box = QMessageBox(self)
            box.setWindowTitle("Требуются права администратора")
            box.setText("Для работы приложения требуются права администратора.\nПерезапустить с повышенными правами?")
            box.setIcon(QMessageBox.Warning)
            box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            box.setDefaultButton(QMessageBox.Yes)
            box.setStyleSheet("""
                QMessageBox {
                    background-color: #1E2030;
                    color: #E6E9F0;
                    border: 1px solid #2B3A64;
                }
                QMessageBox QLabel {
                    color: #E6E9F0;
                    font-size: 13px;
                }
                QPushButton {
                    background-color: #2D5BE3;
                    color: white;
                    border-radius: 6px;
                    padding: 6px 16px;
                }
                QPushButton:hover {
                    background-color: #3B74FF;
                }
            """)
            answer = box.exec()

            if answer == QMessageBox.Yes:
                self.run_as_admin()
            else:
                pass

        self.log("Интерфейс готов.")
        self.update_ui_state()

    def show_error(self, title: str, message: str):
        box = QMessageBox(self)
        box.setWindowTitle(title)
        box.setText(message)
        box.setIcon(QMessageBox.Critical)
        box.setStyleSheet("""
            QMessageBox {
                background-color: #1E2030;
                color: #E6E9F0;
                border: 1px solid #2B3A64;
            }
            QMessageBox QLabel {
                color: #E6E9F0;
                font-size: 13px;
            }
            QPushButton {
                background-color: #2D5BE3;
                color: white;
                border-radius: 6px;
                padding: 6px 16px;
            }
            QPushButton:hover {
                background-color: #3B74FF;
            }
        """)
        box.exec()

    def set_widget_locked(self, widget, locked):
        if isinstance(widget, QComboBox):
            arrow_path = (self.script_dir / "arrow_down_white.svg").as_posix()

            if locked:
                widget.setStyleSheet(f"""
                    QComboBox {{
                        background-color: #282B3A;
                        color: #9FA4B7;
                        border: 1px solid #2F3650;
                        border-radius: 6px;
                        height: 38px;
                        padding: 0 36px 0 10px;
                    }}

                    QComboBox::drop-down {{
                        subcontrol-origin: padding;
                        subcontrol-position: top right;
                        width: 36px;
                        border-left: 1px solid #2F3650;
                        background-color: #3A3D4F;
                        border-top-right-radius: 6px;
                        border-bottom-right-radius: 6px;
                    }}

                    QComboBox::down-arrow {{
                        image: url({arrow_path});
                        width: 30px;
                        height: 30px;
                        margin-right: 0px;
                        margin-top: 0px;
                    }}

                    QComboBox QAbstractItemView {{
                        background-color: #1A1F3A;
                        border: 1px solid #2B3A64;
                        selection-background-color: #3A4C82;
                        color: #9FA4B7;
                        outline: none;
                    }}
                """)
                widget.setEnabled(False)
            else:
                widget.setStyleSheet(f"""
                    QComboBox {{
                        background-color: #1E2030;
                        color: #E6E9F0;
                        border: 1px solid #2B3A64;
                        border-radius: 6px;
                        height: 38px;
                        padding: 0 36px 0 10px;
                    }}

                    QComboBox::drop-down {{
                        subcontrol-origin: padding;
                        subcontrol-position: top right;
                        width: 36px;
                        border-left: 1px solid #2B3A64;
                        background-color: #2D5BE3;
                        border-top-right-radius: 6px;
                        border-bottom-right-radius: 6px;
                    }}

                    QComboBox::down-arrow {{
                        image: url({arrow_path});
                        width: 30px;
                        height: 30px;
                        margin-right: 0px;
                        margin-top: 0px;
                    }}

                    /* ВЫПАДАЮЩИЙ СПИСОК */
                    QComboBox QAbstractItemView {{
                        background-color: #1A1F3A;
                        border: 1px solid #2B3A64;
                        selection-background-color: #2E4DB7;
                        selection-color: #FFFFFF;
                        color: #E9ECF5;
                        outline: none;
                    }}

                    /* КАСТОМНЫЙ SCROLLBAR */
                    QComboBox QScrollBar:vertical {{
                        border: none;
                        background: #1A1F3A;
                        width: 10px;
                        margin: 2px 2px 2px 0;
                        border-radius: 4px;
                    }}

                    QComboBox QScrollBar::handle:vertical {{
                        background: #2D5BE3;
                        min-height: 20px;
                        border-radius: 4px;
                    }}

                    QComboBox QScrollBar::handle:vertical:hover {{
                        background: #3B74FF;
                    }}

                    QComboBox QScrollBar::add-line:vertical,
                    QComboBox QScrollBar::sub-line:vertical {{
                        background: none;
                        height: 0px;
                    }}

                    QComboBox QScrollBar::add-page:vertical,
                    QComboBox QScrollBar::sub-page:vertical {{
                        background: none;
                    }}
                """)
                widget.setEnabled(True)
            return

        effect = QGraphicsOpacityEffect()
        effect.setOpacity(0.5 if locked else 1.0)
        widget.setGraphicsEffect(effect)
        widget.setEnabled(not locked)

        effect = QGraphicsOpacityEffect()
        effect.setOpacity(0.5 if locked else 1.0)
        widget.setGraphicsEffect(effect)
        widget.setEnabled(not locked)

    def update_cursor_state(self):
        """Обновляет курсоры всех кликабельных элементов в зависимости от состояния"""
        if self.is_connected:
            self.connect_button.setCursor(Qt.PointingHandCursor)
            self.combo.setCursor(Qt.ForbiddenCursor)
            self.game_mode.setCursorType(Qt.ForbiddenCursor)

            view = self.combo.view()
            if view:
                view.viewport().setCursor(Qt.ForbiddenCursor)
                view.setCursor(Qt.ForbiddenCursor)

            self.combo.setStyleSheet(self.combo.styleSheet() + " QComboBox::drop-down { cursor: forbidden; }")

        else:
            self.connect_button.setCursor(Qt.PointingHandCursor)
            self.combo.setCursor(Qt.PointingHandCursor)
            self.game_mode.setCursor(Qt.PointingHandCursor)

            view = self.combo.view()
            if view:
                view.viewport().setCursor(Qt.PointingHandCursor)
                view.setCursor(Qt.PointingHandCursor)

            self.combo.setStyleSheet(self.combo.styleSheet() + " QComboBox::drop-down { cursor: pointinghand; }")

    def style_button_green(self):
        return """
        QPushButton {
            background-color: #16A34A;
            color: white;
            border-radius: 10px;
            height: 45px;
            font-weight: bold;
        }
        QPushButton:hover { background-color: #15803D; }
        """

    def style_button_red(self):
        return """
        QPushButton {
            background-color: #DC2626;
            color: white;
            border-radius: 10px;
            height: 45px;
            font-weight: bold;
        }
        QPushButton:hover { background-color: #B91C1C; }
        """

    def apply_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(27, 34, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(24, 28, 43))
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(27, 34, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        QApplication.instance().setPalette(palette)

    def load_settings(self):
        try:
            if self.settings_path.exists():
                with open(self.settings_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def save_settings(self):
        data = {
            "selected_strategy": self.combo.currentText(),
            "game_mode": self.game_mode.isChecked()
        }
        try:
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            return False

    def run_as_admin(self):
        try:
            params = " ".join(f'"{arg}"' for arg in sys.argv[1:])
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, f'"{__file__}" {params}', None, 1
            )
            sys.exit(0)
        except Exception as e:
            self.show_error("Ошибка", f"Не удалось запустить от имени администратора:\n{e}")

    def log(self, msg):
        print(f"[{time.strftime('%H:%M:%S')}] {msg}")

    def handle_connect_toggle(self):
        if self.is_connected:
            self.stop_zapret()
        else:
            self.start_zapret()

    def start_zapret(self):
        try:
            if not self.winws_exe.exists():
                self.show_error("Ошибка", f"Файл {self.winws_exe} не найден!")
                return
            if not self.lists_dir.exists():
                self.show_error("Ошибка", f"Папка {self.lists_dir} не найдена!")
                return

            mode = self.combo.currentText()
            self.log(f"Запуск режима: {mode}")

            params = self.get_script_parameters(mode)
            cmd = [str(self.winws_exe)] + params

            self.log("Выполняется команда:")
            self.log(" ".join(cmd))

            self.current_thread = WorkerThread(cmd, str(self.bin_dir))
            self.current_thread.output.connect(self.log)
            self.current_thread.finished.connect(self.on_process_finished)
            self.current_thread.start()

            self.is_connected = True
            self.update_ui_state()

        except Exception as e:
            self.show_error("Ошибка запуска", str(e))

    def stop_zapret(self):
        try:
            if self.current_thread and self.current_thread.isRunning():
                self.current_thread.stop()
            else:
                subprocess.run(["taskkill", "/f", "/im", "winws.exe"], capture_output=True)

            self.current_thread = None
            self.is_connected = False
            self.update_ui_state()
            self.log("Процесс winws.exe остановлен.")
        except Exception as e:
            self.log(f"Ошибка остановки: {e}")
            self.show_error("Ошибка", f"Не удалось остановить процесс:\n{e}")

    def on_process_finished(self):
        self.log("Процесс завершён.")
        self.current_thread = None
        self.is_connected = False
        self.update_ui_state()

    def on_game_mode_toggle(self):
        if self.game_mode.isChecked():
            self.log("Игровой режим включён (фильтр: 1024-65535)")
        else:
            self.log("Игровой режим выключен (фильтр: 12)")
        self.save_settings()

    def update_ui_state(self):
        if self.is_connected:
            self.connect_button.setText("Отключить")
            self.connect_button.setStyleSheet(self.style_button_red())
            self.status_value.setText("Подключено")
            self.status_value.setStyleSheet("color: #16A34A;")

            self.combo.setEnabled(False)
            self.game_mode.setEnabled(False)

            self.set_widget_locked(self.combo, True)
            self.game_mode.setLocked(True)

        else:
            self.connect_button.setText("Подключить")
            self.connect_button.setStyleSheet(self.style_button_green())
            self.status_value.setText("Отключено")
            self.status_value.setStyleSheet("color: gray;")

            self.combo.setEnabled(True)
            self.game_mode.setEnabled(True)

            self.set_widget_locked(self.combo, False)
            self.game_mode.setLocked(False)

        self.connect_button.setCursor(Qt.PointingHandCursor)
        self.combo.setCursor(Qt.PointingHandCursor)
        self.game_mode.setCursor(Qt.PointingHandCursor)

    def closeEvent(self, event):
        if self.is_connected:
            self.stop_zapret()

        self.save_settings()
        event.accept()

    def get_script_parameters(self, mode):
        if self.game_mode.isChecked():
            game_filter = "1024-65535"
        else:
            game_filter = "12"

        base_params = [
            f"--wf-tcp=80,443,2053,2083,2087,2096,8443,{game_filter}",
            f"--wf-udp=443,19294-19344,50000-50100,{game_filter}"
        ]

        base_filters = [
            '--filter-udp=443', '--hostlist', f'{self.lists_dir}/list-general.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6',
            '--dpi-desync-fake-quic', f'{self.bin_dir}/quic_initial_www_google_com.bin', '--new',

            '--filter-udp=19294-19344,50000-50100', '--filter-l7=discord,stun',
            '--dpi-desync=fake', '--dpi-desync-repeats=6', '--new',

            '--filter-tcp=80', '--hostlist', f'{self.lists_dir}/list-general.txt',
            '--dpi-desync=fake,multisplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new'
        ]

        mode_params = {
            "Стандартный": [
                '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
                '--dpi-desync=fake,multidisorder', '--dpi-desync-split-pos=midsld',
                '--dpi-desync-repeats=8', '--dpi-desync-fooling=md5sig,badseq', '--new',

                '--filter-tcp=443', '--hostlist', f'{self.lists_dir}/list-general.txt',
                '--dpi-desync=fake,multidisorder', '--dpi-desync-split-pos=midsld',
                '--dpi-desync-repeats=8', '--dpi-desync-fooling=md5sig,badseq', '--new',

                '--filter-udp=443', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake', '--dpi-desync-repeats=6',
                '--dpi-desync-fake-quic', f'{self.bin_dir}/quic_initial_www_google_com.bin', '--new',

                '--filter-tcp=80', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake,multisplit', '--dpi-desync-autottl=2',
                '--dpi-desync-fooling=md5sig', '--new',

                f'--filter-tcp=443,{game_filter}', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake,multidisorder', '--dpi-desync-split-pos=midsld',
                '--dpi-desync-repeats=6', '--dpi-desync-fooling=md5sig,badseq', '--new',

                f'--filter-udp={game_filter}', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=10',
                '--dpi-desync-any-protocol=1',
                '--dpi-desync-fake-unknown-udp', f'{self.bin_dir}/quic_initial_www_google_com.bin',
                '--dpi-desync-cutoff=n2'
            ],

            "ALT": [
                '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
                '--dpi-desync=fake,fakedsplit', '--dpi-desync-repeats=6', '--dpi-desync-fooling=ts',
                '--dpi-desync-fakedsplit-pattern=0x00', '--dpi-desync-fake-tls', f'{self.bin_dir}/tls_clienthello_www_google_com.bin', '--new',

                '--filter-tcp=443', '--hostlist', f'{self.lists_dir}/list-general.txt',
                '--dpi-desync=fake,fakedsplit', '--dpi-desync-repeats=6', '--dpi-desync-fooling=ts',
                '--dpi-desync-fakedsplit-pattern=0x00', '--dpi-desync-fake-tls', f'{self.bin_dir}/tls_clienthello_www_google_com.bin', '--new',

                '--filter-udp=443', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake', '--dpi-desync-repeats=6',
                '--dpi-desync-fake-quic', f'{self.bin_dir}/quic_initial_www_google_com.bin', '--new',

                '--filter-tcp=80', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake,multisplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new',

                f'--filter-tcp=443,{game_filter}', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake,fakedsplit', '--dpi-desync-repeats=6', '--dpi-desync-fooling=ts',
                '--dpi-desync-fakedsplit-pattern=0x00', '--dpi-desync-fake-tls', f'{self.bin_dir}/tls_clienthello_www_google_com.bin', '--new',

                f'--filter-udp={game_filter}', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=12',
                '--dpi-desync-any-protocol=1', '--dpi-desync-fake-unknown-udp', f'{self.bin_dir}/quic_initial_www_google_com.bin', '--dpi-desync-cutoff=n3'
            ],

            "ALT2 (Рекомендуемый)": [
                '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
                '--dpi-desync=multisplit', '--dpi-desync-split-seqovl=652', '--dpi-desync-split-pos=2',
                '--dpi-desync-split-seqovl-pattern', f'{self.bin_dir}/tls_clienthello_www_google_com.bin', '--new',

                '--filter-tcp=443', '--hostlist', f'{self.lists_dir}/list-general.txt',
                '--dpi-desync=multisplit', '--dpi-desync-split-seqovl=652', '--dpi-desync-split-pos=2',
                '--dpi-desync-split-seqovl-pattern', f'{self.bin_dir}/tls_clienthello_www_google_com.bin', '--new',

                '--filter-udp=443', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fake-quic',
                f'{self.bin_dir}/quic_initial_www_google_com.bin', '--new',

                '--filter-tcp=80', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake,multisplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new',

                f'--filter-tcp=443,{game_filter}', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=multisplit', '--dpi-desync-split-seqovl=652', '--dpi-desync-split-pos=2',
                '--dpi-desync-split-seqovl-pattern', f'{self.bin_dir}/tls_clienthello_www_google_com.bin', '--new',

                f'--filter-udp={game_filter}', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=12',
                '--dpi-desync-any-protocol=1', '--dpi-desync-fake-unknown-udp', f'{self.bin_dir}/quic_initial_www_google_com.bin', '--dpi-desync-cutoff=n2'
            ],

            "ALT3": [
                '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
                '--dpi-desync=fakedsplit', '--dpi-desync-split-pos=1', '--dpi-desync-autottl',
                '--dpi-desync-fooling=badseq', '--dpi-desync-repeats=8', '--new',

                '--filter-tcp=443', '--hostlist', f'{self.lists_dir}/list-general.txt',
                '--dpi-desync=fakedsplit', '--dpi-desync-split-pos=1', '--dpi-desync-autottl',
                '--dpi-desync-fooling=badseq', '--dpi-desync-repeats=8', '--new',

                '--filter-udp=443', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fake-quic',
                f'{self.bin_dir}/quic_initial_www_google_com.bin', '--new',

                '--filter-tcp=80', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake,multisplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new',

                f'--filter-tcp=443,{game_filter}', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fakedsplit', '--dpi-desync-split-pos=1', '--dpi-desync-autottl',
                '--dpi-desync-fooling=badseq', '--dpi-desync-repeats=8', '--new',

                f'--filter-udp={game_filter}', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=10',
                '--dpi-desync-any-protocol=1', '--dpi-desync-fake-unknown-udp',
                f'{self.bin_dir}/quic_initial_www_google_com.bin', '--dpi-desync-cutoff=n2'
            ],

            "ALT4": [
                '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
                '--dpi-desync=fake,multisplit', '--dpi-desync-repeats=6', '--dpi-desync-fooling=md5sig',
                '--dpi-desync-fake-tls', f'{self.bin_dir}/tls_clienthello_www_google_com.bin', '--new',

                '--filter-tcp=443', '--hostlist', f'{self.lists_dir}/list-general.txt',
                '--dpi-desync=fake,multisplit', '--dpi-desync-repeats=6', '--dpi-desync-fooling=md5sig',
                '--dpi-desync-fake-tls', f'{self.bin_dir}/tls_clienthello_www_google_com.bin', '--new',

                '--filter-udp=443', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fake-quic',
                f'{self.bin_dir}/quic_initial_www_google_com.bin', '--new',

                '--filter-tcp=80', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake,multisplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new',

                f'--filter-tcp=443,{game_filter}', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake,multisplit', '--dpi-desync-repeats=6', '--dpi-desync-fooling=md5sig',
                '--dpi-desync-fake-tls', f'{self.bin_dir}/tls_clienthello_www_google_com.bin', '--new',

                f'--filter-udp={game_filter}', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=10',
                '--dpi-desync-any-protocol=1', '--dpi-desync-fake-unknown-udp',
                f'{self.bin_dir}/quic_initial_www_google_com.bin', '--dpi-desync-cutoff=n2'
            ],

            "ALT5": [
                '--filter-l3=ipv4', '--filter-tcp=443,2053,2083,2087,2096,8443', '--dpi-desync=syndata', '--new',

                '--filter-tcp=80', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake,multisplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new',

                '--filter-udp=443', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fake-quic',
                f'{self.bin_dir}/quic_initial_www_google_com.bin', '--new',

                f'--filter-udp={game_filter}', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=14',
                '--dpi-desync-any-protocol=1', '--dpi-desync-fake-unknown-udp',
                f'{self.bin_dir}/quic_initial_www_google_com.bin', '--dpi-desync-cutoff=n3'
            ],

            "ALT6": [
                '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
                '--dpi-desync=multisplit', '--dpi-desync-split-seqovl=681', '--dpi-desync-split-pos=1',
                '--dpi-desync-split-seqovl-pattern', f'{self.bin_dir}/tls_clienthello_www_google_com.bin', '--new',

                '--filter-tcp=443', '--hostlist', f'{self.lists_dir}/list-general.txt',
                '--dpi-desync=multisplit', '--dpi-desync-split-seqovl=681', '--dpi-desync-split-pos=1',
                '--dpi-desync-split-seqovl-pattern', f'{self.bin_dir}/tls_clienthello_www_google_com.bin', '--new',

                '--filter-udp=443', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fake-quic',
                f'{self.bin_dir}/quic_initial_www_google_com.bin', '--new',

                '--filter-tcp=80', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake,multisplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new',

                f'--filter-tcp=443,{game_filter}', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=multisplit', '--dpi-desync-split-seqovl=681', '--dpi-desync-split-pos=1',
                '--dpi-desync-split-seqovl-pattern', f'{self.bin_dir}/tls_clienthello_www_google_com.bin', '--new',

                f'--filter-udp={game_filter}', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=12',
                '--dpi-desync-any-protocol=1', '--dpi-desync-fake-unknown-udp',
                f'{self.bin_dir}/quic_initial_www_google_com.bin', '--dpi-desync-cutoff=n2'
            ],

            "ALT7": [
                '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
                '--dpi-desync=multisplit', '--dpi-desync-split-pos=2,sniext+1', '--dpi-desync-split-seqovl=679',
                '--dpi-desync-split-seqovl-pattern', f'{self.bin_dir}/tls_clienthello_www_google_com.bin', '--new',

                '--filter-tcp=443', '--hostlist', f'{self.lists_dir}/list-general.txt',
                '--dpi-desync=multisplit', '--dpi-desync-split-pos=2,sniext+1', '--dpi-desync-split-seqovl=679',
                '--dpi-desync-split-seqovl-pattern', f'{self.bin_dir}/tls_clienthello_www_google_com.bin', '--new',

                '--filter-udp=443', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fake-quic',
                f'{self.bin_dir}/quic_initial_www_google_com.bin', '--new',

                '--filter-tcp=80', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake,multisplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new',

                '--filter-tcp=443', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=syndata', '--new',

                f'--filter-udp={game_filter}', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=12',
                '--dpi-desync-any-protocol=1', '--dpi-desync-fake-unknown-udp',
                f'{self.bin_dir}/quic_initial_www_google_com.bin', '--dpi-desync-cutoff=n2'
            ],

            "ALT8": [
                '--filter-tcp=80', '--hostlist', f'{self.lists_dir}/list-general.txt',
                '--dpi-desync=fake,split2', '--dpi-desync-autottl=2', '--dpi-desync-fooling=badseq',
                '--dpi-desync-badseq-increment=2', '--new',

                '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
                '--dpi-desync=fake', '--dpi-desync-fake-tls-mod=none', '--dpi-desync-repeats=6',
                '--dpi-desync-fooling=badseq', '--dpi-desync-badseq-increment=2', '--new',

                '--filter-tcp=443', '--hostlist', f'{self.lists_dir}/list-general.txt',
                '--dpi-desync=fake', '--dpi-desync-fake-tls-mod=none', '--dpi-desync-repeats=6',
                '--dpi-desync-fooling=badseq', '--dpi-desync-badseq-increment=2', '--new',

                '--filter-udp=443', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fake-quic',
                f'{self.bin_dir}/quic_initial_www_google_com.bin', '--new',

                '--filter-tcp=80', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake,split2', '--dpi-desync-autottl=2', '--dpi-desync-fooling=badseq',
                '--dpi-desync-badseq-increment=2', '--new',

                '--filter-tcp=443', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=syndata', '--new',

                f'--filter-udp={game_filter}', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=12',
                '--dpi-desync-any-protocol=1', '--dpi-desync-fake-unknown-udp',
                f'{self.bin_dir}/quic_initial_www_google_com.bin', '--dpi-desync-cutoff=n2'
            ],

            "FAKE TLS AUTO": [
                '--filter-udp=443', '--hostlist', f'{self.lists_dir}/list-general.txt',
                '--dpi-desync=fake', '--dpi-desync-repeats=11', '--dpi-desync-fake-quic',
                f'{self.bin_dir}/quic_initial_www_google_com.bin', '--new',

                '--filter-tcp=80', '--hostlist', f'{self.lists_dir}/list-general.txt',
                '--dpi-desync=fake,fakedsplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new',

                '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
                '--dpi-desync=fake,multidisorder', '--dpi-desync-split-pos=1,midsld',
                '--dpi-desync-repeats=11', '--dpi-desync-fooling=badseq',
                '--dpi-desync-fake-tls=0x00000000', '--dpi-desync-fake-tls=!',
                '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

                '--filter-tcp=443', '--hostlist', f'{self.lists_dir}/list-general.txt',
                '--dpi-desync=fake,multidisorder', '--dpi-desync-split-pos=1,midsld',
                '--dpi-desync-repeats=11', '--dpi-desync-fooling=badseq',
                '--dpi-desync-fake-tls=0x00000000', '--dpi-desync-fake-tls=!',
                '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

                '--filter-udp=443', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake', '--dpi-desync-repeats=11', '--dpi-desync-fake-quic',
                f'{self.bin_dir}/quic_initial_www_google_com.bin', '--new',

                '--filter-tcp=80', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake,fakedsplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new',

                f'--filter-tcp=443,{game_filter}', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake,multidisorder', '--dpi-desync-split-pos=1,midsld',
                '--dpi-desync-repeats=11', '--dpi-desync-fooling=badseq',
                '--dpi-desync-fake-tls=0x00000000', '--dpi-desync-fake-tls=!',
                '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

                f'--filter-udp={game_filter}', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=10',
                '--dpi-desync-any-protocol=1', '--dpi-desync-fake-unknown-udp',
                f'{self.bin_dir}/quic_initial_www_google_com.bin', '--dpi-desync-cutoff=n2'
            ],

            "FAKE TLS AUTO ALT": [
                '--filter-udp=443', '--hostlist', f'{self.lists_dir}/list-general.txt',
                '--dpi-desync=fake', '--dpi-desync-repeats=11', '--dpi-desync-fake-quic',
                f'{self.bin_dir}/quic_initial_www_google_com.bin', '--new',

                '--filter-tcp=80', '--hostlist', f'{self.lists_dir}/list-general.txt',
                '--dpi-desync=fake,fakedsplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new',

                '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
                '--dpi-desync=fake,fakedsplit', '--dpi-desync-split-pos=1',
                '--dpi-desync-fooling=badseq', '--dpi-desync-badseq-increment=10000000',
                '--dpi-desync-repeats=8', '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

                '--filter-tcp=443', '--hostlist', f'{self.lists_dir}/list-general.txt',
                '--dpi-desync=fake,fakedsplit', '--dpi-desync-split-pos=1',
                '--dpi-desync-fooling=badseq', '--dpi-desync-badseq-increment=10000000',
                '--dpi-desync-repeats=8', '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

                '--filter-udp=443', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake', '--dpi-desync-repeats=11', '--dpi-desync-fake-quic',
                f'{self.bin_dir}/quic_initial_www_google_com.bin', '--new',

                '--filter-tcp=80', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake,fakedsplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new',

                f'--filter-tcp=443,{game_filter}', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake,fakedsplit', '--dpi-desync-split-pos=1',
                '--dpi-desync-fooling=badseq', '--dpi-desync-badseq-increment=10000000',
                '--dpi-desync-repeats=8', '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

                f'--filter-udp={game_filter}', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=10',
                '--dpi-desync-any-protocol=1', '--dpi-desync-fake-unknown-udp',
                f'{self.bin_dir}/quic_initial_www_google_com.bin', '--dpi-desync-cutoff=n2'
            ],

            "FAKE TLS AUTO ALT2": [
                '--filter-udp=443', '--hostlist', f'{self.lists_dir}/list-general.txt',
                '--dpi-desync=fake', '--dpi-desync-repeats=11', '--dpi-desync-fake-quic',
                f'{self.bin_dir}/quic_initial_www_google_com.bin', '--new',

                '--filter-tcp=80', '--hostlist', f'{self.lists_dir}/list-general.txt',
                '--dpi-desync=fake,fakedsplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new',

                '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
                '--dpi-desync=fake,multisplit', '--dpi-desync-split-seqovl=681',
                '--dpi-desync-split-pos=1', '--dpi-desync-fooling=badseq',
                '--dpi-desync-badseq-increment=10000000', '--dpi-desync-repeats=8',
                '--dpi-desync-split-seqovl-pattern', f'{self.bin_dir}/tls_clienthello_www_google_com.bin',
                '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',


                '--filter-tcp=443', '--hostlist', f'{self.lists_dir}/list-general.txt',
                '--dpi-desync=fake,multisplit', '--dpi-desync-split-seqovl=681',
                '--dpi-desync-split-pos=1', '--dpi-desync-fooling=badseq',
                '--dpi-desync-badseq-increment=10000000', '--dpi-desync-repeats=8',
                '--dpi-desync-split-seqovl-pattern', f'{self.bin_dir}/tls_clienthello_www_google_com.bin',
                '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',


                '--filter-udp=443', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake', '--dpi-desync-repeats=11', '--dpi-desync-fake-quic',
                f'{self.bin_dir}/quic_initial_www_google_com.bin', '--new',


                '--filter-tcp=80', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake,fakedsplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new',


                f'--filter-tcp=443,{game_filter}', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake,multisplit', '--dpi-desync-split-seqovl=681',
                '--dpi-desync-split-pos=1', '--dpi-desync-fooling=badseq',
                '--dpi-desync-badseq-increment=10000000', '--dpi-desync-repeats=8',
                '--dpi-desync-split-seqovl-pattern', f'{self.bin_dir}/tls_clienthello_www_google_com.bin',
                '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',

                f'--filter-udp={game_filter}', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=10',
                '--dpi-desync-any-protocol=1', '--dpi-desync-fake-unknown-udp',
                f'{self.bin_dir}/quic_initial_www_google_com.bin', '--dpi-desync-cutoff=n2'
            ],

            "FAKE TLS AUTO ALT3": [
                '--filter-udp=443', '--hostlist', f'{self.lists_dir}/list-general.txt',
                '--dpi-desync=fake', '--dpi-desync-repeats=11', '--dpi-desync-fake-quic',
                f'{self.bin_dir}/quic_initial_www_google_com.bin', '--new',

                '--filter-tcp=80', '--hostlist', f'{self.lists_dir}/list-general.txt',
                '--dpi-desync=fake,fakedsplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new',

                '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
                '--dpi-desync=fake,multisplit', '--dpi-desync-split-seqovl=681',
                '--dpi-desync-split-pos=1', '--dpi-desync-fooling=ts',
                '--dpi-desync-repeats=8', '--dpi-desync-split-seqovl-pattern',
                f'{self.bin_dir}/tls_clienthello_www_google_com.bin', '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',


                '--filter-tcp=443', '--hostlist', f'{self.lists_dir}/list-general.txt',
                '--dpi-desync=fake,multisplit', '--dpi-desync-split-seqovl=681',
                '--dpi-desync-split-pos=1', '--dpi-desync-fooling=ts',
                '--dpi-desync-repeats=8', '--dpi-desync-split-seqovl-pattern',
                f'{self.bin_dir}/tls_clienthello_www_google_com.bin', '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',


                '--filter-udp=443', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake', '--dpi-desync-repeats=11', '--dpi-desync-fake-quic',
                f'{self.bin_dir}/quic_initial_www_google_com.bin', '--new',


                '--filter-tcp=80', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake,fakedsplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new',


                f'--filter-tcp=443,{game_filter}', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake,multisplit', '--dpi-desync-split-seqovl=681',
                '--dpi-desync-split-pos=1', '--dpi-desync-fooling=ts',
                '--dpi-desync-repeats=8', '--dpi-desync-split-seqovl-pattern',
                f'{self.bin_dir}/tls_clienthello_www_google_com.bin', '--dpi-desync-fake-tls-mod=rnd,dupsid,sni=www.google.com', '--new',


                f'--filter-udp={game_filter}', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=10',
                '--dpi-desync-any-protocol=1', '--dpi-desync-fake-unknown-udp',
                f'{self.bin_dir}/quic_initial_www_google_com.bin', '--dpi-desync-cutoff=n2'
            ],

            "SIMPLE FAKE (MGTS)": [
                '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
                '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fooling=ts',
                '--dpi-desync-fake-tls', f'{self.bin_dir}/tls_clienthello_www_google_com.bin', '--new',

                '--filter-tcp=443', '--hostlist', f'{self.lists_dir}/list-general.txt',
                '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fooling=ts',
                '--dpi-desync-fake-tls', f'{self.bin_dir}/tls_clienthello_www_google_com.bin', '--new',

                '--filter-udp=443', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fake-quic',
                f'{self.bin_dir}/quic_initial_www_google_com.bin', '--new',

                '--filter-tcp=80', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake,multisplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new',

                f'--filter-tcp=443,{game_filter}', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fooling=ts',
                '--dpi-desync-fake-tls', f'{self.bin_dir}/tls_clienthello_www_google_com.bin', '--new',

                f'--filter-udp={game_filter}', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=12',
                '--dpi-desync-any-protocol=1', '--dpi-desync-fake-unknown-udp',
                f'{self.bin_dir}/quic_initial_www_google_com.bin', '--dpi-desync-cutoff=n3'
            ],

            "SIMPLE FAKE ALT (MGTS ALT)": [
                '--filter-tcp=2053,2083,2087,2096,8443', '--hostlist-domains=discord.media',
                '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fooling=badseq',
                '--dpi-desync-badseq-increment=10000000', '--dpi-desync-fake-tls',
                f'{self.bin_dir}/tls_clienthello_www_google_com.bin', '--new',

                '--filter-tcp=443', '--hostlist', f'{self.lists_dir}/list-general.txt',
                '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fooling=badseq',
                '--dpi-desync-badseq-increment=10000000', '--dpi-desync-fake-tls',
                f'{self.bin_dir}/tls_clienthello_www_google_com.bin', '--new',

                '--filter-udp=443', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fake-quic',
                f'{self.bin_dir}/quic_initial_www_google_com.bin', '--new',

                '--filter-tcp=80', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake,multisplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new',

                f'--filter-tcp=443,{game_filter}', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake', '--dpi-desync-repeats=6', '--dpi-desync-fooling=badseq',
                '--dpi-desync-badseq-increment=10000000', '--dpi-desync-fake-tls',
                f'{self.bin_dir}/tls_clienthello_www_google_com.bin', '--new',

                f'--filter-udp={game_filter}', '--ipset', f'{self.lists_dir}/ipset-all.txt',
                '--dpi-desync=fake', '--dpi-desync-autottl=2', '--dpi-desync-repeats=10',
                '--dpi-desync-any-protocol=1', '--dpi-desync-fake-unknown-udp',
                f'{self.bin_dir}/quic_initial_www_google_com.bin', '--dpi-desync-cutoff=n2'
            ]
        }

        params = base_params + base_filters
        if mode in mode_params:
            params += mode_params[mode]

        return params

if __name__ == "__main__":
    app = QApplication(sys.argv)
    icon_path = Path(__file__).parent / "icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
