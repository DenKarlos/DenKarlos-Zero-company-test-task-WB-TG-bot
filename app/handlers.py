from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

import app.keyboard as kb
from app.tools import *
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from datetime import datetime, date, timedelta

router = Router()
            
class Form(StatesGroup):
    api_key = State()
    shop_name = State()
    
class Delete_Form(StatesGroup):
    shop_name = State()
    confirm = State()
    
class Period(StatesGroup):
    date_from = State()
    date_to = State()



@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Привет!\nДанный Telegram-бот предназначен для аналитики продаж на Wildberries\n\
/help - узнать о доступных командах',)
    # await kb.inline_shops()

@router.message(Command('shops'))
async def shops_help(message: Message,  state: FSMContext):
    shops = get_user_shops(str(message.from_user.id))
    if shops:
        await state.update_data(user_shops=shops)
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
async def report(message: Message):
    await message.answer('Нажми на кнопку магазина и появится отчёт.\n/shops - список магазинов')
    
@router.message(Command('help'))
async def get_help(message: Message):
    help = '\n'.join(['/addshop - добавление магазина',
                     '/delshop - удаление магазина',
                     '/shops - список магазинов',
                     '/report - получение отчета о продажах'])
    await message.answer(help)
    
    
@router.message(Form.api_key,)
async def get_shop_name(message: Message, state: FSMContext):
    # shops = get_user_shops(str(message.from_user.id))
    if is_shop(message.text):
        await state.update_data(api_key = message.text)
        await message.answer('Введите название магазина')
        await state.set_state(Form.shop_name)
    else:
        await state.clear()
        await message.answer('Невозможно добавить магазин')
    
@router.message(Form.shop_name)
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
    

@router.message(Delete_Form.shop_name)
async def del_new_shop(message: Message, state: FSMContext):
    shops = [shop['shop_name'] for shop in get_user_shops(str(message.from_user.id))]
    if message.text in shops:
        await message.reply('Точно хотите удалить:', reply_markup=await kb.answer_kb())   
        await state.update_data(shop_name = message.text)
        await state.set_state(Delete_Form.confirm)   
    else:
        await state.clear()
        await message.answer('Название такого магазина не обнаружено у пользователя')
        
@router.message(Delete_Form.confirm)
async def delete_shop(message: Message, state: FSMContext):
    if message.text == "Да":
        data = await state.get_data()
        del_shop(str(message.from_user.id), data['shop_name'])
        await message.answer("Магазин удалён", reply_markup=ReplyKeyboardRemove())
        await state.clear()
    else:
        await message.answer('Магазин не удален!', reply_markup=ReplyKeyboardRemove())
        await state.clear()
        
@router.callback_query(F.data.startswith('shop'))
async def shop_report(call: CallbackQuery, state: FSMContext):
    try:
        await call.answer('')
        shop_name = call.data.replace('shop_', '')
        context = await state.get_data()
        api_key = get_api_by_shop_name(context['user_shops'], shop_name)
        if api_key:
            await state.update_data(api_key=api_key, shop_name=shop_name)
            await call.message.answer(f'Выберите период отчёта для магазина "{shop_name}":', reply_markup= await kb.report_time())
            context = await state.get_data()
            print(context['shop_name'])
        else:
            await call.message.answer('Обновите список магазинов: /shops')
    except Exception as ex:
        print(repr(ex))
        await call.message.answer('Обновите список магазинов: /shops')
        
    
@router.callback_query(F.data.startswith('rt_'))
async def shop_report(call: CallbackQuery, state: FSMContext):
    try:
        await call.answer('')
        report_time = call.data.replace('rt_', '')
        today = date.today()
        context = await state.get_data()
        api_key = context['api_key']
        
        if report_time == 'today':
            await call.message.answer(get_report(api_key, str(today), datetime.now().strftime('%Y-%m-%dT%H:%M:%S')))
        elif report_time == 'yesterday':
            await call.message.answer(get_report(api_key, str(today-timedelta(days=1)), str(date.today())))
        elif report_time == 'last_7_days':
            await call.message.answer(get_report(api_key, str(today-timedelta(days=7)), str(date.today())))
        elif report_time == 'period':
            await call.message.answer('Введите с какого числа (ДД-ММ-ГГГГ):')
            await state.set_state(Period.date_from)
    except Exception as ex:
        print(repr(ex))
        await call.message.answer('Выберите для какого магазина из списка будет осуществляться отчёт: /shops')
        
@router.message(F.text, Period.date_from)
async def period_date_from(message: Message, state: FSMContext):
    try:
        date_from = validate_date(message.text)
        if date_from:
            await state.update_data(date_from=date_from)
            await message.answer(f'Введённая дата: {str(date_from)}')
            await message.answer('по какое число (ДД-ММ-ГГГГ):')
            await state.set_state(Period.date_to)
        else:
            await message.answer('Неправильный формат даты.\nПопробуйте ввести дату заново (ДД-ММ-ГГГГ):')
            await state.set_state(Period.date_from)
    except Exception as ex:
        print(repr(ex))
        await message.answer('Что-то пошло не так!:')   
        
@router.message(F.text, Period.date_to)
async def period_date_to(message: Message, state: FSMContext):
    try:
        date_to = validate_date(message.text)
        if date_to:
            await state.update_data(date_to=date_to)
            context = await state.get_data()
            print(context, '- состояние контекста')
            if context['date_from'] > context['date_to']:
                context['date_from'], context['date_to'] = context['date_to'], context['date_from']
            await state.clear()            
            await message.answer(get_report(context['api_key'], str(context['date_from']), str(context['date_to'])))           
        else:
            await state.update_data(date_to=date_to)
            await message.answer('Неправильный формат даты.\nПопробуйте ввести дату заново (ДД-ММ-ГГГГ):')
            await state.set_state(Period.date_to)
    except Exception as ex:
        print(repr(ex))
        await message.answer('Что-то пошло не так!:')