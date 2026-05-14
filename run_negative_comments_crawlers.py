import subprocess
import sys
import time

scripts = [
    "data/lam-dep-suc-khoe-tiki/crawl-comment.py",
    "data/thoi-trang-nu-tiki/crawl-comment.py",
    "data/bach-hoa-online-tiki/crawl-comment.py"
]

retry_wait = 10

for script in scripts:
    print("\n=== Chạy script:", script)
    while True:
        try:
            process = subprocess.run(
                [sys.executable, script],
                capture_output=True,
                text=True,
            )
        except Exception as exc:
            print(f"Lỗi khi chạy {script}: {exc}")
            print(f"Đợi {retry_wait}s rồi thử lại...")
            time.sleep(retry_wait)
            continue

        print(process.stdout)
        if process.returncode == 0:
            print(f"Đã hoàn thành {script} thành công.")
            break

        print(f"Script {script} trả về mã lỗi {process.returncode}.")
        if process.stderr:
            print("--- STDERR ---")
            print(process.stderr)
            print("--- END STDERR ---")
        print(f"Đợi {retry_wait}s rồi chạy lại {script}...")
        time.sleep(retry_wait)

print("\n=== Đã hoàn tất tất cả các script crawler.")
