# -*- coding: utf-8 -*-
import os
from flask import Flask, request
import telebot
from telebot import types
import botToken
import helpers as hp
import time
import datetime
import logging

TOKEN = botToken.GetBotToken()
bot = telebot.TeleBot(TOKEN, threaded=False)
server = Flask(__name__)

user_dict = {}

class TripInfo:
    def __init__(self, fuelPrice):
        self.fuelPrice = fuelPrice
        self.fuelCons = None
        self.pointA = None
        self.aList = None
        self.pointB = None
        self.bList = None


# Handle '/start' and '/help'
@bot.message_handler(commands=['start'])
def send_start(message):
    msg = bot.reply_to(message, 
        "Hi there, I am CostTripBot.\r\n" +
        "I can calculate the cost of the trip from point A to point B.\r\n" +
        "Let's start! Enter the price 1 litre of fuel:\r\n")
    bot.register_next_step_handler(msg, process_fuel_price)

# Handle any text message
@bot.message_handler(content_types=['text'])
def send_other(message):
    if message.text != '/start':
        bot.send_message(message.from_user.id, 'To start calculation enter /start')
        logging.info("user: {}; time: {}; message: {};".format(
            message.from_user.first_name, 
            str(datetime.datetime.now()), 
            message.text)
        )

def process_fuel_price(message):
    try:
        chat_id = message.chat.id
        try:
            fuelPrice = float(message.text)
        except:
            msg = bot.reply_to(message, 'Fuel price should be a number.')
            bot.register_next_step_handler(msg, process_fuel_price)
            return
        tripInfo = TripInfo(fuelPrice)
        user_dict[chat_id] = tripInfo
        msg = bot.send_message(chat_id, 'Enter fuel consumption per 100 km.')
        bot.register_next_step_handler(msg, process_fuel_consumption)
    except Exception as e:
        bot.reply_to(message, 'oooops\r\n'+str(e))

def process_fuel_consumption(message):
    try:
        chat_id = message.chat.id
        try:
            fuelCons = float(message.text)
        except:
            msg = bot.reply_to(message, 'Fuel consumption should be a number.')
            bot.register_next_step_handler(msg, process_fuel_consumption)
            return
        tripInfo = user_dict[chat_id]
        tripInfo.fuelCons = fuelCons
        msg = bot.send_message(chat_id, 'Enter title of Point A')
        bot.register_next_step_handler(msg, process_get_pointA)
    except Exception as e:
        bot.reply_to(message, 'oooops')

def process_get_pointA(message):
    try:
        chat_id = message.chat.id
        pointA = message.text
        tripInfo = user_dict[chat_id]        

        locA = hp.SearchLocation(pointA)
        aList = hp.LocationsInfo(locA)

        if len(aList) == 0:
            msg = bot.reply_to(message, 'Point not found. Try again.')
            bot.register_next_step_handler(msg, process_get_pointA)
            return

        msgText = hp.GetOptionMsg(aList)
        tripInfo.aList = aList
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)

        counter = 0
        for _ in range(len(aList)): 
            counter += 1   
            markup.add(str(counter))

        msg = bot.send_message(
            chat_id, 
            'Choose variant of Point A,\r\n{}'.format(msgText), 
            reply_markup=markup
        )
        bot.register_next_step_handler(msg, process_get_pointA_location)
    except Exception as e:
        bot.reply_to(message, 'oooops')

def process_get_pointA_location(message):
    try:
        chat_id = message.chat.id
        locA = int(message.text)
        tripInfo = user_dict[chat_id]
        tripInfo.pointA = tripInfo.aList[locA-1]["position"]
        msg = bot.send_message(chat_id, 'Enter title of Point B')
        bot.register_next_step_handler(msg, process_get_pointB)
    except Exception as e:
        bot.reply_to(message, 'oooops\r\n'+ e.message)

def process_get_pointB(message):
    try:
        chat_id = message.chat.id
        pointB = message.text
        tripInfo = user_dict[chat_id]        

        locB = hp.SearchLocation(pointB)
        bList = hp.LocationsInfo(locB)

        if len(bList) == 0:
            msg = bot.reply_to(message, 'Point not found. Try again.')
            bot.register_next_step_handler(msg, process_get_pointB)
            return

        msgText = hp.GetOptionMsg(bList)
        tripInfo.bList = bList
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)

        counter = 0
        for _ in range(len(bList)): 
            counter += 1   
            markup.add(str(counter))

        msg = bot.send_message(
            chat_id, 
            'Choose variant of Point B,\r\n{}'.format(msgText), 
            reply_markup=markup
        )
        bot.register_next_step_handler(msg, process_get_pointB_location)
    except Exception as e:
        bot.reply_to(message, 'oooops')

def process_get_pointB_location(message):
    try:
        chat_id = message.chat.id
        locB = int(message.text)
        tripInfo = user_dict[chat_id]
        tripInfo.pointB = tripInfo.bList[locB-1]["position"]
        calc_cost(message)
    except Exception as e:
        bot.reply_to(message, 'oooops\r\n'+ e.message)

def calc_cost(message):
    try:
        chat_id = message.chat.id
        finish = message.text
        tripInfo = user_dict[chat_id]

        routParams = hp.GetRouting(tripInfo.pointA,tripInfo.pointB)
        msg = hp.CalcCostResult(tripInfo.fuelCons, tripInfo.fuelPrice, routParams)

        bot.send_message(chat_id, msg)
        user_dict.pop(chat_id)

    except Exception as e:
        bot.reply_to(message, 'oooops')



@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://cost-trip-bot.herokuapp.com/' + TOKEN)
    return "!", 200


if __name__ == "__main__":    
    logging.basicConfig(filename="request.log", level=logging.INFO)    
    try:
        server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
    except Exception as e:
        # print(e)    # или import traceback; traceback.print_exc() для печати полной инфы
        logging.error(e)
        time.sleep(15)