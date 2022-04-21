from django.core.management import BaseCommand
import asyncio

# face_test_photo
from face_recognition.modules.Controller import Controller
from face_recognition.services.face_service import get_gender_and_age
from main.models import Subscriber


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(worker())


async def child(avatar: str, controller: Controller):
    result = await get_gender_and_age(avatar, controller)
    print(result)


async def worker():
    loop = asyncio.get_event_loop()
    controller = Controller(loop)
    avatar = "4302310__chelscaruso"
    await child(avatar, controller)
