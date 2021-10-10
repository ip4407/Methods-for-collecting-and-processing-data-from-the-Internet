#!/usr/bin/env python
# coding: utf-8

# # Тема "Методы сбора и обработки данных из сети Интернет"

# ### Урок 3. Системы управления базами данных MongoDB

# ---
# ### Задание 1
# 
# 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию.
# Добавить в решение со сбором вакансий(продуктов) функцию, которая будет добавлять только новые
# вакансии/продукты в вашу базу.


import requests
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient
# from pymongo.errors import DuplicateKeyError as dke
# from pprint import pprint

position = input('Введите искомую должность: ')

# https://hh.ru/search/vacancy?area=1&fromSearchLine=true&st=searchVacancy&text=%D0%9F%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%81%D1%82+python&from=suggest_post&page=0
url = 'https://hh.ru'
params = {'area': 1,
          'fromSearchLine': 'true',
          'st': 'searchVacancy',
          'text': position,
          'page': 0
          }
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/94.0.4606.71 Safari/537.36 Edg/94.0.992.38'}

url_full = url + '/search/vacancy'


# Функция выборки мин. и макс. зарплаты из полученного тэга, если таковой есть
def salary_values(salary_soup):
    if not salary_soup:
        salary_min = None
        salary_max = None
        salary_currency = None
    else:
        salary_list = salary_soup.getText().replace(u'\u202f', u'').split()
        if salary_list[0] == 'от':
            salary_min = int(salary_list[1])
            salary_max = None
        elif salary_list[0] == 'до':
            salary_min = None
            salary_max = int(salary_list[1])
        else:
            salary_min = int(salary_list[0])
            salary_max = int(salary_list[2])
        if len(salary_list) > 3:
            salary_currency = ' '.join(salary_list[3:])
        else:
            salary_currency = salary_list[2]
    return [salary_min, salary_max, salary_currency]


# Функция добавления в БД нового документа или его обновление, если такой уже существует
def doc_to_db(doc):
    try:
        # Обновляем документ на случай, если были изменения каких-либо данных в уже существующей вакансии, если это
        # не требуется и необходимо сохранять историю изменений, то просто делаем insert_one
        vacancies.update_one({'_id': doc['_id']}, {'$set': doc}, upsert=True)
    except Exception as ex:
        print(f"Не удалось добавить либо обновить документ с _id={doc['_id']}, причина: {ex}")


# Подключение к БД hh_vacancies и коллекции vacancies
client = MongoClient('127.0.0.1', 27017)
db = client['hh_vacancies']
vacancies = db.vacancies

while True:
    response = requests.get(url_full, params=params, headers=headers)
    soup = bs(response.text, 'html.parser')
    position_list = soup.find_all('div', attrs={'class': 'vacancy-serp-item'})

    for position in position_list:
        position_data = {}

        position_info1 = position.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'})
        position_info2 = position.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-address'})
        position_info3 = position.find('div', attrs={'class': 'vacancy-serp-item__meta-info-company'})
        position_info4 = position.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})

        position_data['website'] = url
        position_data['_id'] = position_info1['href'].split('?')[0].split('/')[-1]
        position_data['title'] = position_info1.getText()
        position_data['employer'] = position_info3.getText().replace(u'\xa0', u' ')
        position_data['address'] = position_info2.getText()
        position_data['salary_min'] = salary_values(position_info4)[0]
        position_data['salary_max'] = salary_values(position_info4)[1]
        position_data['salary_currency'] = salary_values(position_info4)[2]
        position_data['link'] = position_info1['href']

        # Добавление в БД нового документа или его оновление, если такой уже существует
        doc_to_db(position_data)

        # Добавление в БД нового документа, если документ с таким же _id  уже есть, то он не добавиться
        # try:
        #     vacancies.insert_one(position_data)
        # except dke:
        #     continue

    # переход к следующей странице, если она есть
    # Поиск кнопки "дальше"
    button_next = soup.find('a', text='дальше')

    # Проверяем есть ли кнопка "дальше"
    if not button_next or not response.ok:
        print('Страницы закончились\n')
        # выходим из цикла, если кнопки "дальше" нет
        break
    else:
        # Увеличиваем номер страницы если кнопка "дальше" есть
        params['page'] += 1
        print(f"Переходим на следующую страницу {int(params['page']) + 1}")

print(f'Количество собранных вакансий: {vacancies.count_documents({})}')
