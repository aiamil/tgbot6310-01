import sqlite3
import os

print("=" * 50)
print("ПРОВЕРКА БАЗЫ ДАННЫХ")
print("=" * 50)

# Путь к базе
db_file = "data/bot.db"

if not os.path.exists(db_file):
    print(f"❌ Файл не найден: {db_file}")
    exit()

try:
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # 1. Таблицы
    print("\n📋 ТАБЛИЦЫ:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    for table in tables:
        print(f"✅ {table[0]}")
    
    # 2. Данные пользователей
    print("\n👥 ПОЛЬЗОВАТЕЛИ:")
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    
    if users:
        print(f"Найдено пользователей: {len(users)}")
        for user in users:
            print(f"ID: {user[0]}, Имя: {user[2] or 'нет'}, @{user[1] or 'нет'}")
    else:
        print("Нет пользователей")
    
    # 3. Тесты
    print("\n🎯 ТЕСТЫ:")
    cursor.execute("SELECT * FROM tests")
    tests = cursor.fetchall()
    
    if tests:
        print(f"Найдено тестов: {len(tests)}")
        for test in tests:
            print(f"ID теста: {test[0]}, ID юзера: {test[1]}, Тест: {test[2]}, Результат: {test[3]}")
    else:
        print("Нет тестов")
    
    conn.close()
    print("\n✅ Проверка завершена!")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")