import sqlite3
import os

print("=" * 40)
print("ПРОВЕРКА БАЗЫ ДАННЫХ")
print("=" * 40)

# Путь к базе данных
db_file = "data/bot.db"

# Проверяем существует ли файл
if not os.path.exists(db_file):
    print(f"❌ Файл базы данных не найден: {db_file}")
    print("Создайте папку 'data' и запустите бота для создания базы")
    exit()

# Подключаемся к базе
try:
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # 1. Показываем все таблицы
    print("\n📋 ТАБЛИЦЫ В БАЗЕ:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    for table in tables:
        print(f"  - {table[0]}")
    
    # 2. Показываем пользователей
    print("\n👥 ПОЛЬЗОВАТЕЛИ:")
    cursor.execute("SELECT user_id, username, first_name, created_at FROM users ORDER BY created_at DESC")
    users = cursor.fetchall()
    
    if users:
        print(f"Всего пользователей: {len(users)}")
        print("ID       | Username     | Имя       | Дата регистрации")
        print("-" * 60)
        for user in users:
            user_id, username, first_name, created_at = user
            username = username if username else "нет"
            first_name = first_name if first_name else "нет"
            print(f"{user_id:<8} | {username:<12} | {first_name:<10} | {created_at[:10]}")
    else:
        print("Пользователей пока нет")
    
    # 3. Показываем тесты
    print("\n🎬 ПРОЙДЕННЫЕ ТЕСТЫ:")
    cursor.execute("SELECT test_name, result, test_date FROM tests ORDER BY test_date DESC")
    tests = cursor.fetchall()
    
    if tests:
        print(f"Всего тестов: {len(tests)}")
        print("Тест                     | Результат                     | Дата")
        print("-" * 80)
        for test in tests:
            test_name, result, test_date = test
            result_short = result[:30] + "..." if len(result) > 30 else result
            print(f"{test_name:<25} | {result_short:<30} | {test_date[:19]}")
    else:
        print("Тестов пока нет")
    
    # 4. Общая статистика
    print("\n📊 СТАТИСТИКА:")
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tests")
    total_tests = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT user_id) FROM tests")
    active_users = cursor.fetchone()[0]
    
    print(f"Всего пользователей: {total_users}")
    print(f"Всего тестов пройдено: {total_tests}")
    print(f"Активных пользователей (прошли тест): {active_users}")
    
    conn.close()
    print("\n✅ Проверка завершена!")

except sqlite3.Error as e:
    print(f"❌ Ошибка SQLite: {e}")
except Exception as e:
    print(f"❌ Ошибка: {e}")