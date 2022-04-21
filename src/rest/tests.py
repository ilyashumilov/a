import requests
from bs4 import BeautifulSoup

url = "https://9net.ru/171-instagram-top-50.html"
resp = requests.get(url).content

soup = BeautifulSoup(resp, features="html.parser")
table = soup.find_all('table')[1]
trs = table.find_all('tr')
for tr in trs:
    try:
        inst = tr.find('a').get('href')
        print(inst.replace('https://instagram.com/', '').replace('/', ''))
    except Exception as e:
        print(e)
