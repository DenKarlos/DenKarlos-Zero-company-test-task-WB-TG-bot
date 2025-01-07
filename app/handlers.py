from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

import app.keyboard as kb
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import requests
import json

router = Router()

def is_shop(api_key: str):
    r = requests.get('https://common-api.wildberries.ru/ping', headers={'Authorization': api_key})
    if r.status_code == 200:
        return True
        # print('Добавляем магазин')
    return False
    # elif r.status_code == 401:
    #     print('Невозможно найти такой магазин')
    # elif r.status_code == 429:
    #     print('Сервер перегружен! Попробуйте зарегистрировать магазин немного позже')

def add_shop(user_id: str, shop_name: str, api_shop: str):
    filename = 'config.json'
    with open(filename, 'r', encoding='utf-8') as f:
        users = json.load(f)
    users[user_id].append({"shop_name": shop_name, "authorization_key": api_shop} )
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=3, ensure_ascii=False)
        
def del_shop(user_id: str, shop_name: str):
    filename = 'config.json'
    with open(filename, 'r', encoding='utf-8') as f:
        users = json.load(f)
    shops = users[user_id]
    shops = list(filter(lambda s: s["shop_name"] != shop_name, shops))
    users[user_id] = shops
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=3, ensure_ascii=False)

def get_user_shops(user_id: str):
    filename = 'config.json'
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            users = json.load(f)
        if user_id in list(users):
            return users[user_id]
        else:
            users[user_id] = []
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(users, f, indent=3, ensure_ascii=False)
            return users[user_id]
                        
    except FileNotFoundError or json.JSONDecodeError:
        with open(filename, 'w', encoding='utf-8') as f:
            users = dict()
            users[user_id] = []
            json.dump(users, f, indent=3, ensure_ascii=False)
        return users[user_id]
            
class Form(StatesGroup):
    api_key = State()
    shop_name = State()
    
class Delete_Form(StatesGroup):
    shop_name = State()
    confirm = State()



@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Привет!\nДанный Telegram-бот предназначен для аналитики продаж на Wildberries\n\
/help - узнать о доступных командах',)
    # await kb.inline_shops()

@router.message(Command('shops'))
async def shops_help(message: Message):
    shops = get_user_shops(str(message.from_user.id))
    if shops:
        await message.reply('Список доступных магазинов:', reply_markup=await kb.inline_shops(shops))
    else:
        await message.reply('У Вас ещё нет добавленных магазинов\n/addshop - добавление магазина')
        
@router.message(Command('addshop'))
async def shops_help(message: Message, state: FSMContext):
    await message.answer('Введите API key магазина')
    await state.set_state(Form.api_key)
    # if message.text
    
        
@router.message(Command('delshop'))
async def shops_help(message: Message, state: FSMContext):
    await message.answer('Имя магазина, который хотите удалить:')
    await state.set_state(Delete_Form.shop_name)
    

@router.message(Command('report'))
async def get_report(message: Message):
    await message.answer(help)
    
@router.message(Command('help'))
async def get_help(message: Message):
    help = '\n'.join(['/addshop - добавление магазина',
                     '/delshop - удаление магазина',
                     '/shops - список магазинов',
                     '/report - получение отчета о продажах'])
    await message.answer(help)
    
    
@router.message(F.text, Form.api_key)
async def get_shop_name(message: Message, state: FSMContext):
    # shops = get_user_shops(str(message.from_user.id))
    if is_shop(message.text):
        await state.update_data(api_key = message.text)
        await message.answer('Введите название магазина')
        await state.set_state(Form.shop_name)
    else:
        await state.clear()
        await message.answer('Невозможно добавить магазин')
    
@router.message(F.text, Form.shop_name)
async def set_new_shop(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(shop_name = message.text)
        data = await state.get_data()
        add_shop(str(message.from_user.id), data['shop_name'], data['api_key'])
        await message.answer("Магазин добавлен")
        await state.clear()
    else:
        await state.clear()
        await message.answer('Магазин должен как-то называться!')
    

@router.message(F.text, Delete_Form.shop_name)
async def del_new_shop(message: Message, state: FSMContext):
    shops = [shop['shop_name'] for shop in get_user_shops(str(message.from_user.id))]
    if message.text in shops:
        await message.reply('Точно хотите удалить:', reply_markup=await kb.answer_kb())   
        await state.update_data(shop_name = message.text)
        await state.set_state(Delete_Form.confirm)   
    else:
        await state.clear()
        await message.answer('Название такого магазина не обнаружено у пользователя')
        
@router.message(F.text, Delete_Form.confirm)
async def delete_shop(message: Message, state: FSMContext):
    if message.text and message.text == "Да":
        data = await state.get_data()
        del_shop(str(message.from_user.id), data['shop_name'])
        await message.answer("Магазин удалён", reply_markup=ReplyKeyboardRemove())
        await state.clear()
    else:
        await state.clear()
        await message.answer('Магазин не удален!', reply_markup=ReplyKeyboardRemove())
        
@router.callback_query(F.data.startswith('shop'))
async def shop_report(call: CallbackQuery):
    shop_name = call.data.replace('shop_', '')
    user_shops = get_user_shops(str(call.from_user.id))
    shop = list(filter(lambda s: s["shop_name"]==shop_name, user_shops))[0]
    response = requests.get('https://statistics-api.wildberries.ru/api/v5/supplier/reportDetailByPeriod', params={'dateFrom':'2024-01-01', 'dateTo':'2025-01-01'}, headers={'Authorization': shop["authorization_key"]})
    
    with open('report.json','w', encoding='utf-8') as f:
        json.dump(response.json(), f, indent=3, ensure_ascii=False)
    s = sum([product['retail_amount'] for product in response.json()])
    await call.message.answer(f'Общая сумма продаж за прошедший год: {s:.2f}')
    
    
    
    

