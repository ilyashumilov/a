from django.core.management import BaseCommand
import asyncio


# face_test_util
from face_recognition.modules.Controller import Controller


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")
        loop = asyncio.get_event_loop()
        loop.create_task(worker(loop))
        loop.run_forever()


async def worker(loop):
    with open('test.jpg', 'rb') as f:
        data = f.read()
    t=await Controller(loop).get_face_properties(data)
    print(t)
