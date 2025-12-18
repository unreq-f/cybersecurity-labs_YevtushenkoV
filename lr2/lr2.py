import pandas as pd

# Український алфавіт
ALPHABET = "абвгґдеєжзиійклмнопрстуфхцчшщьюя"


# --- 1. Функції для шифру Цезаря ---
def caesar_encrypt(text, shift):
    result = ""
    for char in text.lower():
        if char in ALPHABET:
            idx = ALPHABET.find(char)
            new_idx = (idx + shift) % len(ALPHABET)
            result += ALPHABET[new_idx]
        else:
            result += char
    return result


def caesar_decrypt(text, shift):
    return caesar_encrypt(text, -shift)


# --- 2. Функції для шифру Віженера ---
def vigenere_encrypt(text, key):
    result = ""
    key = key.lower()
    key_indices = [ALPHABET.find(k) for k in key if k in ALPHABET]

    key_idx = 0
    for char in text.lower():
        if char in ALPHABET:
            char_idx = ALPHABET.find(char)
            shift = key_indices[key_idx % len(key_indices)]
            new_idx = (char_idx + shift) % len(ALPHABET)
            result += ALPHABET[new_idx]
            key_idx += 1
        else:
            result += char
    return result


def vigenere_decrypt(text, key):
    result = ""
    key = key.lower()
    key_indices = [ALPHABET.find(k) for k in key if k in ALPHABET]

    key_idx = 0
    for char in text.lower():
        if char in ALPHABET:
            char_idx = ALPHABET.find(char)
            shift = key_indices[key_idx % len(key_indices)]
            new_idx = (char_idx - shift) % len(ALPHABET)
            result += ALPHABET[new_idx]
            key_idx += 1
        else:
            result += char
    return result


# --- 3. Основна частина програми ---
def main():
    print("--- Порівняльний аналіз класичних шифрів ---")

    # Введення даних
    full_name = input("Введіть ваше прізвище: ")
    birth_date = input("Введіть дату народження (наприклад, 15.03.1995): ")
    test_text = "Безпека програм та даних – важлива дисципліна"

    # Генерируємо ключі
    caesar_shift = sum(int(digit) for digit in birth_date if digit.isdigit())
    vigenere_key = full_name

    # Шифрування
    c_encrypted = caesar_encrypt(test_text, caesar_shift)
    v_encrypted = vigenere_encrypt(test_text, vigenere_key)

    # Виведення результатів
    print(f"\nТестовий текст: {test_text}")
    print(f"Ключ Цезаря (сума цифр дати): {caesar_shift}")
    print(f"Ключ Віженера (прізвище): {vigenere_key}")

    print(f"\nРезультат Цезаря: {c_encrypted}")
    print(f"Результат Віженера: {v_encrypted}")

    # --- 4. Таблиця порівняння ---
    comparison_data = [
        {
            "Алгоритм": "Цезар",
            "Довжина": len(c_encrypted),
            "Читабельність": "Низька (збережено структуру)",
            "Складність ключа": "Дуже проста (число)"
        },
        {
            "Алгоритм": "Віженер",
            "Довжина": len(v_encrypted),
            "Читабельність": "Дуже низька (змінено частотність)",
            "Складність ключа": "Середня (слово)"
        }
    ]

    df = pd.DataFrame(comparison_data)
    print("\nТаблиця порівняння:")
    print(df.to_string(index=False))

    # --- 5. Висновки ---
    print("\nВисновки про стійкість:")
    print(
        "1. Шифр Цезаря є найменш стійким, оскільки має лише 33 варіанти зсуву (для укр. алфавіту) і легко зламується перебором.")
    print(
        "2. Шифр Віженера стійкіший, бо він поліалфавітний — одна і та сама літера тексту може стати різними літерами шифру.")


if __name__ == "__main__":
    main()