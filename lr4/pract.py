import hashlib, os

resume_path = "resume_Evtushenko.pdf"
signature_path = "signature.sig"
tampered_path = "resume_Evtushenko_tampered.pdf"

MOD = 1000007
MULT = 7

def sha256_file(path: str) -> bytes:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            data = f.read(8192)
            if not data:
                break
            h.update(data)
    return h.digest()

def int_to_bytes_repeat(n: int, length: int) -> bytes:
    if n == 0:
        base = b"\x00"
    else:
        blen = (n.bit_length() + 7) // 8
        base = n.to_bytes(blen, "big")
    if len(base) >= length:
        return base[:length]
    reps = (length + len(base) - 1) // len(base)
    return (base * reps)[:length]

def generate_keys_from_personal(name: str, birth: str, secret_word: str):
    txt = f"{name}|{birth}|{secret_word}"
    h = hashlib.sha256(txt.encode("utf-8")).digest()
    priv_int = int.from_bytes(h, "big") % MOD
    pub_int = (priv_int * MULT) % MOD
    return priv_int, pub_int

def sign_document(doc_path: str, private_key: int) -> bytes:
    doc_hash = sha256_file(doc_path)
    key_bytes = int_to_bytes_repeat(private_key, len(doc_hash))
    signature = bytes(d ^ k for d,k in zip(doc_hash, key_bytes))
    with open(signature_path, "wb") as f:
        f.write(signature)
    return signature

def modinv(a: int, m: int) -> int:
    a0, m0 = a, m
    x0, x1 = 1, 0
    while m0 != 0:
        q = a0 // m0
        a0, m0 = m0, a0 - q * m0
        x0, x1 = x1, x0 - q * x1
    if a0 != 1:
        raise ValueError("Modular inverse does not exist")
    return x0 % m

def verify_signature(doc_path: str, signature_bytes: bytes, public_key: int):
    inv = modinv(MULT, MOD)
    derived_priv = (public_key * inv) % MOD
    key_bytes = int_to_bytes_repeat(derived_priv, len(signature_bytes))
    recovered_hash = bytes(s ^ k for s,k in zip(signature_bytes, key_bytes))
    current_hash = sha256_file(doc_path)
    return (recovered_hash == current_hash), recovered_hash.hex(), current_hash.hex(), derived_priv

#Створюю простий текст UTF-8 та зберiгаю його як файл .pdf для демонстрації
name = "Євтушенко Владислав Віталійович"
birth = "01011990"
secret_word = "secret_word"
text_lines = [
    "Резюме: Євтушенко Владислав Віталійович",
    "Посада: Дата-iнженер",
    "Освіта: Бакалавр з інженерії програмного забезпечення",
    "Досвід: розробка програмних продуктів",
    "Контакти: vlad2002571@gmail.com"
]
with open(resume_path, "wb") as f:
    f.write("\n".join(text_lines).encode("utf-8"))

# Генерація ключів, підпис, перевірка, втручання
priv, pub = generate_keys_from_personal(name, birth, secret_word)
signature = sign_document(resume_path, priv)
is_valid, rec_hex, cur_hex, derived_priv = verify_signature(resume_path, signature, pub)

# Тампер: перевернути на один біт
with open(resume_path, "rb") as f:
    data = bytearray(f.read())
if len(data) > 10:
    data[10] ^= 0x01
else:
    data[-1] ^= 0x01
with open(tampered_path, "wb") as f:
    f.write(data)

is_valid_t, rec_hex_t, cur_hex_t, derived_priv_t = verify_signature(tampered_path, signature, pub)

# Вихідний підсумок
print("=== Keys ===")
print(f"Private key (int mod {MOD}): {priv}")
print(f"Public  key: {pub}")
print()
print("=== Hashes ===")
print("Document SHA256:", sha256_file(resume_path).hex())
print("Tampered SHA256:", sha256_file(tampered_path).hex())
print()
print("=== Signature file ===")
print("Signature saved to:", signature_path)
print("Signature (hex, first 64 chars):", signature.hex()[:64], "...")
print()
print("=== Verification (original) ===")
print("Derived private from public:", derived_priv)
print("Recovered hash from signature:", rec_hex)
print("Current doc hash:            ", cur_hex)
print("Result:", "Підпис ДІЙСНИЙ" if is_valid else "Підпис ПІДРОБЛЕНИЙ")
print()
print("=== Verification (tampered) ===")
print("Derived private from public:", derived_priv_t)
print("Recovered hash from signature:", rec_hex_t)
print("Tampered doc hash:            ", cur_hex_t)
print("Result:", "Підпис ДІЙСНИЙ" if is_valid_t else "Підпис ПІДРОБЛЕНИЙ")
print()
print("Files created:")
for p in [resume_path, signature_path, tampered_path]:
    print(p, "-", os.path.getsize(p), "bytes")
