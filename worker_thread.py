import time
import subprocess
from PySide6.QtCore import QThread, Signal


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