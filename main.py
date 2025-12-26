import telebot
import requests
import os
from telebot import types

token = os.environ.get("API_TOKEN")
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "Вітаємо!! Цей бот дає змогу дізнатися курс валют до гривні.")
    start(message)

def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Перевірити курси валют")
    item2 = types.KeyboardButton("Перевести валюту")
    markup.add(item1, item2)
    bot.send_message(message.chat.id, "Оберіть дію:", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def main_menu(message):
    if message.text == "Перевірити курси валют":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("USD")
        item2 = types.KeyboardButton("EUR")
        markup.row(item1, item2)
        item3 = types.KeyboardButton("PLN")
        item4 = types.KeyboardButton("GBP")
        markup.row(item3, item4)
        back = types.KeyboardButton("Назад")
        markup.add(back)
        bot.send_message(message.chat.id, "Оберіть валюту для перевірки курсу:", reply_markup=markup)
        bot.register_next_step_handler(message, get_currency_rate)
    elif message.text == "Перевести валюту":
        bot.send_message(message.chat.id, "Введіть суму для конвертації (числом):")
        bot.register_next_step_handler(message, convert_currency)
    elif message.text == "Назад":
        bot.register_next_step_handler(message, start)

def get_currency_rate(message):
    response = requests.get("https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json")
    if message.text in ['USD', 'EUR', 'PLN', 'GBP']:
        currency_code = message.text
        for currency in response.json():
            if currency['cc'] == currency_code:
                rate = currency['rate']
                bot.send_message(message.chat.id, f"Курс {currency_code} до гривні: {rate} UAH")
                break
        bot.register_next_step_handler(message, get_currency_rate)
    elif message.text == "Назад":
        start(message)

def convert_currency(message):
    amount = float(message.text)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=False)
    item1 = types.KeyboardButton("USD to UAH")
    item2 = types.KeyboardButton("EUR to UAH")
    item3 = types.KeyboardButton("PLN to UAH")
    item4 = types.KeyboardButton("GBP to UAH")
    markup.row(item1, item2, item3, item4)
    item5 = types.KeyboardButton("UAH to USD")
    item6 = types.KeyboardButton("UAH to EUR")
    item7 = types.KeyboardButton("UAH to PLN")
    item8 = types.KeyboardButton("UAH to GBP")
    markup.row(item5, item6, item7, item8)
    back = types.KeyboardButton("Назад")
    markup.add(back)
    bot.send_message(message.chat.id, "Оберіть напрямок конвертації:", reply_markup=markup)
    bot.register_next_step_handler(message, perform_conversion, amount)

def perform_conversion(message, amount):
    response = requests.get("https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json")
    currency_code = message.text.split()[0]
    second_currency = message.text.split()[2]
    if currency_code == "UAH":
        for currency in response.json():
            if currency['cc'] == second_currency:
                rate = currency['rate']
                converted_amount = amount / rate
                bot.send_message(message.chat.id, f"{amount} UAH = {converted_amount} {second_currency}")
                break
    else:
        for currency in response.json():
            if currency['cc'] == currency_code:
                rate = currency['rate']
                converted_amount = amount * rate
                bot.send_message(message.chat.id, f"{amount} {currency_code} = {converted_amount} UAH")
                break
    start(message)

bot.infinity_polling()