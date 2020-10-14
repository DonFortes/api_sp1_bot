import os
import requests
import telegram
import time
from dotenv import load_dotenv

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
        else:
            verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    except Exception as e:
        print(f'Возникла проблема: {e}')
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
    except Exception as e:
        print(f'Возникла проблема: {e}')
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
            check_time = new_homework.get('current_date')
            if check_time is not None:
                current_timestamp = check_time
            time.sleep(300)

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
