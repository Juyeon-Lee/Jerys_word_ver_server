from django.shortcuts import render, redirect, reverse
from django.views.generic.edit import FormView, UpdateView, CreateView
from django.views.generic import DetailView
from django.http import JsonResponse
from django.db.models import Count
from django.core import serializers
import subprocess, json
from .forms import TopicForm, TopicForm2
from .models import Topic, Article, WordCloud
from ..scripts.search import run


class IndexFormViewCreate(FormView):  # index
    model = Topic
    form_class = TopicForm
    object = None
    template_name = 'news/index.html'
    success_url = 'result'  # url하드코딩이 아닌 이름을 쓴다.

    # 항상실행 --> delete.py
    def get_context_data(self, **kwargs):       # template에보낼 context설정
        if 'object' not in kwargs :
            kwargs['object'] = self.object
        if 'form' not in kwargs :
            kwargs['form'] = self.form_class(instance=self.object)
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        # post & is_ajax일 때만 동작
        if self.request.is_ajax and self.request.method == "POST" : ### Ajax
            form = self.form_class(data=request.POST, instance=self.object)
            if form.is_valid() :  # 정상적인 데이터인지 검증
                return self.form_valid(form)  # form_valid함수 콜
            else :
                return self.form_invalid(form)
        return JsonResponse({"error" : "post 과정에서 에러 발생"}, status=400)  #### Ajax

    def form_valid(self, form) :
        """제출된 폼이 유효성 검사를 통과하면 호출됨. result.html에 값 표시"""
        # commit=False form데이터를 저장. 그러나 쿼리실행은 x
        topic = form.cleaned_data.get("topic")
        model_tp = form.save()  # get_or_create-> 유일하도록. cleaned_data 전에 호출하면 오류남.
        print("topic id : %d" % model_tp.id)
        print(model_tp)

        ret_str = call_search_py(model_tp.id)  # topic
        # 모델에 기존에 학습된 단어가 아닐 때/ 기타 에러
        if ret_str != 'OK' :
            form.add_error('topic', ret_str)
            return JsonResponse({"error": form.errors}, status=400)

        res_json = json.dumps({"topic": topic, "pk": str(model_tp.id), 'str' : " "})
        #  In order to allow non-dict objects to be serialized set the safe parameter to False.
        return JsonResponse(res_json, safe=False, status=200)

    def form_invalid(self, form) :
        """유효성 검사를 통과하지 않으면 index.html로 이동, 에러메세지"""
        res_json = json.dumps({"error" : form.errors})
        return JsonResponse(res_json, safe=False, status=400)


class IndexFormViewUpdate(IndexFormViewCreate):  # result page
    model = Topic
    template_name = 'news/result.html'
    form_class = TopicForm2
    object = None

    def get_context_data(self, **kwargs):
        super(IndexFormViewCreate, self).get_context_data(**kwargs)
        kwargs['form'] = self.form_class(instance=self.object)
        kwargs['pk'] = self.kwargs.get('pk')
        kwargs['topic'] = self.object
        kwargs['list'] = Article.objects.filter(search=self.object)
        kwargs['wordcloud'] = WordCloud.objects.filter(topic=self.object)
        return super().get_context_data(**kwargs)

    def get_object(self, queryset=None):
        return Topic.objects.filter(id=self.kwargs.get('pk')).first()

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)  # 여기서 get_context_data() 호출되는듯.

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)


class IndexFormViewDelete(IndexFormViewCreate):
    template_name = ''

    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.get_object().delete()
        return redirect(self.success_url)


def wclist(request, topic) :
    context = {'form' : TopicForm2(), 'topic' : topic}
    return render(request, "news/wordcloud.html", context)


def wcphoto_list(request) :
    """기사&워드클라우드"""
    wcphotos = WordCloud.objects.all()
    return render(request, 'news/wordcloud.html', {'wcphoto':wcphotos})
    # wcphoto라는 템플릿 변수 같이 전달


class WordCloudDV(DetailView):
    model = WordCloud
    template_name = 'news/wordcloud.html'

def call_search_py(topic_id):  # str_topic
    """
    비동기 함수 처리 - return 까지 기다리지 않음.
    topic에 잘못된 값이 있으면 호출 안 됨.
    """
    # use news and get list of top10 기사 
    #                                    3 (필수)/search.py명/인자넣을거임/인자
    args = ['python', 'manage.py', 'runscript', 'search', '--script-args', str(topic_id)]

    # process 결과 출력, 예외처리
    try :
        #print('Running command : %s' % (subprocess.list2cmdline(args))) # args출력
        print('Call Search.run()')
        #subprocess.check_call(args, shell=True) # search.py 연결
        run(str(topic_id))
        print('search.py 사용 OK')
    except Exception as e :  # search.py 예외처리
        print('Command makes an error')
        # print(e.returncode)
        #if returncode == 401 :  # 학습되지 않은 마이너 단어를 입력했을 때
        #    return "유효한 검색어를 입력하세요."
        #else :  # news.py 에서의 오류
        #    return "검색 도중에 오류가 발생하였습니다.(using search.py)"
        return "검색 도중에 오류가 발생하였습니다.(using search.py)"
    return 'OK'
