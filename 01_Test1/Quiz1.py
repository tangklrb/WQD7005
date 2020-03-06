import os
import requests
from bs4 import BeautifulSoup

host = 'https://www.malaysiastock.biz/'
# alphabets = '0ABCDEFGHIJKLMNOPQRSTUVWXYZ'
alphabets = input('Enter Alphabets: ')

for c in alphabets:
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X '
                             '10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/72.0.3626.109 Safari/537.36'}

    my_url = 'https://www.malaysiastock.biz/Market-Watch.aspx?type=A&value={}'
    url = my_url.format(c)

    list_src = requests.get(url, headers=headers).text
    list_bs4 = BeautifulSoup(list_src, 'html.parser')

    done = False
    for url in list_bs4.select('table#MainContent_tbStockWithAlphabet > tr > td > span > a'):
        print('Scraping '+url.get('href'))
        filename = url.get('href').split('=')[-1] + '.csv'
        with open(filename, 'w', encoding="utf-8") as f:
            stock_src = requests.get(host + url.get('href'), headers=headers).text
            stock = BeautifulSoup(stock_src, 'html.parser')
            for history in stock.select('table#MainContent_gvReport > tr'):
                done = True
                for column in history.select('td'):
                    if column.get('colspan'):
                        break
                    else:
                        if column.find(lambda t: t.name == 'label'):
                            if column.find('img').get('src') == 'App_Themes/images/trend0.ico':
                                trend = '↓'
                            elif column.find('img').get('src') == 'App_Themes/images/trend1.ico':
                                trend = '↑'
                            else:
                                trend = '-'
                            percentage = column.find('label').text
                            print(trend, percentage, file=f)
                        else:
                            print(column.text.replace(',', ''), end=', ', file=f)
        if not done:
            print("Not parent stock, ignored!")
            os.remove(filename)

        # do it on 1 company only
        if done:
            print("Saved!")
            break

    # do it for 1 alphabet only
    break

