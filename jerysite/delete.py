
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jerysite.settings")
import django
django.setup()

from datetime import datetime, timedelta
from .news.models import Topic,Article,WordCloud

# topic 삭제
def delete_outdated_topic():
    topics = Topic.objects.filter(date__lte=datetime.now() - timedelta(days=5)) # days일 만큼 지난 데이터 삭제
    print("Delete {} topic.".format(len(topics)))
    topics.delete()


def delete_outdated_article():
    articles = Article.objects.filter(date__lte=datetime.now() - timedelta(days=5)) # days일 만큼 지난 데이터 삭제
    print("Delete {} article.".format(len(articles)))
    articles.delete()

def delete_outdated_wordcloud():
    wordclouds = WordCloud.objects.filter(date__lte=datetime.now() - timedelta(days=5)) # days일 만큼 지난 데이터 삭제
    print("Delete {} wordcloud.".format(len(wordclouds)))
    wordclouds.delete()

if __name__ == '__main__':
    delete_outdated_topic(),
    delete_outdated_article(),
    delete_outdated_wordcloud(),
    print("topic,article,wc data delete ok")