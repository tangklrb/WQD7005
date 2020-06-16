import sys
import json
import traceback
import requests
import datetime
import pandas as pd
from pathlib import Path


data_directory = '../data/'
poi_data_directory = data_directory + 'new/iproperty/poi/'
Path(poi_data_directory).mkdir(parents=True, exist_ok=True)
log = open('../data/iproperty_crawler.log', 'a+')
coordinates = pd.read_csv('../data/township_coordinates.csv', na_values=['None', '0'], names=['latitude', 'longitude'])
max_crawl_retry = 5


def crawl_poi(latitude, longitude, category=None):
    api = 'https://raptor.rea-asia.com/v1/graphql'

    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-GB',
        'content-type': 'application/json',
        'market': 'MY',
        'origin': 'https://www.iproperty.com.my',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
        'x-market': 'ipropertymy'
    }

    payload = {
        'operationName': None,
        'variables': {
            'lang': 'enGB',
            'location': str(latitude) + ',' + str(longitude),
            'radius': 5000,
            'pageSize': 100,
            'category': category
        },
        'query': 'query ($lang: AcceptLanguage, $location: String!, $radius: Int, $pageSize: Int, $category: PoiCategory) {\n  pois(location: $location, radius: $radius, pageSize: $pageSize, category: $category, lang: $lang) {\n    items {\n      name\n      subTypeLabel\n      subTypeExtra\n      geometry {\n        location {\n          lat\n          lng\n          __typename\n        }\n        __typename\n      }\n      subType\n      category\n      lineName\n      placeId\n      distance\n      distanceFloat\n      completionYear\n      type\n      city\n      district\n      publicType\n      curriculumOffered\n      __typename\n    }\n    __typename\n  }\n}\n'
    }

    retry_count = 0

    while True:
        retry_count = retry_count + 1
        if retry_count >= max_crawl_retry:
            return None

        try:
            request = requests.post(api, headers=headers, data=json.dumps(payload), timeout=30)
            request.raise_for_status()
            response = request.json()
        except requests.exceptions.HTTPError as errh:
            print('Http Error:', errh, '[Retry ' + str(retry_count) + ']', file=log, flush=True)
        except requests.exceptions.ConnectionError as errc:
            print('Error Connecting:', errc, '[Retry ' + str(retry_count) + ']', file=log, flush=True)
        except requests.exceptions.Timeout as errt:
            print('Timeout Error:', errt, '[Retry ' + str(retry_count) + ']', file=log, flush=True)
        except requests.exceptions.RequestException as err:
            print('Unknown Error:', err, '[Retry ' + str(retry_count) + ']', file=log, flush=True)
        else:
            return response



program_start_time = datetime.datetime.now()
print('Program Start:', program_start_time, file=log, flush=True)

try:
    for index, coordinate in coordinates.iterrows():
        try:
            latitude = coordinate['latitude']
            longitude = coordinate['longitude']

            if pd.isna(latitude) or pd.isna(longitude):
                print('Skipped: Invalid GPS Coordinates', latitude, ',', longitude, file=log, flush=True)
                continue

            # crawl POIs by listing
            poi_categories = ['education', 'healthcare', 'transportation']

            print('Crawling POI near by', latitude, ',', longitude, file=log, flush=True)
            for category in poi_categories:
                poi_list = list()
                response = crawl_poi(latitude, longitude, category)
                try:
                    poi_list = poi_list + response['data']['pois']['items']
                except:
                    e = str(sys.exc_info()[0]) + str(sys.exc_info()[1]) + str(sys.exc_info()[2])
                    print('Error:', e, file=log, flush=True)
                    print('Error: Skipped and proceed for next POI category', file=log, flush=True)
                    continue

                with open(poi_data_directory + str(latitude) + '_' + str(longitude) + '_' + category + '.json', 'w') as json_file:
                    json.dump(poi_list, json_file)

        except KeyboardInterrupt:
            print('Interrupted by user.', file=log, flush=True)
            exit(0)

        except:
            e = str(sys.exc_info()[0]) + str(sys.exc_info()[1]) + str(sys.exc_info()[2])
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print('Error:', e, file=log, flush=True)
            print('Error: Failed to get listing information', file=log, flush=True)
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)

except:
    print('Terminated.', file=log, flush=True)

finally:
    print(file=log, flush=True)
    program_end_time = datetime.datetime.now()
    print('Time Elapsed:', str(program_end_time - program_start_time), file=log, flush=True)
    print('Program End:', program_end_time, file=log, flush=True)
