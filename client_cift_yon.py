import socket
import time
import os
from PIL import Image, ImageFilter
import numpy as np
import math
from skimage.metrics import structural_similarity as ssim

# === 🛰 Komut girişi ===
uplink_command = input("🛰 Komut girin (örnek: SEND_IMAGE meteor1.jpg): ").strip()

try:
    komut, dosya_adi = uplink_command.split()
    if komut != "SEND_IMAGE":
        raise ValueError
except:
    print("❌ Hatalı komut formatı. Doğru biçim: SEND_IMAGE dosya_adi.jpg")
    exit()

# === 📁 Dosya yolları ===
BASE_DIR = r"C:\Users\bugra\Desktop\CubeSAT"
input_path = os.path.join(BASE_DIR, dosya_adi)
compressed_path = os.path.join(BASE_DIR, "compressed_" + dosya_adi)
reconstructed_path = os.path.join(BASE_DIR, "reconstructed_2" + dosya_adi)

if not os.path.exists(input_path):
    print(f"❌ Dosya bulunamadı: {input_path}")
    exit()

# === 📉 GÖRSEL SIKIŞTIRMA ===
img = Image.open(input_path).convert("RGB")
orig_np = np.array(img)
orig_width, orig_height = img.size

scale_percent = 59
new_width = int(orig_width * scale_percent / 100)
new_height = int(orig_height * scale_percent / 100)
resized_img = img.resize((new_width, new_height), Image.LANCZOS)
resized_img.save(compressed_path, "JPEG", quality=90)

# === 🔍 SIKIŞTIRMA ANALİZİ ===
compressed_img = Image.open(compressed_path).convert("RGB")
compressed_np = np.array(compressed_img)
resized_orig = img.resize((new_width, new_height), Image.LANCZOS)
resized_orig_np = np.array(resized_orig)

mse = np.mean((resized_orig_np - compressed_np) ** 2)
psnr = float("inf") if mse == 0 else 10 * math.log10((255 ** 2) / mse)
ssim_r = ssim(resized_orig_np[:, :, 0], compressed_np[:, :, 0], data_range=255)
ssim_g = ssim(resized_orig_np[:, :, 1], compressed_np[:, :, 1], data_range=255)
ssim_b = ssim(resized_orig_np[:, :, 2], compressed_np[:, :, 2], data_range=255)
ssim_total = (ssim_r + ssim_g + ssim_b) / 3

compressed_size_kb = os.path.getsize(compressed_path) / 1024
print(f"\n📦 Sıkıştırılmış dosya boyutu: {compressed_size_kb:.2f} KB")
print(f"🔊 PSNR (öncesi): {psnr:.2f} dB")
print(f"🔎 SSIM (öncesi): {ssim_total:.4f}")

# === 📤 UYDUDAN GÖNDERİM ===
HOST = 'localhost'
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.connect((HOST, PORT))
    except:
        print("❌ Uydu bağlantısı kurulamadı. Server açık mı?")
        exit()

    filesize = os.path.getsize(compressed_path)
    print(f"\n📤 Sıkıştırılmış görsel gönderiliyor ({filesize / 1024:.2f} KB)...")

    start_time = time.time()
    with open(compressed_path, 'rb') as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            s.sendall(data)
    end_time = time.time()

    elapsed = (end_time - start_time) * 1000
    print(f"✅ Gönderim tamamlandı.")
    print(f"⏱ Aktarım süresi: {elapsed:.2f} ms")

# === 📈 UYDUDAN GERİ AÇMA ===
compressed_img = Image.open(compressed_path).convert("RGB")

# Eski çözünürlüğe LANCZOS ile büyüt
upscaled_img = compressed_img.resize((orig_width, orig_height), Image.LANCZOS)

# Unsharp Mask ile doğal iyileştirme
sharpened = upscaled_img.filter(ImageFilter.UnsharpMask(radius=1.5, percent=80, threshold=3))
sharpened.save(reconstructed_path, "JPEG", quality=100)

# === 📊 Geri Dönüş Kalite Analizi ===
reconstructed_np = np.array(sharpened)
mse_rec = np.mean((orig_np - reconstructed_np) ** 2)
psnr_rec = float("inf") if mse_rec == 0 else 10 * math.log10((255 ** 2) / mse_rec)

ssim_r = ssim(orig_np[:, :, 0], reconstructed_np[:, :, 0], data_range=255)
ssim_g = ssim(orig_np[:, :, 1], reconstructed_np[:, :, 1], data_range=255)
ssim_b = ssim(orig_np[:, :, 2], reconstructed_np[:, :, 2], data_range=255)
ssim_total = (ssim_r + ssim_g + ssim_b) / 3

reconstructed_size_kb = os.path.getsize(reconstructed_path) / 1024
print(f"\n📦 Geri döndürülmüş dosya boyutu: {reconstructed_size_kb:.2f} KB")
print(f"📊 PSNR (geri dönüş sonrası): {psnr_rec:.2f} dB")
print(f"📊 SSIM (geri dönüş sonrası): {ssim_total:.4f}")
