from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pickle
import os
from django.conf import settings


class Article:
    """Common base class for all articles/pages"""

    def __init__(self, url, title, time, description):  # originalurl 제외, description 추가
        #time = datetime.strptime(time, '%a, %d %b %Y %H:%M:%S %z')  # Thu, 16 Apr 2020 15:38:00 +0900
        #time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.source = None
        self.url = url
        self.title = title
        self.time = time
        self.description = description
        self.press_name()   # source 값 업데이트

    def print(self):
        print('신문사: {}'.format(self.source))
        print('URL: {}'.format(self.url))
        print('TITLE: {}'.format(self.title))
        print('발행시간: {}'.format(self.time))
        print('프리뷰: {}'.format(self.description))

    def press_name(self):
        """
        link를 가지고 언론사를 크롤링 한다.
        주의 : url 은 original link가 아닌 그냥 link로 주어야 함
        :return:
        """
        __url__ = self.url
        # TODO: csv 파일로 연결 예정
        with open(os.path.join(settings.BASE_DIR, 'scripts/static/dict.pickle'), 'rb') as handle:
            dic = pickle.load(handle)

        # 네이버 주요 언론사
        if __url__.startswith("https://news.naver.com"):  # url 이 news.naver.com으로 안나오는 경우를 위하여
            raw = requests.get(__url__, headers={'User-Agent': 'Mozilla/5.0'}).text
            html = BeautifulSoup(raw, 'html.parser')
            content = str(html.select('#main_content > div.article_header > div.press_logo > a > img'))
            # print(content)

            # 문자열 슬라이싱
            start = int(content.find("title=", 1)) + 7
            finish = int(content.find("/>")) - 1
            title = content[start:finish]

        else:  # 그 외
            start = int(__url__.find("://")) + 3
            title = __url__[start:]
            finish = int(title.find("/"))
            title = title[0:finish]
            #print(dic.get(title, '언론사'))  # dictionary에 없는 url이 들어올 시 '언론사'라는 default 이름
            title = dic.get(title, '언론사')

        self.source = title
