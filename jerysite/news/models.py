from django.db import models
from django.urls import reverse
from django import forms
import datetime, re, os
# https://docs.djangoproject.com/en/3.0/ref/models/instances/


class TopicField(models.CharField) :
    def to_python(self, value) :
        """Normalize data to a list of strings."""
        # Return an empty list if no input was given.
        if not value :
            return ""
        if type(value) is tuple :
            return ' '.join(value)
        else :
            return value


def topic_validator(value) :
    flag = 1
    if re.search('[0-9]+', value) is not None :
        flag = 0
        raise forms.ValidationError("숫자를 제외하고 입력하세요.")
    if re.search('[a-zA-Z]+', value) is not None :
        flag = 0
        raise forms.ValidationError("영문자를 제외하고 입력하세요.")
    if re.search('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\"\'…》]', value) is not None :
        flag = 0
        raise forms.ValidationError("특수문자를 제외하고 입력하세요.")


class Topic(models.Model) :
    topic = TopicField(max_length=20, validators=[topic_validator])
    date = models.DateTimeField(auto_now_add=True, null=True)
    simword1 = models.CharField(max_length=30, blank=True)
    simword2 = models.CharField(max_length=30, blank=True)
    simword3 = models.CharField(max_length=30, blank=True)
    simword4 = models.CharField(max_length=30, blank=True)
    simword5 = models.CharField(max_length=30, blank=True)
    simword6 = models.CharField(max_length=30, blank=True)
    simword7 = models.CharField(max_length=30, blank=True)
    simword8 = models.CharField(max_length=30, blank=True)
    simword9 = models.CharField(max_length=30, blank=True)
    simword10 = models.CharField(max_length=30, blank=True)

    def get_absolute_url(self) :  # 안 쓰임. 이 함수를 추가하거나 view에 success_url을 추가해야 한다.
        return reverse('result', kwargs={'topic' : self.topic})

    def __str__(self) :
        return self.topic

    def save(self, *args, **kwargs):  # date 갱신
        self.date = datetime.datetime.now()
        super(Topic, self).save(*args, **kwargs)


class Article(models.Model) :
    search = models.ForeignKey(Topic, on_delete=models.CASCADE)  # topic
    title = models.CharField(max_length=30)
    url = models.URLField()
    source = models.CharField(max_length=10)    # 신문사
    time = models.CharField(max_length=25)
    description = models.CharField(max_length=50, default=" ") # 프리뷰
    similarity = models.CharField(max_length=4, default="n%") # 유사도 "n%"
    date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self) :  ## 객체(obj)를 출력할 때 나타날 값
        return self.title


class WordCloud(models.Model) :
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)  # topic
    wcphoto = models.ImageField(upload_to='wcphotos/%Y/%m/%d')  # wcphotos 폴더에 upload
    period = models.CharField(max_length=2)  # topic 1,2,3 으로 표현
    date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self) :
        return self.topic.__str__()

    class Meta :
        ordering = ['period']

    ## 객체의 상세 페이지의 주소를 반환하는 메서드
    ## revers("상세화면 패턴이름", args[url만드는데 필요한 pk값 리스트로 전달])
    def get_absolute_url(self) :
        return reverse("wc", args=[str(self.topic), self.period, self.id])


class WCArticle(models.Model) :
    """result/wc에서 디테일 기사 출력 위해"""
    wc = models.ForeignKey(WordCloud, on_delete=models.CASCADE)  # wordcloud
    title = models.CharField(max_length=30)
    url = models.URLField()
    source = models.CharField(max_length=10)  # 신문사
    time = models.CharField(max_length=25)
    description = models.CharField(max_length=50, default=" ")  # 프리뷰

    def __str__(self) :  ## 객체(obj)를 출력할 때 나타날 값
        return self.title
"""
내용에 대한 쿼리용 함수를 만드려면 : 
https://docs.djangoproject.com/ko/3.0/intro/tutorial02/

모델 변경 후 지침
(models.py 에서) 모델을 변경합니다.
python manage.py makemigrations을 통해 이 변경사항에 대한 마이그레이션을 만드세요.
python manage.py migrate 명령을 통해 변경사항을 데이터베이스에 적용하세요.
"""
