
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import (InlineKeyboardButton,  InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)

# settings = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='8-ой мкр', url='https://www.wildberries.ru')]])

async def report_time():
    report_time = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Сегогдня', callback_data=f'rt_today')],
        [InlineKeyboardButton(text='Вчера', callback_data=f'rt_yesterday')],
        [InlineKeyboardButton(text='Последние 7 дней', callback_data=f'rt_last_7_days')],
        [InlineKeyboardButton(text='Произвольный период', callback_data=f'rt_period')]
    ])
    return report_time
    

async def inline_shops(shops: list):
    keyboard = InlineKeyboardBuilder()
    for shop in shops:
        keyboard.add(InlineKeyboardButton(text=shop['shop_name'], callback_data=f"shop_{shop['shop_name']}"))
    return keyboard.adjust(2).as_markup()

async def answer_kb():
    kb_list = [
        [KeyboardButton(text="Да"), KeyboardButton(text="Нет") ]
    ]

    keyboard = ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True)
    return keyboard
    
