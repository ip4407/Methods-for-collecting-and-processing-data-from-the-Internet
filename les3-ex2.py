#!/usr/bin/env python
# coding: utf-8

# # Тема "Методы сбора и обработки данных из сети Интернет"

# ### Урок 3. Системы управления базами данных MongoDB

# ---
# ### Задание 2
#
# 2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы
# (необходимо анализировать оба поля зарплаты - минимальнную и максимульную).
# Для тех, кто выполнил задание с Росконтролем - напишите запрос для поиска продуктов с рейтингом не ниже введенного
# или качеством не ниже введенного (то есть цифра вводится одна, а запрос проверяет оба поля)


from pymongo import MongoClient

dollar_rub = 71.9882
euro_rub = 83.1248

# Подключение к БД hh_vacancies и коллекции vacancies
client = MongoClient('127.0.0.1', 27017)
db = client['hh_vacancies']
vacancies = db.vacancies


def jobs_by_salary(user_salary_min, usd_rub, eur_rub):
    for doc in vacancies.find(
            {'$or':
                [
                    {'salary_currency': 'руб.',
                     '$or':
                         [
                             {'salary_min': {'$gt': user_salary_min}},
                             {'salary_max': {'$gt': user_salary_min}}
                         ]
                     },
                    {'salary_currency': 'USD',
                     '$or':
                         [
                             {'salary_min': {'$gt': user_salary_min / usd_rub}},
                             {'salary_max': {'$gt': user_salary_min / usd_rub}}
                         ]
                     },
                    {'salary_currency': 'EUR',
                     '$or':
                         [
                             {'salary_min': {'$gt': user_salary_min / eur_rub}},
                             {'salary_max': {'$gt': user_salary_min / eur_rub}}
                         ]
                     }
                ]
            }
    ):
        print(f'{doc["title"]}\nЗарплата {"от " + str(doc["salary_min"]) if doc["salary_min"] is not None else ""} '
              f'{"до " + str(doc["salary_max"]) if doc["salary_max"] is not None else ""} {doc["salary_currency"]}\n'
              f'Место работы: {doc["address"]}\n'
              f'Ссылка на вакансию:\n{doc["link"]}\n')


user_input = int(input('Введите минимальную сумму желаемой заработной платы в рублях: '))

jobs_by_salary(user_input, dollar_rub, euro_rub)
