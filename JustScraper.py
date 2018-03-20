import requests
from bs4 import BeautifulSoup
from csv import DictReader
from urllib.parse import urljoin
import dataset
from multiprocessing.dummy import Pool


DB = dataset.connect('sqlite:///test.db')['rest']


ROOT_URL = 'https://www.just-eat.co.uk'
IMG_ROOT_URL = 'https:'


def url_creator():
    with open('postcodes.csv') as f:
        postcodes = [row['postcode'] for row in DictReader(f)]
        pure_ulr = 'https://www.just-eat.co.uk/area/'

    complete_url = []
    for element in postcodes:
        complete_url.append(pure_ulr + element)
    return complete_url


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
    results = []
    # rest_data = dict.fromkeys(['Rest names', 'Rest urls', 'Rest img', 'Food type', 'Rest address'])
    for data in rest_divs:
        item = {}
        item['rest_name'] = data.h2.text

        datahref = data.a
        if datahref:
            item['rest_url'] = urljoin(ROOT_URL, data.a['href'])
        else:
            item['rest_url'] = 'N/A'

        imgnode = data.find('img', attrs={'data-ft': 'restaurantDetailsLogo'})
        if not imgnode:
            imgnode = data.img

        item['rest_img'] = urljoin(IMG_ROOT_URL, imgnode['data-original'])
        item['food_type'] = data.find('p', attrs={'class': 'c-restaurant__cuisine'}).text
        item['rest_address'] = data.find('p', attrs={'class': 'c-restaurant__address'}).text
        results.append(item)
    return results


def write_to_db(items):
    DB.insert_many(items)
    return True


def tosamoe(url):
    collected_url = collector(url)
    return page_scraper(collected_url)

urls = url_creator()[:10]
# for url in urls:
#    print(tosamoe(url))
pool = Pool(2)
results = pool.map(tosamoe, urls)
pool.close()
pool.join()
for result in results:
    write_to_db(result)
# results = page_scraper(collector('https://www.just-eat.co.uk/area/g11-hillhead'))
# print(results)
# write_to_db(results)
