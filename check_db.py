# check_db.py (в корне проекта, рядом с app/)
import sys
import os
import sqlite3

# Добавляем папку app в путь Python
sys.path.insert(0, 'app')


# Теперь можно импортировать из app
from db import Database

def main():
    print("🔍 Проверка базы данных...")
    
    try:
        # Создаем базу (файл будет в data/bot.db)
        db = Database()
        print("✅ База подключена")
        
        # Проверяем таблицы
        db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = db.cursor.fetchall()
        
        print(f"📊 Найдено таблиц: {len(tables)}")
        for table in tables:
            # Считаем записи в каждой таблице
            db.cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = db.cursor.fetchone()[0]
            print(f"  - {table[0]}: {count} записей")
        
        # Тест: добавляем тестового пользователя
        db.add_user(999999, "test_user", "Test", "User")
        print("✅ Тестовый пользователь добавлен")
        
        # Тест: добавляем тестовый результат
        db.save_test(999999, "Тестовый тест", "Тестовый результат")
        print("✅ Тестовый результат добавлен")
        
        db.close()
        print("✅ Все проверки пройдены!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()