from requests import get as req_get, post as req_post
from threading import Thread
from json import dumps as json_dumps, dump as json_dump, load as json_load
from time import sleep


class NewsBot:
    TOKEN = "2042734022:AAGG6m69NYB1P3GMr-b_LxPYwTHM0aM6wmw"
    BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"
    SUBSCRIBE_MES = "Подписаться"
    UNSUBSCRIBE_MES = "Отписаться"
    SUBSCRIBE_ANS = "Вы подписаны"
    UNSUBSCRIBE_ANS = "Вы отписаны"
    WELCOME_MESSAGE = "Добро пожаловать в новостной IT-канал"
    NOT_DETECTED_MESSAGE = "Неизвестная команда"
    SUBSCRIBE_ANS_AGAIN = "Вы уже подписаны"

    offset = 0

    # клавиатура внизу
    MAIN_KEYBOARD = {"keyboard": [[SUBSCRIBE_MES],
                                  [UNSUBSCRIBE_MES]],
                     "one_time_keyboard": False}

    states = {}
    subscribers = [523468577, 456022925]

    def __init__(self, parser):
        self.parser = parser
        Thread(target=self.check_new_articles).start()
        Thread(target=self.start_parsing).start()

    def check_new_articles(self):
        for new_articles in self.parser.update():
            for article in new_articles:
                buttons = [[{"text": "Читать полностью...", 'url': article["link"]}]]
                keyboard = json_dumps({'inline_keyboard': buttons})
                post_article = '*' + article["name"] + '*' + '\n\n' \
                               + article["link"] + '\n' \
                               + article["text"] + '\n'

                for subscriber in self.subscribers:
                    req_post(self.BASE_URL + "sendMessage",
                             data={"text": post_article,
                                   "chat_id": subscriber,
                                   'parse_mode': 'Markdown',
                                   'reply_markup': keyboard})

    def start_parsing(self):
        while True:
            self.parse_messages()
            sleep(1)

    def process_message(self, mes):
        text = mes.get("text")
        chat_id = mes["chat"]["id"]
        if text:
            state = self.states.get(chat_id, "start")

            if state == "start":
                if text == "/start":
                    req_post(self.BASE_URL + "sendMessage",
                             data={"chat_id": chat_id,
                                   "text": self.WELCOME_MESSAGE,
                                   'reply_markup': json_dumps(self.MAIN_KEYBOARD)})

                elif text == self.SUBSCRIBE_MES:
                    if chat_id in self.subscribers:
                        req_post(self.BASE_URL + "sendMessage",
                                 data={"chat_id": chat_id,
                                       "text": self.SUBSCRIBE_ANS_AGAIN})
                    else:
                        self.subscribers.append(chat_id)
                        req_post(self.BASE_URL + "sendMessage",
                                 data={"chat_id": chat_id,
                                       "text": self.SUBSCRIBE_ANS})

                elif text == self.UNSUBSCRIBE_MES:
                    self.subscribers.remove(chat_id)
                    req_post(self.BASE_URL + "sendMessage",
                             data={"chat_id": chat_id,
                                   "text": self.UNSUBSCRIBE_ANS})

                else:
                    req_post(self.BASE_URL + "sendMessage",
                             data={"chat_id": chat_id,
                                   "text": self.NOT_DETECTED_MESSAGE})

    def parse_messages(self):
        response = req_get(self.BASE_URL + "getUpdates", data={"offset": self.offset}).json()

        for update in response["result"]:
            if mes := update.get("message"):
                self.process_message(mes)

        if response["result"]:
            self.offset = response["result"][-1]['update_id'] + 1
