import scrapy
import time
import datetime
import re
from scrapy.utils.project import get_project_settings
from jeryspider.jeryspider.items import Article  # 직접 정의한 Article 객체 사용; 빨간줄 나도 괜찮!
from scrapy.crawler import CrawlerProcess

"""
<NONO!! 소용없음 >
설정 :터미널에서 실행 시 터미널에 입력할 것
at JERYs-WORD directory
>>python3 -m wikiSpider.wikiSpider.spiders.article_url_spider

<scrapy 실행시키고 json에 저장할 때 명령어>
 : 2가지 방법
>>scrapy runspider article_url_spider.py  # 이 파일 경로에서 실행 필수
>>scrapy crawl jery   # 이 프로젝트 안에서만 하면 된다.
"""


class ArticleUrlSpider(scrapy.Spider) :
    name = "jery"
    allowed_domains = ['yna.co.kr']

    start_urls = []  # 크롤링할 페이지 목록

    def __init__(self) :
        """
        url 초기화 설정
        'https://www.yna.co.kr/economy/all',  # 경제
            'https://www.yna.co.kr/politics/all',  # 정치
            'https://www.yna.co.kr/industry/all',  # 산업
            'https://www.yna.co.kr/society/all',  # 사회
            'https://www.yna.co.kr/local/all',  # 전국
            'https://www.yna.co.kr/international/all',  # 세계
            'https://www.yna.co.kr/culture/all',  # 문화
            'https://www.yna.co.kr/nk/news/all'  # 북한
        """
        urls = [
            'https://www.yna.co.kr/economy/all',  # 경제
            'https://www.yna.co.kr/politics/all',  # 정치
            'https://www.yna.co.kr/industry/all',  # 산업
            'https://www.yna.co.kr/society/all',  # 사회
            'https://www.yna.co.kr/local/all',  # 전국
            'https://www.yna.co.kr/international/all',  # 세계
            'https://www.yna.co.kr/culture/all',  # 문화
            'https://www.yna.co.kr/nk/news/all',  # 북한
            'https://www.yna.co.kr/lifestyle/all',  # 라이프
            'https://www.yna.co.kr/sports/all'  # 스포츠
            # 연예 제외
        ]
        for url in urls :
            for i in range(20) :  # ex. 경제 기사 목록 1~10페이지 링크를 추가해준다.
                if i == 1 :
                    self.start_urls.append(url)
                elif url == 'https://www.yna.co.kr/nk/news/all': # 북한용
                    self.start_urls.append(url + '?page=' + str(i))
                else :
                    self.start_urls.append(url + '/' + str(i))

    def parse(self, response) :
        """
        각 기사 목록 페이지에서 이미지 있는 기사 링크 크롤링
        yield는 generator다 아이템이 생성될때마다 리스트형태로 쌓이게 된다.
        return과 다른 점은 모든 작업이 완료될 때까지 기다리지 않고 다음 작업을 수행한다.
        :param response:
        :return:
        """
        url = response.url
        if re.search(r'/nk/news/all', url):
            div = response.css('.mid-col-wrap')
            link = div.css('.news-con figure a')
            yield from response.follow_all(link, self.parse_nk)
        else :
            div = response.css('.section01')
            link = div.css('.item-box01 figure a')
            time.sleep(5)  # 5초 휴식
            yield from response.follow_all(link, self.parse_article)

    @staticmethod
    def parse_article(response) :
        """
        기사 내부 제목, 본문 크롤링
        :param response:
        :return: Article
        """
        url = response.url
        title = response.css('h1.tit::text').get()
        text = response.xpath('//div[@class="story-news article"]/p//text()').extract()

        article = Article()
        article['url'] = url
        article['title'] = title
        article['text'] = text
        return article  # yield는 generator다 아이템이 생성될때마다 리스트형태로 쌓이게 된다.

    @staticmethod
    def parse_nk(response):
        """
        북한 기사 페이지용 크롤링
        :param response:
        :return: Article
        """
        print('북한 뉴스 크롤러\n')
        url = response.url
        title = response.css('h1.tit-article::text').get()
        text = response.xpath('//div[@class="article"]/p//text()').extract()
        article = Article()
        article['url'] = url
        article['title'] = title
        article['text'] = text
        return article  # yield는 generator다 아이템이 생성될때마다 리스트형태로 쌓이게 된다.


def run() :
    s = get_project_settings()
    s['FEED_FORMAT'] = 'jsonlines'
    s['FEED_URI'] = 'output_' + datetime.datetime.today().strftime('%y%m%d') + '.json'
    s['FEED_EXPORT_ENCODING'] = 'utf8'
    s['LOG_FILE'] = 'log.log'
    s['LOG_LEVEL'] = 'INFO'
    process = CrawlerProcess(s)
    process.crawl(ArticleUrlSpider)
    process.start()
