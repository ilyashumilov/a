import requests
from django.conf import settings
from urllib.parse import unquote


def check_result(task_id: int):
    url = f'{settings.MICROSERVICE_IP}/api/result/{task_id}/'
    response = requests.get(url).json()
    if 'detail' in response:
        return None
    else:
        return response['link']


def check_results(tasks_ids: list):
    url = f'{settings.MICROSERVICE_IP}/api/result/1/'
    # url = f'http://127.0.0.1:8000/api/result/1/'
    response = requests.post(url, json={'tasks_ids': tasks_ids}).json()
    if isinstance(response, list):
        return response
    return []


def url_normalize(link: str):
    return link.replace(r'\u0026', '&')
