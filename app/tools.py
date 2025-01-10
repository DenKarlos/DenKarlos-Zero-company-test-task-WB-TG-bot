import requests
import json
from datetime import datetime

def is_shop(api_key: str):
    r = requests.get('https://common-api.wildberries.ru/ping', headers={'Authorization': api_key})
    if r.status_code == 200:
        return True
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


def response_to_report(response: dict, date_from: str, date_to: str):
    s = sum([product['retail_amount'] for product in response])
    date_to = date_to.replace('T', ' ')
    return f'Общая сумма продаж за период c {date_from} по {date_to}: {s:.2f} рублей'
    
    
def get_report(api_key: str, date_from: str, date_to: str):
    response = requests.get('https://statistics-api.wildberries.ru/api/v5/supplier/reportDetailByPeriod',
    params={'dateFrom': date_from, 'dateTo': date_to},
    headers={'Authorization': api_key})
    response = response.json()
    with open('report.json','w', encoding='utf-8') as f:
        json.dump(response, f, indent=3, ensure_ascii=False)
    return response_to_report(response, date_from, date_to)


def get_api_by_shop_name(shops: list, shop_name: str):
    api_key = ''
    for shop in shops:
        if shop['shop_name'] == shop_name:
            api_key = shop["authorization_key"]
            break
    return api_key

def validate_date(str_date: str):
    try:
       return  datetime.strptime(str_date, '%d-%m-%Y').date()
    except Exception as ex:
        print(repr(ex))
        return False