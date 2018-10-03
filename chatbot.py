# -*- coding: utf-8 -*-

from config import *
from keyboard import *
from classes import *
from token import *

import telebot
import sqlite3
import time
import datetime
import sys
import re
import cherrypy

from telebot import apihelper
apihelper.proxy = {'https':'socks5://:@telegram.vpn99.net:55655'}



bot = telebot.TeleBot(token = BOT_TOKEN, threaded = False)
groups = {}
passwords = {}
names = {}



@bot.message_handler(commands=["menu"])
def menu(message):
	user = User(message.from_user, message.chat.id)
	if (user.group == 0):
		keyboard = start_menu_keyboard()
		text = '''Похоже ты здесь первый раз, либо решил спенить группу.
Можешь войти в уже сущетвующую группу, тогда спроси ID и пароль у старосты.
Или создай новую и передай данные для входа одногруппникам.'''
		bot.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode = "HTML")
	else:
		keyboard = menu_keyboard(user.status)
		bot.send_message(message.chat.id, "<b>Меню</b>", reply_markup=keyboard, parse_mode = "HTML")




@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        user = User(call.message.from_user, call.message.chat.id)
        print('''User: "{} {}"   |   {}'''.format(user.first_name, user.last_name, call.data))
    except:
        print('''Some error''')
        return
    if call.data == "enter_group" or call.data == "group_no" or call.data == "group_yes" or call.data == "create_group":
        if (user.group != 0):
            text = "/menu"
            msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode = "HTML")
            return
    else:
        if (user.group == 0):
            text = "/menu"
            msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode = "HTML")
            return
            
            
            
    if call.message:
        if call.data == "change_group_name":
            text = "Введите новое название группы:\n/cancel - отмена"
            msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode = "HTML")
            bot.register_next_step_handler(msg, change_group_name)
        
        if call.data == "change_group_pass":
            text = "Введите новый пароль группы:\n/cancel - отмена"
            msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode = "HTML")
            bot.register_next_step_handler(msg, change_group_pass)
    
        if call.data == "members":
            text = "<b>Участники группы</b>"
            con = sqlite3.connect(DATABASE_PATH)
            cur = con.cursor()
            cur.execute('SELECT "first_name", "username" FROM users WHERE "group" = {}'.format(user.group))
            users = cur.fetchall()
            for user in users:
                text += "\n" + user[0]
                if (user[1] != "None"):
                    text += " @" + user[1]
            keyboard = members_keyboard()
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = text, reply_markup=keyboard, parse_mode = "HTML")
            return
        if call.data == "create_group":
            text = "Введите название группы:\n/cancel - отмена"
            msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode = "HTML")
            bot.register_next_step_handler(msg, set_name_group)
            
        if call.data == "enter_group" or call.data == "group_no":
            text = "Введите ID группы:\n/cancel - отмена"
            msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode = "HTML")
            bot.register_next_step_handler(msg, find_group)
	
        if call.data == "group_yes":
            text = "Введите пароль:\n/cancel - отмена"
            msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode = "HTML")
            bot.register_next_step_handler(msg, pass_group)
	
        if call.data == "leave_group":
            con = sqlite3.connect(DATABASE_PATH)
            cur = con.cursor()
            cur.execute('''UPDATE "users" SET "group" = {} WHERE "chat_id" = {}'''.format(0, call.message.chat.id))
            con.commit()
            if (user.status != 1):
                cur.execute('''UPDATE users SET "status" = "{}" WHERE chat_id = {}'''.format(0, call.message.chat.id))
                con.commit()
            con.close()
            keyboard = start_menu_keyboard()
            text = '''Похоже ты здесь первый раз, либо решил спенить группу.
Можешь войти в уже сущетвующую группу, тогда спроси ID и пароль у старосты.
Или создай новую и передай данные для входа одногруппникам.'''
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = text, reply_markup=keyboard, parse_mode = "HTML")
        
        if call.data == "menu":
            user = User(call.message.from_user, call.message.chat.id)
            keyboard = menu_keyboard(user.status)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="<b>Меню</b>", reply_markup=keyboard, parse_mode = "HTML")
            

        if call.data == "alert":
            keyboard = alert_keyboard()
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="<b>Проверка</b>", reply_markup=keyboard, parse_mode = "HTML")


        if call.data == "exit":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="/menu",  parse_mode = "HTML")


        if call.data == "settings":
            con = sqlite3.connect(DATABASE_PATH)
            cur = con.cursor()
            cur.execute('''SELECT alert, sign, break FROM users WHERE chat_id = {}'''.format(call.message.chat.id))
            se = cur.fetchone()
            text = "<b>Настройки.</b>\nПроверка: {}\nПодпись: {}\nПерерыв: {}\n<b>Подписка на оповещения Вкл/Выкл:</b>".format(bool(se[0]),bool(se[1]),bool(se[2]))
            keyboard = settings_keyboard()
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=keyboard, parse_mode = "HTML")
            con.close()

        if call.data == "data":
            con = sqlite3.connect(DATABASE_PATH)
            cur = con.cursor()
            user = User(call.message.from_user, call.message.chat.id)
            sign = "Загружено"
            if (user.sign_pic == ""):
                sign = "Не загружено"
            text = '''<b>Данные</b>\nИмя: {}\nФамилия: {}\nГруппа: {}\nID Группы: {}\nПодпись: {}\n<b>Изменить:</b>'''.format(user.first_name, user.last_name, user.group_name, user.group, sign)
            keyboard = data_keyboard()
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=keyboard, parse_mode = "HTML")
            con.close()



        if call.data == "Лектор" or call.data == "Инспектор":
            message = call.message
            user = User(message.from_user, message.chat.id)
            con = sqlite3.connect(DATABASE_PATH)
            cur = con.cursor()
            field = "alert_last"
            if call.data == "Лектор":
                field = "lektor_last"
            cur.execute('''SELECT {} FROM "users" WHERE "chat_id" = {}'''.format(field, user.chat_id))
            delta = int(time.time() - cur.fetchone()[0])
            if (delta <= 1800):
                bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="АНТИ ДУДОС. Подожди {} сек.".format(1800 - delta))
                con.close()
                return
            msg = "<b>АЛЯРМ!</b>\n{} {} вещает.\n{} отмечает!".format(user.first_name, user.last_name, call.data)
            cur.execute('''SELECT COUNT(id) FROM "users"''')
            amt = cur.fetchone()[0]
            cur.execute('''SELECT "chat_id", "alert", "group" FROM users''')
            users = cur.fetchall()
            cur.execute('''UPDATE users SET {} = {} WHERE chat_id = {}'''.format(field, int(time.time()), message.chat.id))
            con.commit()
            con.close()
            for i in range(amt):
                if (users[i][0] != message.chat.id and users[i][1] == 1 and user.group == users[i][2]):
                    bot.send_message(users[i][0], msg, parse_mode='HTML')
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="Спасибо. Народ оповещен.")


        if call.data == "break":
            message = call.message
            user = User(message.from_user, message.chat.id)
            con = sqlite3.connect(DATABASE_PATH)
            cur = con.cursor()
            field = "break_last"
            cur.execute('SELECT {} FROM users WHERE chat_id = {}'.format(field, user.chat_id))
            delta = int(time.time() - cur.fetchone()[0])
            if (delta <= 1800):
                bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="АНТИ ДУДОС. Подожди {} сек.".format(1800 - delta))
                con.close()
                return
            msg = "{} {} вещает.\nПерерыв!".format(user.first_name, user.last_name)
            cur.execute('SELECT COUNT(id) FROM users')
            amt = cur.fetchone()[0]
            cur.execute('SELECT chat_id, break, "group" FROM users')
            users = cur.fetchall()
            cur.execute('UPDATE users SET {} = {} WHERE chat_id = {}'.format(field, int(time.time()), message.chat.id))
            con.commit()
            con.close()
            for i in range(amt):
                if (users[i][0] != message.chat.id and users[i][1] == 1 and user.group == users[i][2]):
                    bot.send_message(users[i][0], msg, parse_mode='HTML')
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="Спасибо. Народ оповещен.")

        if call.data == "name":
            text = "Введи имя:"
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode = "HTML")
            msg = call.message
            bot.register_next_step_handler(msg, set_name)

        if call.data == "surname":
            text = "Введи фамилию:"
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode = "HTML")
            msg = call.message
            bot.register_next_step_handler(msg, set_surname)


        if call.data == "alert_subscription":
            con = sqlite3.connect(DATABASE_PATH)
            cur = con.cursor()
            cur.execute('SELECT alert FROM users WHERE chat_id = {}'.format(call.message.chat.id))
            alarm = cur.fetchone()[0]
            if (alarm == 1):
                cur.execute('UPDATE users SET alert = {} WHERE chat_id = {}'.format(0, call.message.chat.id))
                text = "Оповещения о проверках выключены"
                bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=text)
            else:
                cur.execute('UPDATE users SET alert = {} WHERE chat_id = {}'.format(1, call.message.chat.id))
                text = "Оповещения о проверках включены"
                bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=text)
            con.commit()
            cur.execute('SELECT alert, sign, break FROM users WHERE chat_id = {}'.format(call.message.chat.id))
            se = cur.fetchone()
            text = "<b>Настройки.</b>\nПроверка: {}\nПодпись: {}\nПерерыв: {}\n<b>Подписка на оповещения Вкл/Выкл:</b>".format(bool(se[0]),bool(se[1]),bool(se[2]))
            keyboard = settings_keyboard()
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=keyboard, parse_mode = "HTML")
            con.close()

        if call.data == "sign_subscription":
            con = sqlite3.connect(DATABASE_PATH)
            cur = con.cursor()
            cur.execute('SELECT sign FROM users WHERE chat_id = {}'.format(call.message.chat.id))
            alarm = cur.fetchone()[0]
            if (alarm == 1):
                cur.execute('UPDATE users SET sign = {} WHERE chat_id = {}'.format(0, call.message.chat.id))
                text = "Оповещения о просьбах черкануть отключены."
                bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=text)
            else:
                cur.execute('UPDATE users SET sign = {} WHERE chat_id = {}'.format(1, call.message.chat.id))
                text = "Спасибо, черкани если попросят."
                bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=text)
            con.commit()
            cur.execute('SELECT alert, sign, break FROM users WHERE chat_id = {}'.format(call.message.chat.id))
            se = cur.fetchone()
            text = "<b>Настройки.</b>\nПроверка: {}\nПодпись: {}\nПерерыв: {}\n<b>Подписка на оповещения Вкл/Выкл:</b>".format(bool(se[0]),bool(se[1]),bool(se[2]))
            keyboard = settings_keyboard()
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=keyboard, parse_mode = "HTML")
            con.close()


        if call.data == "break_subscription":
            con = sqlite3.connect(DATABASE_PATH)
            cur = con.cursor()
            cur.execute('SELECT break FROM users WHERE chat_id = {}'.format(call.message.chat.id))
            alarm = cur.fetchone()[0]
            if (alarm == 1):
                cur.execute('UPDATE users SET break = {} WHERE chat_id = {}'.format(0, call.message.chat.id))
                text = "Оповещения о перерывах отключены."
                bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=text)
            else:
                cur.execute('UPDATE users SET break = {} WHERE chat_id = {}'.format(1, call.message.chat.id))
                text = "Оповещения о перерывах включены."
                bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=text)
            con.commit()
            cur.execute('SELECT alert, sign, break FROM users WHERE chat_id = {}'.format(call.message.chat.id))
            se = cur.fetchone()
            text = "<b>Настройки.</b>\nПроверка: {}\nПодпись: {}\nПерерыв: {}\n<b>Подписка на оповещения Вкл/Выкл:</b>".format(bool(se[0]),bool(se[1]), bool(se[2]))
            keyboard = settings_keyboard()
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=keyboard, parse_mode = "HTML")
            con.close()


        if call.data == "schedule":
            con = sqlite3.connect(DATABASE_PATH)
            cur = con.cursor()
            text = ""
            user = User(call.message.from_user, call.message.chat.id)
            week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
            todayb = ""
            todaye = ""
            for j in range(7):
                cur.execute('SELECT COUNT(aud) FROM schedule WHERE "group" = {} AND day = {}'.format(user.group, j + 1))
                amt = cur.fetchone()[0]
                cur.execute('SELECT start_time, end_time, name, aud FROM schedule WHERE "group" = {} AND day = {}'.format(user.group, j + 1))
                sch = cur.fetchall()
                if j == datetime.date.today().weekday():
                    todayb = "<b>"
                    todaye = "</b>"
                else:
                    todayb = ""
                    todaye = ""
                if amt != 0:
                    text += todayb
                    text += week[j] + "\n"
                for i in range(amt):
                    text += str(i + 1) + ") " + sch[i][0] + "-" + sch[i][1] + " " + sch[i][2] + " " + sch[i][3] + "\n"
                if amt != 0:
                    text += todaye
                    text += "\n"
            if text == "":
                text = "Расписание не загружено."
            con.close()
            keyboard = schedule_keyboard()
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=keyboard, parse_mode = "HTML")
        
        if call.data == "sign":
            user = User(call.message.from_user, call.message.chat.id)
            con = sqlite3.connect(DATABASE_PATH)
            cur = con.cursor()
            cur.execute('SELECT sign_last FROM users WHERE chat_id = {}'.format(user.chat_id))
            delta = int(time.time() - cur.fetchone()[0])
            if (delta <= 1800):
                text = "АНТИ ДУДОС! Подожди {} сек.".format(1800 - delta)
                bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=text)
                con.close()
                return
            cur.execute('SELECT COUNT(id) FROM users')
            amt = cur.fetchone()[0]
            cur.execute('SELECT chat_id, sign, "group" FROM users')
            users = cur.fetchall()
            cur.execute('UPDATE users SET sign_last = {} WHERE chat_id = {}'.format(int(time.time()), call.message.chat.id))
            con.commit()
            con.close() 

            text = "Народ оповещен."
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=text)
            msg = "{} {} просит черкануть в ведомости.".format(user.first_name, user.last_name)
            for i in range(amt):
                if (users[i][0] != call.message.chat.id and users[i][1] == 1 and user.group == users[i][2]):
                    bot.send_message(users[i][0], msg)
                    if (user.sign_pic != None and user.sign_pic != "None" and user.sign_pic != ""):
                        bot.send_photo(users[i][0], photo = user.sign_pic)

        if call.data == "info":
            keyboard = info_keyboard()
            text = ABOUT_STR
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=keyboard, parse_mode = "HTML")
        
        if call.data == "links":
            keyboard = links_keyboard()
            text = "<b>Ссылки</b>"
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=keyboard, parse_mode = "HTML")
        
        if call.data == "reboot":
            user = User(call.message.from_user, call.message.chat.id)
            if (user.status == 1):
                print ("Rebooted by admin")
                text = "Бот перезагружен."
                bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=text)
                sys.exit()        

        if call.data == "marks":
            user = User(call.message.from_user, call.message.chat.id)
            con = sqlite3.connect(DATABASE_PATH)
            cur = con.cursor()
            cur.execute('SELECT COUNT(id) FROM marks')
            amt = cur.fetchone()[0]
            cur.execute('SELECT id, "date", "text", "group" FROM marks')
            marks = cur.fetchall()
            text = "<b>Заметки</b>"
            count = 0
            for i in range(amt):
                if (marks[i][1] >= time.time() and user.group == marks[i][3]):
                    count += 1
                    text += "\n{}) {}".format(count, marks[i][2])
            con.close()
            keyboard = marks_keyboard()
            if count == 0:
                text += "\nПока нет заметок"
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=keyboard, parse_mode = "HTML")


        if call.data == "moder":
            keyboard = moder_keyboard()
            text = "<b>Меню старосты</b>"
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=keyboard, parse_mode = "HTML")


        if call.data == "admin":
            keyboard = admin_keyboard()
            text = "<b>Админ меню</b>"
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=keyboard, parse_mode = "HTML")




        if call.data == "sign_pic":
            text = "Отправь фото подписи.\n/cancel - отмена"
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode = "HTML")
            bot.register_next_step_handler(call.message, sign_pic)

        if call.data == "show_sign_pic":
            keyboard = showsign_keyboard()
            user = User(call.message.from_user, call.message.chat.id)
            if (user.sign_pic == None or user.sign_pic == "None" or user.sign_pic == ""):
                text = "<b>Подпись не загружена.</b>"
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup = keyboard, parse_mode = "HTML")
                return
            text = "<b>Подпись</b>"
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode = "HTML")
            bot.send_photo(call.message.chat.id, photo = user.sign_pic)
            bot.send_message(call.message.chat.id, reply_markup = keyboard, text=text, parse_mode = "HTML")
            

        if call.data == "feedback":
            text = "<i>Если у вас есть какие либо пожелания или предложения, пишите.</i>\n\nВведите сообщение:\n/cancel - отмена"
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode = "HTML")
            bot.register_next_step_handler(call.message, feedback)

        if call.data == "admin_message":
            text = "Введите сообщение:\n/cancel - отмена"
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode = "HTML")
            bot.register_next_step_handler(call.message, admin_message)


        if call.data == "add_mark":
            text = "<b>Введите заметку в формате:</b>\n<i>DD/MM/YY HH:MM Текст</i>\nгде указанная дата - дата окончания действия заметки. (Указанная в начале дата является технической иформацией и в заметках в тексте не выводится.)\n/cancel - отмена"
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode = "HTML")
            bot.register_next_step_handler(call.message, add_mark)

        if call.data == "add_schedule":
            text = "<b>Введите расписание в формате:</b>\n[HH].[MM] [HH].[MM] [NAME] [AUD]\n[HH] [MM] [HH] [MM] [NAME] [AUD]\n.\n[HH] [MM] [HH] [MM] [NAME] [AUD]\nи так далее\nГде перые значения [HH].[MM] - время начала пары, а вторые [HH].[MM] - время окончания. [NAME] и [AUD] - название и аудитория соответтвенно вводятся без пробелов, только буквы и цифры. Точка на новой строке раздеяет дни (их ДОЛЖНО быть 6). На строке могут быть либо данные о паре, либо одна точка.\n/cancel - отмена"
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode = "HTML")
            bot.register_next_step_handler(call.message, add_schedule)



def add_mark(message):
    if (message.text == "/cancel"):
        user = User(message.from_user, message.chat.id)
        keyboard = moder_keyboard()
        bot.send_message(message.chat.id, "Отменено!")
        text = "<b>Меню старосты</b>"
        bot.send_message(message.chat.id, text = text, reply_markup = keyboard, parse_mode='HTML')
        return
    pattern = r"\d\d/\d\d/\d\d\s\d\d:\d\d\s\S.{10,1000}"
    if (re.match(pattern, message.text) == None):
        keyboard = moder_keyboard()
        text = "Ошибка!"
        bot.send_message(message.chat.id, text=text,parse_mode = "HTML")
        text = "<b>Меню старосты</b>"
        bot.send_message(message.chat.id, text=text, reply_markup=keyboard, parse_mode = "HTML")
        return
    else:
        con = sqlite3.connect(DATABASE_PATH)
        cur = con.cursor()
        user = User(message.from_user, message.chat.id)
        mark_date = message.text[0:14]
        mark_text = message.text[15:]
        print(mark_date)
        try:
            dt = datetime.datetime.strptime(mark_date, "%d/%m/%y %H:%M") 
        except:
            keyboard = moder_keyboard()
            text = "Ошибка!"
            bot.send_message(message.chat.id, text=text,parse_mode = "HTML")
            text = "<b>Меню старосты</b>"
            bot.send_message(message.chat.id, text=text, reply_markup=keyboard, parse_mode = "HTML")
            return
        print(dt)
        cur.execute('''INSERT INTO marks ("date", "text") VALUES({},"{}")'''.format(dt.timestamp(), mark_text))
        con.commit()
        #cur.execute('SELECT COUNT(id) FROM users')
        #amt = cur.fetchone()[0]
        #cur.execute('SELECT chat_id FROM users')
        #users = cur.fetchall()
        #msg = "<b>Добавлена новая заметка!</b>"
        #for i in range(amt):
        #    if (users[i][0] != message.chat.id):
        #        bot.send_message(users[i][0], msg, parse_mode='HTML')
        con.close()
        keyboard = moder_keyboard()
        text = "Добавлено!"
        bot.send_message(message.chat.id, text=text,parse_mode = "HTML")
        text = "<b>Меню старосты</b>"
        bot.send_message(message.chat.id, text=text, reply_markup=keyboard, parse_mode = "HTML")


def feedback(message):
    if (message.text == "/cancel"):
        user = User(message.from_user, message.chat.id)
        keyboard = menu_keyboard(user.status)
        bot.send_message(message.chat.id, "Отменено!")
        text = "<b>Меню</b>"
        bot.send_message(message.chat.id, text = text, reply_markup = keyboard, parse_mode='HTML')
        return
    pat = r'[a-zA-Z"]'
    user = User(message.from_user, message.chat.id)
    try:
        if (re.search(pat, message.text) != None):
            bot.send_message(message.chat.id, "Неправильный формат! Запрещено использовать символы a-z, A-Z, \".")
            keyboard = menu_keyboard(user.status)
            text = "<b>Меню</b>"
            bot.send_message(message.chat.id, text = text, reply_markup=keyboard, parse_mode = "HTML")
            return
        con = sqlite3.connect(DATABASE_PATH)
        cur = con.cursor()
        cur.execute('''INSERT INTO feedback (chat_id, first_name, "text") VALUES({},"{}","{}")'''.format(user.chat_id, user.first_name, message.text))
        con.commit()
        con.close()
        text = "Cообщение отправлено"
        bot.send_message(message.chat.id, text = text, parse_mode = "HTML")
        keyboard = menu_keyboard(user.status)
        text = "<b>Меню</b>"
        bot.send_message(message.chat.id, text = text, reply_markup=keyboard, parse_mode = "HTML")
    except:
        text = "Что-то пошло не так :("
        bot.send_message(message.chat.id, text = text, parse_mode = "HTML")
        keyboard = menu_keyboard(user.status)
        text = "<b>Меню</b>"
        bot.send_message(message.chat.id, text = text, reply_markup=keyboard, parse_mode = "HTML")

def admin_message(message):
    if (message.text == "/cancel"):
        bot.send_message(message.chat.id, "Отменено!")
        keyboard = admin_keyboard()
        text = "Админ меню"
        bot.send_message(message.chat.id, text = text, reply_markup = keyboard, parse_mode='HTML')
        return
    user = User(message.from_user, message.chat.id)
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute('SELECT COUNT(id) FROM users')
    amt = cur.fetchone()[0]
    cur.execute('SELECT chat_id FROM users')
    users = cur.fetchall()
    con.close()
    bot.send_message(message.chat.id, "Отправлено")
    msg = "<b>Admin:</b> <i>" + message.text + "</i>"
    for i in range(amt):
        if (users[i][0] != message.chat.id):
            bot.send_message(users[i][0], msg, parse_mode='HTML')
    keyboard = admin_keyboard()
    text = "Админ меню"
    bot.send_message(message.chat.id, text = text, reply_markup = keyboard, parse_mode='HTML')


def sign_pic(message):
    if (message.text == "/cancel"):
        bot.send_message(message.chat.id, "Отменено!")
        user = User(message.from_user, message.chat.id)
        sign = "Загружено"
        if (user.sign_pic == ""):
            sign = "Не загружено"
        text = '''<b>Данные</b>\nИмя: {}\nФамилия: {}\nГруппа: {}\nID Группы: {}\nПодпись: {}\n<b>Изменить:</b>'''.format(user.first_name, user.last_name, user.group_name, user.group, sign)
        keyboard = data_keyboard()
        bot.send_message(message.chat.id, text = text, reply_markup = keyboard, parse_mode='HTML')
        return
    try:
        if (message.photo == None):
            raise
        con = sqlite3.connect(DATABASE_PATH)
        cur = con.cursor()
        photo = message.photo[len(message.photo) - 1]
        cur.execute('UPDATE users SET sign_pic = "{}", sign_width = {}, sign_height = {} WHERE chat_id = {}'.format(photo.file_id, photo.width, photo.height, message.chat.id))
        con.commit()
        con.close()
        sign = ""
        bot.send_message(message.chat.id, "Загружено.")
        user = User(message.from_user, message.chat.id)
        sign = "Загружено"
        if (user.sign_pic == ""):
            sign = "Не загружено"        
        text = '''<b>Данные</b>\nИмя: {}\nФамилия: {}\nГруппа: {}\nID Группы: {}\nПодпись: {}\n<b>Изменить:</b>'''.format(user.first_name, user.last_name, user.group_name, user.group, sign)
        keyboard = data_keyboard()
        bot.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode = "HTML")
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так. :(")
        msg = bot.send_message(message.chat.id, "Отправь фото подписи.\n/cancel - отмена")
        bot.register_next_step_handler(msg, sign_pic)

def change_group_name(message):
    if (message.text == "/cancel"):
        bot.send_message(message.chat.id, "Отменено!")
        menu(message)
        return
    pat = r'[,"=\+\.]'
    if (re.search(pat, message.text) != None):
        bot.send_message(message.chat.id, "Неправильный формат!")
        text = "Введите новое название группы:\n/cancel - отмена"
        msg = bot.send_message(chat_id=message.chat.id, text=text, parse_mode = "HTML")
        bot.register_next_step_handler(msg, change_group_name)
        return
    user = User(message.from_user, message.chat.id)
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute('''UPDATE "groups" SET "name" = "{}" WHERE "group" = {}'''.format(message.text, user.group))
    con.commit()
    text = "Название группы успешно изменено."
    bot.send_message(chat_id=message.chat.id, text=text, parse_mode = "HTML")
    text = "<b>Меню старосты</b>"
    keyboard = moder_keyboard()
    msg = bot.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode = "HTML")
    return
    
def change_group_pass(message):
    if (message.text == "/cancel"):
        bot.send_message(message.chat.id, "Отменено!")
        menu(message)
        return
    reg = r'[^a-zA-Z0-9]+'
    if (re.search(reg, message.text) != None):
        bot.send_message(message.chat.id, "Неправильный формат!")
        text = "Введите новый пароль группы:\n/cancel - отмена"
        msg = bot.send_message(chat_id=message.chat.id, text=text, parse_mode = "HTML")
        bot.register_next_step_handler(msg, change_group_pass)
        return
    user = User(message.from_user, message.chat.id)
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute('''UPDATE "groups" SET "pass" = "{}" WHERE "group" = {}'''.format(message.text, user.group))
    con.commit()
    text = "Пароль группы успешно изменен."
    bot.send_message(chat_id=message.chat.id, text=text, parse_mode = "HTML")
    cur.execute('SELECT "chat_id" FROM users WHERE "group" = {}'.format(user.group))
    users = cur.fetchall()
    for user in users:
        if (user[0] != message.chat.id):
            bot.send_message(chat_id=user[0], text="Пароль был изменен!", parse_mode = "HTML")
    text = "<b>Меню старосты</b>"
    keyboard = moder_keyboard()
    msg = bot.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode = "HTML")
    return
    
def set_name_group(message):
    if (message.text == "/cancel"):
        bot.send_message(message.chat.id, "Отменено!")
        menu(message)
        return
    pat = r'[,"=\+\.]'
    if (re.search(pat, message.text) != None):
        bot.send_message(message.chat.id, "Неправильный формат!")
        text = "Введите название группы:\n/cancel - отмена"
        msg = bot.send_message(chat_id=message.chat.id, text=text, parse_mode = "HTML")
        bot.register_next_step_handler(msg, set_name_group)
        return
    names[message.chat.id] = message.text
    text = "Введите пароль:\n/cancel - отмена"
    msg = bot.send_message(chat_id=message.chat.id, text=text, parse_mode = "HTML")
    bot.register_next_step_handler(msg, set_pass_group)
    return
    
def set_pass_group(message):
    if (message.text == "/cancel"):
        bot.send_message(message.chat.id, "Отменено!")
        menu(message)
        return
    reg = r'[^a-zA-Z0-9]+'
    if (re.search(reg, message.text) == None):
        con = sqlite3.connect(DATABASE_PATH)
        cur = con.cursor()
        cur.execute('''INSERT INTO "groups" ("pass", "name", "admin") VALUES("{}","{}", {})'''.format(message.text, names[message.chat.id], message.chat.id))
        cur.execute('''SELECT "group" FROM "groups" ORDER BY "group" DESC LIMIT 1''')
        group = cur.fetchone()[0]
        con.commit()
        cur.execute('''UPDATE users SET "status" = "{}" WHERE chat_id = {}'''.format(2, message.chat.id))
        con.commit()
        bot.send_message(message.chat.id, "Группа успешно создана.\nНазвание группы: {}\nID группы: {}".format(names[message.chat.id], group))
        menu(message)
        return
    else:
        bot.send_message(message.chat.id, "Недопустимые символы.")
        text = "Введите пароль:\n/cancel - отмена"
        msg = bot.send_message(chat_id=message.chat.id, text=text, parse_mode = "HTML")
        bot.register_next_step_handler(msg, set_pass_group)
        return

def find_group(message):
    if (message.text == "/cancel"):
        bot.send_message(message.chat.id, "Отменено!")
        menu(message)
        return
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    try:
        group = int(message.text)
        if (group < 0):
            raise
    except:
        bot.send_message(message.chat.id, "Нужно ввести натуральное число!")
        text = "Введите ID группы:\n/cancel - отмена"
        msg = bot.send_message(chat_id=message.chat.id, text=text, parse_mode = "HTML")
        bot.register_next_step_handler(msg, find_group)
        return
    cur.execute('SELECT "name" FROM "groups" WHERE "group" = {}'.format(group))
    res = cur.fetchone()
    if (res == None):
        bot.send_message(message.chat.id, "Нет группы с таким ID.")
        text = "Введите ID группы:\n/cancel - отмена"
        msg = bot.send_message(chat_id=message.chat.id, text=text, parse_mode = "HTML")
        bot.register_next_step_handler(msg, find_group)
        return
    groups[message.chat.id] = group
    name = res[0]
    keyboard = group_confirm()
    text = 'Вы хотите зайти в эту группу:\n"{}"?'.format(name)
    bot.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode = "HTML")


def pass_group(message):
    if (message.text == "/cancel"):
        bot.send_message(message.chat.id, "Отменено!")
        menu(message)
        return
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    reg = r'[^a-zA-Z0-9]+'
    group = groups[message.chat.id]
    if (re.search(reg, message.text) == None):
        cur.execute('SELECT "pass", "admin" FROM "groups" WHERE "group" = {}'.format(group))
        res = cur.fetchone()
        if (message.text == res[0]):
            cur.execute('UPDATE "users" SET "group" = {} WHERE "chat_id" = {}'.format(group, message.chat.id))
            con.commit()
            if (message.chat.id == res[1]):
                cur.execute('''UPDATE users SET "status" = "{}" WHERE chat_id = {}'''.format(2, message.chat.id))
                con.commit()
            bot.send_message(message.chat.id, "Вход выполнен успешно.")
            menu(message)
            return
        else:
            bot.send_message(message.chat.id, "Неверный пароль.")
            text = "Введите пароль:\n/cancel - отмена"
            msg = bot.send_message(chat_id=message.chat.id, text=text, parse_mode = "HTML")
            bot.register_next_step_handler(msg, pass_group)
            return
    else:
        bot.send_message(message.chat.id, "Недопустимые символы.")
        text = "Введите пароль:\n/cancel - отмена"
        msg = bot.send_message(chat_id=message.chat.id, text=text, parse_mode = "HTML")
        bot.register_next_step_handler(msg, pass_group)
        return


def set_name(message):
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    pat = r'[,"\s]'
    try:
        if (re.search(pat, message.text) != None):
            bot.send_message(message.chat.id, "Неправильный формат!")
            msg = bot.send_message(message.chat.id, "Введите имя:")
            bot.register_next_step_handler(msg, set_name)
            return
        cur.execute('UPDATE users SET "name" = "{}" WHERE chat_id = {}'.format(message.text, message.chat.id))
        con.commit()
        bot.send_message(message.chat.id, "Изменено!")
        user = User(message.from_user, message.chat.id)
        sign = "Загружено"
        if (user.sign_pic == ""):
            sign = "Не загружено"
        text = '''<b>Данные</b>\nИмя: {}\nФамилия: {}\nГруппа: {}\nID Группы: {}\nПодпись: {}\n<b>Изменить:</b>'''.format(user.first_name, user.last_name, user.group_name, user.group, sign)
        keyboard = data_keyboard()
        bot.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode = "HTML")
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так. :(")
        msg = bot.send_message(message.chat.id, "Введи имя:")
        bot.register_next_step_handler(msg, set_name)
    con.close()  

def set_surname(message):
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    pat = r'[,"\s]'
    try:
        if (re.search(pat, message.text) != None):
            bot.send_message(message.chat.id, "Неправильный формат!")
            msg = bot.send_message(message.chat.id, "Введи фамилию:")
            bot.register_next_step_handler(msg, set_surname)
            return
        cur.execute('UPDATE users SET "surname" = "{}" WHERE chat_id = {}'.format(message.text, message.chat.id))
        con.commit()
        bot.send_message(message.chat.id, "Изменено!")
        user = User(message.from_user, message.chat.id)
        sign = "Загружено"
        if (user.sign_pic == ""):
            sign = "Не загружено"
        text = '''<b>Данные</b>\nИмя: {}\nФамилия: {}\nГруппа: {}\nID Группы: {}\nПодпись: {}\n<b>Изменить:</b>'''.format(user.first_name, user.last_name, user.group_name, user.group, sign)
        keyboard = data_keyboard()
        bot.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode = "HTML")
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так. :(")
        msg = bot.send_message(message.chat.id, "Введи фамилию:")
        bot.register_next_step_handler(msg, set_surname)
    con.close() 











def add_schedule(message):
    if (True or message.text == "/cancel"):
        user = User(message.from_user, message.chat.id)
        keyboard = moder_keyboard()
        bot.send_message(message.chat.id, "Отменено!")
        text = "<b>Меню старосты</b>"
        bot.send_message(message.chat.id, text = text, reply_markup = keyboard, parse_mode='HTML')
        return
    pattern = r"\d\d/\d\d/\d\d\s\d\d:\d\d\s\S.{10,1000}"
    if (re.match(pattern, message.text) == None):
        keyboard = moder_keyboard()
        text = "Ошибка!"
        bot.send_message(message.chat.id, text=text,parse_mode = "HTML")
        text = "<b>Меню старосты</b>"
        bot.send_message(message.chat.id, text=text, reply_markup=keyboard, parse_mode = "HTML")
        return
    else:
        con = sqlite3.connect(DATABASE_PATH)
        cur = con.cursor()
        user = User(message.from_user, message.chat.id)
        mark_date = message.text[0:14]
        mark_text = message.text[15:]
        print(mark_date)
        try:
            dt = datetime.datetime.strptime(mark_date, "%d/%m/%y %H:%M") 
        except:
            keyboard = moder_keyboard()
            text = "Ошибка!"
            bot.send_message(message.chat.id, text=text,parse_mode = "HTML")
            text = "<b>Меню старосты</b>"
            bot.send_message(message.chat.id, text=text, reply_markup=keyboard, parse_mode = "HTML")
            return
        print(dt)
        cur.execute('''INSERT INTO marks ("date", "text") VALUES({},"{}")'''.format(dt.timestamp(), mark_text))
        cur.execute('SELECT COUNT(id) FROM users')
        amt = cur.fetchone()[0]
        cur.execute('SELECT chat_id FROM users')
        users = cur.fetchall()
        msg = "<b>Добавлена новая заметка!</b>"
        for i in range(amt):
            if (users[i][0] != message.chat.id):
                bot.send_message(users[i][0], msg, parse_mode='HTML')
        con.commit()
        con.close()
        keyboard = moder_keyboard()
        text = "Добавлено!"
        bot.send_message(message.chat.id, text=text,parse_mode = "HTML")
        text = "<b>Меню старосты</b>"
        bot.send_message(message.chat.id, text=text, reply_markup=keyboard, parse_mode = "HTML")


def parse_schedule(message):
    return













@bot.message_handler(commands=["start"])
def start(message):
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    try:
        cur.execute('''INSERT INTO users (chat_id, first_name, last_name, username, user_id) VALUES({},"{}","{}","{}",{})'''.format(message.chat.id, message.from_user.first_name, message.from_user.last_name, message.from_user.username, message.from_user.id))
        con.commit()
        print ("New user added")
    except:
        try:
            cur.execute('''UPDATE users SET first_name = "{}", last_name = "{}", username = "{}", user_id = {} WHERE chat_id = {}'''.format(message.from_user.first_name, message.from_user.last_name, message.from_user.username, message.from_user.id, message.chat.id))
            con.commit()
            print ("User updated")
        except:
            print ("Error. start command")

    con.close()
    text = '''<b>Добро пожаловать в Group Bot!</b>\n\nОсновные команды:\n/menu - вход в меню\n/cancel - отмена текущего действия\n\nБольше информации во вкладке "О боте" в главном меню.'''
    bot.send_message(message.chat.id, text = text, parse_mode='HTML')

@bot.message_handler(commands=["reboot"])
def reboot(message):
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute('SELECT status FROM users WHERE chat_id = {}'.format(message.chat.id))
    if (cur.fetchone()[0] == 1):
        print ("Rebooted by admin")
        con.close()
        bot.send_message(message.chat.id, "Бот будет перезагружен.")
        sys.exit()
    print ("{} wanted reboot".format(message.chat.first_name))
    con.close()
    bot.send_message(message.chat.id, "Эта команда не для тебя!")



@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    text = ""



WEBHOOK_HOST = '95.165.149.16'
WEBHOOK_PORT = 8443  # 443, 80, 88 или 8443 (порт должен быть открыт!)
WEBHOOK_LISTEN = '0.0.0.0'  # На некоторых серверах придется указывать такой же IP, что и выше



WEBHOOK_SSL_CERT = 'ssl/server.crt'  # Путь к сертификату
WEBHOOK_SSL_PRIV = 'ssl/server.key'  # Путь к приватному ключу

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % ("bot")

class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
                        'content-type' in cherrypy.request.headers and \
                        cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)
			
if __name__ == '__main__':
	bot.remove_webhook()
	bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH, certificate=open(WEBHOOK_SSL_CERT, 'r'))		
	cherrypy.config.update({
    'server.socket_host': WEBHOOK_LISTEN,
    'server.socket_port': WEBHOOK_PORT,
    'server.ssl_module': 'builtin',
    'server.ssl_certificate': WEBHOOK_SSL_CERT,
    'server.ssl_private_key': WEBHOOK_SSL_PRIV
	})
	cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})
