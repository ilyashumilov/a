import aiohttp
import requests
from django.core.management import BaseCommand

from brand_parser import services
from brand_parser.management.commands.parser import fetch
from brand_parser.models import Brand


def get_imgs_for_brands():
    url = 'https://companies.rbc.ru/search/?capital_from=100000&query=&registration_date_from=1999&sorting=last_year_revenue_desc&page={}'
    brands = set()
    for index in range(1, 51):
        content = requests.get(url.format(index))

        if content is False:
            break

        __brands = services.get_images(content.content)

        if __brands:
            brands = brands | __brands

        else:
            break

    for brand in brands:
        if not brand[1]:
            continue
        try:
            print(brand[0])
            brand_entity = Brand.objects.get(name=brand[0].lower().strip())
            brand_entity.catch_img(brand[1])
            brand_entity.img_origin_path = brand[1]
            brand_entity.save()
            print('saved',brand_entity.id,brand_entity.name)
        except Brand.DoesNotExist as e:
            # brand_entity,created = Brand.objects.get_or_create(name=brand[0])
            # brand_entity.catch_img(brand[1])
            # brand_entity.img_origin_path = brand[1]
            # brand_entity.save()
            pass
        except Exception as e:
            print(e)


class Command(BaseCommand):
    def handle(self, *args, **options):
        get_imgs_for_brands()
