import os
import sys
import subprocess
import threading
import time
from pathlib import Path
import ctypes
import customtkinter as ctk
from tkinter import messagebox


# --- Проверка прав администратора ---
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit(0)
    except Exception:
        messagebox.showerror("Ошибка", "Не удалось запустить от имени администратора.")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        # Проверка прав администратора
        if not is_admin():
            answer = messagebox.askyesno(
                "Требуются права администратора",
                "Для работы этого приложения требуются права администратора.\n"
                "Приложение будет перезапущено с повышенными правами.\n\n"
                "Продолжить?"
            )
            if answer:
                run_as_admin()
            else:
                self.destroy()
                sys.exit(0)

        # --- Состояния приложения ---
        self.is_connected = ctk.BooleanVar(value=False)
        self.strategies = [
            "general",
            "alt",
            "alt2",
            "alt3",
            "alt4",
            "alt5",
            "alt6",
            "alt7",
            "alt8",
            "fake_tls_auto",
            "fake_tls_auto_alt",
            "fake_tls_auto_alt2",
            "fake_tls_auto_alt3",
            "simple_fake",
            "simple_fake_alt"
        ]
        self.selected_strategy = ctk.StringVar(value=self.strategies[2])

        # --- Пути ---
        self.script_dir = Path(__file__).parent.absolute()
        self.bin_dir = self.script_dir / "bin"
        self.lists_dir = self.script_dir / "lists"
        self.winws_exe = self.bin_dir / "winws.exe"
        self.current_process = None

        # --- Настройка окна ---
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("Zapret UI")
        self.geometry("360x420")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)
        else:
            print("� ️ icon.ico не найден — иконка не изменена")

        # --- Главный фрейм ---
        main_frame = ctk.CTkFrame(self, fg_color="#24293E")
        main_frame.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        center_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9)
        main_frame.grid_columnconfigure(0, weight=1)

        # --- Заголовок ---
        title = ctk.CTkLabel(
            center_frame,
            text="Zapret UI",
            font=ctk.CTkFont(family="Segoe UI Black", size=54, weight="bold"),
            text_color="#5DADE2"
        )
        title.grid(row=0, column=0, pady=(20, 30), sticky="ew")

        # --- Выпадающий список стратегий ---
        self.strategy_menu = ctk.CTkOptionMenu(
            center_frame,
            variable=self.selected_strategy,
            values=self.strategies,
            font=ctk.CTkFont(size=14),
            height=40,
            dropdown_hover_color="#3498DB"
        )
        self.strategy_menu.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        # --- Кнопка Подключить/Отключить ---
        self.connect_button = ctk.CTkButton(
            center_frame,
            text="Подключить",
            font=ctk.CTkFont(size=18, weight="bold"),
            height=50,
            command=self.handle_connect_toggle
        )
        self.connect_button.grid(row=2, column=0, padx=20, pady=20, sticky="ew")

        # --- Статус подключения ---
        status_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        status_frame.grid(row=3, column=0, pady=10)

        status_text_label = ctk.CTkLabel(
            status_frame,
            text="Статус:",
            font=ctk.CTkFont(size=16),
            text_color="gray"
        )
        status_text_label.pack(side="left", padx=(0, 5))

        center_frame.grid_columnconfigure(0, weight=1)

        self.status_value_label = ctk.CTkLabel(
            status_frame,
            text="Отключено",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.status_value_label.pack(side="left")

        self.update_ui_state()

    # --- Управление подключением ---
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

            thread = threading.Thread(target=self.run_process, args=(cmd,))
            thread.daemon = True
            thread.start()

        except Exception as e:
            messagebox.showerror("Ошибка запуска", str(e))

    def run_process(self, cmd):
        try:
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
                cwd=str(self.bin_dir)
            )
            self.is_connected.set(True)
            self.update_ui_state()
            self.log("Процесс запущен.")

            for line in iter(self.current_process.stdout.readline, ''):
                if not line:
                    break
                print(line.strip())

            self.current_process.wait()
            self.is_connected.set(False)
            self.update_ui_state()
            self.log("Процесс завершён.")
        except Exception as e:
            self.log(f"Ошибка: {e}")
            self.is_connected.set(False)
            self.update_ui_state()

    def stop_zapret(self):
        """Останавливает процесс winws.exe"""
        try:
            if self.current_process and self.current_process.poll() is None:
                # Попробуем завершить стандартно
                self.current_process.terminate()
                time.sleep(1)
                if self.current_process.poll() is None:
                    # Если всё ещё жив, принудительно убиваем
                    subprocess.run(["taskkill", "/f", "/im", "winws.exe"], capture_output=True)
            else:
                # Если объект процесса не существует — просто на всякий случай убьём по имени
                subprocess.run(["taskkill", "/f", "/im", "winws.exe"], capture_output=True)

            self.current_process = None
            self.is_connected.set(False)
            self.update_ui_state()
            self.log("Процесс winws.exe остановлен.")
        except Exception as e:
            self.log(f"Ошибка остановки: {e}")
            messagebox.showerror("Ошибка", f"Не удалось остановить процесс:\n{e}")

    # --- Вспомогательные методы ---
    def get_script_parameters(self, mode):
        """
        Возвращает параметры командной строки для выбранного режима.
        Простая логика: определяем game_filter по наличию файла bin/game_filter.enabled
        и подставляем его в те параметры, где в батниках использовался %GameFilter%.
        """
        # определяем GameFilter (как в service.bat)
        game_flag_file = self.bin_dir / "game_filter.enabled"
        if game_flag_file.exists():
            game_filter = "1024-65535"
        else:
            game_filter = "12"

        # базовые wf-* (вставляем game_filter туда, где это делается в bat)
        base_params = [
            f"--wf-tcp=80,443,2053,2083,2087,2096,8443,{game_filter}",
            f"--wf-udp=443,19294-19344,50000-50100,{game_filter}"
        ]

        # базовые фильтры (аналог первых блоков в батниках)
        base_filters = [
            '--filter-udp=443', '--hostlist', f'{self.lists_dir}/list-general.txt',
            '--dpi-desync=fake', '--dpi-desync-repeats=6',
            '--dpi-desync-fake-quic', f'{self.bin_dir}/quic_initial_www_google_com.bin', '--new',

            '--filter-udp=19294-19344,50000-50100', '--filter-l7=discord,stun',
            '--dpi-desync=fake', '--dpi-desync-repeats=6', '--new',

            '--filter-tcp=80', '--hostlist', f'{self.lists_dir}/list-general.txt',
            '--dpi-desync=fake,multisplit', '--dpi-desync-autottl=2', '--dpi-desync-fooling=md5sig', '--new'
        ]

        # блоки режимов — в них подставляем game_filter в тех местах, где в батах использовалось ,%GameFilter%
        mode_params = {
            "general": [
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

            "alt": [
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

            "alt2": [
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

            "alt3": [
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

            "alt4": [
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

            "alt5": [
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

            "alt6": [
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

            "alt7": [
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

            "alt8": [
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

            "fake_tls_auto": [
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

            "fake_tls_auto_alt": [
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

            "fake_tls_auto_alt2": [
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

            "fake_tls_auto_alt3": [
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

            "simple_fake": [
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

            "simple_fake_alt": [
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

        # Собираем окончательный список параметров
        params = base_params + base_filters
        if mode in mode_params:
            params += mode_params[mode]

        return params

    def log(self, msg: str):
        """Вывод в консоль с таймштампом"""
        print(f"[{time.strftime('%H:%M:%S')}] {msg}")

    def update_ui_state(self):
        """Обновляет внешний вид элементов"""
        if self.is_connected.get():
            self.connect_button.configure(text="Отключить", fg_color="#E74C3C", hover_color="#C0392B")
            self.status_value_label.configure(text="Подключено", text_color="#2ECC71")
            self.strategy_menu.configure(state="disabled")
        else:
            self.connect_button.configure(text="Подключить", fg_color="#2ECC71", hover_color="#27AE60")
            self.status_value_label.configure(text="Отключено", text_color="gray")
            self.strategy_menu.configure(state="normal")
            self.connect_button.configure(state="normal")


if __name__ == "__main__":
    app = App()
    app.mainloop()