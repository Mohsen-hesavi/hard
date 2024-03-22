from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests
import jdatetime
from datetime import datetime

# اطلاعات ورودی وب‌سرویس "پیام متنی"
username = 'Mohsenhesavi'  # نام کاربری وب‌سرویس
password = '@teroxsorce'  # رمز عبور وب‌سرویس
from_number = '5000220090'  # شماره ارسال کننده
to_number = '09169948431'  # شماره گیرنده پیامک

# مسیر هارد اکسترنال که قصد نظارت بر آن را دارید
watch_path = 'C:\\test'

class ChangeHandler(FileSystemEventHandler):
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

        print(f'تغییری {action} در {current_time}: {path}')
        url = 'https://payammatni.com/webservice/url/send.php'
        params = {
            'method': 'sendsms',
            'format': 'json',
            'from': from_number,
            'to': to_number,
            'text': f'فایلی {action} در تاریخ {current_time} \n\n \n اطلاعات تغیر داده شده: {path} \n\n',
            'type': '0',
            'username': username,
            'password': password
        }
        response = requests.get(url, params=params)
        print(f'پاسخ ارسال پیامک: {response.text}')



# راه‌اندازی observer
observer = Observer()
event_handler = ChangeHandler()
observer.schedule(event_handler, watch_path, recursive=True)
observer.start()

try:
    while True:
        pass
except KeyboardInterrupt:
    observer.stop()
observer.join()
