import re
import sys
import html5lib
import requests
from bs4 import BeautifulSoup

url = 'https://www.malaysiastock.biz/Corporate-Infomation.aspx?securityCode='
code = input('Enter Stock Code: ')

stock_src = requests.get(url + code).text
stock = BeautifulSoup(stock_src, 'html.parser')

with open(code + '.csv', 'w', encoding="utf-8") as f:
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
                    print(trend, percentage, file=f)
                else:
                    print(column.text.replace(',', ''), end=', ', file=f)


