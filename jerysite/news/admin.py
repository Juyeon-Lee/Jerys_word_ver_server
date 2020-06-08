from django.contrib import admin
# models에서 Article, WordCloud를 import 해옴.
from .models import Article, Topic
from .models import WordCloud, WCArticle

"""
Article, WordCloud를 admin페이지에서 관리 가능
admin.ModelAdmin클래스 상속
"""


class NewsAdmin(admin.ModelAdmin) :
    list_display = ['search', 'title', 'date', 'similarity', 'source']  # 목록에 보일 필드
    list_filter = ['source', 'time']  # 필터기능
    search_fields = ['title', 'search']  # 검색 기능 사용할 필드
    ordering = ['search', 'date', 'similarity']  # 사이트상 정렬값 설정


admin.site.register(Article, NewsAdmin)


class WCAdmin(admin.ModelAdmin) :
    list_display = ['period', 'topic', 'date']
    list_filter = ['topic']
    ordering = ['topic', 'date']


admin.site.register(WordCloud, WCAdmin)


class TopicAdmin(admin.ModelAdmin) :
    list_display = ['id', 'topic', 'date']
    list_filter = ['topic', 'date']
    ordering = ['id', 'topic']


admin.site.register(Topic, TopicAdmin)


class WCArtAdmin(admin.ModelAdmin) :
    list_display = ['wc', 'title', 'time']
    list_filter = ['wc', 'title', 'time']
    ordering = ['wc', 'title']


admin.site.register(WCArticle, WCArtAdmin)
