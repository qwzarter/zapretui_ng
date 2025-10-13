import os
import sys
import json
import subprocess
import threading
import time
from pathlib import Path
import ctypes
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import tkinter as tk

class CustomDropdown(ctk.CTkFrame):
    def __init__(self, master, values, variable=None, width=325, font=None, bold_font=None, **kwargs):
        super().__init__(master, fg_color="#1E2030", corner_radius=10, **kwargs)
        self.font = font or ctk.CTkFont(family="Segoe UI", size=14)
        self.bold_font = bold_font or ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        self.values = values
        self.variable = variable or ctk.StringVar(value=values[0])
        self.width = width
        self.configure(width=self.width, height=44, cursor="hand2")

        self.label = ctk.CTkLabel(
            self, text=self.variable.get(),
            font=self.font,
            text_color="#E6E9F0", anchor="w"
        )
        self.label.place(relx=0.05, rely=0.5, anchor="w")

        self.arrow = ctk.CTkLabel(
            self, text="▾",
            font=self.font,
            text_color="#2D5BE3"
        )
        self.arrow.place(relx=0.95, rely=0.5, anchor="e")

        self._bound = True
        for w in (self, self.label, self.arrow):
            w.bind("<Button-1>", self.toggle_dropdown)

        self.dropdown = None
        self.master.bind("<Button-1>", self._click_outside, add="+")

        try:
            self.variable.trace_add("write", self._on_variable_change)
        except Exception:
            try:
                self.variable.trace("w", lambda *a: self._on_variable_change())
            except Exception:
                pass

    def _on_variable_change(self, *args):
        try:
            self.label.configure(text=self.variable.get())
        except Exception:
            pass

    def toggle_dropdown(self, event=None):
        if not self._bound:
            return
        if self.dropdown and self.dropdown.winfo_exists():
            self.close_dropdown()
        else:
            self.open_dropdown()

    def open_dropdown(self):
        if self.dropdown and self.dropdown.winfo_exists():
            self.close_dropdown()

        self.update_idletasks()

        parent = self.winfo_toplevel()

        abs_x = self.winfo_rootx()
        abs_y = self.winfo_rooty() + self.winfo_height() + 4

        x_real = abs_x - parent.winfo_rootx()
        y_real = abs_y - parent.winfo_rooty()

        item_height = 38
        desired_visible_rows = 6
        pad = 12
        inner_pad = 6

        screen_h = parent.winfo_screenheight()
        space_below = screen_h - (self.winfo_rooty() + self.winfo_height())
        max_rows_by_space = max(1, space_below // item_height)
        visible_rows = min(desired_visible_rows, max_rows_by_space)

        if visible_rows < 3:
            space_above = self.winfo_rooty() - parent.winfo_rooty()
            rows_above = max(1, space_above // item_height)
            if rows_above >= 3:
                y_real = (self.winfo_rooty() - parent.winfo_rooty()) - (item_height * min(desired_visible_rows, rows_above)) - 6
                visible_rows = min(desired_visible_rows, rows_above)
            else:
                visible_rows = max(1, visible_rows)

        dropdown_width = self.width
        dropdown_height = item_height * visible_rows + (pad * 2)

        screen_w = parent.winfo_screenwidth()
        if (x_real + dropdown_width) > screen_w:
            x_real = max(8, screen_w - dropdown_width - 8)
        if (y_real + dropdown_height) > screen_h:
            y_real = max(8, screen_h - dropdown_height - 8)

        self.dropdown = ctk.CTkFrame(
            parent,
            fg_color="#1A1F3A",
            corner_radius=12,
            width=dropdown_width,
            height=dropdown_height
        )
        self.dropdown.place(x=x_real, y=y_real)

        buffer_frame = ctk.CTkFrame(
            self.dropdown,
            fg_color="#1A1F3A",
            corner_radius=12,
            width=dropdown_width - (pad),
            height=dropdown_height - (pad)
        )
        buffer_frame.place(x=pad//2, y=pad//2)

        scroll_w = dropdown_width - (pad + 8)
        scroll_h = dropdown_height - (pad + 8)

        scroll_area = ctk.CTkScrollableFrame(
            buffer_frame,
            fg_color="#1A1F3A",
            corner_radius=0,
            width=scroll_w,
            height=scroll_h
        )
        scroll_area.place(x=(pad//2) - 2, y=(pad//2) - 2)

        self.option_buttons = []
        for val in self.values:
            btn = ctk.CTkButton(
                scroll_area,
                text=val,
                fg_color="transparent",
                hover_color="#2E4DB7",
                text_color="#E9ECF5",
                height=34,
                corner_radius=6,
                anchor="w",
                font=self.font,
                command=lambda v=val: self.select_value(v)
            )
            btn.pack(fill="x", padx=inner_pad, pady=2)
            self.option_buttons.append(btn)

        self.dropdown.lift()
        try:
            self.dropdown.configure(border_color="#2B3A64", border_width=1)
        except Exception:
            pass

    def select_value(self, value):
        self.variable.set(value)
        self.label.configure(text=value)
        self.close_dropdown()

    def close_dropdown(self):
        if self.dropdown and self.dropdown.winfo_exists():
            self.dropdown.destroy()
            self.dropdown = None

    def _click_outside(self, event):
        if not self.dropdown or not self.dropdown.winfo_exists():
            return
        x1, y1 = self.dropdown.winfo_rootx(), self.dropdown.winfo_rooty()
        x2 = x1 + self.dropdown.winfo_width()
        y2 = y1 + self.dropdown.winfo_height()
        if not (x1 <= event.x_root <= x2 and y1 <= event.y_root <= y2):
            self.close_dropdown()

    def disable(self):
        if self._bound:
            for w in (self, self.label, self.arrow):
                try:
                    w.unbind("<Button-1>")
                    w.configure(cursor="no")
                except Exception:
                    pass
            try:
                self.configure(fg_color="#2A2C36", cursor="no")
                self.label.configure(text_color="#AAB0BB")
                self.arrow.configure(text_color="#7A85B8")
            except Exception:
                pass
            self._bound = False

    def enable(self):
        if not self._bound:
            for w in (self, self.label, self.arrow):
                try:
                    w.bind("<Button-1>", self.toggle_dropdown)
                    w.configure(cursor="hand2")
                except Exception:
                    pass
            try:
                self.configure(fg_color="#1E2030", cursor="hand2")
                self.label.configure(text_color="#E6E9F0")
                self.arrow.configure(text_color="#2D5BE3")
            except Exception:
                pass
            self._bound = True

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        if not self.is_admin():
            answer = messagebox.askyesno(
                "Требуются права администратора",
                "Для работы этого приложения требуются права администратора.\n"
                "Приложение будет перезапущено с повышенными правами.\n\n"
                "Продолжить?"
            )
            if answer:
                self.run_as_admin()
            else:
                self.destroy()
                sys.exit(0)

        self.settings_path = Path(__file__).parent / "settings.json"
        self.settings = self.load_settings()
        # Централизованные шрифты
        self.default_font = ctk.CTkFont(family="Segoe UI", size=14)
        self.bold_font = ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        self.title_font = ctk.CTkFont(family="Segoe UI Black", size=54, weight="bold")


        self.is_connected = ctk.BooleanVar(value=False)
        self.strategies = [
            "Стандартный",
            "ALT",
            "ALT2 (Рекомендуемый)",
            "ALT3",
            "ALT4",
            "ALT5",
            "ALT6",
            "ALT7",
            "ALT8",
            "FAKE TLS AUTO",
            "FAKE TLS AUTO ALT",
            "FAKE TLS AUTO ALT2",
            "FAKE TLS AUTO ALT3",
            "SIMPLE FAKE (MGTS)",
            "SIMPLE FAKE ALT (MGTS ALT)"
        ]
        self.selected_strategy = ctk.StringVar(value=self.settings.get("selected_strategy", "ALT2 (Рекомендуемый)"))
        self.game_mode = ctk.BooleanVar(value=self.settings.get("game_mode", False))

        try:
            self.selected_strategy.trace_add("write", lambda *a: self.save_settings())
            self.game_mode.trace_add("write", lambda *a: self.save_settings())
        except Exception:
            try:
                self.selected_strategy.trace("w", lambda *a: self.save_settings())
                self.game_mode.trace("w", lambda *a: self.save_settings())
            except Exception:
                pass

        self.script_dir = Path(__file__).parent.absolute()
        self.bin_dir = self.script_dir / "bin"
        self.lists_dir = self.script_dir / "lists"
        self.winws_exe = self.bin_dir / "winws.exe"
        self.current_process = None

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.geometry("400x480")
        self.title("Zapret UI")
        self.resizable(False, False)
        try:
            icon_path = os.path.join(self.script_dir, "icon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception:
            pass
        self.configure(fg_color=("#1B2235", "#111427"))

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        center_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9)
        center_frame.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(center_frame, fg_color="transparent")
        header.grid(row=0, column=0, pady=(0, 25))
        try:
            logo = ctk.CTkImage(
                light_image=Image.open(os.path.join(self.script_dir, "icon.png")),
                dark_image=Image.open(os.path.join(self.script_dir, "icon.png")),
                size=(44, 44)
            )
            logo_label = ctk.CTkLabel(header, image=logo, text="")
            logo_label.pack(side="left", padx=(0, 10))
        except Exception:
            pass

        title = ctk.CTkLabel(
            header,
            text="Zapret UI",
            font=self.title_font,
            text_color="#3B82F6"
        )
        title.pack(side="left")

        self.dropdown = CustomDropdown(
            center_frame,
            values=self.strategies,
            variable=self.selected_strategy,
            width=325,
            font=self.default_font,
            bold_font=self.bold_font
        )
        self.dropdown.grid(row=1, column=0, pady=(0, 20))

        self.connect_button = ctk.CTkButton(
            center_frame,
            text="Подключить",
            font=self.bold_font,
            fg_color="#16A34A",
            hover_color="#15803D",
            text_color="#FFFFFF",
            corner_radius=12,
            height=50,
            command=self.handle_connect_toggle
        )
        self.connect_button.grid(row=2, column=0, sticky="ew", pady=(10, 25))

        status_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        status_frame.grid(row=3, column=0, pady=(0, 10))
        status_label = ctk.CTkLabel(status_frame, text="Статус:",
                                    font=self.default_font, text_color="gray")
        status_label.pack(side="left", padx=(0, 5))
        self.status_value_label = ctk.CTkLabel(status_frame, text="Отключено",
                                               font=self.bold_font,
                                               text_color="gray")
        self.status_value_label.pack(side="left")

        footer = ctk.CTkFrame(center_frame, fg_color="#181C2B", corner_radius=12)
        footer.grid(row=4, column=0, pady=(20, 0), sticky="ew")
        footer.grid_columnconfigure(0, weight=1)
        mode_label = ctk.CTkLabel(footer, text="Игровой режим:",
                                  font=self.default_font, text_color="white")
        mode_label.grid(row=0, column=0, padx=(18, 0), pady=10, sticky="w")

        self.game_switch = ctk.CTkSwitch(
            footer, text="", variable=self.game_mode,
            onvalue=True, offvalue=False,
            switch_width=60, switch_height=30,
            progress_color="#16A34A", fg_color="#555",
            button_color="white", button_hover_color="#DDD",
            command=self.on_game_mode_toggle,
            cursor="hand2"
        )
        self.game_switch.place(relx=1.075, rely=0.5, anchor="e")

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.log("Интерфейс готов.")
        self.update_ui_state()

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
            "selected_strategy": self.selected_strategy.get(),
            "game_mode": self.game_mode.get()
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
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit(0)
        except Exception:
            messagebox.showerror("Ошибка", "Не удалось запустить от имени администратора.")

    def handle_connect_toggle(self):
        if self.is_connected.get():
            self.stop_zapret()
        else:
            self.start_zapret()

    def start_zapret(self):
        """Запуск winws.exe с параметрами выбранного режима"""
        try:
            if not self.winws_exe.exists():
                messagebox.showerror("Ошибка", f"Файл {self.winws_exe} не найден!")
                return
            if not self.lists_dir.exists():
                messagebox.showerror("Ошибка", f"Папка {self.lists_dir} не найдена!")
                return

            mode = self.selected_strategy.get()
            self.log(f"Запуск режима: {mode}")

            params = self.get_script_parameters(mode)
            cmd = [str(self.winws_exe)] + params

            self.log("Выполняется команда:")
            self.log(" ".join(cmd))

            thread = threading.Thread(target=self.run_process, args=(cmd,), daemon=True)
            thread.start()

        except Exception as e:
            messagebox.showerror("Ошибка запуска", str(e))

    def run_process(self, cmd):
        try:
            creationflags = 0
            try:
                creationflags = subprocess.CREATE_NO_WINDOW
            except Exception:
                creationflags = 0

            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=creationflags,
                cwd=str(self.bin_dir)
            )
            self.is_connected.set(True)
            self.update_ui_state()
            self.log("Процесс запущен.")

            for line in iter(self.current_process.stdout.readline, ''):
                if not line:
                    break
                print(line.rstrip())

            self.current_process.wait()
            self.is_connected.set(False)
            self.update_ui_state()
            self.log("Процесс завершён.")
            self.current_process = None
        except Exception as e:
            self.log(f"Ошибка: {e}")
            self.is_connected.set(False)
            self.update_ui_state()
            self.current_process = None

    def stop_zapret(self):
        """Останавливает процесс winws.exe"""
        try:
            if self.current_process and self.current_process.poll() is None:
                self.current_process.terminate()
                time.sleep(1)
                if self.current_process.poll() is None:
                    subprocess.run(["taskkill", "/f", "/im", "winws.exe"], capture_output=True)
            else:
                subprocess.run(["taskkill", "/f", "/im", "winws.exe"], capture_output=True)

            self.current_process = None
            self.is_connected.set(False)
            self.update_ui_state()
            self.log("Процесс winws.exe остановлен.")
        except Exception as e:
            self.log(f"Ошибка остановки: {e}")
            messagebox.showerror("Ошибка", f"Не удалось остановить процесс:\n{e}")

    def get_script_parameters(self, mode):
        """
        Возвращает параметры командной строки для выбранного режима.
        game_filter теперь определяется по self.game_mode:
          True  -> "1024-65535"
          False -> "12"
        """
        if self.game_mode.get():
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

    def disable_game_switch(self):
        self.switch_locked = True
        self.game_switch.configure(
            state="disabled",
            progress_color="#6B7280",
            fg_color="#374151",
            button_color="#9CA3AF",
            cursor="no"
        )

    def enable_game_switch(self):
        self.switch_locked = False
        self.game_switch.configure(
            state="normal",
            progress_color="#16A34A",
            fg_color="#555",
            button_color="white",
            cursor="hand2"
        )

    def update_ui_state(self):
        if self.is_connected.get():
            self.connect_button.configure(text="Отключить", fg_color="#DC2626", hover_color="#B91C1C")
            self.status_value_label.configure(text="Подключено", text_color="#16A34A")
            try:
                self.dropdown.disable()
            except Exception:
                pass
            try:
                self.disable_game_switch()
            except Exception:
                try:
                    self.disable_game_switch()
                except Exception:
                    pass
        else:
            self.connect_button.configure(text="Подключить", fg_color="#16A34A", hover_color="#15803D")
            self.status_value_label.configure(text="Отключено", text_color="gray")
            try:
                self.dropdown.enable()
            except Exception:
                pass
            try:
                self.enable_game_switch()
            except Exception:
                try:
                    self.game_switch.configure(state="normal")
                except Exception:
                    pass

    def on_game_mode_toggle(self):
        if self.game_mode.get():
            self.log("Игровой режим включён (фильтр: 1024-65535)")
        else:
            self.log("Игровой режим выключен (фильтр: 12)")

    def log(self, msg: str):
        print(f"[{time.strftime('%H:%M:%S')}] {msg}")

    def on_close(self):
        if self.current_process and self.current_process.poll() is None:
            answer = messagebox.askyesno(
                "Процесс работает",
                "Процесс winws.exe всё ещё работает. Вы уверены, что хотите выйти? (это попытается остановить процесс)"
            )
            if not answer:
                return
            try:
                subprocess.run(["taskkill", "/f", "/im", "winws.exe"], capture_output=True)
            except Exception:
                pass

        self.save_settings()
        try:
            self.destroy()
        except Exception:
            sys.exit(0)


if __name__ == "__main__":
    app = App()
    app.mainloop()
