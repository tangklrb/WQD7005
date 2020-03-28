import datetime
import json
import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


def format_url(input_string):
    return re.sub(r'\W+', '-', input_string.strip().lower())


def format_key(input_string):
    return re.sub(r'\W+', '_', input_string.strip().lower())


data_directory = '../data/brickz_transaction/new/'

townships_headers = {
    'accept': 'application/json, text/javascript, */*; q = 0.01',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'cookie': '_ga=GA1.3.906229850.1584801440; PHPSESSID=6bsrikeh7k5v65onjr2kh9m4b3; '
              'KP_UID=31f38d05-ea3c-84c2-d0e5-75e338958aa5; _gid=GA1.3.1148108848.1585155670; '
              '__atuvc=7%7C12%2C50%7C13; __atuvs=5e7b8e551ced1a9602a; _gat=1; '
              'KP_UIDz=svAXqqrMvvz%2F01GtJeZnXQ%3D%3D%3A'
              '%3AIC3VaoHbalTOWNhkxdVa4cxSBftfKvNa3tS0KKUOVTq6gUqzz5mNAchxMRJTS1BowICEc0427D4XaDI7nKK3nAsmYjgBEnvth5pMKSPZrE585vFyFnYs%2FOsXn3Bg4h3xwoRqUyVDumBE2DDuCKVLQom9Z9eBo3nO7OQUB6iRZ8zdU%2FARaJ3E5lewsSfHbFYHXSLEykMYFuWEi5mSUhW7qy%2FFqxaGIIZRPk9xzUiCXXQN4Dvi3TpOA%2B2sPR5ChUcHYVrMMP4blLeEqIAxwzHBgFwVuzX%2Fy3kdkRU76ff3U2Hj3SvajhUk7gi9jv3uIfNhqoAsg17j9QfBMkuye2WjxfR0weR6v1UdUHVKeoOAvHwicsl%2FagNMvleiPksLIJpaNskvkVeSfNPf44b8xgBPwhiAMd%2BbGB%2Bf2cMV%2FGiWFlkR0y2m9PEWCmzW%2B%2FlwLpWP3sRbRDBYK6wfSvS%2F%2FmRPHVnRIwGAM%2FE%2BhCQ22TPqlqzna7BowDhmKzef7TrJz8YshawAC%2BkcuFoz9f9WKdcf3w%3D%3D',
    'if-modified-since': 'Fri, 13 Mar 2020 01:04:12 UTC',
    'referer': 'https://www.brickz.my/transactions/residential/',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 '
                  'Safari/537.36',
    'x-requested-with': 'XMLHttpRequest'
}

transactions_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3;q=0.9',
    'cookie': '_ga=GA1.3.906229850.1584801440; PHPSESSID=6bsrikeh7k5v65onjr2kh9m4b3; '
              'KP_UID=31f38d05-ea3c-84c2-d0e5-75e338958aa5; _gid=GA1.3.1148108848.1585155670; '
              '__atuvc=7%7C12%2C50%7C13; __atuvs=5e7b8e551ced1a9602a; _gat=1; '
              'KP_UIDz=svAXqqrMvvz%2F01GtJeZnXQ%3D%3D%3A'
              '%3AIC3VaoHbalTOWNhkxdVa4cxSBftfKvNa3tS0KKUOVTq6gUqzz5mNAchxMRJTS1BowICEc0427D4XaDI7nKK3nAsmYjgBEnvth5pMKSPZrE585vFyFnYs%2FOsXn3Bg4h3xwoRqUyVDumBE2DDuCKVLQom9Z9eBo3nO7OQUB6iRZ8zdU%2FARaJ3E5lewsSfHbFYHXSLEykMYFuWEi5mSUhW7qy%2FFqxaGIIZRPk9xzUiCXXQN4Dvi3TpOA%2B2sPR5ChUcHYVrMMP4blLeEqIAxwzHBgFwVuzX%2Fy3kdkRU76ff3U2Hj3SvajhUk7gi9jv3uIfNhqoAsg17j9QfBMkuye2WjxfR0weR6v1UdUHVKeoOAvHwicsl%2FagNMvleiPksLIJpaNskvkVeSfNPf44b8xgBPwhiAMd%2BbGB%2Bf2cMV%2FGiWFlkR0y2m9PEWCmzW%2B%2FlwLpWP3sRbRDBYK6wfSvS%2F%2FmRPHVnRIwGAM%2FE%2BhCQ22TPqlqzna7BowDhmKzef7TrJz8YshawAC%2BkcuFoz9f9WKdcf3w%3D%3D',
    'Sec-Fetch-Dest': 'document',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 '
                  'Safari/537.36 '
}

townships_url = 'https://www.brickz.my/transactions/residential/page/1/?range=1992+JAN-'

while True:
    request = requests.get(townships_url, headers=townships_headers)
    response = request.text

    uri = townships_url.strip().replace('https://www.brickz.my/transactions/residential/', '').split('/')
    print('-- Page:', uri[1], '--')

    town_page_html = BeautifulSoup(response, 'html.parser')
    township_rows = town_page_html.find_all('tr', attrs={'itemtype': 'https://schema.org/AdministrativeArea'})
    for township_row in township_rows:
        township = {}
        columns = township_row.find_all('td')
        township_link = columns[0].find('a', class_='ptd_list_item_title')
        township['name'] = township_link.find('span', attrs={'itemprop': 'name'}).text
        township['url'] = township_link['href']
        uri = township['url'].strip().replace('https://www.brickz.my/transactions/residential/', '').split('/')
        township['state'] = uri[0]
        township['area'] = uri[1]
        township['township'] = uri[2]
        township['category'] = uri[3]
        township['tenure'] = columns[1].find('span', class_='ptd_list_item_title').text
        township['building_type'] = columns[1].find(text=True, recursive=False)
        psf_quartiles = columns[2].find('span', class_='ptd_list_item_title').get("title").split('\n')
        for psf_quartile in psf_quartiles:
            psf_quartile_key, psf_quartile_value = psf_quartile.split(':')
            township[format_key(psf_quartile_key.strip())] = psf_quartile_value.strip()
        township['median_psf'] = columns[2].text
        price_quartiles = columns[3].find('span', class_='ptd_list_item_title').get("title").split('\n')
        for price_quartile in price_quartiles:
            price_quartile_key, price_quartile_value = price_quartile.split(':')
            township[format_key(price_quartile_key.strip())] = price_quartile_value.strip()
        township['median_price'] = columns[3].text

        print('  Township:', township['name'])

        url = township['url'].replace('?range=', 'view/map/?range=')
        browser = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver')
        browser.get(url)
        browser.add_cookie({'name': '_ga', 'value': 'GA1.3.906229850.1584801440'})
        browser.add_cookie({'name': 'PHPSESSID', 'value': '6bsrikeh7k5v65onjr2kh9m4b3'})
        browser.add_cookie({'name': '__atuvc', 'value': '7%7C12%2C50%7C13'})
        browser.add_cookie({'name': '__atuvs', 'value': '5e7b8e551ced1a9602a'})
        browser.add_cookie({'name': '_gat', 'value': '1'})
        browser.add_cookie({'name': 'KP_UIDz', 'value': 'svAXqqrMvvz%2F01GtJeZnXQ%3D%3D%3A%3AIC3VaoHbalTOWNhkxdVa4cxSBftfKvNa3tS0KKUOVTq6gUqzz5mNAchxMRJTS1BowICEc0427D4XaDI7nKK3nAsmYjgBEnvth5pMKSPZrE585vFyFnYs%2FOsXn3Bg4h3xwoRqUyVDumBE2DDuCKVLQom9Z9eBo3nO7OQUB6iRZ8zdU%2FARaJ3E5lewsSfHbFYHXSLEykMYFuWEi5mSUhW7qy%2FFqxaGIIZRPk9xzUiCXXQN4Dvi3TpOA%2B2sPR5ChUcHYVrMMP4blLeEqIAxwzHBgFwVuzX%2Fy3kdkRU76ff3U2Hj3SvajhUk7gi9jv3uIfNhqoAsg17j9QfBMkuye2WjxfR0weR6v1UdUHVKeoOAvHwicsl%2FagNMvleiPksLIJpaNskvkVeSfNPf44b8xgBPwhiAMd%2BbGB%2Bf2cMV%2FGiWFlkR0y2m9PEWCmzW%2B%2FlwLpWP3sRbRDBYK6wfSvS%2F%2FmRPHVnRIwGAM%2FE%2BhCQ22TPqlqzna7BowDhmKzef7TrJz8YshawAC%2BkcuFoz9f9WKdcf3w%3D%3D'})
        browser.add_cookie({'name': 'KP_UID', 'value': '31f38d05-ea3c-84c2-d0e5-75e338958aa5'})
        browser.add_cookie({'name': '_gid', 'value': 'A1.3.1148108848.1585155670'})
        browser.refresh()

        delay = 10
        try:
            myElem = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'gmnoscreen')))
        except TimeoutException:
            print("  -- Loading timed-out!")

        google_map = browser.find_element_by_xpath('//a[@title="Open this area in Google Maps (opens a new window)"]')
        township['map_url'] = google_map.get_attribute('href')

        if township['map_url']:
            map_host, map_uri = township['map_url'].split('?')
            map_query_parameters = map_uri.split('&')
            for map_query_parameter in map_query_parameters:
                map_query_key, map_query_value = map_query_parameter.split('=')
                if map_query_key == 'll':
                    map_coordinate_lat, map_coordinate_lng = map_query_value.split(',')
                    township['coordinate'] = {'lat': map_coordinate_lat, 'lng': map_coordinate_lng}

        session_datetime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        with open(data_directory + 'township/' + township['state'] + '_' + township['area'] + '_' + township['name']
                  + '_' + township['category'] + '_' + str(session_datetime) + '.json', 'w') as json_file:
            json.dump(township, json_file)

        browser.quit()

        url = township['url']
        request = requests.get(url, headers=transactions_headers)
        response = request.text

        transaction_page_html = BeautifulSoup(response, 'html.parser')

        header_column_index = 0
        header_columns = {}
        transaction_table = transaction_page_html.find('table', id='ptd_list_detail_table')
        transaction_table_headers = transaction_table.find('thead')

        transaction_table_columns = transaction_table_headers.find_all('th')
        for transaction_table_column in transaction_table_columns:
            if transaction_table_column.has_attr('class') and 'ptd_summary' in transaction_table_column.get("class"):
                continue
            header_columns[header_column_index] = format_key(transaction_table_column.text)
            header_column_index += 1

        transactions = []
        transaction_rows = transaction_page_html.select('table#ptd_list_detail_table > tbody > tr')
        for transaction_row in transaction_rows:
            transaction_column_index = 0
            transaction = {}

            columns = transaction_row.find_all('td')
            for column in columns:
                if column.has_attr('class') and 'ptd_summary' in column.get("class"):
                    continue
                transaction[header_columns[transaction_column_index]] = column.text.strip()
                transaction_column_index += 1

            transactions.append(transaction)

        with open(data_directory + 'transaction/' + township['state'] + '_' + township['area'] + '_' + township['name']
                  + '_' + township['category'] + '_' + str(session_datetime) + '.json', 'w') as json_file:
            json.dump(transactions, json_file)

    next_page = town_page_html.find('a', attrs={'class': 'next'})
    if next_page:
        townships_url = next_page.get('href')
    else:
        break

