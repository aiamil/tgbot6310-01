import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_path="data/bot.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()
    
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_db(self):
        """Создаем все необходимые таблицы"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Таблица тестов (основная)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            test_name TEXT NOT NULL,
            result TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        ''')
        
        # Таблица для теста 3 (викторина)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS test3_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            correct_count INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            percentage REAL NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id, username=None, first_name=None, last_name=None):
        """Добавить пользователя"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
        VALUES (?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name))
        
        conn.commit()
        conn.close()
        return True
    
    def save_test(self, user_id, test_name, result):
        """Сохранить результат теста"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Сначала проверяем, есть ли result
        if result is None:
            result = "Результат не определен"
        
        cursor.execute('''
        INSERT INTO tests (user_id, test_name, result)
        VALUES (?, ?, ?)
        ''', (user_id, test_name, str(result)))
        
        conn.commit()
        conn.close()
        return True
    
    def save_test3_result(self, user_id, correct_count, total_questions, percentage):
        """Сохранить результат теста 3 (викторины)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO test3_results (user_id, correct_count, total_questions, percentage)
        VALUES (?, ?, ?, ?)
        ''', (user_id, correct_count, total_questions, percentage))
        
        conn.commit()
        conn.close()
        return True
    
    def get_user_stats(self, user_id):
        """Получить статистику пользователя"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Общее количество тестов
            cursor.execute("SELECT COUNT(*) FROM tests WHERE user_id = ?", (user_id,))
            test_count = cursor.fetchone()[0]
            
            # Количество тестов 3
            cursor.execute("SELECT COUNT(*) FROM test3_results WHERE user_id = ?", (user_id,))
            test3_count = cursor.fetchone()[0]
            
            # Последний тест
            cursor.execute('''
            SELECT test_name, result, created_at 
            FROM tests 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT 1
            ''', (user_id,))
            
            row = cursor.fetchone()
            last_test = None
            
            if row:
                last_test = {
                    'test_name': row['test_name'],
                    'result': row['result'],
                    'created_at': row['created_at']
                }
            
            # Результаты теста 3
            cursor.execute('''
            SELECT correct_count, total_questions, percentage, created_at
            FROM test3_results 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT 5
            ''', (user_id,))
            
            test3_results = []
            rows = cursor.fetchall()
            for row in rows:
                test3_results.append({
                    'correct_count': row['correct_count'],
                    'total_questions': row['total_questions'],
                    'percentage': row['percentage'],
                    'created_at': row['created_at']
                })
            
            return {
                'test_count': test_count,
                'test3_count': test3_count,
                'last_test': last_test,
                'test3_results': test3_results
            }
        except Exception as e:
            print(f"Ошибка в get_user_stats: {e}")
            # Возвращаем базовую структуру в случае ошибки
            return {
                'test_count': 0,
                'test3_count': 0,
                'last_test': None,
                'test3_results': []
            }
        finally:
            conn.close()

# Создаем глобальный экземпляр
db = Database()