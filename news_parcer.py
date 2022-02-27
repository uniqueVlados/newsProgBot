from requests import get as req_get
from time import sleep


class NewsParser:
    last_article = None
    RESOURCE_URL = "https://tproger.ru/"

    def get_update(self):
        response = req_get(self.RESOURCE_URL)
        raw_articles = response.text.split('class="article__main"')
        return raw_articles

    @staticmethod
    def _parse_element(raw_text, start_text, end_text, last_index=0):
        start = raw_text.find(start_text, last_index) + len(start_text)
        end = raw_text.find(end_text, start + 1)
        element = raw_text[start:end]
        return element, end

    def _get_article(self, raw_article):
        link_start_text = 'href="'
        link_end_text = '" class="article__link">'
        link, last_index = self._parse_element(raw_article, link_start_text, link_end_text)

        header_start_text = '" class="article__link">'
        header_end_text = '</a'
        header, last_index = self._parse_element(raw_article, header_start_text, header_end_text, last_index)

        text_start = 'class="article__excerpt article__excerpt--icon">'
        text_end = '</p>'
        text, last_index = self._parse_element(raw_article, text_start, text_end, last_index)

        article = {"name": header, "link": link, "text": text}
        return article

    def parse_news(self):
        raw_articles = self.get_update()
        articles = []
        for raw_article in raw_articles[1:]:
            articles.append(self._get_article(raw_article))

        return articles

    def one_update(self):
        new_articles = self.parse_news()
        if not new_articles or new_articles[-1] == self.last_article:
            return []

        index = -1
        if self.last_article in new_articles:
            index = new_articles.index(self.last_article)

        self.last_article = new_articles[index]

        return new_articles[index + 1:][::-1]

    def update(self):
        while True:
            new_articles = self.one_update()

            if new_articles:
                yield new_articles
            sleep(600)
