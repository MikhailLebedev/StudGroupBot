# -*- coding: utf-8 -*-

from classes import *
from config import *
from chatbot import *

import config
import telebot
import sqlite3
import telebot
import time
import datetime
import sys

def start_menu_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton(text="Создать группу", callback_data="create_group")
    button2 = telebot.types.InlineKeyboardButton(text="Войти в группу", callback_data="enter_group")
    button3 = telebot.types.InlineKeyboardButton(text="Выход", callback_data="exit")
    keyboard.add(button1)
    keyboard.add(button2)
    keyboard.add(button3)
    return keyboard

def menu_keyboard(status = 0):
    keyboard = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton(text="Оповещения >", callback_data="alert")
    button2 = telebot.types.InlineKeyboardButton(text="None", callback_data="None")
    button3 = telebot.types.InlineKeyboardButton(text="Настройки >", callback_data="settings")
    button4 = telebot.types.InlineKeyboardButton(text="Данные >", callback_data="data")
    button5 = telebot.types.InlineKeyboardButton(text="Расписание", callback_data="schedule")
    button6 = telebot.types.InlineKeyboardButton(text="О боте", callback_data="info")
    button7 = telebot.types.InlineKeyboardButton(text="Выход", callback_data="exit")
    button8 = telebot.types.InlineKeyboardButton(text="Ссылки >", callback_data="links")
    button9 = telebot.types.InlineKeyboardButton(text="Заметки", callback_data="marks")
    button10 = telebot.types.InlineKeyboardButton(text="Админ >", callback_data="admin")
    button11 = telebot.types.InlineKeyboardButton(text="Староста >", callback_data="moder")
    button12 = telebot.types.InlineKeyboardButton(text="Обр. связь", callback_data="feedback")
    button13 = telebot.types.InlineKeyboardButton(text="Участники", callback_data="members")
    keyboard.add(button1)
    keyboard.add(button3, button4)
    keyboard.add(button5, button6)
    keyboard.add(button8, button9)
    keyboard.add(button13, button12)
    if (status == 1):
        keyboard.add(button10, button11)
    elif (status == 2):
        keyboard.add(button11)
    keyboard.add(button7)
    return keyboard

def alert_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton(text="Лектор", callback_data="Лектор")
    button2 = telebot.types.InlineKeyboardButton(text="Инспектор", callback_data="Инспектор")
    button4 = telebot.types.InlineKeyboardButton(text="Перерыв", callback_data="break")
    button5 = telebot.types.InlineKeyboardButton(text="Черкануть", callback_data="sign")
    button3 = telebot.types.InlineKeyboardButton(text="Назад", callback_data="menu")
    keyboard.add(button1, button2)
    keyboard.add(button4, button5)
    keyboard.add(button3)
    return keyboard

def settings_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton(text="Проверка", callback_data="alert_subscription")
    button2 = telebot.types.InlineKeyboardButton(text="Подпись", callback_data="sign_subscription")
    button4 = telebot.types.InlineKeyboardButton(text="Перерыв", callback_data="break_subscription")
    button3 = telebot.types.InlineKeyboardButton(text="Назад", callback_data="menu")
    keyboard.add(button1, button2, button4)
    keyboard.add(button3)
    return keyboard

def data_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton(text="Имя", callback_data="name")
    button2 = telebot.types.InlineKeyboardButton(text="Фамилия", callback_data="surname")
    button3 = telebot.types.InlineKeyboardButton(text="Покинуть группу", callback_data="leave_group")
    button4 = telebot.types.InlineKeyboardButton(text="Назад", callback_data="menu")
    button5 = telebot.types.InlineKeyboardButton(text="Загрузить подпись", callback_data="sign_pic")
    button6 = telebot.types.InlineKeyboardButton(text="Показать подпись", callback_data="show_sign_pic")
    keyboard.add(button1, button2)
    keyboard.add(button5, button6)
    keyboard.add(button3)
    keyboard.add(button4)
    return keyboard

def schedule_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton(text="Назад", callback_data="menu")
    keyboard.add(button1)
    return keyboard

def info_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton(text="Назад", callback_data="menu")
    keyboard.add(button1)
    return keyboard

def marks_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup()
    button4 = telebot.types.InlineKeyboardButton(text="Назад", callback_data="menu")
    keyboard.add(button4)
    return keyboard

def links_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup()
    url1 = ""
    url2 = ""
    url3 = "https://docs.google.com/spreadsheets/d/1jPWpbivxCf3xRv-jAueWEF-XmPo1I3kLS2o6UyDBDMU/htmlview"
    url4 = "https://cmc.ejudge.ru"
    button1 = telebot.types.InlineKeyboardButton(text="Яндекс I", callback_data="yandex1", url = url1)
    button2 = telebot.types.InlineKeyboardButton(text="Яндекс II", callback_data="yandex2", url = url2)
    button3 = telebot.types.InlineKeyboardButton(text="Гугл диск", callback_data="google", url = url3)
    button5 = telebot.types.InlineKeyboardButton(text="Еджадж", callback_data="ejudje", url = url4)
    button4 = telebot.types.InlineKeyboardButton(text="Назад", callback_data="menu")
    #keyboard.add(button1, button2)
    keyboard.add(button3, button5)
    keyboard.add(button4)
    return keyboard

def showsign_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup()
    button4 = telebot.types.InlineKeyboardButton(text="Назад", callback_data="data")
    keyboard.add(button4)
    return keyboard

def admin_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton(text="Ребут", callback_data="reboot")
    button2 = telebot.types.InlineKeyboardButton(text="Сообщение", callback_data="admin_message")
    button3 = telebot.types.InlineKeyboardButton(text="Фото", callback_data="pic_analyse")
    button4 = telebot.types.InlineKeyboardButton(text="Назад", callback_data="menu")
    keyboard.add(button1)
    keyboard.add(button2)
    #keyboard.add(button3)
    keyboard.add(button4)
    return keyboard

def moder_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup()
    button5 = telebot.types.InlineKeyboardButton(text="Изменить название", callback_data="change_group_name")
    button6 = telebot.types.InlineKeyboardButton(text="Изменить пароль", callback_data="change_group_pass")
    button1 = telebot.types.InlineKeyboardButton(text="Загрузить расписание", callback_data="add_schedule")
    button2 = telebot.types.InlineKeyboardButton(text="Добавить заметку", callback_data="add_mark")
    button3 = telebot.types.InlineKeyboardButton(text="Удалить заметку", callback_data="remove_mark")
    button4 = telebot.types.InlineKeyboardButton(text="Назад", callback_data="menu")
    keyboard.add(button5)
    keyboard.add(button6)
    keyboard.add(button1)
    keyboard.add(button2)
    keyboard.add(button3)
    keyboard.add(button4)
    return keyboard

def signok_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton(text="Я отметил!", callback_data="OK")
    keyboard.add(button1)
    return keyboard
    
def group_confirm():
    keyboard = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton(text="Да", callback_data="group_yes")
    button2 = telebot.types.InlineKeyboardButton(text="Нет", callback_data="group_no")
    keyboard.add(button1, button2)
    return keyboard
    
def members_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton(text="Назад", callback_data="menu")
    keyboard.add(button1)
    return keyboard