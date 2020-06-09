"""
manage.py 경로에서 실행
>>python manage.py runscript news

parameter가 있을 경우
ex) run(*args):
python manage.py runscript news --script-args <값>
"""
import datetime
import json
import os
import time
import re
import sys
import urllib.request
from urllib.parse import urlparse
from typing import List

import gensim
import pandas as pd
from django.conf import settings
from gensim.models import KeyedVectors
from konlpy.tag import Okt
from news.models import Topic, SimTopic  # 빨간줄이지만 잘 실행됨.
from news.models import Article, WordCloud, WCArticle  # 빨간줄이지만 잘 실행됨.

from scripts.article import Article as art  # jerysite.scripts
from scripts.wordcloud import Wordcloud as main_wc
from scripts.crawler import Crawler


class Search :
    """
    검색 기능; NAVER API 사용
    속성 : topic, wv(word_vector)
    """

    def __init__(self, topic_id) :
        self.tmp_titles = []  # 기사 중복 막기 위해 제목 저장
        self.articles = []
        model = gensim.models.Word2Vec.load(os.path.join(settings.BASE_DIR, 'scripts/static/model_updated.model'))
        self.wv = model.wv
        del model
        print(topic_id)
        print(topic_id[0])
        self.topic_id = int(topic_id[0])
        # model 연결 - topic으로 불러오기  simword1
        self.model_topic = Topic.objects.filter(id=self.topic_id).first()  #
        self.topic = self.model_topic.topic
        self.model_wc1 = WordCloud.objects.create(topic=self.model_topic, period=1)
        self.model_wc2 = WordCloud.objects.create(topic=self.model_topic, period=2)
        self.model_wc3 = WordCloud.objects.create(topic=self.model_topic, period=3)

    @staticmethod
    def set_request(topic, period, again=0) :
        """
        set url. 복수의 토픽을 '+'으로 묶어줌.
        :param topic: 리스트 형태의 토픽; 복수 가능
        :param period:
        :param again=0: 원하는 양의 기사가 추출되지 않았을 때 start를 다르게 해서 시도하기 위함.
        :return:
        """
        if again % 2 :
            sort = 'sim'
        else :
            sort = 'date'
        start = (330 * (period - 1) + 1) + (100 * again) if period else 1  # 기한 시작 위치 설정
        if start < 0 :
            start = 1
        elif start > 999 :
            start = 900
        topic_text = urllib.parse.quote('+'.join([str(t) for t in topic]))  # 한글 텍스트 인코딩
        num = 100 if period != 1 else 10  # 4~6일전, 7~9일전일 때 100개 뽑음.
        url = ('https://openapi.naver.com/v1/search/news.json?query='
               + topic_text +  # 키워드
               '&start=' + str(start) +  # 기한 시작 위치
               '&display=' + str(num)  # 100개(최대) 기사 추출
               + '&sort=' + sort  # 정렬 기준 : 유사도(sim) / 날짜(date)- default
               )
        print(url)
        """set request using url"""
        client_id = "waVUZElBGQAO9PS_ECpn"  # 개발자센터에서 발급받은 Client ID 값
        client_secret = "eG1ROqWCAo"  # 개발자센터에서 발급받은 Client Secret 값
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", client_id)
        request.add_header("X-Naver-Client-Secret", client_secret)
        return request

    def get_articles_original(self, response) :
        """
        [for WordCloud]
        네이버 api 이용 기사 list 받아옴.
        content 객체에 저장
        :param response: api 호출 후 받은 response
        - period ==0 이며 10개 기사(0~9일)
        :return:
        """
        articles = response['items']
        print('number of articles : ' + str(len(articles)))

        # 뽑을 날짜 설정
        KST = datetime.timezone(datetime.timedelta(hours=9))
        today = datetime.datetime.now(tz=KST).date()
        start = today + datetime.timedelta(-9)
        end = today
        print('{} ~ {}'.format(start, end))

        cnt = 0
        art_list = []
        for article in articles :  # article :  source, url, title, time, description
            if cnt == 10 :  # 최대 10개만 저장.
                break
            title = self.preprocess(article["title"], slice=True)
            if title in self.tmp_titles :  # 중복검사- 이미 있으면 건너뜀.
                continue
            print(title)
            time = datetime.datetime.strptime(article['pubDate'], '%a, %d %b %Y %H:%M:%S %z')
            strtime = time.strftime("%Y-%m-%d %H:%M")
            date = time.date()
            print(date)
            if start <= date :  # 기간에 맞는 기사만 저장.
                cnt += 1
            else :
                continue  # 다음 article 검사

            self.tmp_titles.append(title)  # 기사 중복 막기 위해 제목 저장
            con = art(article['link'], title,
                      strtime, self.preprocess(article['description']))
            art_list.append(con)
            # for문 종료
        print('cnt : %d' % cnt)
        return art_list

    def get_articles_wc(self, response, period) :
        """
        [for WordCloud]
        네이버 api 이용 기사 list 받아옴.
        content 객체에 저장
        :param response: api 호출 후 받은 response; 100개 기사있음
        :param period: 기간 (1/2/3)
        :return:
        """
        articles = response['items']
        print('number of articles : ' + str(len(articles)))

        # 뽑을 날짜 설정
        KST = datetime.timezone(datetime.timedelta(hours=9))
        today = datetime.datetime.now(tz=KST).date()
        start = today + datetime.timedelta(-(period * 3))  # 3,6,9일 전
        if period == 1 :
            end = today  # 0일전
        else :
            end = start + datetime.timedelta(+2)  # 4,7일 전
        print('{} ~ {}'.format(start, end))

        cnt = 0
        url_list = []
        title_list = []
        for article in articles :  # article :  url, title, time, description
            if cnt == 10 :  # 최대 10개만 저장.  https://news.naver.com/
                break
            urlobj = urlparse(article['link'])
            print(urlobj.netloc)
            if urlobj.netloc != 'news.naver.com' :  # 네이버 뉴스만 저장
                continue
            title = self.preprocess(article['title'], slice=True)  # 전처리
            if title in title_list :  # 이미 있는 뉴스는 저장 안함.
                continue
            title_list.append(title)
            print(title)

            time = datetime.datetime.strptime(article['pubDate'], '%a, %d %b %Y %H:%M:%S %z')
            strtime = time.strftime("%Y-%m-%d %H:%M")
            date = time.date()
            print(date)
            if start <= date <= end :  # 기간에 맞는 기사만 저장.
                cnt += 1
            else :
                continue  # 다음 article 검사

            url = article['link']
            url_list.append(url)

            descrip = self.preprocess(article['description'])  # 전처리
            con = art(url, " ", " ", " ")
            # Model WCArticle : wc(foreign), title, url, source, time, description
            WCArticle.objects.create(wc={1 : self.model_wc1, 2 : self.model_wc2, 3 : self.model_wc3}[period],
                                     title=title, url=url,
                                     source=con.source, time=strtime, description=descrip)

            # for문 종료
        print('cnt : %d' % cnt)
        return url_list

    def get_result(self, topic, period) :
        """
        period : 1- 제일 최근 뉴스 / 2- 2nd 최근 뉴스/ 3- 3rd 최근 뉴스
        기사 list를 유사도에 따라 정제.
        :param topic: 검색할 topic
        :param period: 기간 (1/2/3)
        :return: 기사 list, 유사도
        """
        tmp_result = []
        num_list = [0, 1, -1, 2, -2, 3, -3]
        for num in num_list :
            request = self.set_request(topic, period, num)
            response = urllib.request.urlopen(request)
            rescode = response.getcode()
            if rescode == 200 :
                response_body = response.read()
                # print(response_body.decode('utf-8'))
            else :
                print("Error Code:" + rescode)
                return None

            responsejson = json.loads(response_body)
            if period == 0 :  # 유사도 기사 검색용
                tmp_result = self.get_articles_original(responsejson)
            else :
                tmp_result.extend(self.get_articles_wc(responsejson, period))
                if len(tmp_result) < 5 :  # 값이 5개 이상 안나왔으면 다시 시도..
                    print("true.... there is nothing..")
                    continue

            break  # while문 종료
        return tmp_result

    def preprocess(self, text, slice=False) :
        text = re.sub(r'\(종합[^)]*\)', '', text)  # (종합)/(종합*보)
        text = re.sub(r'\(상보[^)]*\)', '', text)  # (상보)
        text = re.sub(r'\[[^]]*\]', '', text)  # [단독|현장연결|...]
        text = re.sub('[-=+,#/\?:^$.@*\"※~%ㆍ!』\\‘|\(\)\[\]`\"\'…》]', '', text)  # 특수 문자 없애기
        text = re.sub('<.*?>', '', text)
        if slice and len(text) > 34:  # 35 자 이상은 뒤에 ...으로 대체
            text = text[:35] + '...'
        return text

    def s2v_sim_with_word(self, text) :
        """
        topic과 text의 유사도를 계산 후 반환
        :param text: 기사 제목
        :param topic: 사용자가 입력한 키워드(list)
        :return: 유사도 반환(float)
        """
        # pre-processing
        s = self.preprocess(text)

        # Tokenizing
        okt = Okt()
        tokenlist = okt.nouns(s)  # 단어 토큰화, 명사만 리스트에 넣음
        with open(os.path.join(settings.BASE_DIR, 'scripts/static/stopwords.txt'), 'rt', encoding='UTF8') as f :
            b = f.read().split()
            for i in b :
                if i in tokenlist :
                    tokenlist.remove(i)

        # text 안 model에 없는 단어 삭제
        vocab = list(self.wv.vocab)  # 모델 안 단어 리스트
        text = [i for i in tokenlist if i in vocab]
        if not text :  # 모델과 겹치는 것이 아무 것도 없으면
            return 0
        # print('words in text & model :' + str(text))
        return self.wv.n_similarity(text, [str(t) for t in self.topic])

    def extract10sim_topic(self) :
        # 유사 topic 10 개 추출 -> 유사토픽 나온거 모델에 적용하기
        topic10 = self.wv.most_similar(self.topic, topn=10)
        for i in range(10) :
            SimTopic.objects.create(origin_topic=self.model_topic,
                                    simtopic=topic10[i][0],
                                    simrank=(i + 1),
                                    similarity=round(topic10[i][1], 2))
        for i, t in enumerate(topic10) :
            print(str(i) + 'st of new 10 topics : ' + str(t[0]))
        return topic10

    def select_10art_use_simwords(self, topic10) :
        start = time.time()
        # 총 10번 api 사용하여 총 100개 기사 추출 - self.articles에 저장
        for t in topic10 :
            tem = [t[0], self.topic]
            arlist = self.get_result(tem, period=0)  # 10 개 기사 추출 - api 1번 호출
            self.articles.extend(arlist)
            print("누적 기사 수 : %d" % len(self.articles))
        hundred = time.time()

        print('중복검사 완료 : %d' % (len(self.tmp_titles)))

        # 중복검사 후의 기사 100개 중 제목의 유사도로 10개 추출, 유사도 저장
        df1 = pd.DataFrame({
            'article' : self.articles,
            'title' : self.tmp_titles,
            'sim' : [self.s2v_sim_with_word(t) for t in self.tmp_titles]},  # 제목과 키워드 유사도 도출 함수
            index=range(len(self.tmp_titles))
        )
        sim = time.time()
        df1['rank'] = df1['sim'].rank(ascending=False)
        df1 = df1.sort_values(by='rank', ascending=True)  # rank 순으로 정렬
        # df1.to_csv('df.csv')
        sort = time.time()
        print("#" * 50)
        print("hundred WorkTime: {0:0.2f} sec\n".format(hundred - start))  # 10sec
        print("sim 계산 WorkTime: {0:0.2f} sec\n".format(sim - hundred))  # 4.4 sec
        print("sort WorkTime: {0:0.2f} sec\n".format(sort - sim))  # 4.4 sec

        return df1

    def filter_model_error(self) :
        # 예외처리 - 학습되지 않은 마이너 단어를 입력했을 때
        str_to = []
        for to in self.topic.split() :
            print('each : ' + to)
            str_to.append(to)
            if to not in self.wv.vocab :
                print("학습되지 않은 단어 입력")
                sys.exit(401)  # 401 에러 코드 전송
        self.topic = str_to

    def set_wordcloud(self, period) :  # , arlist=None
        """
        get_result -> get_articles_wc 를 이용하여 Wordcloud Model 안 기사 저장
        """
        urls = self.get_result(self.topic, period)
        tmp_crawler = Crawler(urls=urls, period=period)
        print('%s<<period==%d url test 출력>>%s' % ('=' * 20, period, '=' * 20))
        if len(urls) :
            print(urls[0])
        # print('%s<<period==%d 기사 test 출력>>%s' % ('=' * 20, period, '=' * 20))
        # for a in wc.articles :
        #    a.print()
        return tmp_crawler

    def get_react_make_wc(self, crawler1, crawler2, crawler3) :
        """
        Cralwer 클래스 이용하여 댓글 모음 txt 생성
        Wordcloud.wordcloud 이미지 생성 후 DB저장
        """
        underscore_topic = '_'.join(self.topic)
        crawler1.get_reactions_total(underscore_topic)
        crawler2.get_reactions_total(underscore_topic)
        crawler3.get_reactions_total(underscore_topic)
        print("댓글 모음 txt 생성 완료")

        custom_wc = main_wc(self.model_topic)
        custom_wc.wordcloud(period=1, topic=underscore_topic)
        custom_wc.wordcloud(period=2, topic=underscore_topic)
        custom_wc.wordcloud(period=3, topic=underscore_topic)
        print("워드클라우드 이미지 생성 완료")

    def search(self) :
        """
        키워드의 기간별 검색 결과인 top10 기사 list와 유사도를 받아옴.
        :return: 기사 list, 유사도, wordcloud 3개
        """
        # 예외처리 - 학습되지 않은 마이너 단어를 입력했을 때
        self.filter_model_error()

        # 시간 재기 시작
        start_time = time.time()
        # 유사 topic 10 개 추출
        topic10 = self.extract10sim_topic()
        topic10_time = time.time()

        # 유사 topic으로 기사 100개 받은 후 10개 추림.
        df1 = self.select_10art_use_simwords(topic10)
        select10_time = time.time()

        # Article Django Model에 저장
        for i in range(10) :  # 결과 출력
            if i >= len(df1) :  # 10개 이내의 데이터만 있을 때 오류 방지
                break
            title = df1.iloc[i]['title']
            sim = df1.iloc[i]['sim']
            a = df1.iloc[i]['article']
            print('%dst. title: %s' % (i, title))
            print('=> sim: %f' % sim)
            a.print()
            Article.objects.create(search=self.model_topic, title=a.title,
                                   url=a.url,
                                   source=a.source, time=a.time,
                                   description=a.description,
                                   similarity=round(sim * 100, 2))
        store_art_time = time.time()

        # 3개 기간에 따라 Crawler 저장, period 설정 -WCArticle 객체 이용
        crawler1 = self.set_wordcloud(period=1)
        crawler2 = self.set_wordcloud(period=2)
        crawler3 = self.set_wordcloud(period=3)
        wcart_store_time = time.time()

        # Cralwer 클래스 이용하여 댓글 모음 txt 생성
        # Wordcloud.wordcloud 이미지 생성 후 DB저장
        self.get_react_make_wc(crawler1, crawler2, crawler3)
        """"""
        # search() 종료
        end_time = time.time()
        print("Search.py TOTAL WorkTime: {0:0.2f} sec\n".format(end_time - start_time))
        print("유사 topic 10개 추출 WorkTime: {0:0.2f} sec\n".format(topic10_time - start_time))
        print("기사 100개 받은 후 10개 고름 WorkTime: {0:0.2f} sec\n".format(select10_time - topic10_time))
        print("Article Django Model에 저장 WorkTime: {0:0.2f} sec\n".format(store_art_time - select10_time))
        print("Crawler 세팅, wcart 저장 WorkTime: {0:0.2f} sec\n".format(wcart_store_time - store_art_time))
        print("댓글 모아 wc 이미지 생성 WorkTime: {0:0.2f} sec\n".format(end_time - wcart_store_time))
        return 0


# runscript를 위함
def run(*args) :  # 변수 : news id
    search = Search(args)
    return search.search()
