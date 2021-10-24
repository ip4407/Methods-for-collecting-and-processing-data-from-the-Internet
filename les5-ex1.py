# Методы сбора и обработки данных из сети Интернет.

# Урок 5. Selenium в Python.
#
# Задание 1.
# Написать программу, которая собирает входящие письма из своего или тестового
# почтового ящика и сложить данные о письмах в базу данных (от кого, дата отправки, тема письма, текст письма полный)
# Логин тестового ящика: study.ai_172@mail.ru Пароль тестового ящика: NextPassword172???


import time
from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common import exceptions as se
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError as dke
from datetime import datetime


client = MongoClient('127.0.0.1', 27017)
db = client['ya_mails']
if 'newsletters' in db.list_collection_names():
    mails_collection = db.get_collection('newsletters')
else:
    mails_collection = db.create_collection('newsletters')

chrome_options = Options()

try:
    # Start the driver
    # with Chrome() as driver:
    driver = Chrome(executable_path='./chromedriver.exe', options=chrome_options)  # если необходимо, proxy=proxy, где proxy = ip:port и пр. см. док.
    # driver.maximize_window()

    # Проверка, не открыты ли другие окна.
    assert len(driver.window_handles) == 1

    # Setup wait for later
    wait = WebDriverWait(driver, 5)

    # Открываем URL
    driver.get('https://passport.yandex.ru/auth?from=mail&origin=hostroot_homer_auth_ru&retpath=https%3A%2F%2Fmail.yandex.ru%2F&backpath=https%3A%2F%2Fmail.yandex.ru%3Fnoretpath%3D1')

    # Проверка, заголовка страницы, если необходимо, пример:
    # assert 'Авторизация' in driver.title - для mail.ru
   
    elem = wait.until(EC.presence_of_element_located((By.NAME, "login")))
    elem.send_keys('******')
    elem.send_keys(Keys.ENTER)

    elem = wait.until(EC.presence_of_element_located((By.NAME, "passwd")))
    elem.send_keys('******')
    elem.send_keys(Keys.ENTER)

    elem = wait.until(EC.presence_of_element_located((By.XPATH, "//a[@title='Социальные сети']")))
    elem.click()

    counter = 0
   
    while True:

        try:
            button = wait.until(EC.visibility_of_element_located((By.XPATH, "//button[contains(@class, 'js-message-load-more')]"))).click()
            counter += 1
            print(counter)
        except se.TimeoutException:
            break
        except se.StaleElementReferenceException:
            continue
        links = driver.find_elements(By.XPATH, "//a[contains(@href, '#message/')]")

    links_list = set()
    for link in links:
        links_list.add(link.get_attribute('href'))
    
    for link in links_list:
        mails = dict()
        driver.get(link)
        time.sleep(2)
        
        mails['date_time'] = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'mail-Message-Date')]"))).text
        mails['title'] = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'mail-Message-Toolbar-Subject')]"))).text
        mails['sender_name'] = wait.until(EC.visibility_of_element_located((By.XPATH, "//span[contains(@class, 'ns-view-message-head-sender-name')]"))).text
        mails['sender_email'] = wait.until(EC.visibility_of_element_located((By.XPATH, "//span[contains(@class, 'mail-Message-Sender-Email')]"))).text
        mails['text'] = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'mail-Message-Body-Content')]"))).text
        mails['link'] = link

        try:
            mails_collection.insert_one(mails)
            mails_collection.create_index('link', unique=True)
        except dke:
            continue
                
    print(len(links_list))
    print(mails_collection.estimated_document_count())
    
finally:
    driver.quit()
