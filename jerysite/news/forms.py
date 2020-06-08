from django import forms
from django.forms import ModelForm
from django.core.validators import validate_slug
from .models import Topic


class ToSpForm(ModelForm):
    class Meta:
        model = Topic  # 어떤 모델 쓸래
        fields = ['topic']  # 뭐 입력받을래
        labels = {"topic": ''}

    def clean(self):
        super(ToSpForm, self).clean()

    def save(self, commit=True):
        model_tp = Topic.objects.create(topic=self.cleaned_data.get('topic'))
        return model_tp


class TopicForm(ToSpForm):
    """index.html의 form / ToSpForm 상속"""
    def __init__(self, *args, **kwargs):
        super(ToSpForm, self).__init__(*args, **kwargs)
        self.fields['topic'].widget.attrs = {  # 클래스 적용
            'style' : "background-color:transparent;",
            'class' : "form-control form-control-lg keyword-field",
            'placeholder' : "검색어를 입력하세요.",
            'id' : 'topic-index-text',
            'required': True
        }


class TopicForm2(ToSpForm):
    """result.html의 form / ToSpForm 상속"""
    def __init__(self, *args, **kwargs):
        super(ToSpForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)
            field.widget = forms.TextInput(attrs={
                'placeholder' : field.label ,
                'class':"form-control mr-sm-2",
                'id' : 'topic-main-text',
                'required' : True
            })

