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
    try:
        homework_name = homework.get('homework_name')
        homework_status = homework.get('status')
        if homework_status == 'rejected':
            verdict = 'К сожалению в работе нашлись ошибки.'
        elif homework_status == 'approved':
            verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
        else:
            return 'Неизвестный статус домашки'

    except requests.exceptions.ConnectionError as e:
        logging.debug(f'Возникла проблема ConnectionError: {e}')
        send_message(f'Возникла проблема ConnectionError: {e}')
    except requests.exceptions.Timeout as e:
        logging.debug(f'Timeout Error: {e}.')
        send_message(f'Возникла проблема Timeout Error: {e}')
    except requests.exceptions.ValueError as e:
        logging.debug(f'ValueError: {e}.')
        send_message(f'Возникла проблема ValueError: {e}')
    except requests.exceptions.InvalidURL as e:
        logging.debug(f'InvalidURL: {e}.')
        send_message(f'Возникла проблема InvalidURL: {e}')
    except requests.exceptions.RequestException as e:
        logging.debug(f'Возникла проблема: {e}')
        send_message(f'Возникла проблема: {e}')

    else:
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):

    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    from_date = current_timestamp
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'

    try:
        homework_statuses = requests.get(url, headers=headers, params={
            'from_date': from_date,
        }).json()

    except requests.exceptions.ConnectionError as e:
        logging.debug(f'Возникла проблема ConnectionError: {e}')
        send_message(f'Возникла проблема ConnectionError: {e}')
    except requests.exceptions.Timeout as e:
        logging.debug(f'Timeout Error: {e}.')
        send_message(f'Возникла проблема Timeout Error: {e}')
    except requests.exceptions.ValueError as e:
        logging.debug(f'ValueError: {e}.')
        send_message(f'Возникла проблема ValueError: {e}')
    except requests.exceptions.InvalidURL as e:
        logging.debug(f'InvalidURL: {e}.')
        send_message(f'Возникла проблема InvalidURL: {e}')
    except requests.exceptions.RequestException as e:
        logging.debug(f'Возникла проблема: {e}')
        send_message(f'Возникла проблема: {e}')

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
            check_time = new_homework.get('current_date', value=0)
            if check_time is not None:
                current_timestamp = check_time
            time.sleep(300)

        except Exception as e:
            logging.debug(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
