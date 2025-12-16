from telebot import types

# Вопросы и варианты ответов для теста про фильмы
FILM_QUESTIONS = [
    {
        'question': '🎬 **Вопрос 1/4:**\nКакой фильм получил больше всего наград "Оскар"?',
        'answers': [
            ('Титаник', 'film_step1_titanic'),
            ('Властелин колец: Возвращение короля', 'film_step1_lotr'),
            ('Бен-Гур', 'film_step1_benhur'),
            ('Ла-Ла Ленд', 'film_step1_lalaland')
        ],
        'correct': 'film_step1_lotr'
    },
    {
        'question': '🎬 **Вопрос 2/4:**\nКто режиссер фильма "Криминальное чтиво"?',
        'answers': [
            ('Мартин Скорсезе', 'film_step2_scorsese'),
            ('Квентин Тарантино', 'film_step2_tarantino'),
            ('Стивен Спилберг', 'film_step2_spielberg'),
            ('Дэвид Финчер', 'film_step2_fincher')
        ],
        'correct': 'film_step2_tarantino'
    },
    {
        'question': '🎬 **Вопрос 3/4:**\nВ каком году вышел фильм "Матрица"?',
        'answers': [
            ('1998', 'film_step3_1998'),
            ('1999', 'film_step3_1999'),
            ('2000', 'film_step3_2000'),
            ('2001', 'film_step3_2001')
        ],
        'correct': 'film_step3_1999'
    },
    {
        'question': '🎬 **Вопрос 4/4:**\nКакой актер сыграл Тони Старка в фильмах Marvel?',
        'answers': [
            ('Крис Эванс', 'film_step4_evans'),
            ('Роберт Дауни-младший', 'film_step4_downey'),
            ('Крис Хемсворт', 'film_step4_hemsworth'),
            ('Марк Руффало', 'film_step4_ruffalo')
        ],
        'correct': 'film_step4_downey'
    }
]

# Словарь для временного хранения результатов
temp_results = {}

def start_films_test(bot, message):
    """Начало теста про фильмы"""
    user_id = message.from_user.id
    
    # Создаем запись о начале теста в БД
    try:
        from db import db
        db.start_test(user_id, test_name="Тест знаний фильмов")
        temp_results[user_id] = [0, 0, 0, 0]
    except Exception as e:
        print(f"Ошибка при сохранении в БД: {e}")
        temp_results[user_id] = [0, 0, 0, 0]
    
    # Отправляем первый вопрос
    film_step1_question(bot, message)

def film_step1_question(bot, message):
    """Первый вопрос теста"""
    question_data = FILM_QUESTIONS[0]
    markup = types.InlineKeyboardMarkup()
    
    for text, callback_data in question_data['answers']:
        markup.add(types.InlineKeyboardButton(text, callback_data=callback_data))
    
    bot.send_message(message.chat.id, question_data['question'], 
                     reply_markup=markup, parse_mode="Markdown")

def film_step2_question(bot, call):
    """Второй вопрос теста"""
    user_id = call.from_user.id
    is_correct = 1 if call.data == FILM_QUESTIONS[0]['correct'] else 0
    
    # Сохраняем результат
    if user_id in temp_results:
        temp_results[user_id][0] = is_correct
    
    question_data = FILM_QUESTIONS[1]
    markup = types.InlineKeyboardMarkup()
    
    for text, callback_data in question_data['answers']:
        markup.add(types.InlineKeyboardButton(text, callback_data=callback_data))
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=question_data['question'],
        reply_markup=markup,
        parse_mode="Markdown"
    )

def film_step3_question(bot, call):
    """Третий вопрос теста"""
    user_id = call.from_user.id
    is_correct = 1 if call.data == FILM_QUESTIONS[1]['correct'] else 0
    
    # Сохраняем результат
    if user_id in temp_results:
        temp_results[user_id][1] = is_correct
    
    question_data = FILM_QUESTIONS[2]
    markup = types.InlineKeyboardMarkup()
    
    for text, callback_data in question_data['answers']:
        markup.add(types.InlineKeyboardButton(text, callback_data=callback_data))
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=question_data['question'],
        reply_markup=markup,
        parse_mode="Markdown"
    )

def film_step4_question(bot, call):
    """Четвертый вопрос теста"""
    user_id = call.from_user.id
    is_correct = 1 if call.data == FILM_QUESTIONS[2]['correct'] else 0
    
    # Сохраняем результат
    if user_id in temp_results:
        temp_results[user_id][2] = is_correct
    
    question_data = FILM_QUESTIONS[3]
    markup = types.InlineKeyboardMarkup()
    
    for text, callback_data in question_data['answers']:
        markup.add(types.InlineKeyboardButton(text, callback_data=callback_data))
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=question_data['question'],
        reply_markup=markup,
        parse_mode="Markdown"
    )

def show_film_final_result(bot, call):
    """Показываем финальный результат теста"""
    user_id = call.from_user.id
    
    # Сохраняем последний ответ
    is_correct = 1 if call.data == FILM_QUESTIONS[3]['correct'] else 0
    
    # Сохраняем результат
    if user_id in temp_results:
        temp_results[user_id][3] = is_correct
        results = temp_results[user_id]
    else:
        results = [0, 0, 0, 0]
    
    total_questions = 4
    correct_answers = sum(results)
    
    # Определяем уровень знаний
    if correct_answers == total_questions:
        level = "🎬 КиноГУРУ! 🏆"
        description = "Вы настоящий знаток кино! Ваши знания впечатляют!"
    elif correct_answers >= total_questions * 0.75:  # 3 из 4
        level = "🎬 Киноман 🍿"
        description = "Отличные знания! Вы хорошо разбираетесь в фильмах."
    elif correct_answers >= total_questions * 0.5:  # 2 из 4
        level = "🎬 Зритель со стажем 🎥"
        description = "Неплохой результат! Есть что вспомнить и узнать."
    else:
        level = "🎬 Начинающий зритель 📺"
        description = "Есть куда расти! Смотрите больше классических фильмов."
    
    # Сохраняем результат теста в БД
    try:
        from db import db
        db.finish_test(user_id, result=level)
    except Exception as e:
        print(f"Ошибка сохранения в БД: {e}")
    
    # Удаляем временные данные
    if user_id in temp_results:
        del temp_results[user_id]
    
    # Создаем результат
    result_text = f"""
📊 **Результат теста "Проверка знаний фильмов"**

✅ Правильных ответов: **{correct_answers}/{total_questions}**

🏆 **Ваш уровень:** {level}

📝 {description}

🔍 **Ваши ответы:**
1. {'✅ Верно' if results[0] else '❌ Неверно'}
2. {'✅ Верно' if results[1] else '❌ Неверно'}
3. {'✅ Верно' if results[2] else '❌ Неверно'}
4. {'✅ Верно' if results[3] else '❌ Неверно'}

Хотите пройти еще раз или попробовать другой тест?
    """
    
    # Кнопка для возврата в меню
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Вернуться в меню", callback_data="back_to_menu"))
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=result_text,
        reply_markup=markup,
        parse_mode="Markdown"
    )