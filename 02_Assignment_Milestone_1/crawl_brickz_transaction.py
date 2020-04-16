import datetime
import json
import re
import sys
import time

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
              'KP_UID=b1f158dd-7352-106c-9cef-70c96b5c296e; _gid=GA1.3.1780907631.1585685551; _gat=1; '
              'KP_UIDz=%2FPyZIkcrGc5kIJ0hTnfB2w%3D%3D%3A%3AVtWI4XjoaD25'
              '%2BrxTiyDVnNyHkPljUaWcZIwvy8FOaePHiQkIqETm33klNh3NJ1F77xOffb749NslsQI7eyvRGI4XXrNUqWyEQVZchLT5lcVCgZw'
              '%2BKGcd8y1xhCz9yPXw7T5N%2BPm%2BnW4oAEC6WSHdYAzOk5pGeGCn4bHeo0DbTXS64Yv14w0%2BYCbhvAga'
              '%2FQtrBRiA0Ue9uu8fc4%2FkebQacrTjAsAB9MUsMGQaoF4VtStQ1tuyTgiZ0OUlzbRRFh1sYyEGbX5iamk9YwoKG3cENpVP'
              '%2F5XhYcG3N2%2FslwT7aii9Qm5DU8DF7kkfDlN6tQzW8Maokl3iJeBmGDeEbxoQcLEW%2BPMDYUiQBNs%2BqDqbjSXgvSO'
              '%2BqprM9pBepnulSf6De5qWaC%2FDnmH1OIkq0GdWSj3hUTC7fHbui%2FvjneCwY2WeahKfKTqM2GnMfmUe1NZd'
              '%2BTzQQMCDsfgphUCvntY%2BCgE4CtEa3gNgEqzNF%2Ff6xf5gWwjoeMbskdZH%2BaLbovx6MV9hpSv5ZPFbM908OjNcCQ%3D%3D; '
              '__atuvc=7%7C12%2C134%7C13%2C17%7C14; __atuvs=5e865c568a99321e004',
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
              'KP_UID=b1f158dd-7352-106c-9cef-70c96b5c296e; _gid=GA1.3.1780907631.1585685551; _gat=1; '
              'KP_UIDz=%2FPyZIkcrGc5kIJ0hTnfB2w%3D%3D%3A%3AVtWI4XjoaD25'
              '%2BrxTiyDVnNyHkPljUaWcZIwvy8FOaePHiQkIqETm33klNh3NJ1F77xOffb749NslsQI7eyvRGI4XXrNUqWyEQVZchLT5lcVCgZw'
              '%2BKGcd8y1xhCz9yPXw7T5N%2BPm%2BnW4oAEC6WSHdYAzOk5pGeGCn4bHeo0DbTXS64Yv14w0%2BYCbhvAga'
              '%2FQtrBRiA0Ue9uu8fc4%2FkebQacrTjAsAB9MUsMGQaoF4VtStQ1tuyTgiZ0OUlzbRRFh1sYyEGbX5iamk9YwoKG3cENpVP'
              '%2F5XhYcG3N2%2FslwT7aii9Qm5DU8DF7kkfDlN6tQzW8Maokl3iJeBmGDeEbxoQcLEW%2BPMDYUiQBNs%2BqDqbjSXgvSO'
              '%2BqprM9pBepnulSf6De5qWaC%2FDnmH1OIkq0GdWSj3hUTC7fHbui%2FvjneCwY2WeahKfKTqM2GnMfmUe1NZd'
              '%2BTzQQMCDsfgphUCvntY%2BCgE4CtEa3gNgEqzNF%2Ff6xf5gWwjoeMbskdZH%2BaLbovx6MV9hpSv5ZPFbM908OjNcCQ%3D%3D; '
              '__atuvc=7%7C12%2C134%7C13%2C17%7C14; __atuvs=5e865c568a99321e004',
    'Sec-Fetch-Dest': 'document',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 '
                  'Safari/537.36 '
}

page = 1 if sys.argv[1] is None else sys.argv[1]

townships_url_template = 'https://www.brickz.my/transactions/residential/page/{}/?range=1992+JAN-'

townships_url = townships_url_template.format(str(page))

while True:

    print('-- Page', page, ':', townships_url, '--')

    try:
        request = requests.get(townships_url, headers=townships_headers, timeout=60)
    except:
        print('  Error Requesting Page:', townships_url)
        print('  Sleep for 10 seconds and retry')
        time.sleep(10)
        continue

    response = request.text

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

        print('  -- Township:', township['name'])

        url = township['url'].replace('?range=', 'view/map/?range=')
        browser = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver')
        browser.get(url)
        browser.add_cookie({'name': '_ga', 'value': 'GA1.3.906229850.1584801440'})
        browser.add_cookie({'name': 'PHPSESSID', 'value': '6bsrikeh7k5v65onjr2kh9m4b3'})
        browser.add_cookie({'name': '__atuvc', 'value': '7%7C12%2C134%7C13%2C9%7C14'})
        browser.add_cookie({'name': '__atuvs', 'value': '5e849ae5361ea20c000'})
        browser.add_cookie({'name': '_gat', 'value': '1'})
        browser.add_cookie({'name': 'KP_UIDz',
                            'value': 'fCV5zEoTsU5ZlSkVfr%2FJug%3D%3D%3A%3AQPXBC9gIkLH4N0Hb9K4%2FUQB2pmolDQ81fHZO%2FbGrgyBWURNFjh4pRsUEa74f20JNe4fUUqHZ8rcL7d3SNRoHwU6i%2FFn3oOj%2B2iig88MEmbrkcI5bPJsDrn%2BQf8mYEag0NpQhK3hruHSpc6vTiBzAllr%2F777Haon5rbMz5GL27ZM%2F00ifZTMBpqeHAW6Np%2FQYnM4FpQYIbnMWaSeb%2FU9faZdsxokokzL9yZe5UHiDmabPTxRF%2F8pXDUKaIRgfHR9HiD6C3XeJkKfdLEuGr0Z%2BemQjHHxZlFe94GROXh1KZ3o66yxEmeGSXQGyXVnHRO0xzr665tLfYOiS8SQPhwbVvw3bW%2FeJGbOghKTQ5vxUzfy%2Fg2GZxLV6Zxco%2BMIHeHxNhq%2FNeotLOVmVECvB0AIlNBR7rDjZa4G88Qm%2BTjEZZOsLt1RAQD0ZqXCGX4DrhlnWBB9Ldnz3XF%2BBO5xUIKmWBFJqFDLR8aBUxRw5hvIJg3XlF6zXRtbrB%2B%2BUJ5wtGr27'})
        browser.add_cookie({'name': 'KP_UID', 'value': 'b1f158dd-7352-106c-9cef-70c96b5c296e'})
        browser.add_cookie({'name': '_gid', 'value': 'GA1.3.1780907631.1585685551'})

        delay = 120
        while True:
            try:
                browser.refresh()
                myElem = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'gmnoscreen')))
                google_map = browser.find_element_by_xpath('//a[@title="Open this area in Google Maps (opens a new window)"]')
            except TimeoutException:
                print('    - Error Requesting Page:', url)
                print('    - Sleep for 10 seconds and retry')
                time.sleep(10)
            else:
                township['map_url'] = google_map.get_attribute('href')
                break

        if township['map_url']:
            map_host, map_uri = township['map_url'].split('?')
            map_query_parameters = map_uri.split('&')
            for map_query_parameter in map_query_parameters:
                map_query_key, map_query_value = map_query_parameter.split('=')
                if map_query_key == 'll':
                    map_coordinate_lat, map_coordinate_lng = map_query_value.split(',')
                    township['coordinate'] = {'lat': map_coordinate_lat, 'lng': map_coordinate_lng}

        session_datetime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        with open(data_directory + 'township/' + township['state'] + '_' + township['area'] + '_' + township['township']
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

        with open(data_directory + 'transaction/' + township['state'] + '_' + township['area'] + '_' + township[
            'township']
                  + '_' + township['category'] + '_' + str(session_datetime) + '.json', 'w') as json_file:
            json.dump(transactions, json_file)

    page = int(page) + 1
    townships_url = townships_url_template.format(str(page))
    # next_page = town_page_html.find('a', attrs={'class': 'next'})
    # if next_page:
    #     townships_url = next_page.get('href')
    # else:
    #     break
