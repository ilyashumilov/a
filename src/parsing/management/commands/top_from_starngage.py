import requests
from bs4 import BeautifulSoup
from django.core.management import BaseCommand


# top_from_starngage
class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")

        worker()


def worker():
    url = 'https://starngage.com/app/global/influencer/ranking/france'
    #     table table-hover table-responsive-sm
    response = requests.get(url)
    soup = BeautifulSoup(response.content, features="html.parser")
    table = soup.find('table', {"class": "table table-hover table-responsive-sm"})
    trs = table.find_all('tr')
    counter=0
    for tr in trs:
        try:
            td = tr.find('td', {'class': "align-middle text-break"})
            login = str(td.next.next.next.text).replace('@', '')
            print(login)
            counter+=1
            if counter>100:
                break
        except Exception as e:
            pass
