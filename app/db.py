# app/db.py
import sqlite3
from datetime import datetime
import os

class Database:
    def __init__(self, db_path='../data/bot.db'):  # ← ВАЖНО: путь ВВЕРХ из app/
        # Определяем абсолютный путь
        current_dir = os.path.dirname(os.path.abspath(__file__))
        abs_db_path = os.path.join(current_dir, db_path)
        
        # Создаем папку data если её нет
        os.makedirs(os.path.dirname(abs_db_path), exist_ok=True)
        
        # Подключаем базу
        self.conn = sqlite3.connect(abs_db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        # Таблица пользователей
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                join_date TIMESTAMP
            )
        ''')
        
        # Таблица тестов
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                test_name TEXT,
                result TEXT,
                test_date TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def add_user(self, user_id, username, first_name, last_name=None):
        """Сохранить пользователя"""
        self.cursor.execute('''
            INSERT OR IGNORE INTO users 
            (user_id, username, first_name, last_name, join_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name, datetime.now()))
        self.conn.commit()
    
    def save_test(self, user_id, test_name, result):
        """Сохранить результат теста"""
        self.cursor.execute('''
            INSERT INTO tests (user_id, test_name, result, test_date)
            VALUES (?, ?, ?, ?)
        ''', (user_id, test_name, result, datetime.now()))
        self.conn.commit()
    
    def get_user_stats(self, user_id):
        """Статистика пользователя"""
        self.cursor.execute('SELECT COUNT(*) FROM tests WHERE user_id = ?', (user_id,))
        test_count = self.cursor.fetchone()[0]
        
        self.cursor.execute('''
            SELECT test_name, result, test_date 
            FROM tests 
            WHERE user_id = ? 
            ORDER BY test_date DESC 
            LIMIT 1
        ''', (user_id,))
        last_test = self.cursor.fetchone()
        
        return {
            'test_count': test_count,
            'last_test': last_test
        }
    
    def close(self):
        """Закрыть БД"""
        self.conn.close()

# Глобальная база
db = Database()