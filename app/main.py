import config
import telebot
from telebot import types

bot = telebot.TeleBot(config.token)

# Создаем словарь для хранения пользователей (временное решение)
temp_user_data = {}

@bot.message_handler(commands=['start'])
def start_command(message):
    user = message.from_user
    
    # Сохраняем пользователя в БД
    try:
        from db import db
        db.add_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
    except Exception as e:
        print(f"Ошибка при сохранении пользователя: {e}")
    
    # Создаем клавиатуру с тремя кнопками
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Тест 1: Какой сериал вам подходит?")
    btn2 = types.KeyboardButton("Тест 2: Проверка знаний фильмов 🎥")
    btn3 = types.KeyboardButton("📊 Моя статистика")
    markup.add(btn1, btn2, btn3)
    
    # Приветствие
    bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}! 🎬\nВыберите тест:",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == "Тест 1: Какой сериал вам подходит?")
def handle_test1(message):
    # Импортируем внутри функции, чтобы избежать циклического импорта
    try:
        from test1_module import start_serials_test
        start_serials_test(bot, message)
    except Exception as e:
        print(f"Ошибка в тесте 1: {e}")
        bot.send_message(message.chat.id, "⚠️ Произошла ошибка при запуске теста.")

@bot.message_handler(func=lambda message: message.text == "Тест 2: Проверка знаний фильмов 🎥")
def handle_test2(message):
    # Импортируем внутри функции, чтобы избежать циклического импорта
    try:
        from test2_module import start_films_test
        start_films_test(bot, message)
    except Exception as e:
        print(f"Ошибка в тесте 2: {e}")
        bot.send_message(message.chat.id, "⚠️ Произошла ошибка при запуске теста.")

@bot.message_handler(func=lambda message: message.text == "📊 Моя статистика")
def handle_stats(message):
    user_id = message.from_user.id
    
    try:
        from db import db
        
        # Получаем статистику
        stats = db.get_user_stats(user_id)
        
        # Формируем текст сообщения
        text = f"""
📊 *Ваша статистика:*

👤 Имя: {message.from_user.first_name}
🆔 ID: {user_id}
📋 Всего тестов: {stats.get('test_count', 0)}
🎯 Тестов викторин: {stats.get('test3_count', 0)}
        """
        
        # Проверяем наличие последнего теста
        last_test = stats.get('last_test')
        if last_test:
            test_name = last_test.get('test_name', 'Неизвестный тест')
            result = last_test.get('result', 'Нет результата')
            created_at = last_test.get('created_at', 'Неизвестная дата')
            
            # Обрезаем длинный результат
            if len(str(result)) > 50:
                result = str(result)[:50] + "..."
            
            text += f"\n🎬 *Последний тест:*\n├ Тест: {test_name}\n├ Результат: {result}\n└ Дата: {created_at[:10] if created_at else 'Неизвестно'}"
        
        # Если есть результаты теста 3
        test3_results = stats.get('test3_results', [])
        if test3_results:
            text += f"\n\n🎯 *Последние викторины:*"
            for i, test in enumerate(test3_results[:3], 1):  # Показываем последние 3
                correct = test.get('correct_count', 0)
                total = test.get('total_questions', 0)
                percent = test.get('percentage', 0)
                date = test.get('created_at', '')[:10] if test.get('created_at') else ''
                
                text += f"\n{i}. {correct}/{total} правильных ({percent}%) - {date}"
        
        # Если у пользователя нет тестов
        if stats.get('test_count', 0) == 0 and stats.get('test3_count', 0) == 0:
            text += "\n\nℹ️ Вы еще не проходили тесты. Выберите тест из меню!"
        
        bot.send_message(message.chat.id, text, parse_mode="Markdown")
        
    except Exception as e:
        print(f"Ошибка при получении статистики: {e}")
        bot.send_message(
            message.chat.id, 
            f"⚠️ Не удалось получить статистику. Ошибка: {str(e)[:100]}\nПопробуйте позже или пройдите тест сначала."
        )

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    try:
        # Обрабатываем callback для теста 1 (сериалы)
        if call.data.startswith("step1_"):
            from test1_module import step2_question
            step2_question(bot, call)
        elif call.data.startswith("step2_"):
            from test1_module import step3_question
            step3_question(bot, call)
        elif call.data.startswith("step3_"):
            from test1_module import step4_question
            step4_question(bot, call)
        elif call.data.startswith("step4_"):
            from test1_module import show_final_result
            show_final_result(bot, call)
        
        # Обрабатываем callback для теста 2 (фильмы)
        elif call.data.startswith("film_step1_"):
            from test2_module import film_step2_question
            film_step2_question(bot, call)
        elif call.data.startswith("film_step2_"):
            from test2_module import film_step3_question
            film_step3_question(bot, call)
        elif call.data.startswith("film_step3_"):
            from test2_module import film_step4_question
            film_step4_question(bot, call)
        elif call.data.startswith("film_step4_"):
            from test2_module import show_film_final_result
            show_film_final_result(bot, call)
        
        # Обработка кнопки "Вернуться в меню"
        elif call.data == "back_to_menu":
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="Возвращаемся в главное меню..."
            )
            # Показываем главное меню
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Тест 1: Какой сериал вам подходит?")
            btn2 = types.KeyboardButton("Тест 2: Проверка знаний фильмов 🎥")
            btn3 = types.KeyboardButton("📊 Моя статистика")
            markup.add(btn1, btn2, btn3)
            
            bot.send_message(
                call.message.chat.id,
                f"Главное меню 🎬\nВыберите тест:",
                reply_markup=markup
            )
    
    except Exception as e:
        print(f"Ошибка в обработке callback: {e}")
        bot.answer_callback_query(call.id, text="Произошла ошибка. Попробуйте снова.")
    
    # Убираем "часики" на кнопке
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    """Обработка всех остальных сообщений"""
    # Если пользователь отправил что-то кроме кнопок
    if message.text not in ["Тест 1: Какой сериал вам подходит?", 
                           "Тест 2: Проверка знаний фильмов 🎥", 
                           "📊 Моя статистика"]:
        
        # Показываем меню
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Тест 1: Какой сериал вам подходит?")
        btn2 = types.KeyboardButton("Тест 2: Проверка знаний фильмов 🎥")
        btn3 = types.KeyboardButton("📊 Моя статистика")
        markup.add(btn1, btn2, btn3)
        
        bot.send_message(
            message.chat.id,
            f"Пожалуйста, выберите один из вариантов меню:",
            reply_markup=markup
        )

if __name__ == '__main__':
    print("🤖 Бот запущен...")
    bot.infinity_polling()