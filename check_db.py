from db import Database

def main():
    print("🔍 Проверка базы данных...")
    
    try:
        # Создаем базу
        db = Database()
        print("✅ База создана")
        
        # Проверяем таблицы
        db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = db.cursor.fetchall()
        
        print(f"📊 Таблицы: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Тест: добавляем тестового пользователя
        db.add_user(123456, "test_user", "Test", "User")
        print("✅ Тестовый пользователь добавлен")
        
        # Тест: добавляем тест
        db.save_test(123456, "Сериал тест", "ИП ПИРОГОВА")
        print("✅ Тестовый результат добавлен")
        
        # Тест: проверяем статистику
        stats = db.get_user_stats(123456)
        print(f"📈 Статистика: {stats['test_count']} тестов")
        
        db.close()
        print("✅ Все тесты пройдены")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()