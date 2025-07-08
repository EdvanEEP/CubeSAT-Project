import socket
import time
import os

HOST = 'localhost'
PORT = 65432
SAVE_PATH = r"C:\Users\bugra\Desktop\CubeSAT\client_uydu_deneme_1_sonuc.jpg"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("🛰 Server hazır, bağlantı bekleniyor...")
    conn, addr = s.accept()
    with conn:
        print(f"📡 Bağlantı geldi: {addr}")
        with open(SAVE_PATH, 'wb') as f:
            total_received = 0
            start_time = time.time()
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                f.write(data)
                total_received += len(data)
            end_time = time.time()

        elapsed = (end_time - start_time) * 1000
        print(f"💾 Dosya kaydedildi: {SAVE_PATH}")
        print(f"📦 Alınan boyut: {total_received / 1024:.2f} KB")
        print(f"⏱ Alım süresi: {elapsed:.2f} ms")
