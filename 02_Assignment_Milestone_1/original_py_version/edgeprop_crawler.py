import json
import re
import sys
import requests
import datetime
from pathlib import Path


def format_url(input_string):
    if input_string is None:
        return 'null'
    return input_string.replace(' ', '%20').strip()


def format_slug(input_string):
    if input_string is None:
        return 'null'
    return re.sub(r'\W+', '-', input_string.strip().lower())


data_directory = '../data/'
township_data_directory = data_directory + 'new/edgeprop/townships/'
transaction_data_directory = data_directory + 'new/edgeprop/transactions/'
Path(township_data_directory).mkdir(parents=True, exist_ok=True)
Path(transaction_data_directory).mkdir(parents=True, exist_ok=True)
log = open('../data/edgeprop_crawler.log', 'a+')
coordinates = open('../data/township_coordinates.csv', 'a+')
max_crawl_retry = 5


def edgeprop_crawler(url):
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 '
                      'Safari/537.36 '
    }

    retry_count = 0
    while True:
        retry_count = retry_count + 1
        if retry_count >= max_crawl_retry:
            return None

        try:
            request = requests.get(url, headers=headers, timeout=60)
            request.raise_for_status()
            response = request.json()
        except requests.exceptions.HTTPError as errh:
            print('Http Error:', str(errh), '[Retry ' + str(retry_count) + ']', file=log, flush=True)
            continue
        except requests.exceptions.ConnectionError as errc:
            print('Error Connecting:', str(errc), '[Retry ' + str(retry_count) + ']', file=log, flush=True)
            continue
        except requests.exceptions.Timeout as errt:
            print('Timeout Error:', str(errt), '[Retry ' + str(retry_count) + ']', file=log, flush=True)
            continue
        except requests.exceptions.RequestException as err:
            print('Unknown Error:', str(err), '[Retry ' + str(retry_count) + ']', file=log, flush=True)
            continue
        except ValueError as jerr:
            print('Json Error:', str(jerr), '[Retry ' + str(retry_count) + ']', file=log, flush=True)
            continue
        else:
            return response


api_url = 'https://www.edgeprop.my/jwdalice/api/v1/transactions/'
townships_url_template = api_url + 'search?&category=RESIDENTIAL&state={}&datefrom={}&dateto={}&page={}&respp=10&key='
transactions_url_template = api_url + 'details?&category=RESIDENTIAL&state={}&area={}&datefrom={}&dateto={}&project={}&page={}&key='

states = [
    'JOHOR', 'KEDAH', 'KELANTAN', 'KUALA LUMPUR', 'LABUAN', 'MELAKA', 'NEGERI SEMBILAN', 'PAHANG',
    'PENANG', 'PERAK', 'PERLIS', 'PUTRAJAYA', 'SABAH', 'SARAWAK', 'SELANGOR', 'TERENGGANU'
]

jump_start_page = 0 if not len(sys.argv) > 1 else sys.argv[1]
jump_start_township = 0 if not len(sys.argv) > 2 else sys.argv[2]

print('Program Starts:', datetime.datetime.now(), file=log, flush=True)
for state in states:
    if jump_start_page > 0:
        page = jump_start_page
        jump_start_page = 0
    else:
        page = 1

    date_from = '2015-01-01'
    date_to = '2019-12-31'

    retry_count = 0
    township_count = (page - 1) * 10 + 1
    print('State:', state, file=log, flush=True)
    while True:
        # format - townships_url_template
        # 1: state
        # 2: dateFrom
        # 3: dateTo
        # 4: page
        townships_url = townships_url_template.format(format_url(state), date_from, date_to, str(page))
        print(' Page', page, ':', townships_url, file=log, flush=True)

        township_list = edgeprop_crawler(townships_url)

        if township_list is None:
            print('  Error Requesting Page:', townships_url, file=log, flush=True)
            print('  Try next page', file=log, flush=True)

            page = page + 1
            retry_count = retry_count + 1
            if retry_count >= max_crawl_retry:
                print('  Tried', retry_count, 'pages. Skipped to next state.', file=log, flush=True)
                break

            continue

        retry_count = 0
        total_pages = township_list['totalpages']
        total_townships = township_list['total']
        townships = township_list['property']

        if page == 1:
            print('  Total Townships:', total_townships, file=log, flush=True)
            print('  Total Pages:', total_pages, file=log, flush=True)

        if page > int(total_pages):
            break

        print('   Page', page, 'of', total_pages, file=log, flush=True)

        # Write townships to files
        with open(
                township_data_directory + format_slug(state) + '_' + date_from + '_' + date_to + '_' +
                str(page) + '_' + 'of' + '_' + str(total_pages) + '.json', 'w'
        ) as json_file:
            json.dump(townships, json_file)

        for township in townships:
            # Additional control if going to manually re-run the crawler & skipping certain townships
            if jump_start_township > 0:
                if township_count < jump_start_township:
                    township_count = township_count + 1
                    continue
            else:
                jump_start_township = 0

            # transactions_url_template
            # 1: state
            # 2: area
            # 3: dateFrom
            # 4: dateTo
            # 5: project
            # 6: page
            area = township['area']
            transaction_date_from = date_from
            transaction_date_to = date_to
            project = township['project_name']
            asset_id = township['asset_id']
            latitude = township['lat']
            longitude = township['lon']
            filed_transaction_count = township['fieldtransactions']
            transaction_page = 1

            print('    ' + str(township_count) + '.', 'Township:', project,
                  '- Estimated', filed_transaction_count, 'Transactions', file=log, flush=True)

            if int(filed_transaction_count) > 0:
                retry_count = 0
                crawled_transaction_count = 0
                crawled_page_count = 0

                # print coordinates to files for POI crawler
                print(str(latitude) + "," + str(longitude), file=coordinates, flush=True)

                while True:
                    transactions_url = transactions_url_template.format(
                        format_url(state), format_url(area), transaction_date_from, transaction_date_to,
                        format_url(project), str(transaction_page)
                    )

                    print('     Date To:', transaction_date_to, ':', transactions_url, file=log, flush=True)

                    transaction_list = edgeprop_crawler(transactions_url)
                    if transaction_list is None:
                        print('      Error Requesting Page:', transactions_url, file=log, flush=True)

                        retry_count = retry_count + 1
                        if retry_count >= max_crawl_retry:
                            print('      Tried', retry_count, 'times. Skipped to next township.', file=log, flush=True)
                            break

                        continue

                    retry_count = 0
                    total_transaction_pages = transaction_list['totalpages']
                    transactions = transaction_list['property']

                    if len(transactions) == 0:
                        break

                    oldest_transaction = transactions[-1]

                    crawled_transaction_count = crawled_transaction_count + len(transactions)
                    crawled_page_count = crawled_page_count + 1

                    print('      Crawled', crawled_page_count,
                          'pages with', crawled_transaction_count, 'transactions', file=log, flush=True)

                    # write transactions to files
                    with open(
                            transaction_data_directory + str(asset_id) + '_' + format_slug(project) + '_' +
                            transaction_date_to + '_' + str(crawled_transaction_count) + '.json', 'w'
                    ) as json_file:
                        json.dump(transactions, json_file)

                    if total_transaction_pages == 1:
                        break

                    date_from_unixtimestamp = datetime.datetime.strptime(transaction_date_from, '%Y-%m-%d')
                    previous_date_to_unixtimestamp = datetime.datetime.strptime(transaction_date_to, '%Y-%m-%d')
                    new_date_to_unixtimestamp = datetime.datetime.utcfromtimestamp(oldest_transaction['date'])

                    if previous_date_to_unixtimestamp == new_date_to_unixtimestamp:
                        if date_from_unixtimestamp == new_date_to_unixtimestamp:
                            break
                        else:
                            new_date_to_unixtimestamp = new_date_to_unixtimestamp - datetime.timedelta(days = 1)

                    transaction_date_to = new_date_to_unixtimestamp.strftime('%Y-%m-%d')

            township_count = township_count + 1

        page = page + 1
print('Program Ends:', datetime.datetime.now(), file=log, flush=True)
