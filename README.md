# JERYs-WORD
## Sejong Univ. capstone project; JERY's Word; 단어유사도 인공신경망>
### 검색 후 평균 실행시간 약 30초

필수 라이브러리 :
gensim, konlpy, wordcloud, numpy, scrapy, django, django-extensions

현재 상태 :

###### gitignore(python, jupyternotebook, pycharm, windows, venv)설정,
###### scrapy 크롤링 완료(연합뉴스 사이트)  - 1회 구동 : 약 3678 개 기사 크롤링 
###### 기본 클래스 틀 제작, learnModel, Search, Article 클래스 초안 완성
###### django 연결 1차 완료
-> jerysite 디렉토리에 이동 후 터미널에 아래 명령어 입력하면 개발 서버 구동 시작.
>>>python manage.py runserver

jerysite/scripts 안에 기존 코드 복사 후 수정완료.
jerysite/scripts/staic 안에 model, txt 등의 정적 파일 넣음.

## About current w2v model :

모델 학습 파라미터 :
#### size :300; 문자 벡터 차원 수
#### window :10;  문자열 컨텍스트 크기(학습 알고리즘이 고려해야 하는 컨텍스트의 단어 수)
#### min_count :4;  최소 문자 수
#### workers :4;  병렬 처리 스레드 수
#### iter :5;  epochs 반복횟수
#### alpha :0.05;  The initial learning rate 학습률

### - 5.8 모델 학습 기록 -
=> 10188 word 가진 model임.
### - 6.2 모델 학습 기록 -
=> 21572 word 가진 model임.
### - 6.8 모델 학습 기록 -
=> 24018 word 가진 model

수정 파라미터 적용하여 model.model 학습(articles.json 이용)
###### number of learned word 4317
###### Tokenizing WorkTime: 65.03 sec
###### learning_at_first WorkTime: 3.76 sec

output_200505.json 추가로 학습 후 model_updated.model 학습
###### Tokenizing WorkTime: 32.19 sec
###### update WorkTime: 1.67 sec
output_200510.json 추가로 학습 후 model_updated.model 학습

output_200515.json 추가로 학습 후 model_updated.model 학습

output_200521.json 추가로 학습 후 model_updated.model 학습
###### 472079 effective words/s

output_200526.json 추가로 학습 후 model_updated.model 학습

output_200602.json 추가로 학습 후 model_updated.model 학습
######938352 effective words/s