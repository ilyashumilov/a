from rest_framework.views import APIView
from rest_framework.response import Response
from main.models.main import *
from work_modules.TaskCreator import TaskCreator
import time

'''Creating Blogger instance in DB if not exists'''
def create_blogger_instance(logins_list):
    retreive_blg = TaskCreator().filtering_bloggers(logins_list)
    bloggers = []
    while True:
        for i in logins_list:
            if i not in bloggers:
                try:
                    bloggers.append(Blogger.objects.get(login=i).login)
                except:
                    pass
            if len(logins_list) == len(bloggers):
                break
        time.sleep(18000) # waiting for the update

class InteractionAPI(APIView):
    def post(self,request):
        if request.data.command == 'register':
            try:
                blg = Blogger.objects.get(login=request.data.login)
            except:
                blg = create_blogger_instance() # moving that to Celery task

            return Response('Done')
