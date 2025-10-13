import os
import subprocess
import threading
import webview
import time

# مسیر پروژه
project_path = r"D:\Couse Zakawat\Zakawat-Academic-Institute"

# مسیر پایتون داخل محیط مجازی
venv_python = os.path.join(project_path, "venv", "Scripts", "python.exe")

def run_django():
    # اجرای سرور Django با محیط مجازی
    subprocess.call([venv_python, "manage.py", "runserver"], cwd=project_path)

def open_window():
    # چند ثانیه صبر می‌کند تا سرور شروع شود
    time.sleep(3)
    webview.create_window("Zakawat Academic Institute", "http://127.0.0.1:8000")
    webview.start()

if __name__ == "__main__":
    threading.Thread(target=run_django, daemon=True).start()
    open_window()
