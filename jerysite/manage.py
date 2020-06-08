#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jerysite.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()


"""
models.py 변경한 경우
>>python manage.py makemigrations news
>>python manage.py migrate

static 파일 변경 후
>>python manage.py collectstatic

>>python manage.py createsuperuser
실행 후 uesrname, password 입력 후 관리자 사이트 활성화
개발 서버 시작
>>python manage.py runserver

Username (leave blank to use 'user'): jeryadmin
Email address: ljy97@kakao.com
password : jery0514

django.db.utils.OperationalError: no such table: news_topic 과 같은 에러가 날때 : 
>>python manage.py migrate --run-syncdb
"""