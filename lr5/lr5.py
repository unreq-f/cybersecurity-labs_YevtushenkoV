import os, hashlib, hmac, base64

def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()

def hmac_sha256(key: bytes, data: bytes) -> bytes:
    return hmac.new(key, data, hashlib.sha256).digest()

def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))

def generate_key_from_personal(email: str, passphrase: str) -> bytes:
    seed = (email + "|" + passphrase).encode("utf-8")
    return sha256(seed)

def keystream(key: bytes, nonce: bytes, length: int) -> bytes:
    out = bytearray()
    counter = 0
    while len(out) < length:
        ctr_bytes = counter.to_bytes(8, "big")
        block = hmac_sha256(key, nonce + ctr_bytes)
        out.extend(block)
        counter += 1
    return bytes(out[:length])

def encrypt_message(plaintext: str, email: str, passphrase: str) -> str:
    key = generate_key_from_personal(email, passphrase)
    enc_key = sha256(key + b"enc")
    mac_key = sha256(key + b"mac")
    nonce = os.urandom(16)
    pt_bytes = plaintext.encode("utf-8")
    ks = keystream(enc_key, nonce, len(pt_bytes))
    ciphertext = xor_bytes(pt_bytes, ks)
    mac = hmac_sha256(mac_key, nonce + ciphertext)
    payload = nonce + ciphertext + mac
    return base64.b64encode(payload).decode("ascii")

def decrypt_message(b64_payload: str, email: str, passphrase: str):
    try:
        payload = base64.b64decode(b64_payload)
    except Exception as e:
        return False, f"Base64 decode error: {e}"
    if len(payload) < 16 + 32:
        return False, "Payload too short"
    nonce = payload[:16]
    mac = payload[-32:]
    ciphertext = payload[16:-32]
    key = generate_key_from_personal(email, passphrase)
    enc_key = sha256(key + b"enc")
    mac_key = sha256(key + b"mac")
    expected_mac = hmac_sha256(mac_key, nonce + ciphertext)
    if not hmac.compare_digest(expected_mac, mac):
        return False, "MAC verification failed — message may be tampered or wrong key."
    ks = keystream(enc_key, nonce, len(ciphertext))
    plaintext_bytes = xor_bytes(ciphertext, ks)
    try:
        plaintext = plaintext_bytes.decode("utf-8")
    except Exception:
        plaintext = plaintext_bytes.decode("utf-8", errors="replace")
    return True, plaintext

# Демонстрація
sender_email = "vlad2002571@gmail.com"
receiver_email = "ivan.petrenko@gmail.com"
shared_secret = "meeting_shared_secret_2025"
message = "Зустрічаємося завтра о 15:00"

print("=== Key derivation ===")
sender_key = generate_key_from_personal(sender_email, shared_secret)
receiver_key = generate_key_from_personal(receiver_email, shared_secret)
print(f"Sender key (hex)   : {sender_key.hex()}")
print(f"Receiver key (hex) : {receiver_key.hex()}")
print("(Different because emails differ — in a real exchange both sides must derive the same shared key.)\n")

# Використовую однакову ідентифікаційну особу з обох сторін для безпечного обміну демо-версіями
demo_email_for_both = sender_email
enc = encrypt_message(message, demo_email_for_both, shared_secret)
print("=== Encryption ===")
print("Plaintext:", message)
print("Encrypted (base64):", enc)

print("\n=== Decryption (correct) ===")
ok, out = decrypt_message(enc, demo_email_for_both, shared_secret)
print("MAC_OK:", ok)
print("Decrypted plaintext:", out)

print("\n=== Decryption attempt with wrong email (wrong key) ===")
ok2, out2 = decrypt_message(enc, receiver_email, shared_secret)
print("MAC_OK:", ok2)
print("Result:", out2)

print("\n=== Tampering demonstration ===")
payload = bytearray(base64.b64decode(enc))
# вибрати байт у області зашифрованого тексту для перетворення (переконатися, що індекс знаходиться в межах діапазону)
if len(payload) > 32:
    idx = 20
    payload[idx] ^= 0x01
tampered_b64 = base64.b64encode(bytes(payload)).decode("ascii")
ok3, out3 = decrypt_message(tampered_b64, demo_email_for_both, shared_secret)
print("MAC_OK:", ok3)
print("Result:", out3)

print("\nFunctions available: generate_key_from_personal, encrypt_message, decrypt_message")
print("Change 'shared_secret' to any passphrase you and peer agree on out-of-band.")
