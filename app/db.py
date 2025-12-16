import sqlite3
from pathlib import Path

class Database:
    def __init__(self, db_path="data/bot.db"):
        # Создаем директорию если ее нет
        Path("data").mkdir(exist_ok=True)
        
        self.db_path = db_path
        self._init_db()
    
    def _get_connection(self):
        """Создает соединение с базой данных"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_db(self):
        """Инициализация базы данных и создание таблиц"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Таблица пользователей
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                user_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Таблица тестов
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                test_name TEXT NOT NULL,
                result TEXT,
                test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Таблица ответов на вопросы (для теста фильмов)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id INTEGER,
                question_num INTEGER,
                is_correct INTEGER DEFAULT 0
            )
            ''')
            
            conn.commit()
        finally:
            conn.close()
    
    def add_user(self, user_id, username=None, first_name=None, last_name=None):
        """Добавляет или обновляет пользователя"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name))
            conn.commit()
            return True
        finally:
            conn.close()
    
    def start_test(self, user_id, test_name):
        """Начинает новый тест и возвращает его ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO tests (user_id, test_name)
            VALUES (?, ?)
            ''', (user_id, test_name))
            test_id = cursor.lastrowid
            conn.commit()
            return test_id
        finally:
            conn.close()
    
    def save_answer(self, user_id, question_num, is_correct):
        """Сохраняет ответ на вопрос теста"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Находим последний тест пользователя
            cursor.execute('''
            SELECT id FROM tests 
            WHERE user_id = ? 
            ORDER BY test_date DESC 
            LIMIT 1
            ''', (user_id,))
            
            test = cursor.fetchone()
            if test:
                test_id = test['id']
                cursor.execute('''
                INSERT INTO test_answers (test_id, question_num, is_correct)
                VALUES (?, ?, ?)
                ''', (test_id, question_num, is_correct))
                conn.commit()
                return True
        finally:
            conn.close()
        return False
    
    def get_test_results(self, user_id):
        """Получает результаты последнего теста пользователя"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Находим последний тест пользователя
            cursor.execute('''
            SELECT id FROM tests 
            WHERE user_id = ? 
            ORDER BY test_date DESC 
            LIMIT 1
            ''', (user_id,))
            
            test = cursor.fetchone()
            if test:
                test_id = test['id']
                cursor.execute('''
                SELECT is_correct FROM test_answers 
                WHERE test_id = ? 
                ORDER BY question_num
                ''', (test_id,))
                
                results = [row['is_correct'] for row in cursor.fetchall()]
                return results if results else [0, 0, 0, 0]
        finally:
            conn.close()
        
        return [0, 0, 0, 0]
    
    def finish_test(self, user_id, result):
        """Завершает тест и сохраняет результат"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Находим последний тест пользователя
            cursor.execute('''
            SELECT id FROM tests 
            WHERE user_id = ? 
            ORDER BY test_date DESC 
            LIMIT 1
            ''', (user_id,))
            
            test = cursor.fetchone()
            if test:
                test_id = test['id']
                cursor.execute('''
                UPDATE tests 
                SET result = ? 
                WHERE id = ?
                ''', (result, test_id))
                conn.commit()
                return True
        finally:
            conn.close()
        return False
    
    def save_test(self, user_id, test_name, result):
        """Сохраняет результат теста (упрощенный метод для сериалов)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO tests (user_id, test_name, result)
            VALUES (?, ?, ?)
            ''', (user_id, test_name, result))
            conn.commit()
            return True
        finally:
            conn.close()
    
    def get_user_stats(self, user_id):
        """Получает статистику пользователя"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Количество тестов
            cursor.execute('SELECT COUNT(*) as count FROM tests WHERE user_id = ?', (user_id,))
            test_row = cursor.fetchone()
            test_count = test_row['count'] if test_row else 0
            
            # Последний тест
            cursor.execute('''
            SELECT test_name, result, test_date 
            FROM tests 
            WHERE user_id = ? 
            ORDER BY test_date DESC 
            LIMIT 1
            ''', (user_id,))
            
            last_test_row = cursor.fetchone()
            
            last_test = None
            if last_test_row:
                last_test = (
                    last_test_row['test_name'], 
                    last_test_row['result'], 
                    last_test_row['test_date']
                )
            
            return {
                'test_count': test_count,
                'last_test': last_test
            }
        finally:
            conn.close()
    
    def get_all_users(self):
        """Получает всех пользователей"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
            return cursor.fetchall()
        finally:
            conn.close()

# Создаем глобальный экземпляр базы данных
db = Database()