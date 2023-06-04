import openai
import telebot
from telebot import types
import threading
from threading import Timer
import requests
import json
import datetime

bot = telebot.TeleBot("")
apiKeyOpenai = ''
openai.api_key = apiKeyOpenai

USER_EXAMPLE = {
    "telegram_chat_id": 0,
    "telegram_name": "",
    "name": "",
    "text": "",
    "status_id": 1,
    "age": 0,
    "city": "",
    "photos": [],
    "words": []
}

ALL_USERS = dict()

def firstLetterUp(str):
    return str[0].upper() + str[1:]

def send_info_to_api(ALL_USERS, id):
    data = json.dumps(ALL_USERS[f'{id}'])
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'}
    response = requests.request("POST", 'http://k92900u9.beget.tech/bot/create_user.php', headers=headers, data=data)
    print(response)
    response = response.json()
    print(response)
    ALL_USERS.pop(f'{id}')

def essay(message):
    bot.send_message(message.chat.id, 'Прекрасный рассказ! 😎\nСейчас его обработает нейросеть. Нужно только немножко подождать...')
    t = Timer(10.0, essayKeywords, [message])
    t.start() 

def essayKeywords(message):
    try:
        a = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": f'{message.text}\nнапиши 10 ключевых слов исключительно с помощью русских символов из данного рассказа, выведи в ответе только ключевые слова, без тире, только через запятую, начиная с маленькой буквы'}
            ]
        )
        a = a.choices[0].message.content

        # a = 'технологии, смартфоне, приложения, программирование, отечественные продукты, развитие, проекты, поддержка, опыт, мероприятия.'

        print(a)
        aa = a.split(',')
        print(aa)
    except:
        a = 'не указано'
        print(a)
        aa = ['не указано']
        print(aa)
    
    ALL_USERS[f'{message.chat.id}'] = dict(USER_EXAMPLE)
    ALL_USERS[f'{message.chat.id}']['words'] = aa
    ALL_USERS[f'{message.chat.id}']['telegram_chat_id'] = int(message.chat.id) 
    if message.from_user.username == None:
        ALL_USERS[f'{message.chat.id}']['telegram_name'] = 'none'
    else:
        ALL_USERS[f'{message.chat.id}']['telegram_name'] = message.from_user.username
    ALL_USERS[f'{message.chat.id}']['name'] = message.from_user.first_name

    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Продолжить ➡️", callback_data='continue_registration')
    markup.add(button)
    s = '\n'
    bot.send_message(message.chat.id, f'🤖 Нейронная сеть нашла следующие тэги:\n    ➖ {f"{s}    ➖ ".join([firstLetterUp(word.strip()) for word in aa])}', reply_markup=markup)



def getAge(message):
    try:
        ALL_USERS[f'{message.chat.id}']['age'] = int(message.text)
    except:
        ALL_USERS[f'{message.chat.id}']['age'] = 0

    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Я - один, ищу участника", callback_data='whatYourFind_1')
    markup.add(button1)
    button2 = types.InlineKeyboardButton("Я - один, ищу команду", callback_data='whatYourFind_2')
    markup.add(button2)
    button3 = types.InlineKeyboardButton("Мы - команда, ищем участников", callback_data='whatYourFind_3')
    markup.add(button3)
    bot.send_message(message.chat.id, '🤖 Отлично, возраст принят!\n✏️ Выбери нужный тебе вариант', reply_markup=markup)


def getCity(message):
    if message.text == None:
        ALL_USERS[f'{message.chat.id}']['city'] = 'не указан'
    else:
        ALL_USERS[f'{message.chat.id}']['city'] = message.text

    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("🖼 Прикрепить", callback_data='get_photo')
    markup.add(button)
    bot.send_message(message.chat.id, '📸 Теперь время прикрепить фотографию профиля', reply_markup=markup)


def getPhoto(message):
    try:
        photoId = message.photo[-1].file_id
    except:
        photoId = 'AgACAgIAAxkBAAIB_2R5p39S_bgirrvMYSG5hIwAAR6VbAACwsUxG0scyEsWxiTNOMFY6gEAAwIAA3gAAy8E'

    ALL_USERS[f'{message.chat.id}']['photos'] = [photoId]

    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Завершить регистрацию", callback_data='finish')
    markup.add(button)
    bot.send_message(message.chat.id, 'Отлично! Ты заполним все нужные данные 😎', reply_markup=markup)













@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == 'continue_registration':
        msg = bot.send_message(call.message.chat.id, '✏️ А теперь напиши свой возраст')
        bot.register_next_step_handler(msg, getAge)
    elif call.data == 'get_photo':
        msg = bot.send_message(call.message.chat.id, '🤖Отправь мне фотографию\n❗️Отправлять нужно именно фотографией, а не файлом')
        bot.register_next_step_handler(msg, getPhoto)
    elif call.data == 'whatYourFind_1' or call.data == 'whatYourFind_2' or call.data == 'whatYourFind_3':
        if call.data == 'whatYourFind_1':
            status_id = 1
        elif call.data == 'whatYourFind_2':
            status_id = 2
        elif call.data == 'whatYourFind_3':
            status_id = 3
        ALL_USERS[f'{call.message.chat.id}']['status_id'] = status_id
        msg = bot.send_message(call.message.chat.id, '📝 А в каком городе ты живёшь? \n❔ Если у тебя команда, можешь указать города участников через запятую')
        bot.register_next_step_handler(msg, getCity)

    elif call.data == 'finish':
        send_info_to_api(ALL_USERS, call.message.chat.id)        
        print(ALL_USERS)
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton("🪪 Мой профиль", callback_data='profile')
        markup.add(button1)
        button2 = types.InlineKeyboardButton("✈️ Рекомендации", callback_data='recommendation')
        markup.add(button2)
        button3 = types.InlineKeyboardButton("🎲 Случайные знакомства", callback_data='random')
        markup.add(button3)
        bot.send_message(call.message.chat.id, '🏠 Меню:', reply_markup=markup)

    elif call.data == 'go_home':
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton("🪪 Мой профиль", callback_data='profile')
        markup.add(button1)
        button2 = types.InlineKeyboardButton("✈️ Рекомендации", callback_data='recommendation')
        markup.add(button2)
        button3 = types.InlineKeyboardButton("🎲 Случайные знакомства", callback_data='random')
        markup.add(button3)
        bot.send_message(call.message.chat.id, '🏠 Меню:', reply_markup=markup)

    elif call.data == 'profile':
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'}
            response = requests.request("GET", f'http://k92900u9.beget.tech/bot/get_user_by_chat.php?id={str(call.message.chat.id)}', headers=headers)
            print(response)
            response = response.json()
            print(response)
            s = '\n'
            caption = f'👤 {response["name"]}\n🔢 {response["age"]}\n\n🔠 Тэги пользователя:\n    ➖ {f"{s}    ➖ ".join([firstLetterUp(word.strip()) for word in response["words"]])}\n\n🏙 {response["city"]}\n\n🗯 {response["status"]}'
            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton("🏡 На главную", callback_data='go_home')
            markup.add(button1)
            bot.send_photo(str(response['telegram_chat_id']), response['photos'][0], caption, reply_markup=markup)
        except Exception as e:
            bot.send_message(call.message.chat.id, f'Ошибка при открытии профиля\n```\n{e}\n```\nПожалуйста, сообщите эту ошибку либо перешлите это сообщение главному разработчику — @chesnokpeter')

    elif call.data == 'recommendation':
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'}
            response = requests.request("GET", f'http://k92900u9.beget.tech/bot/get_user_by_chat.php?id={call.message.chat.id}', headers=headers)
            response = response.json()
            print(response)
            iddb = response["id"]
            words = response["words"]
            data = json.dumps({
                "seeker_id" : iddb,
                "words" : words
            })
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'}
            response = requests.request("POST", 'http://k92900u9.beget.tech/bot/similar_user.php', headers=headers, data=data)
            print(response)
            response = response.json()
            print(response)
            contact = response["telegram_name"]
            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton("✔️✔️✔️", callback_data=f'accept|{contact}')
            button2 = types.InlineKeyboardButton("❌", callback_data='recommendation')
            markup.add(button1, button2)
            button3 = types.InlineKeyboardButton("🏡 На главную", callback_data='go_home')
            markup.add(button3)
            s = '\n'
            caption = f'👤 {response["name"]}\n🔢 {response["age"]}\n\n🔠 Тэги пользователя:\n    ➖ {f"{s}    ➖ ".join([firstLetterUp(word.strip()) for word in response["words"]])}\n\n🏙 {response["city"]}\n\n🗯 {response["status"]}'
            bot.send_photo(call.message.chat.id, response['photos'][0], caption, reply_markup=markup)
        except:
            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton("🏡 На главную", callback_data='go_home')
            markup.add(button1)
            bot.send_message(call.message.chat.id, '😔 Эх, в системе рекомендаций ничего не нашлось...\nПопробуйте открыть 🎲 Случайные знакомства', reply_markup=markup)


    elif call.data == 'random':
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'}
            response = requests.request("GET", f'http://k92900u9.beget.tech/bot/get_user_by_chat.php?id={call.message.chat.id}', headers=headers)
            response = response.json()
            print(response)
            iddb = response["id"]
            response = requests.request("GET", f'http://k92900u9.beget.tech/bot/fast_search.php?id={iddb}', headers=headers)
            print(response)
            response = response.json()
            print(response)
            contact = response["telegram_name"]
            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton("✔️✔️✔️", callback_data=f'accept|{contact}')
            button2 = types.InlineKeyboardButton("🎲", callback_data='random')
            markup.add(button1, button2)
            button3 = types.InlineKeyboardButton("🏡 На главную", callback_data='go_home')
            markup.add(button3)
            s = '\n'
            caption = f'👤 {response["name"]}\n🔢 {response["age"]}\n\n🔠 Тэги пользователя:\n    ➖ {f"{s}    ➖ ".join([firstLetterUp(word.strip()) for word in response["words"]])}\n\n🏙 {response["city"]}\n\n🗯 {response["status"]}'
            bot.send_photo(call.message.chat.id, response['photos'][0], caption, reply_markup=markup)
        except:
            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton("🏡 На главную", callback_data='go_home')
            markup.add(button1)
            bot.send_message(call.message.chat.id, '😔 Эх, в боте ничего не нашлось...', reply_markup=markup)


    else:
        try:
            accept = call.data.split('|')
            accept = accept[1]

            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton("🏡 На главную", callback_data='go_home')
            markup.add(button1)
            bot.send_message(call.message.chat.id, 'Отлично! Команда "ФрэндUP" рада, что ты смог найти нового друга 😎')
            bot.send_message(call.message.chat.id, f'Telegram-профиль: @{accept}')
            bot.send_message(call.message.chat.id, 'Хорошего общения и продуктивного сотрудничества 💪🏻', reply_markup=markup)
        except:
            pass







@bot.message_handler(commands=['start'])
def start_message(message):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'}
    response = requests.request("GET", f'http://k92900u9.beget.tech/bot/get_user_by_chat.php?id={message.chat.id}', headers=headers)

    with open('textdata/start.txt', 'a+') as data:
        print(f'{datetime.datetime.now()}    @{message.from_user.username}    {message.chat.id}    /start', file=data)

    if response.status_code == 404:
        bot.send_message(message.chat.id, '👋 Добрый день!\nТебя приветствует бот ФрендUP 🤖\nОн сможет помочь тебе найти новые знакомства согласно твоим интересам 🔎')
        bot.send_message(message.chat.id, 'Для начала необходимо зарегистрироваться в 🤖\nЭто не сложно, но очень важно❗️\nТебе нужно: \n    ➖Написать развёрнутый рассказ про себя или свою команду. В нём нужно рассказать об увлечениях, интересах и о плана на будущее;\n    ➖Написать город, в котором ты или твоя команда проживает;\n    ➖ Указать твой возраст;\n    ➖ Прислать фотографию для своего профиля')
        msg = bot.send_message(message.chat.id, 'Что ж, приступим!\n✏️ Напиши развёрнутый рассказ о себе\n❓Напиши то, чем ты хочешь поделиться с окружающими. Например, опиши свои увлечения или планы на будущее. Не переживай, оригинал текста никто не увидит')
        bot.register_next_step_handler(msg, essay)
    else:    
        # bot.send_message(message.chat.id, 'Вы уже зарегистрированы!')
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton("🪪 Мой профиль", callback_data='profile')
        markup.add(button1)
        button2 = types.InlineKeyboardButton("✈️ Рекомендации", callback_data='recommendation')
        markup.add(button2)
        button3 = types.InlineKeyboardButton("🎲 Случайные знакомства", callback_data='random')
        markup.add(button3)
        bot.send_message(message.chat.id, '🏠 Меню:', reply_markup=markup)




@bot.message_handler(commands=['about'])
def start_message(message):
    bot.send_message(message.chat.id, '🧑🏻‍💻Разработчики проекта:\nchesnok @chesnokpeter;\nАнтон Дахин @gg_ad;')



@bot.message_handler(content_types=['text'])
def send_echo(message):
    pass













if __name__=='__main__':
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception as e:
            with open('textdata/exception.txt', 'a+') as errors:
                print(f'{datetime.datetime.now()}    {e}', file=errors)
            print(e)
            continue
# bot.polling(none_stop=True, interval=0)




