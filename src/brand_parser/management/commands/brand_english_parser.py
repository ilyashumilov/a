import bs4
import requests
from django.core.management import BaseCommand
from bs4 import BeautifulSoup

# brand_english_parser
from brand_parser.models import Brand


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")

        worker()


def from_html(url):
    # https://companiesmarketcap.com/img/company-logos/64/AAPL.webp
    brands = []
    response = requests.get(url)
    soup = BeautifulSoup(response.content, features="html.parser")
    div = soup.find('div', {"class": "table-container shadow"}).find('tbody')
    trs = div.find_all('tr')
    for tr in trs:
        tr: bs4.Tag
        img = tr.find('div', {"class": "logo-container"}).find('img').get('src')
        name = tr.find('div', {"class": 'company-name'}).text.lower().strip()
        brand = Brand(name=name, img=f'https://companiesmarketcap.com{img}')
        brands.append(brand)
    print(url, 'len', len(brands))
    Brand.objects.bulk_create(brands, ignore_conflicts=True)
    print('count', Brand.objects.count())


def worker():
    url = 'https://companiesmarketcap.com/page/{}/'
    for i in range(1, 62):
        from_html(url.format(i))
    pass
