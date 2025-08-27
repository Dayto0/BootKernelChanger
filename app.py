import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import subprocess
import tempfile
import shutil
import os
from pathlib import Path
import queue
import sys

class ToolTip:
    def __init__(self, widget, text=""):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, _event=None):
        if self.tipwindow or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f'+{x}+{y}')
        label = ttk.Label(tw, text=self.text, padding=(6, 4))
        label.pack()

    def hide(self, _event=None):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None


class BootAssemblerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Boot.img Assembler by Dayto")
        self.geometry("720x460")
        self.minsize(640, 420)
        self.iconbitmap(default='')
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('Header.TLabel', font=('Segoe UI', 16, 'bold'))
        style.configure('Sub.TLabel', font=('Segoe UI', 10))
        style.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=8)
        style.configure('Path.TLabel', font=('Segoe UI', 10), foreground='#333333')

        self.selected_kernel = None
        self.selected_boot = None

        # <-- правильный отступ!
        if getattr(sys, 'frozen', False):
            base_path = Path(getattr(sys, '_MEIPASS', Path(sys.executable).parent))
            self.magiskboot = base_path / 'magiskboot.exe'
        else:
            self.magiskboot = Path(__file__).with_name('magiskboot.exe')

        self.log_queue = queue.Queue()

        self._create_widgets()
        self._start_log_pump()


    def _create_widgets(self):
        header = ttk.Frame(self, padding=12)
        header.pack(fill=tk.X)
        ttk.Label(header, text="Сборщик boot.img", style='Header.TLabel').pack(anchor=tk.W)
        ttk.Label(header, text="Замена kernel в boot.img с помощью magiskboot", style='Sub.TLabel').pack(anchor=tk.W, pady=(2, 6))

        main = ttk.Frame(self, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(main)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

        kernel_frame = ttk.LabelFrame(left, text='Kernel (Image)', padding=8)
        kernel_frame.pack(fill=tk.X, padx=(0, 10), pady=6)
        self.kernel_path_label = ttk.Label(kernel_frame, text='Не выбран', style='Path.TLabel')
        self.kernel_path_label.pack(fill=tk.X)
        ToolTip(self.kernel_path_label, text='Путь к выбранному kernel')

        kbtns = ttk.Frame(kernel_frame)
        kbtns.pack(fill=tk.X, pady=(8,0))
        ttk.Button(kbtns, text='Выбрать kernel', command=self.select_kernel).pack(side=tk.LEFT)
        ttk.Button(kbtns, text='Очистить', command=self.clear_kernel).pack(side=tk.LEFT, padx=6)

        boot_frame = ttk.LabelFrame(left, text='Boot image (boot.img)', padding=8)
        boot_frame.pack(fill=tk.X, padx=(0, 10), pady=6)
        self.boot_path_label = ttk.Label(boot_frame, text='Не выбран', style='Path.TLabel')
        self.boot_path_label.pack(fill=tk.X)
        ToolTip(self.boot_path_label, text='Путь к выбранному boot.img')

        bbtns = ttk.Frame(boot_frame)
        bbtns.pack(fill=tk.X, pady=(8,0))
        ttk.Button(bbtns, text='Выбрать boot.img', command=self.select_boot).pack(side=tk.LEFT)
        ttk.Button(bbtns, text='Очистить', command=self.clear_boot).pack(side=tk.LEFT, padx=6)

        build_frame = ttk.Frame(left, padding=8)
        build_frame.pack(fill=tk.X, padx=(0, 10), pady=12)
        self.big_assemble_btn = ttk.Button(build_frame, text='Собрать', command=self.on_assemble)
        self.big_assemble_btn.pack(fill=tk.X, pady=6, ipady=8)

        right = ttk.Frame(main)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        log_frame = ttk.LabelFrame(right, text='Лог операций', padding=8)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=(0,0))
        self.log_text = tk.Text(log_frame, height=12, wrap='none', state='disabled')
        self.log_text.pack(fill=tk.BOTH, expand=True)

        bottom = ttk.Frame(self, relief=tk.FLAT, padding=(8,6))
        bottom.pack(fill=tk.X)
        self.progress = ttk.Progressbar(bottom, mode='indeterminate')
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,8))
        self.status_label = ttk.Label(bottom, text='Готово', anchor='e')
        self.status_label.pack(side=tk.RIGHT)

    def select_kernel(self):
        path = filedialog.askopenfilename(title='Выберите kernel (Image)', filetypes=[('All files', '*.*')])
        if path:
            self.selected_kernel = Path(path)
            self.kernel_path_label.config(text=self.selected_kernel.name)
            ToolTip(self.kernel_path_label, text=str(self.selected_kernel))

    def select_boot(self):
        path = filedialog.askopenfilename(title='Выберите boot.img', filetypes=[('boot images', '*.img'), ('All files', '*.*')])
        if path:
            self.selected_boot = Path(path)
            self.boot_path_label.config(text=self.selected_boot.name)
            ToolTip(self.boot_path_label, text=str(self.selected_boot))

    def clear_kernel(self):
        self.selected_kernel = None
        self.kernel_path_label.config(text='Не выбран')

    def clear_boot(self):
        self.selected_boot = None
        self.boot_path_label.config(text='Не выбран')

    def on_assemble(self):
        if not getattr(self, 'selected_kernel', None) or not getattr(self, 'selected_boot', None):
            messagebox.showerror('Ошибка', 'Выберите оба файла: kernel (Image) и boot.img')
            return

        if not (self.magiskboot.exists()):
            messagebox.showerror('Ошибка', f'magiskboot.exe не найден: {self.magiskboot}')
            return

        self.big_assemble_btn.config(state='disabled')
        self.progress.start(10)
        self.status_label.config(text='Работаем...')

        thread = threading.Thread(target=self._assemble_worker, daemon=True)
        thread.start()

    def _assemble_worker(self):
        temp_dir = Path(tempfile.mkdtemp(prefix='boot_'))
        try:
            self._log(f'Создана временная папка: {temp_dir}')

            boot_dest = temp_dir / 'boot.img'
            kernel_dest = temp_dir / 'Image'
            shutil.copy(self.selected_boot, boot_dest)
            self._log(f'Скопирован boot.img -> {boot_dest.name}')
            shutil.copy(self.selected_kernel, kernel_dest)
            self._log(f'Скопирован kernel -> {kernel_dest.name}')

            cmd_unpack = [str(self.magiskboot), 'unpack', 'boot.img']
            self._log('Выполняется: ' + ' '.join(cmd_unpack))
            result = subprocess.run(cmd_unpack, cwd=str(temp_dir), capture_output=True, text=True)
            self._log(result.stdout or result.stderr)
            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, cmd_unpack, output=result.stdout, stderr=result.stderr)

            kernel_file = temp_dir / 'kernel'
            image_file = temp_dir / 'Image'
            if kernel_file.exists():
                kernel_file.unlink()
                self._log('Старый kernel удалён')
            if image_file.exists():
                image_file.rename(kernel_file)
                self._log('Image переименован в kernel')

            cmd_repack = [str(self.magiskboot), 'repack', 'boot.img']
            self._log('Выполняется: ' + ' '.join(cmd_repack))
            result = subprocess.run(cmd_repack, cwd=str(temp_dir), capture_output=True, text=True)
            self._log(result.stdout or result.stderr)
            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, cmd_repack, output=result.stdout, stderr=result.stderr)

            new_boot = temp_dir / 'new-boot.img'
            if new_boot.exists():
                self._log(f'new-boot.img создан: {new_boot}')
                self.after(0, lambda: self._handle_new_boot_created(str(new_boot), str(temp_dir)))
            else:
                raise FileNotFoundError('new-boot.img не найден после repack')

        except Exception as e:
            self._log(f'Ошибка: {e}')
            try:
                shutil.rmtree(str(temp_dir))
                self._log('Временная папка удалена (ошибка).')
            except Exception:
                pass
            self.after(0, lambda: self._show_error('Ошибка', str(e)))
            self.after(0, self._finish)

    def _handle_new_boot_created(self, new_boot_path: str, temp_dir: str):
        try:
            save_path = filedialog.asksaveasfilename(title='Сохранить новый boot.img', defaultextension='.img', filetypes=[('Image','*.img')])
            if save_path:
                shutil.copy(new_boot_path, save_path)
                self._log(f'Новый boot.img сохранён: {save_path}')
                self._show_info('Успех', f'Новый boot.img сохранён: {save_path}')
            else:
                self._log(f'Пользователь отменил сохранение — файл: {new_boot_path}')
                self._show_info('Готово', f'Новый boot.img создан: {new_boot_path}')
        except Exception as e:
            self._log(f'Ошибка при сохранении: {e}')
            self._show_error('Ошибка сохранения', str(e))
        finally:
            try:
                shutil.rmtree(temp_dir)
                self._log('Временная папка удалена')
            except Exception as ex:
                self._log(f'Не удалось удалить временную папку: {ex}')
        self._finish()

    def _finish(self):
        self.progress.stop()
        self.big_assemble_btn.config(state='normal')
        self.status_label.config(text='Готово')

    def _log(self, text):
        self.log_queue.put(str(text) + '\n')

    def _start_log_pump(self):
        def pump():
            try:
                while True:
                    line = self.log_queue.get_nowait()
                    self.log_text.config(state='normal')
                    self.log_text.insert('end', line)
                    self.log_text.see('end')
                    self.log_text.config(state='disabled')
            except queue.Empty:
                pass
            self.after(200, pump)
        pump()

    def _show_error(self, title, message):
        self.after(0, lambda: messagebox.showerror(title, message))

    def _show_info(self, title, message):
        self.after(0, lambda: messagebox.showinfo(title, message))


if __name__ == '__main__':
    app = BootAssemblerApp()
    app.mainloop()