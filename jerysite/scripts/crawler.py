import requests
from bs4 import BeautifulSoup
import re
import os


class Crawler :
    """
    댓글용 크롤러
    오퍼레이션 : get_reactions, flatten
    속성 : number_of_comment, urls, period

    get_reactions() 호출 후 flatten() 호출하면 txt파일 생성
    """

    def __init__(self, urls, period) :
        """
        한 기간의 기사들의 댓글 총 개수
        :param urls: 기사들의 링크 모음
        :param period: 기사 검색 기간
            1: 0~3일전 / 2: 4~6일전 / 3: 7~9일전
        """
        self.List = []       # 댓글 리스트
        self.number_of_comment = 0
        self.urls = urls
        self.period = period

    def get_reactions_total(self, topic):
        """
        urls를 이용하여 각 기사의 댓글을 최대 50개 크롤링 후 Reactions txt를 반환
        :return: List of Reactions (format : txt)
        """
        for url in self.urls:
            self.get_reactions_a_url(url)
        self.flatten(topic)         # reactions. txt 생성

    def get_reactions_a_url(self, url):
        """
        url를 이용하여 한 기사의 댓글을 최대 50개 크롤링 후 self.List에 append
        20개만으로 수정
        """
        text = " "

        res = requests.get(url)
        res.text

        oid = url.split("oid=")[1].split("&")[0]
        aid = url.split("aid=")[1]
        page = 1

        headers = {"referer" : url,
                   "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"}
        while True :
            c_url = "https://apis.naver.com/commentBox/cbox/web_neo_list_jsonp.json?ticket=news&templateId=default_society&pool=cbox5&_callback=jQuery1707138182064460843_1523512042464&lang=ko&country=&objectId=news" + oid + "%2C" + aid + "&categoryId=&pageSize=20&indexSize=10&groupId=&listType=OBJECT&pageType=more&page=" + str(
                page) + "&refresh=false&sort=FAVORITE"

            res = requests.get(c_url, headers=headers)
            cont = BeautifulSoup(res.content, 'html.parser')
            total_comm = str(cont).split('comment":')[1].split(",")[0]  # 실제 댓글 split

            # print(str(cont))
            match = re.findall('"contents":([^\*]*),"userIdNo"',
                               str(cont))  # "content": 뒤에 나오는 전체 문장 끝은 ,"userIdNo"로 끝나는...
            # print(match)
            self.List.append(match)

            # 한 번에 댓글이 20개씩 보이기 때문에 한 페이지씩 몽땅 댓글을 긁어오기
            if int(total_comm) <= (page * 20) :
                break
            else :
                page += 1
                # 2페이지(댓글 40개)까지 긁어오기 => 1페이지만으로 수정
                if page >= 2 :
                    break

    def flatten(self, topic):
        """
        리스트에 댓글의 원소를 집어넣고, 텍스트파일로 저장
        :return: 저장한 텍스트 파이명
        """
        # TODO: 중복을 막기 위한 파일명 설정
        flatList = []
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        file_name = os.path.join(THIS_FOLDER, "%s_%d.txt" % (topic, self.period))

        if os.path.exists(file_name):
            os.remove(file_name)
        # 날짜로 저장 a: 이어서 저장됨
        f = open(file_name, 'a', encoding='utf-8')
        for elem in self.List:
            if type(elem) == list:  # 타입이 list이면 그 안의 원소를 추가
                for e in elem:
                    flatList.append(e)
                    f.write(e)
            else:  # 타입이 list가 아닌 원소라면 바로 추가
                flatList.append(elem)
                f.write(elem)

        return file_name

