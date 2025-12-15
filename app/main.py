import config
import telebot
from telebot import types

from db import db

bot = telebot.TeleBot(config.token)

@bot.message_handler(commands=['start'])
def start_command(message):
    user = message.from_user
    
    # ⭐ ДОБАВЬ ЭТО - сохраняем пользователя в БД
    db.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    # Создаем клавиатуру с двумя кнопками
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Тест 1 : Какой сериал вам подходит?")
    btn2 = types.KeyboardButton("Вторая кнопка")
    btn3 = types.KeyboardButton("📊 Моя статистика")  # ← Новая кнопка
    markup.add(btn1, btn2, btn3)
    
    # Приветствие
    bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}! 🎬\nВыберите тест:",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == "Тест 1 : Какой сериал вам подходит?")
def handle_test1(message):
    # Импортируем функцию из test1_module.py
    from test1_module import start_serials_test
    start_serials_test(bot, message)

@bot.message_handler(func=lambda message: message.text == "Вторая кнопка")
def handle_button2(message):
    bot.send_message(message.chat.id, "Это вторая кнопка! 📌")

# ⭐ ДОБАВЬ ЭТУ ФУНКЦИЮ - для кнопки "Моя статистика"
@bot.message_handler(func=lambda message: message.text == "📊 Моя статистика")
def handle_stats(message):
    user_id = message.from_user.id
    
    # Получаем статистику из БД
    stats = db.get_user_stats(user_id)
    
    text = f"""
📊 *Ваша статистика:*

👤 Имя: {message.from_user.first_name}
🆔 ID: {user_id}
📋 Всего тестов: {stats['test_count']}
    """
    
    # Если есть последний тест
    if stats['last_test']:
        test_name, result, date = stats['last_test']
        text += f"\n🎬 Последний тест:\n  - {test_name}\n  - Результат: {result}\n  - Дата: {date[:10]}"
    
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    # Обрабатываем callback для теста 1
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
    
    # Убираем "часики" на кнопке
    bot.answer_callback_query(call.id)

if __name__ == '__main__':
    print("🤖 Бот запущен...")
    bot.infinity_polling()