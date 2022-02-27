from news_parcer import NewsParser
from news_bot import NewsBot

if __name__ == "__main__":
    parser = NewsParser()
    tg_bot = NewsBot(parser)
    print("Запущен!")
