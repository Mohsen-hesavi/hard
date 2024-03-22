import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests
import jdatetime
from threading import Thread

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, log_callback, sms_settings):
        self.log_callback = log_callback
        self.sms_settings = sms_settings

    def on_created(self, event):
        self.notify_change(event.src_path, 'ایجاد شده است')

    def on_deleted(self, event):
        self.notify_change(event.src_path, 'حذف شده است')

    def on_modified(self, event):
        self.notify_change(event.src_path, 'ویرایش شده است')

    def on_moved(self, event):
        self.notify_change(event.dest_path, 'جابجا شده است به ' + event.dest_path)

    def notify_change(self, path, action):
        current_time = jdatetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f'تغییری {action} در {current_time}: {path}'
        self.log_callback(message)
        url = 'https://payammatni.com/webservice/url/send.php'
        params = {
            'method': 'sendsms',
            'format': 'json',
            'from': self.sms_settings['from_number'],
            'to': self.sms_settings['to_number'],
            'text': f'فایلی {action} در تاریخ {current_time} \n\n \n اطلاعات تغیر داده شده: {path} \n\n',
            'type': '0',
            'username': self.sms_settings['username'],
            'password': self.sms_settings['password']
        }
        response = requests.get(url, params=params)
        self.log_callback(f'پاسخ ارسال پیامک: {response.text}')

class App:
    def __init__(self, root):
        self.root = root
        root.title('نظارت بر فایل‌سیستم')
        
        self.sms_settings = {}

        tk.Label(root, text='مسیر پوشه:').pack()
        self.path_entry = tk.Entry(root)
        self.path_entry.pack(pady=5)

        self.configure_sms_button = tk.Button(root, text='تنظیمات پیامک', command=self.configure_sms)
        self.configure_sms_button.pack(pady=5)

        self.start_button = tk.Button(root, text='شروع نظارت', command=self.start_monitoring)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(root, text='توقف نظارت', command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.log_area = scrolledtext.ScrolledText(root, width=80, height=20)
        self.log_area.pack(pady=10)

        self.observer = None

    def configure_sms(self):
        self.sms_settings['username'] = simpledialog.askstring("تنظیمات پیامک", "نام کاربری:")
        self.sms_settings['password'] = simpledialog.askstring("تنظیمات پیامک", "رمز عبور:", show='*')
        self.sms_settings['from_number'] = simpledialog.askstring("تنظیمات پیامک", "شماره فرستنده:")
        self.sms_settings['to_number'] = simpledialog.askstring("تنظیمات پیامک", "شماره گیرنده:")

    def validate_sms_settings(self):
        # اینجا کد اعتبارسنجی اطلاعات پنل پیامکی قرار می‌گیرد
        # به دلیل محدودیت‌های محیط، فرض می‌کنیم اطلاعات همیشه معتبر هستند
        return True

    def log_message(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def start_monitoring(self):
        path = self.path_entry.get()
        if not path:
            messagebox.showwarning('هشدار', 'لطفا یک مسیر معتبر وارد کنید.')
            return
        if not self.validate_sms_settings():  # اعتبارسنجی تنظیمات پیامک
            return  # در صورت نامعتبر بودن، عملیات را متوقف کن
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.event_handler = ChangeHandler(self.log_message, self.sms_settings)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, path, recursive=True)
        self.observer.start()
        self.log_message(f"شروع نظارت بر: {path}")

    def stop_monitoring(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            self.log_message("توقف نظارت.")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

root = tk.Tk()
app = App(root)
root.mainloop()
