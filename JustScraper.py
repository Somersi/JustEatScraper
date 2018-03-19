import requests
from bs4 import BeautifulSoup
from csv import DictReader
import dataset
import sqlite3


with open('postcodes.csv') as f:
    postcodes = [row['postcode'] for row in DictReader(f)]
    urls_with_postcodes = []
    pure_ulr = 'https://www.just-eat.co.uk/area/'

complete_url = []
for element in postcodes:
    complete_url.append(pure_ulr + element)


def collector(url):
    headers = {
        'Host': 'www.just-eat.co.uk',
'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Accept-Language': 'en-US,en;q=0.5',
'Accept-Encoding': 'gzip, deflate, br',
'Cookie': 'je-user_percentage=50; je-auser=c9a4b581-5a8b-4bc0-9c46-6ccdfaf55fdf; visid_incap_441629=7BtZls8gRbGPbDY+2UXHPXXCiloAAAAAQUIPAAAAAADz/wUXiE7gPTlTvMuNlOtd; je-location=g12; je-last_searched_string=G12; incap_ses_376_441629=Zt/wAiaWJXqm+JerFNI3BZmjjFoAAAAA31iwZAVjM13vW8LuM5RiCg==; je-banner_cookie=130315; je-consumerweb-id=.; nlbi_441629=EQ26CN/IYgvZDbi1e/Nw+AAAAABqXUrbsDLm6HzVOL7CTDRq; incap_ses_729_441629=RKkkaj5lYD6hbEti+e0dCnb5jloAAAAAqxytDiVlIWhulm0E00k+PA==',
'Connection': 'keep-alive',
'Upgrade-Insecure-Requests': '1',
'Cache-Control': 'max-age=0'
    }
    session = requests.Session()
    html_content = session.get(url, headers=headers).text
    soup = BeautifulSoup(html_content, 'lxml')
    rest_divs = soup('div', attrs={'class': ['o-tile c-restaurant', 'o-tile c-restaurant c-restaurant--offline']})
    return rest_divs

def page_scraper(rest_divs):
    rest_data = {}
    for data in rest_divs:
        for names in data('h2'):
            rest_data['Rest names'] = names.text
        for urls in data('a'):
            if urls.has_attr('href'):
                rest_data['Rest url'] = 'https://www.just-eat.co.uk' + urls.atts['href']
        for imgs in data('img'):
            if imgs.has_attr('src'):
                rest_data['Rest img'] = 'https:' + imgs.attrs['src']
        for food_type in data('p', attrs={'class', 'c-restaurant__cuisine'}):
            rest_data['Food type'] = food_type.text
        for adress in data('p', attrs={'class', 'c-restaurant__address'}):
            rest_data['Rest address'] = adress.text
    print(rest_data)

page_scraper(collector('https://www.just-eat.co.uk/area/g11-hillhead'))
