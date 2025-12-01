from PIL import Image
import numpy as np
import os, math, pandas as pd

script_dir = os.path.dirname(os.path.abspath(__file__))

cover_path = os.path.join(script_dir, "cover_gradient.png")
stego_path = os.path.join(script_dir, "stego_image.png")
txt_path = os.path.join(script_dir, "extracted_message.txt")


def bytes_to_bits(b: bytes) -> str:
    return ''.join(f"{byte:08b}" for byte in b)


def bits_to_bytes(bits: str) -> bytes:
    chunks = [bits[i:i + 8] for i in range(0, len(bits), 8)]
    return bytes(int(c, 2) for c in chunks if len(c) == 8)


def hide_message(image: Image.Image, message: str) -> Image.Image:
    msg_bytes = message.encode('utf-8')
    msg_bits = bytes_to_bits(msg_bytes)
    msg_len = len(msg_bits)
    header = format(msg_len, "032b")
    full_bits = header + msg_bits

    arr = np.array(image.convert("RGB"))
    h, w, _ = arr.shape
    capacity = h * w * 3
    if len(full_bits) > capacity:
        raise ValueError(f"Message too large: capacity {capacity} bits, need {len(full_bits)} bits.")

    flat = arr.flatten().astype(np.int32)
    bits_iter = iter(full_bits)

    for i in range(len(flat)):
        try:
            bit = next(bits_iter)
        except StopIteration:
            break
        flat[i] = (flat[i] & 0xFE) | int(bit)

    flat = flat.astype(np.uint8)
    new_arr = flat.reshape(arr.shape)
    return Image.fromarray(new_arr, 'RGB')


def extract_message(image: Image.Image) -> str:
    arr = np.array(image.convert("RGB"))
    flat = arr.flatten()
    header_bits = ''.join(str(int(flat[i]) & 1) for i in range(32))
    msg_len = int(header_bits, 2)
    msg_bits = ''.join(str(int(flat[i]) & 1) for i in range(32, 32 + msg_len))
    msg_bytes = bits_to_bytes(msg_bits)
    return msg_bytes.decode('utf-8', errors='replace')


def generate_gradient_image(width=400, height=400, filename=cover_path):
    arr = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            arr[y, x] = [
                (x * 255) // (width - 1),
                (y * 255) // (height - 1),
                ((x + y) * 255) // (width + height - 2)
            ]
    img = Image.fromarray(arr, 'RGB')
    img.save(filename)
    return img


def mse(img1: Image.Image, img2: Image.Image) -> float:
    a = np.array(img1.convert("RGB"), dtype=np.float64)
    b = np.array(img2.convert("RGB"), dtype=np.float64)
    return float(np.mean((a - b) ** 2))


def psnr(img1: Image.Image, img2: Image.Image) -> float:
    m = mse(img1, img2)
    if m == 0:
        return float('inf')
    max_pixel = 255.0
    return 20 * math.log10(max_pixel / math.sqrt(m))


def changed_pixels_count(img1: Image.Image, img2: Image.Image) -> int:
    a = np.array(img1.convert("RGB"))
    b = np.array(img2.convert("RGB"))
    diff = np.any(a != b, axis=2)
    return int(np.sum(diff))


# Підготовка повідомлення (дані користувача)
user_initials = "ЄВВ"
user_full = "Євтушенко Владислав Віталійович"
message = f"Ініціали: {user_initials}; Повне ім'я: {user_full}."

print("Генерація покриваючого зображення...")
cover = generate_gradient_image(400, 400)

print("Приховування повідомлення...")
stego = hide_message(cover, message)
stego.save(stego_path)

print("Витягування повідомлення...")
extracted = extract_message(stego)
with open(txt_path, "w", encoding="utf-8") as f:
    f.write(extracted)

cover_size = os.path.getsize(cover_path)
stego_size = os.path.getsize(stego_path)
m = mse(cover, stego)
p = psnr(cover, stego)
changed = changed_pixels_count(cover, stego)

df = pd.DataFrame([
    {"file": "cover_gradient.png", "path": cover_path, "size_bytes": cover_size},
    {"file": "stego_image.png", "path": stego_path, "size_bytes": stego_size},
    {"file": "extracted_message.txt", "path": txt_path, "size_bytes": os.path.getsize(txt_path)}
])

print("\n" + "=" * 60)
print("----- Витягнуте повідомлення (перевірка) -----")
print(extracted)
print("\n" + "=" * 60)
print("----- Аналіз зображень -----")
print(f"Розмір cover (bytes):  {cover_size}")
print(f"Розмір stego (bytes):  {stego_size}")
print(f"MSE між зображеннями:  {m:.9f}")
print(f"PSNR між зображеннями: {p:.3f} dB")
total_pixels = cover.size[0] * cover.size[1]
print(f"Змінених пікселів: {changed} з {total_pixels} ({changed / total_pixels * 100:.6f}%)")
print("=" * 60)

print("\nСтворені файли:")
print(f"  ✓ {cover_path}")
print(f"  ✓ {stego_path}")
print(f"  ✓ {txt_path}")

print("\nТаблиця файлів:")
print(df.to_string(index=False))