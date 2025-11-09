import os
import time
import configparser

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
USER_DATA_DIR = config['DEFAULT']['UserDataDir']
if '\\' not in USER_DATA_DIR:
    raise 'Не указан путь к папке хрома в файле config.ini'

MAX_ID = int(config['DEFAULT']['MaxID'])
first_id = 1



def start_browser():
    options = uc.ChromeOptions()

    options.add_argument(f"--user-data-dir={USER_DATA_DIR}")

    options.add_argument(f'--disable-gpu')  # Отключает использование GPU (иногда ускоряет headless)
    options.add_argument(f'--window-size=1920,1080')  # Фиксированный размер окна, важно для корректного рендеринга

    # ===== Отключение расширений и лишнего UI =====
    options.add_argument(f'--disable-extensions')  # Отключение всех расширений Chrome
    options.add_argument(f'--disable-translate')  # Отключение встроенного перевода
    options.add_argument(f'--disable-notifications')  # Отключение веб-уведомлений
    options.add_argument(f'--disable-popup-blocking')  # Отключение блокировки всплывающих окон
    options.add_argument(f'--mute-audio')  # Отключение звука
    options.add_argument(f'--no-first-run')  # Пропустить мастер первого запуска
    options.add_argument(f'--disable-infobars')  # Убирает баннер "Chrome is being controlled by automated software"

    # ===== Отключение фоновой активности =====
    options.add_argument(
        f'--disable-background-networking')  # Отключение фоновой сетевой активности (обновления, сервисы)
    options.add_argument(f'--disable-component-update')  # Не обновлять встроенные компоненты
    options.add_argument(f'--disable-sync')  # Отключение синхронизации с Google
    options.add_argument(
        f'--disable-background-timer-throttling')  # Таймеры на фоновых вкладках работают без замедлений
    options.add_argument(f'--disable-renderer-backgrounding')  # Фоновые вкладки не теряют приоритет процессора

    # ===== Отключение анимаций и упрощение рендеринга =====
    options.add_argument(f'--disable-threaded-animation')  # Отключение анимаций браузера
    options.add_argument(f'--disable-threaded-scrolling')  # Отключение параллельной прокрутки
    options.add_argument(f'--disable-partial-raster')  # Упрощает отрисовку
    options.add_argument(f'--disable-features=PaintHolding')  # Не откладывать коммиты отрисовки
    options.add_argument(f'--in-process-gpu')  # Использование GPU в процессе браузера, экономия памяти

    options.add_argument(f'--deterministic-mode')

    return uc.Chrome(options=options)


def restart_browser(browser_restart):
        time.sleep(5)
        browser_restart.quit()
        time.sleep(5)
        browser_restart = start_browser()
        browser_restart.get(f'https://teslacraft.org/members/name.{1}/card')
        time.sleep(10)
        return browser_restart


if os.path.exists('first_id.txt'):
    with open('first_id.txt', 'r', encoding='utf-8') as file:
        first_id = file.read()
else:
    print('Не найден файл "first_id.txt", создаём...')
    with open('first_id.txt', 'w', encoding='utf-8') as file:
        file.write(str(first_id))
    print(f'Файл создан, значение в нём — {first_id}')


print('Первый старт браузера для прохождения капчи')
browser = start_browser()
browser.get(f'https://teslacraft.org/members/name.{1}/card')
time.sleep(10)

if not os.path.exists('users.txt'):
    with open('users.txt', 'w', encoding='utf-8'):
        pass

for i in range(int(first_id), MAX_ID + 1):
    start_time = time.time()
    if i % 2000 == 0:
        browser = restart_browser(browser)
    try:
        browser.get(f'https://teslacraft.org/members/name.{i}/card')
        ratings = int(
            browser.find_element(By.CSS_SELECTOR, 'span[style="color:#6fca13"]').text.replace('+', '').replace(' ', ''))
        name = browser.find_element(By.CLASS_NAME, 'username').text

        print(name, ratings)

        with open('first_id.txt', 'w', encoding='utf-8') as file:
            file.write(f'{i}')

        if ratings >= 100:
            with open('users.txt', 'a', encoding='utf-8') as file:
                file.write(f'{name} {ratings}\n')
            print('Игрок и значение рейтингов записаны в файл users.txt')

        print("--- %s seconds ---" % (time.time() - start_time))
    except Exception as e:
        print('Ошибка:', e)
        print("--- %s seconds ---" % (time.time() - start_time))

browser.quit()

ratings_dict = {}
with open('users.txt', 'r', encoding='utf-8') as file:
    while line := file.readline():
        line = line.split()
        ratings_dict[line[0]] = int(line[1])

with open('users_sort.txt', 'w', encoding='utf-8'):
    pass

ratings_dict = {k: v for k, v in sorted(ratings_dict.items(), key=lambda item: item[1], reverse=True)}

number = 0
for i in ratings_dict.items():
    number += 1
    print(f'{number}. {i[0]}: {i[1]}')
    with open('users_sort.txt', 'a', encoding='utf-8') as file:
        file.write(f'{number}. {i[0]}: {i[1]}\n')
print('Топ по рейтингам (отсортированные данные) записан в файл users_sort.txt')