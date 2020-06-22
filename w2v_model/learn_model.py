from konlpy.tag import Okt
from gensim.models import Word2Vec
from jeryspider.jeryspider.spiders.article_url_spider import run
import datetime
import time
import json
import re
import csv


class learnModel :
    @staticmethod
    def run_spider_auto() :
        """
        script에서 spider 자동실행
        :return: 같은 디렉터리에 'output_[오늘날짜].json' 으로 저장됨.
        """
        start_time = time.time()
        run()  # spider run
        end_time = time.time()
        print("%sfinished!%s" % ('-' * 20, '-' * 20))
        print("Crawling WorkTime: {0:0.2f} sec\n".format(end_time - start_time))

    @staticmethod
    def test_print() :
        # 데이터파일 잘 읽어와지는지 확인
        data_dir = 'output_200506.json'  # 파일 경로
        ftest = open(data_dir, 'r', encoding="utf-8")

        i = 0
        while True :
            line = ftest.readline()
            if line != '\n' :
                i = i + 1
                print("%d번째 줄 :" % i + line)
            if i == 5 :
                break
        ftest.close()

    @staticmethod
    def pre_process(data_dir) :
        """
        json 파일에서 필요없는 url, text의 앞 1문장, 뒤에서 2문장 삭제
        정규 표현식 이용 쓸데없는 말 삭제
        data.txt에 정제된 데이터 저장
        :param data_dir:
        :return: outfile dir
        """
        json_data = []
        for line in open(data_dir, "r", encoding='UTF8') :  # 데이터 파일 읽기
            json_data.append(json.loads(line))
        titles = []
        texts = []
        for article in json_data :  # 한 기사씩 처리
            # 제목 정제
            s = str(article["title"])
            s = re.sub(r'\(종합[^)]*\)', '', s)  # (종합)/(종합*보)
            s = re.sub(r'\[[^]]*\]', '', s)  # [...]
            titles.append(s)

            # 본문 정제
            temp = article["text"][:-2]  # 뒤 2문장 자르기
            s = str(temp)
            s = re.sub(r'\([^)]*=[^)]*\)', '', s)  # (지역=연합뉴스)
            s = re.sub(r'\<[^>]*\>', '', s)  # <...>
            s = re.sub(r'\(종합[^)]*\)', '', s)  # (종합)/(종합*보)
            s = re.sub('^.+=', '', s)  # 특파원/기자 =
            # print('대체함 : ' + s)

            texts.append(s)

        outfile = 'data.txt'
        make_file = open(outfile, 'w', encoding="utf-8")  # 데이터 파일 쓰기
        for title in titles :
            make_file.write(title + '\n')
        for text in texts :
            make_file.write(str(text) + '\n')
        make_file.close()

        return outfile

    @staticmethod
    def pre_process_csv(data_dir) :
        """
        csv 파일에서 정규 표현식 이용 쓸데없는 말 삭제
        data.txt에 정제된 데이터 저장
        :param data_dir:
        :return: outfile dir
        """
        texts = []
        with open(data_dir, 'r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                print(row[0])
                texts.append(row[0])
                #print(f'{row[0]}')

        output =[]
        for s in texts :  # 한 문장씩 처리
            print(s)
            # 정제
            s = re.sub(r'\(종합[^)]*\)', '', s)  # (종합)/(종합*보)
            s = re.sub(r'\[[^]]*\]', '', s)  # [...]
            s = re.sub(r'\([^)]*=[^)]*\)', '', s)  # (지역=연합뉴스)
            s = re.sub(r'\<[^>]*\>', '', s)  # <...>
            s = re.sub('^.+=', '', s)  # 특파원/기자 =
            output.append(s)

        outfile = 'data.txt'
        make_file = open(outfile, 'w', encoding="utf-8")  # 데이터 파일 쓰기
        for i in output :
            make_file.write(str(i) + '\n')
        make_file.close()

        return outfile

    def tokenizing(self, data_dir) :
        """
        tokenizing 후 명사만 골라 return
        :param data_dir: 파일 위치
        :return: tokenizing 후 명사만 고른 result
        """
        # pre_processing
        outfile = self.pre_process(data_dir)  # self.pre_process_csv(data_dir)
        print("pre-process 완료")

        okt = Okt()  # Tokenizing
        fread = open(outfile, 'r', encoding="utf-8")  # 데이터 파일 읽기

        n = 0
        result = []
        start_time = time.time()

        while True :
            line = fread.readline()  # 한 줄씩 읽음
            if not line :
                break  # 모두 읽으면 while문 종료

            n = n + 1
            if n % 5000 == 0 :  # 5,000의 배수로 While문이 실행될 때마다 몇 번째 실행인지 출력
                print("%d번째 While문." % n)

            tokenlist = okt.nouns(line)  # 단어 토큰화, 명사만 리스트에 넣음

            # 이 부분 추가
            words = []
            for length in tokenlist :
                if len(length) > 1 :
                    words.append(length)

            with open('stopwords.txt', 'rt', encoding='UTF8') as f :
                b = f.read().split()
                for i in b :
                    if i in words :
                        words.remove(i)

            if words :  # 이번에 읽은 데이터에 명사가 존재할 경우에만
                result.append(words)  # 결과에 저장
        fread.close()

        end_time = time.time()
        print("\n", len(result))
        print("Tokenizing WorkTime: {0:0.2f} sec\n".format(end_time - start_time))

        return result

    def learn_model(self) :
        """
        초기 모델 학습 후 저장
        연합뉴스 크롤링한 json 파일을 tokenizing하여 저장.
        기사 1261개 함유
        titles, texts 구조: [[str,str,str],...,[str,...,str]]

        모델 학습 파라미터 :
        size # 문자 벡터 차원 수
        window # 문자열 컨텍스트 크기(학습 알고리즘이 고려해야 하는 컨텍스트의 단어 수)
        min_count # 최소 문자 수
        workers # 병렬 처리 스레드 수
        iter # epochs 반복횟수
        alpha # The initial learning rate 학습률
        sg # 0/1 방식 선택 CBOW와 Skip-Gram
        """
        vec_size = 300
        context_win = 10
        min_count = 4  # 1로 바꿀까
        alpha = 0.05
        iter = 10

        data_dir = 'articles.json'  # 파일 경로
        result = self.tokenizing(data_dir)  # 데이터 전처리

        start_time = time.time()
        model = Word2Vec(result, size=vec_size, window=context_win,
                         min_count=min_count, workers=4, alpha=alpha,
                         iter=iter, sg=0)
        model.save('model.model')
        model.init_sims(replace=True)  # 학습이 완료 되면 필요없는 메모리를 unload 시킨다.
        end_time = time.time()
        print("learning_at_first WorkTime: {0:0.2f} sec\n".format(end_time - start_time))

    def update_model(self) :
        """
        새로운 데이터로 기존 모델 업데이트
        tokenizing()사용
        :return
        """
        self.run_spider_auto()  # 먼저 학습용 데이터 마련
        print("크롤러 작동을 완료하였습니다. 모델 업데이트를 시작합니다.")
        data_dir = 'output_' + datetime.datetime.today().strftime('%y%m%d') + '.json'  # 파일 경로
        # data_dir = '3_news_4.csv'  # 파일 경로

        result = self.tokenizing(data_dir)  # 데이터 전처리
        start_time = time.time()
        
        # 미리 학습된 모델 load
        file_name = 'model_updated.model'
        model_updated = Word2Vec.load(file_name)

        # 모델 업데이트 학습
        model_updated.build_vocab(result, update=True)
        model_updated.train(result, total_examples=len(result), epochs=10)
        model_updated.save('model_updated.model')
        print(len(list(model_updated.wv.vocab)))
        model_updated.init_sims(replace=True)  # If you’re finished training a model( = no more updates, only querying), you can do

        end_time = time.time()
        print("update WorkTime: {0:0.2f} sec\n".format(end_time - start_time))


if __name__ == "__main__" :
    """
    이 파일을 실행시키면 자동으로 크롤링 후 모델을 업데이트 한다.
    """
    learn = learnModel()
    #learn.tokenizing("3_news_2.csv")

    learn.update_model()
    """
    learn.run_spider_auto()
    learn.test_print()
    learn.learn_model()
    learn.update_model() # 자동으로 크롤링도 먼저 되므로 그렇게 할건지 생각.
    

    # 모델 안 데이터 시각화
    from sklearn.manifold import TSNE
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import pandas as pd
    import gensim

    model = gensim.models.Word2Vec.load('model_updated.model')
    word_vec = model.wv
    vocab = list(word_vec.vocab)
    X = model[vocab]
    del model

    # 그래프에서 마이너스 폰트 깨지는 문제에 대한 대처
    mpl.rcParams['axes.unicode_minus'] = False
    plt.text(0.3, 0.3, '한글', size=30)
    plt.rc('font', family='Malgun Gothic')

    print(len(X))
    print(X[0])
    tsne = TSNE(n_components=2)

    # 100개의 단어에 대해서만 시각화
    X_tsne = tsne.fit_transform(X[:200, :]) # 그냥 X만 넣어도 됨.

    df = pd.DataFrame(X_tsne, index=vocab[:200], columns=['x', 'y'])
    df.shape
    df.head(10)

    fig = plt.figure()
    fig.set_size_inches(40, 20)
    ax = fig.add_subplot(1, 1, 1)

    ax.scatter(df['x'], df['y'])

    for word, pos in df.iterrows() :
        ax.annotate(word, pos, fontsize=20)
    plt.show()
    """
