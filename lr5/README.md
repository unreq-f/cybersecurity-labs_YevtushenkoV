Програма реалізує authenticated encryption з використанням HMAC-SHA256

Вимоги:
1) Python 3.6+
2) Стандартна бібліотека (без додаткових залежностей)

Запуск: 
python lr5.py

Основні функції:

encrypt_message(plaintext, email, passphrase) - Шифрує текстове повідомлення
Параметри:
plaintext (str) - текст для шифрування
email (str) - email користувача
passphrase (str) - спільний секретний пароль


decrypt_message(b64_payload, email, passphrase) - Дешифрує повідомлення з перевіркою цілісності
Параметри:
b64_payload (str) - зашифроване повідомлення в base64
email (str) - email користувача
passphrase (str) - спільний секретний пароль


generate_key_from_personal(email, passphrase) -  Генерує криптографічний ключ з персональних даних.
Параметри:
email (str) - email користувача
passphrase (str) - спільний пароль
Повертає: 32-байтовий ключ


Демонстрація
Програма включає 4 демонстраційні сценарії:

Генерація ключів - показує, як різні email створюють різні ключі
Успішне шифрування/дешифрування - повний цикл роботи
Невірний ключ - демонстрація відхилення при неправильному паролі
Виявлення підробки - показує захист від модифікації даних

Важливо:
Обидві сторони повинні використовувати однакові email + passphrase


Приклад виводу:
=== Key derivation ===
Sender key (hex)   : b561a7a20bb6bba1a3bc7a9ed5c4ccc51ab444a0bee961e4a9f01c86a2fabf16
Receiver key (hex) : ef3cf52c96eb57736ca29449c6bd678235200ddf06c6a61042fc719b417d8c4c
(Different because emails differ — in a real exchange both sides must derive the same shared key.)

=== Encryption ===
Plaintext: Зустрічаємося завтра о 15:00
Encrypted (base64): mOfQNlNgGmi2uPEq8feh5PdZ9iVBkFcRz+H8E+MKg/VxHwttQT4uTVEbekuvHDWL8wn9t1Qnbpc4yg0+QjndC39dj1791OcKo2fwhR9z14X7oRg5ZZtg5LdmBbf8Tb7t

=== Decryption (correct) ===
MAC_OK: True
Decrypted plaintext: Зустрічаємося завтра о 15:00

=== Decryption attempt with wrong email (wrong key) ===
MAC_OK: False
Result: MAC verification failed — message may be tampered or wrong key.

=== Tampering demonstration ===
MAC_OK: False
Result: MAC verification failed — message may be tampered or wrong key.

Functions available: generate_key_from_personal, encrypt_message, decrypt_message
Change 'shared_secret' to any passphrase you and peer agree on out-of-band.



