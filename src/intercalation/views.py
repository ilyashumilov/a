from rest_framework.views import APIView
from rest_framework.response import Response
from main.models.main import *
from .work_modules.TaskCreator import TaskCreator
import time

'''Creating Blogger instance in DB if not exists'''

def create_blogger_instance(login):
    a = []
    a.append(login)
    retreive_blg = TaskCreator().filtering_bloggers(a)

# 1	Парсинг лайков
# 2	Парсинг комментариев
# 3	Парсинг комментариев детально
# 4	Парсинг информации о профиле
# 5	Парсинг подписчиков
# 6	Парсинг постов
# 7	Парсинг подписчиков детально
# 8   Фильтрация аккаунтов по social_id, login
# 9   Фильтрация аккаунтов по social_id, login

class InteractionAPI(APIView):
    def post(self,request):
        result = {}
        if request.data["command"] == 'register':

            task_type = request.data['task_id']

            if task_type == 1:
                return Response(request.data['task_id'])
            if task_type == 2:
                pass
            if task_type == 3:
                pass

            if (task_type == 4) or (task_type == 5) or (task_type == 6):
                for i in request.data['items']:
                    result[i] = ''
                    try:
                        blg = Blogger.objects.get(login=request.data.login)
                        t, c = TaskCreator.create_parsing_task(blg)
                        task_id = None
                        if task_type == 4:
                            task_id = TaskCreator.posts(t).parser_task_id
                        if task_type == 5:
                            task_id = TaskCreator.subscribers(t).parser_task_id
                        if task_type == 6:
                            task_id = TaskCreator.posts(t).parser_task_id

                        result[i] = task_id

                    except:

                        blg = create_blogger_instance(i)
                        result[i] = 'Blogger creation'

                    return Response(result)

            if request.data.task_id == 7:
                pass
            if request.data.task_id == 8:
                pass
            if request.data.task_id == 9:
                pass

            return Response()
