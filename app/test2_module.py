from telebot import types
import logging

try:
    from db import db
    DB_AVAILABLE = True
except ImportError as e:
    logging.error(f"Не удалось импортировать модуль db: {e}")
    DB_AVAILABLE = False
except Exception as e:
    logging.error(f"Ошибка при импорте db: {e}")
    DB_AVAILABLE = False

logger = logging.getLogger(__name__)

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
        'correct': 'film_step1_lotr',
        'explanation': '✅ Правильно! "Властелин колец: Возвращение короля" получил 11 Оскаров.',
        'correct_answer': 'Властелин колец: Возвращение короля'
    },
    {
        'question': '🎬 **Вопрос 2/4:**\nКто режиссер фильма "Криминальное чтиво"?',
        'answers': [
            ('Мартин Скорсезе', 'film_step2_scorsese'),
            ('Квентин Тарантино', 'film_step2_tarantino'),
            ('Стивен Спилберг', 'film_step2_spielberg'),
            ('Дэвид Финчер', 'film_step2_fincher')
        ],
        'correct': 'film_step2_tarantino',
        'explanation': '✅ Верно! Режиссер - Квентин Тарантино, фильм вышел в 1994 году.',
        'correct_answer': 'Квентин Тарантино'
    },
    {
        'question': '🎬 **Вопрос 3/4:**\nВ каком году вышел фильм "Матрица"?',
        'answers': [
            ('1998', 'film_step3_1998'),
            ('1999', 'film_step3_1999'),
            ('2000', 'film_step3_2000'),
            ('2001', 'film_step3_2001')
        ],
        'correct': 'film_step3_1999',
        'explanation': '✅ Точно! "Матрица" братьев Вачовски вышла в 1999 году.',
        'correct_answer': '1999'
    },
    {
        'question': '🎬 **Вопрос 4/4:**\nКакой актер сыграл Тони Старка в фильмах Marvel?',
        'answers': [
            ('Крис Эванс', 'film_step4_evans'),
            ('Роберт Дауни-младший', 'film_step4_downey'),
            ('Крис Хемсворт', 'film_step4_hemsworth'),
            ('Марк Руффало', 'film_step4_ruffalo')
        ],
        'correct': 'film_step4_downey',
        'explanation': '✅ Правильно! Роберт Дауни-младший сыграл Железного человека.',
        'correct_answer': 'Роберт Дауни-младший'
    }
]

# Словарь для временного хранения результатов
temp_results = {}

def start_films_test(bot, message):
    """Начало теста про фильмы"""
    user_id = message.from_user.id
    
    logger.info(f"Начат тест по фильмам для пользователя {user_id}")
    
    # Инициализируем результаты для пользователя
    temp_results[user_id] = {
        'answers': [],  # список ответов (0/1)
        'user_choices': [],  # список выбранных вариантов
        'answer_texts': [],  # текст выбранных ответов
        'test_id': None
    }
    
    # Создаем запись о тесте в БД
    try:
        from db import db
        test_id = db.start_test(user_id, "Тест знаний фильмов")
        temp_results[user_id]['test_id'] = test_id
    except Exception as e:
        logger.error(f"Ошибка при создании теста в БД: {e}")
    
    # Отправляем первый вопрос
    send_question(bot, message.chat.id, 0)

def send_question(bot, chat_id, question_index):
    """Универсальная функция для отправки вопроса"""
    question_data = FILM_QUESTIONS[question_index]
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # Создаем кнопки с вариантами ответов
    buttons = []
    for text, callback_data in question_data['answers']:
        buttons.append(types.InlineKeyboardButton(text, callback_data=callback_data))
    
    # Распределяем кнопки по 2 в ряд
    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            markup.add(buttons[i], buttons[i + 1])
        else:
            markup.add(buttons[i])
    
    bot.send_message(chat_id, question_data['question'], 
                     reply_markup=markup, parse_mode="Markdown")

def process_answer(bot, call, current_step):
    """Обработка ответа пользователя"""
    user_id = call.from_user.id
    
    # Получаем текст выбранного ответа
    question_data = FILM_QUESTIONS[current_step]
    answer_text = None
    for text, callback_data in question_data['answers']:
        if callback_data == call.data:
            answer_text = text
            break
    
    # Проверяем правильность ответа
    is_correct = 1 if call.data == question_data['correct'] else 0
    
    # Сохраняем результат
    if user_id not in temp_results:
        temp_results[user_id] = {
            'answers': [], 
            'user_choices': [],
            'answer_texts': [],
            'test_id': None
        }
    
    temp_results[user_id]['answers'].append(is_correct)
    temp_results[user_id]['user_choices'].append(call.data)
    temp_results[user_id]['answer_texts'].append(answer_text)
    
    # Сохраняем детальный ответ в БД
    if temp_results[user_id]['test_id']:
        try:
            from db import db
            db.save_test_answers(
                test_id=temp_results[user_id]['test_id'],
                question_num=current_step + 1,
                is_correct=is_correct,
                answer_text=answer_text,
                correct_answer=question_data['correct_answer']
            )
        except Exception as e:
            logger.error(f"Ошибка сохранения ответа в БД: {e}")
    
    # Отправляем быструю обратную связь
    feedback_text = "✅ Верно!" if is_correct else "❌ Неверно!"
    bot.answer_callback_query(
        call.id,
        text=feedback_text,
        show_alert=False
    )
    
    # Если это последний вопрос, показываем результат
    if current_step == len(FILM_QUESTIONS) - 1:
        show_film_final_result(bot, call)
    else:
        # Иначе показываем следующий вопрос
        show_next_question(bot, call, current_step)

def show_next_question(bot, call, current_step):
    """Показывает следующий вопрос"""
    next_step = current_step + 1
    question_data = FILM_QUESTIONS[next_step]
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for text, callback_data in question_data['answers']:
        buttons.append(types.InlineKeyboardButton(text, callback_data=callback_data))
    
    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            markup.add(buttons[i], buttons[i + 1])
        else:
            markup.add(buttons[i])
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=question_data['question'],
        reply_markup=markup,
        parse_mode="Markdown"
    )

def film_step1_question(bot, message):
    """Первый вопрос теста"""
    send_question(bot, message.chat.id, 0)

def film_step2_question(bot, call):
    """Второй вопрос теста"""
    process_answer(bot, call, 0)

def film_step3_question(bot, call):
    """Третий вопрос теста"""
    process_answer(bot, call, 1)

def film_step4_question(bot, call):
    """Четвертый вопрос теста"""
    process_answer(bot, call, 2)

def show_film_final_result(bot, call):
    """Показываем финальный результат теста"""
    user_id = call.from_user.id
    
    # Получаем текст последнего ответа
    question_data = FILM_QUESTIONS[3]
    answer_text = None
    for text, callback_data in question_data['answers']:
        if callback_data == call.data:
            answer_text = text
            break
    
    # Проверяем правильность последнего ответа
    is_correct = 1 if call.data == question_data['correct'] else 0
    
    if user_id in temp_results:
        temp_results[user_id]['answers'].append(is_correct)
        temp_results[user_id]['user_choices'].append(call.data)
        temp_results[user_id]['answer_texts'].append(answer_text)
        results = temp_results[user_id]['answers']
        test_id = temp_results[user_id]['test_id']
        
        # Сохраняем последний ответ в БД
        if test_id:
            try:
                from db import db
                db.save_test_answers(
                    test_id=test_id,
                    question_num=4,
                    is_correct=is_correct,
                    answer_text=answer_text,
                    correct_answer=question_data['correct_answer']
                )
            except Exception as e:
                logger.error(f"Ошибка сохранения последнего ответа: {e}")
    else:
        results = [0, 0, 0, 0]
        test_id = None
    
    total_questions = len(FILM_QUESTIONS)
    correct_answers = sum(results)
    percentage = int((correct_answers / total_questions) * 100)
    
    # Определяем уровень знаний
    level_data = get_level(correct_answers, total_questions)
    
    # Сохраняем результат теста в БД
    try:
        from db import db
        # Сохраняем в совместимую таблицу
        db.save_film_test_result(user_id, correct_answers, total_questions, percentage)
        
        # Обновляем основной тест если есть test_id
        if test_id:
            result_text = f"{level_data['level']}: {correct_answers}/{total_questions}"
            # Обновляем запись теста
            conn = db._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE tests 
                SET result = ?, score = ?, total_questions = ?
                WHERE id = ?
            ''', (result_text, correct_answers, total_questions, test_id))
            conn.commit()
            conn.close()
            
        logger.info(f"Тест завершен для пользователя {user_id}: {correct_answers}/{total_questions}")
    except Exception as e:
        logger.error(f"Ошибка сохранения в БД: {e}")
    
    # Создаем текст результата
    result_text = create_result_text(user_id, results, correct_answers, total_questions, percentage, level_data)
    
    # Кнопки для действий после теста
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu"))
    markup.add(types.InlineKeyboardButton("🔄 Пройти еще раз", callback_data="retry_film_test"))
    markup.add(types.InlineKeyboardButton("📊 История тестов", callback_data="film_test_history"))
    markup.add(types.InlineKeyboardButton("📈 Моя статистика", callback_data="show_stats"))
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=result_text,
        reply_markup=markup,
        parse_mode="Markdown"
    )
    
    # Очищаем временные данные
    if user_id in temp_results:
        del temp_results[user_id]

def get_level(correct_answers, total_questions):
    """Определяет уровень знаний пользователя"""
    percentage = (correct_answers / total_questions) * 100
    
    if percentage == 100:
        return {
            'level': "КиноГУРУ",
            'description': "Вы настоящий знаток кино! Ваши знания впечатляют.",
            'emoji': "🏆",
            'stars': "⭐⭐⭐⭐⭐"
        }
    elif percentage >= 75:
        return {
            'level': "Киноман",
            'description': "Отличные знания! Вы хорошо разбираетесь в фильмах.",
            'emoji': "🍿",
            'stars': "⭐⭐⭐⭐"
        }
    elif percentage >= 50:
        return {
            'level': "Зритель со стажем",
            'description': "Неплохой результат! Есть что вспомнить и узнать.",
            'emoji': "🎥",
            'stars': "⭐⭐⭐"
        }
    else:
        return {
            'level': "Начинающий зритель",
            'description': "Есть куда расти! Смотрите больше классических фильмов.",
            'emoji': "📺",
            'stars': "⭐⭐"
        }

def create_result_text(user_id, results, correct_answers, total_questions, percentage, level_data):
    """Создает текст с результатами теста"""
    result_lines = [
        f"🎬 *РЕЗУЛЬТАТ ТЕСТА ПО ФИЛЬМАМ*",
        f"",
        f"📊 *Статистика:*",
        f"   ✅ Правильно: **{correct_answers}/{total_questions}**",
        f"   📈 Процент: **{percentage}%**",
        f"",
        f"{level_data['emoji']} *Ваш уровень:* **{level_data['level']}**",
        f"{level_data['stars']}",
        f"",
        f"📝 *{level_data['description']}*",
        f"",
        f"🔍 *Подробные ответы:*"
    ]
    
    # Добавляем информацию по каждому вопросу
    for i, (is_correct, question) in enumerate(zip(results, FILM_QUESTIONS), 1):
        emoji = "✅" if is_correct else "❌"
        explanation = question['explanation'].replace('✅ ', '').replace('❌ ', '')
        result_lines.append(f"{i}. {emoji} {explanation}")
    
    result_lines.extend([
        f"",
        f"---",
        f"",
        f"*Что дальше?*"
    ])
    
    return "\n".join(result_lines)

def show_film_test_history(bot, call):
    """Показывает историю тестов пользователя по фильмам"""
    user_id = call.from_user.id
    
    try:
        from db import db
        history = db.get_film_test_history(user_id, limit=5)
        
        if not history:
            text = "📊 *История тестов по фильмам*\n\nУ вас пока нет завершенных тестов."
        else:
            text = "📊 *История ваших тестов по фильмам:*\n\n"
            for i, (correct, total, percentage, date) in enumerate(history, 1):
                # Форматируем дату
                date_str = date[:16] if len(date) > 10 else date
                text += f"*Тест #{i}* ({date_str}):\n"
                text += f"  ✅ {correct}/{total} ({percentage}%)\n\n"
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu"))
        markup.add(types.InlineKeyboardButton("🎬 Новый тест", callback_data="retry_film_test"))
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=markup,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Ошибка при показе истории: {e}")
        bot.answer_callback_query(call.id, text="Ошибка при получении истории", show_alert=True)

def retry_film_test(bot, call):
    """Повторное прохождение теста по фильмам"""
    start_films_test(bot, call.message)