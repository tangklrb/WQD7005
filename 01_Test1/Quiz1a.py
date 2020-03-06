import re
import sys
import html5lib
import requests
from bs4 import BeautifulSoup

host = 'https://www.malaysiastock.biz/'
list_src = requests.get('https://www.malaysiastock.biz/Market-Watch.aspx?type=A&value=C').text
# print(sc)
list_bs4 = BeautifulSoup(list_src, 'html.parser')
for url in list_bs4.select('table#MainContent_tbStockWithAlphabet > tr > td > span > a'):
    print(url.get('href'))
    stock_src = requests.get(host + url.get('href')).text
    stock = BeautifulSoup(stock_src, 'html.parser')
    for history in stock.select('table#MainContent_gvReport > tr'):
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
                    print(trend, percentage)
                else:
                    print(column.text.replace(',', ''), end=', ')
    print()

