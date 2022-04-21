import bs4
import requests


def parse_trademark_single_page(page_url):
    """ class to get single trademark (with pict and name)- <a> TrademarksTable__trademarks-table__link__dutJdro"""
    page = requests.get(page_url).text
    print(page_url)
    print(page)
    soup = bs4.BeautifulSoup(page, 'html.parser')
    all_items = soup.find_all('div', {'class': 'TrademarksTable__trademarks-table__logo__mqLmtD9'})
    #print(all_items)
    for item in all_items:
        print(item.style)
        return


def parse_trademarks_page(page_url):
    page_with_list_of_trademarks = requests.get(page_url).text
    trademarks = bs4.BeautifulSoup(page_with_list_of_trademarks, 'html.parser') \
        .find_all('a',
                  {'class': 'trademark-card__title'})
    for trademark in trademarks:
        parse_trademark_single_page(trademark['href'])
        return

def parsing_through_trademarks():
    page_url = "https://companies.rbc.ru/search/trademarks/?query="

    """
        class to get num of last pagination page - <a> pagination__item
    """

    pagin_page = requests.get(page_url).text
    soup = bs4.BeautifulSoup(pagin_page, 'html.parser')
    pagination_tags = soup.find_all('a', {'class': 'pagination__item'})
    last_page_value = int(pagination_tags[-2].text)

    go_through_pages = "https://companies.rbc.ru/search/trademarks/?query=&page={}"
    for page_num in range(last_page_value):
        parse_trademarks_page(go_through_pages.format(str(page_num)))
        return