class StrTopicConverter:
    regex='[ㄱ-힣]+[ㄱ-힣\s]*'

    def to_python(self, value):
        return value

    def to_url(self,value):
        return value