import aiohttp
import requests
from bs4 import BeautifulSoup

#
from brand_parser.management.commands.parser import fetch
from brand_parser.models import Brand

# async def get_url_html(url: str, index):
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url) as response:
#             return await response.text(encoding='utf-8')


import string

accept_signs = (string.ascii_lowercase + "абвгдеёжзийклмнопрстуфхцчшщъыьэюя" + '-_—.,"' + string.digits)
accept_signs = set(list(accept_signs))


# lower text stripped
def exclude(text: str):
    if len(text) > 50:
        return True
    if 'торговая марка' in text:
        return True
    text_set = set(list(text))
    for sign in text_set:
        if sign not in accept_signs:
            return True


def exclude_searchable(text: str):
    if len(text) < 3:
        return True
    text_set = set(list(text))
    for sign in text_set:
        if sign not in accept_signs:
            return True


def parse_html(content: str):
    brands = set()
    try:
        soup = BeautifulSoup(content, 'lxml')
        tags = soup.find_all('a', {'class': 'company-name-highlight'})

        for i in tags:
            new_text = str(i.text).lower().strip()
            t = new_text.split(' ')
            if len(t[0]) <= 3:
                new_text = (' '.join(t[1:])).strip()

            if not exclude(new_text):
                brands.add(new_text)

        return brands
    except Exception as e:
        print(e)
        return False


def get_images(content: str):
    brands_and_img_path = set()
    try:
        soup = BeautifulSoup(content, features="html.parser")
        tags = soup.find_all('a', {'class': 'company-name-highlight'})

        for i in tags:
            new_text = str(i.text).lower().strip()
            href_to_brands_page = str(i['href'])

            t = new_text.split(' ')
            if len(t[0]) <= 3:
                new_text = (' '.join(t[1:])).strip()

            content_from_brand_page = requests.get(href_to_brands_page).text

            soup_for_img = BeautifulSoup(content_from_brand_page, features="html.parser")
            img_tag = soup_for_img.find('img', {'class': 'company-headline__img'})
            img_href = None
            if img_tag:
                img_href = str(img_tag['src'])
            print(img_href)

            if not exclude(new_text):
                brands_and_img_path.add((new_text, img_href))
        return brands_and_img_path
    except Exception as e:
        print(e)
        return False
