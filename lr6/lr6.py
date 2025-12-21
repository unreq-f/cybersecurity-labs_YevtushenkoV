import sqlite3, os, pandas as pd, textwrap

DB_PATH = "demo_sql_injection.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.executescript("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    full_name TEXT,
    email TEXT,
    role TEXT,
    password TEXT
);
""")
users = [
    ('vlad', 'Євтушенко Владислав Віталійович', 'vlad2002571@gmail.com', 'user', 'pwd_vlad'),
    ('ivan', 'Іван Петренко', 'ivan.petrenko@gmail.com', 'admin', 'pwd_ivan'),
    ('olga', 'Ольга Коваль', 'olga.koval@example.com', 'user', 'pwd_olga'),
    ('test', 'Тест Юзер', 'test@example.com', 'user', 'pwd_test'),
]
cur.executemany("INSERT INTO users (username, full_name, email, role, password) VALUES (?, ?, ?, ?, ?)", users)
conn.commit()

def df_from_query(q, params=()):
    return pd.read_sql_query(q, conn, params=params)

def vulnerable_search(name_fragment):
    query = f"SELECT id, username, full_name, email, role FROM users WHERE full_name LIKE '%{name_fragment}%'"
    print("VULNERABLE QUERY:", query)
    cur = conn.cursor()
    cur.execute(query)
    return cur.fetchall()

def protected_search(name_fragment):
    query = "SELECT id, username, full_name, email, role FROM users WHERE full_name LIKE ?"
    param = ('%' + name_fragment + '%',)
    print("PROTECTED QUERY:", query, "params=", param)
    cur = conn.cursor()
    cur.execute(query, param)
    return cur.fetchall()

def vulnerable_login(username_input, password_input):
    query = f"SELECT username, full_name, role FROM users WHERE username = '{username_input}' AND password = '{password_input}'"
    print("VULNERABLE LOGIN QUERY:", query)
    cur = conn.cursor()
    cur.execute(query)
    return cur.fetchone()

def protected_login(username_input, password_input):
    query = "SELECT username, full_name, role FROM users WHERE username = ? AND password = ?"
    print("PROTECTED LOGIN QUERY:", query, "params=", (username_input, password_input))
    cur = conn.cursor()
    cur.execute(query, (username_input, password_input))
    return cur.fetchone()

print("=== Initial users table ===")
print(df_from_query("SELECT id, username, full_name, email, role FROM users"))

print("\n=== Normal search (name fragment 'Владислав') ===")
print("Vulnerable result:", vulnerable_search("Владислав"))
print("Protected result :", protected_search("Владислав"))

malicious_input = "' OR '1'='1"
print("\n=== Malicious search input to exfiltrate data ===")
print("Malicious input:", malicious_input)
print("\nVULNERABLE search with malicious input (returns ALL rows):")
vuln_res = vulnerable_search(malicious_input)
print("Rows returned:", len(vuln_res))
for r in vuln_res:
    print(r)
print("\nPROTECTED search with same input (treated as literal):")
prot_res = protected_search(malicious_input)
print("Rows returned:", len(prot_res))
for r in prot_res:
    print(r)

print("\n=== Vulnerable login (auth bypass) demonstration ===")
attacker_user = "doesnotmatter"
attacker_pass = "' OR '1'='1"
print("Attempting vulnerable_login with attacker payload:")
res = vulnerable_login(attacker_user, attacker_pass)
print("Result:", res, "(AUTH BYPASS if not None)")

print("\n=== Protected login (prevents bypass) ===")
res2 = protected_login(attacker_user, attacker_pass)
print("Result:", res2)

print("\nProtected login with real credentials (vlad/pwd_vlad):", protected_login("vlad", "pwd_vlad"))

report = textwrap.dedent(f"""
    SQL Injection Demo Report
    Database: {DB_PATH}
    Результати аналізу:
    1. Вразливий пошук дозволив отримати доступ до всіх даних.
    2. Захищений пошук сприйняв ін'єкцію як звичайний текст.
    3. Вхід у систему було обійдено через вразливий метод.
""")

# Тепер цей код буде виконуватися правильно
with open("sql_injection_report.txt", "w", encoding="utf-8") as f:
    f.write(report)

print("\nReport written to sql_injection_report.txt")
print("Database saved to:", DB_PATH)

# Показати швидкий фрейм даних для завантаження
df = df_from_query("SELECT id, username, full_name, email, role FROM users")

# Якщо ви запускаєте це локально, рядок нижче можна видалити або закоментувати
# import caas_jupyter_tools as jt; jt.display_dataframe_to_user("Users table (demo)", df)