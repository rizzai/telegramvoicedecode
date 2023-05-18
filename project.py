import telebot
import os
import requests
import speech_recognition as sr
import librosa
import soundfile as sf
import openai
recognizer = sr.Recognizer()
openai.api_key = "PASTE_OPENAI_TOKEN"
TOKEN = "PASTE_TELEBOT_TOKEN"
bot = telebot.TeleBot(token=TOKEN)


def ask(prompt):
    completion = openai.Completion.create(engine="text-davinci-003",
                                          prompt=prompt,
                                          temperature=0.5,
                                          max_tokens=1000)
    return f"Расшифровка с ChatGPT: {completion.choices[0]['text']}"


def convert(path):
    global text
    with sr.AudioFile(path) as source:
        audio = recognizer.record(source)
        text = recognizer.recognize_google(audio, language='ru-RU')


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(
        message.chat.id, 'Привет! Отправь мне голосовое сообщение.')


@bot.message_handler(content_types=['voice'])
def handle_voice_message(message):
    try:
        bot.send_message(message.chat.id, "Ждите...")
        voice = message.voice
        file_id = voice.file_id
        file_info = bot.get_file(file_id)
        file = requests.get(
            'https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, file_info.file_path))
        with open('voice_message.mp3', 'wb') as f:
            f.write(file.content)
        y, sr = librosa.load('voice_message.mp3', sr=16000)
        file1 = 'voice_message.wav'
        sf.write(file1, y, sr)
        convert("voice_message.wav")
        prompt = f"Я предоставлю тебе текст на русском языке. Твоя задача - расставить в нём запятые и точки. Если ты видишь слово, вообще не подходящее по контексту, то наверняка на его месте стоит слово с похожим звучанием и написанием. Тебе стоит заменить его. Например, если ты видишь слово 'не', но оно не вписывается в контекст, то ты ставишь слово 'мне', ведь оно вписывается. В качестве ответа выдай строку исправленного текста c изменёнными словами и поставленными знаками. Вот текст: {text}"

        bot.send_message(message.chat.id, ask(prompt))
        os.remove("voice_message.wav")
        os.remove("voice_message.mp3")
    except:
        bot.reply_to(
            message, "Произошла какая-то ошибка")


bot.polling()
