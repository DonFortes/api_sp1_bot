import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

logging.basicConfig(
    filename="test.log",
    level=logging.DEBUG,
    format='%(asctime)s:%(levelname)s:%(message)s'
    )

load_dotenv()


PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def parse_homework_status(homework):

    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')

    if homework_name is None or homework_status is None:
        return "Ошибка ответа от Практикума"

    if homework_status == "rejected":
        verdict = "К сожалению в работе нашлись ошибки."
    elif homework_status == 'approved':
        verdict = ("Ревьюеру всё понравилось, можно "
                   "приступать к следующему уроку.")
    else:
        return 'Неизвестный статус домашки'

    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):

    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    from_date = current_timestamp
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'

    try:
        homework_statuses = requests.get(url, headers=headers, params={
            'from_date': from_date,
        }).json()

    except requests.exceptions.RequestException as e:
        logging.debug(f'Возникла проблема: {e}')
        return {}

    else:
        return homework_statuses


bot = telegram.Bot(token=TELEGRAM_TOKEN)


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(new_homework.get
                                                   ('homeworks')[0]))
            current_timestamp = new_homework.get('current_date', 0)
            time.sleep(20*60)

        except Exception as e:
            logging.debug(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
