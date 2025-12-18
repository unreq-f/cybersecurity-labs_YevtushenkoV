import re


def analyze_password():
    print("--- Програма аналізу безпеки пароля ---")

    # 1. Введення даних
    password = input("Введіть пароль: ")
    name = input("Введіть ваше ім'я: ").lower()
    birth_date = input("Введіть дату народження (ДД.ММ.РРРР): ")

    # Підготовка даних для аналізу
    birth_parts = birth_date.split('.')
    year = birth_parts[2] if len(birth_parts) > 2 else ""

    issues = []
    recommendations = []
    score = 0

    # 2. Аналіз зв'язку з особистими даними
    found_personal = False
    if name in password.lower():
        issues.append("Пароль містить ваше ім'я")
        found_personal = True

    if year and (year in password or year[-2:] in password):
        issues.append("Пароль містить рік народження")
        found_personal = True

    # 3. Оцінювання складності (критерії)

    # Перевірка довжини
    length = len(password)
    if length >= 12:
        score += 4
    elif length >= 8:
        score += 2
    else:
        issues.append("Пароль занадто короткий (менше 8 символів)")

    # Перевірка різноманітності символів
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", password))

    if has_upper:
        score += 1
    else:
        issues.append("Відсутні великі літери")

    if has_lower: score += 1

    if has_digit:
        score += 1
    else:
        issues.append("Відсутні цифри")

    if has_special:
        score += 1
    else:
        issues.append("Відсутні спеціальні символи")

    # Перевірка на словникові/прості слова
    common_patterns = ["123", "qwerty", "password", "admin"]
    for pattern in common_patterns:
        if pattern in password.lower():
            score -= 2
            issues.append(f"Використано поширене сполучення: {pattern}")
            break

    # 4. Формування фінальної оцінки (від 1 до 10)
    # Якщо знайдені особисті дані, суттєво знижуємо бал
    if found_personal:
        score -= 3

    # Обмежуємо оцінку в межах 1-10
    final_score = max(1, min(10, score))

    # 5. Формування рекомендацій
    if found_personal:
        recommendations.append("Уникайте використання особистих даних у паролі")
    if length < 12:
        recommendations.append("Збільште довжину пароля до 12-16 символів")
    if not has_special or not has_upper:
        recommendations.append("Додайте спеціальні символи та великі літери")
    if final_score > 8:
        recommendations.append("Ваш пароль достатньо надійний")

    # 6. Виведення результатів
    print("\n" + "=" * 30)
    print("РЕЗУЛЬТАТИ АНАЛІЗУ:")
    print(f"Пароль: {'*' * len(password)}")
    print(f"Оцінка: {final_score} з 10")

    if issues:
        print("\nВиявлені проблеми:")
        for issue in issues:
            print(f"- {issue}")

    print("\nРекомендації:")
    if recommendations:
        for rec in recommendations:
            print(f"- {rec}")
    else:
        print("- Пароль відповідає всім нормам безпеки.")
    print("=" * 30)


if __name__ == "__main__":
    analyze_password()