import serial
import csv
import time
import argparse
import button 
from datetime import datetime
from serial import SerialException

# ====== Xử lý tham số dòng lệnh ======
parser = argparse.ArgumentParser(description="Thu thập dữ liệu từ serial và lưu ra CSV.")

parser.add_argument(
    "--port", type=str, default="/dev/serial0",
    help="Tên cổng serial (mặc định: /dev/serial0)"
)
parser.add_argument(
    "--baud", type=int, default=256000,
    help="Baudrate cho UART (mặc định: 256000)"
)
parser.add_argument(
    "--channels", type=int, default=12,
    help="Số kênh dữ liệu (mặc định: 12)"
)
parser.add_argument(
    "--outfile", type=str, default=None,
    help="Tên file CSV (mặc định: tự tạo theo timestamp)"
)

args = parser.parse_args()

PORT = args.port
BAUD = args.baud
NUM_CHANNELS = args.channels
OUTFILE = args.outfile

write_condition = button.get_state
TIMEOUT = 1.0

# ====== Serial Setup ======
try:
    ser = serial.Serial(PORT, BAUD, timeout=TIMEOUT)
except SerialException as e:
    print(f"[!] Không thể mở cổng {PORT}: {e}")
    ser = None

# ====== Bộ nhớ dữ liệu ======
all_data = [[] for _ in range(NUM_CHANNELS)]
sample_count = 0
awaiting_response = False


def save_to_csv():
    """Ghi toàn bộ dữ liệu ra file CSV có timestamp."""
    if not any(all_data):
        print("[ℹ️] Không có dữ liệu để lưu.")
        return

    filename = OUTFILE or f"py_serial_log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    print(f"💾 Đang ghi dữ liệu ra file {filename} ...")
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        # writer.writerow([f"Channel {i}" for i in range(NUM_CHANNELS)])
        for row in zip(*all_data):
            writer.writerow(row)
    print(f"✅ Hoàn tất. Đã lưu {len(all_data[0])} mẫu.")


print(f"📡 Đang kết nối tới {PORT} @ {BAUD} baud ... Nhấn Ctrl+C để dừng.")

try:
    button.start_thread()
    while True:
#        print(write_condition())
        if ser:
            try:
                if not awaiting_response:
                    #ser.write(b'g')
                    awaiting_response = True

                line = ser.readline().decode('utf-8').strip()

                if (not line) or (not write_condition()):
                    continue

                try:
                    values = list(map(float, filter(None, line.split(','))))
                    if len(values) < NUM_CHANNELS:
                        print(f"[!] Thiếu dữ liệu ({len(values)}/{NUM_CHANNELS}): {line}")
                        continue

                    for i in range(NUM_CHANNELS):
                        all_data[i].append(values[i])
                    
                    print(values)
                    sample_count += 1

                    if sample_count % 1000 == 0:
                        print(f"[+] Đã thu {sample_count} mẫu...")

                    awaiting_response = False
                    #time.sleep(0.05)

                except ValueError:
                    print(f"[!] Lỗi giá trị: {line}")
                    awaiting_response = False
                    pass

            except SerialException:
                print("\n⚠️  Mất kết nối serial! Ghi dữ liệu hiện có...")
                save_to_csv()
                pass

        else:
            if any(all_data):
                save_to_csv()
                for lst in all_data:
                    lst.clear()
            else:
                time.sleep(0.5)

except KeyboardInterrupt:
    button.stop_thread()
    button.GPIO.cleanup()
    print("\n⏹️  Người dùng dừng chương trình.")

finally:
    if ser and ser.is_open:
        ser.close()
    save_to_csv()
    print("[+] Đã đóng cổng serial và lưu dữ liệu.")
