import os
from collections import Counter

import numpy as np
from PIL import Image
from django.conf import settings
from django.core.files import File
from konlpy.tag import Hannanum
from news.models import WordCloud  # 빨간줄이지만 잘 실행됨.
from wordcloud import WordCloud as wc
import os


class Wordcloud:
    """
    워드 클라우드 함수,
    period, articles 저장용
    """
    def __init__(self, model_topic):   #, period
        # self.period = period
        self.articles = []
        self.model_topic = model_topic

    def wordcloud(self, period, topic):
        """
        한 기간의 댓글 모음을 이용하여 빈도수로 워드 클라우드를 생성하여 반환
        :return: wordcloud 이미지
        """

        # 일단 텍스트 파일에서 가져오는 걸로 해놈
        text = ''
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        file_reactions = os.path.join(THIS_FOLDER, "%s_%d.txt" % (topic, period))
        # with open(os.path.join(settings.BASE_DIR, file_reactions), encoding="utf-8") as f:
        with open(file_reactions, encoding="utf-8") as f:
            text = f.read()
            #first_char = f.read(1)
            if not text:
                print("file is empty")
                # 임시 텍스트 파일 삭제
                os.remove(file_reactions)
                return
            else:
                print("file is full")

        # 한나눔 사용 변수 지정
        hannanum = Hannanum()

        # 명사 분석
        nouns = hannanum.nouns(text)
        # print(nouns)

        # midle_time = time.time()

        # 명사 중에 길이가 2이상일때만
        words = []
        for n in nouns:
            if len(n) > 1:
                words.append(n)

        # 빈도수 계산
        count = Counter(words)
        # 상위 100건 추출
        most = count.most_common(100)

        # 딕셔너리 구성
        tags = {}
        for n, c in most:
            tags[n] = c

        # 워드 클라우드 생성
        print(topic)
        file_name = (topic + "_%d" % self.model_topic.id + "_%d.png" % period)  # topic 2개이면 파일명 'topic1_topic2_10_1.png'
        mask = np.array(Image.open(os.path.join(THIS_FOLDER, 'mask_img_512px.png')))
        wc_image_gen = wc(font_path=os.path.join(THIS_FOLDER, 'NanumSquareEB.ttf'),
                            mask=mask,
                          background_color='white'
                          ).generate_from_frequencies(tags)   # wordcloud 용 댓글 하나도 없을 경우..
        wc_image_gen.to_file(os.path.join(THIS_FOLDER,file_name))  # 경로에 이미지 파일 생성

    #file_reactions = os.path.join(THIS_FOLDER, "%s_%d.txt" % (topic, period))
        with open(os.path.join(THIS_FOLDER, file_name), 'rb') as tmp_file:
            # tmp_wc = WordCloud(period=period, topic=self.model_topic)
            # get해서 해야됨. -> django db 에 저장
            tmp_wc = WordCloud.objects.filter(topic=self.model_topic, period=period).first()
            tmp_wc.wcphoto.save(file_name, File(tmp_file))

        # 임시 이미지 파일 삭제
        os.remove(os.path.join(THIS_FOLDER, file_name))
        # 임시 텍스트 파일 삭제
        os.remove(file_reactions)
        """
        # Display the generated image:
        plt.imshow(wc_image_gen, interpolation='bilinear')
        plt.axis("off")
        plt.show()

        """

        # end_time = time.time()
        # print("midletime - startime : {0:0.2f} sec\n".format(midle_time - start_time))
        # print("wordcloud(using tokenizing) WorkTime: {0:0.2f} sec\n".format(end_time - start_time))


def run(*args) :  # 변수 : topic
    # python manage.py runscript wordcloud --script-args test
    print(str(args))
    __wc__ = Wordcloud(1)
    __wc__.wordcloud(str(args))

