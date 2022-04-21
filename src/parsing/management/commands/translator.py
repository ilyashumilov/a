import time

import aiohttp
from django.core.management import BaseCommand
import asyncio
import requests

# translator
from django.db.models import Q
from main.models import Language, Category, Address
from parsing.AsyncParsingNew.utils import chunks


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(worker())


class Translate:
    def __init__(self):
        self.time_last_upd = time.monotonic()
        self.__iam_token = ""

    @property
    def iam_token(self):
        if self.__iam_token == '' or (time.monotonic() - self.time_last_upd) > 60 * 60:
            # {
            #  "iamToken": "t1.9euelZqPkI-Ql4uXjpHPk5WPlZuOmu3rnpWazpqQnYqcko2PkpKax8iMi47l8_dhbwxu-e8eZRJd_t3z9yEeCm757x5lEl3-.A9QDLwVJStimjbiQCCNn9aniAkjDzceezcSmDOQBFe24HKAVtN6jAhmIE40mCDzQHkY32TCQ1CX08QLLpfxWAw",
            #  "expiresAt": "2022-03-25T07:35:58.341527905Z"
            # }
            data = '{"yandexPassportOauthToken":"AQAAAABezZ_rAATuwSHUV7u7fEJrpPOAmw30QDE"}'

            response = requests.post('https://iam.api.cloud.yandex.net/iam/v1/tokens', data=data).json()
            iam_token = response['iamToken']
            self.__iam_token = iam_token
            return iam_token
        else:
            return self.__iam_token

    async def translate_ru(self, items: list):
        pass

    async def translate_en(self, items: list):
        pass

    async def translate(self, items, lang) -> list:
        IAM_TOKEN = self.iam_token  # Токен
        folder_id = 'b1gqtm0e1glgo8v0e94k'  # Идентификатор каталога

        HEADERS = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {0}".format(IAM_TOKEN)
        }

        translate_url = 'https://translate.api.cloud.yandex.net/translate/v2/translate'
        body = {
            "targetLanguageCode": lang,
            "texts": items,
            "folderId": folder_id
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(translate_url, json=body, headers=HEADERS) as resp:
                response_json = await resp.json()
                print(response_json)
                data = []
                for i in response_json['translations']:
                    if 'text' in i:
                        data.append(i['text'])
                    else:
                        data.append('')

                print(data)
                return data


alf = set(list('АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнОоПпСсТтУуФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯя'.lower()))


def check(signs: list):
    size = len(signs) // 2
    counter = 0
    for i in signs:
        if i in alf:
            counter += 1
    if counter > size:
        return True
    else:
        return False


async def worker():
    addresses = Address.objects.filter(~Q(native_country=None) & Q(original_country=None))
    print(len(addresses))
    array = list(addresses)

    if len(array) == 0:
        return

    trans = Translate()

    for mini in list(chunks(array, 50)):
        arr = [i.native_country for i in mini]
        data = await trans.translate(arr, 'en')

        for obj, translated_name in zip(mini, data):
            obj.original_country = translated_name
        Address.objects.bulk_update(mini, fields=['original_country'])
