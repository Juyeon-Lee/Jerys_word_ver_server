from django.urls import path, re_path, register_converter
from .views import IndexFormViewCreate, IndexFormViewUpdate, WordCloudDV
from . import views, converters

register_converter(converters.StrTopicConverter, 'topic')

urlpatterns = [
    # the 'name' value as called by the {% url %} template tag

    path('', IndexFormViewCreate.as_view(), name='index'),   # ex : / <slug:topic>
    path('result/<topic:slug>/<int:pk>', IndexFormViewUpdate.as_view(), name='result'),  #<slug:topic>
    # path('result/wc', views.wcphoto_list, name='wc'),  #
    path('result/<topic:slug>/<int:period>/<int:pk>', WordCloudDV.as_view(), name='wc'),  #

]