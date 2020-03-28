import os
import sys
import json
import traceback
import requests
import datetime

data_directory = '../data/iproperty_listing/'
reaasia_graphql_api = 'https://raptor.rea-asia.com/v1/graphql'
log = open('../data/crawl_iproperty_listing.log', 'a+')
max_crawl_retry = 5
sub_dir = sys.argv[1]

def crawl_poi(gps_coordinate, category=None, ref_url=None):
    api = reaasia_graphql_api

    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-GB',
        'content-type': 'application/json',
        'market': 'MY',
        'origin': 'https://www.iproperty.com.my',
        'referer': ref_url,
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
        'x-market': 'ipropertymy'
    }

    page_size = 100
    payload = {
        'operationName': None,
        'variables': {
            'lang': 'enGB',
            'location': str(gps_coordinate['Latitude']) + ',' + str(gps_coordinate['Longitude']),
            'radius': 3000,
            'pageSize': page_size,
            'category': category
        },
        'query': 'query ($lang: AcceptLanguage, $location: String!, $radius: Int, $pageSize: Int, $category: PoiCategory) {\n  pois(location: $location, radius: $radius, pageSize: $pageSize, category: $category, lang: $lang) {\n    items {\n      name\n      subTypeLabel\n      subTypeExtra\n      geometry {\n        location {\n          lat\n          lng\n          __typename\n        }\n        __typename\n      }\n      subType\n      category\n      lineName\n      placeId\n      distance\n      distanceFloat\n      completionYear\n      type\n      city\n      district\n      publicType\n      curriculumOffered\n      __typename\n    }\n    __typename\n  }\n}\n'
    }

    print('Crawl: POI(' + category + '),', 'From', ref_url, file=log, flush=True)
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
            print('Http Error:', errh, '[Retry ' + str(retry_count) + ']')
        except requests.exceptions.ConnectionError as errc:
            print('Error Connecting:', errc, '[Retry ' + str(retry_count) + ']')
        except requests.exceptions.Timeout as errt:
            print('Timeout Error:', errt, '[Retry ' + str(retry_count) + ']')
        except requests.exceptions.RequestException as err:
            print('Unknown Error:', err, '[Retry ' + str(retry_count) + ']')
        else:
            return response

    return response


program_start_time = datetime.datetime.now()
print('Program Start:', program_start_time, file=log, flush=True)

try:
    listing_dir = data_directory + 'existing_listing/' + sub_dir
    crawled_listing_dir = data_directory + 'crawled_listing'
    for listing_file in os.listdir(listing_dir):
        with open(os.path.join(listing_dir, listing_file)) as json_file:
            current_listing = json.load(json_file)

        print('Crawl POI for previously downloaded Listings', listing_file, file=log, flush=True)
        filename = listing_file.replace('.json', '').split('_')
        # session_datetime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        session_datetime = filename[2]

        for listing in current_listing:
            try:
                listing_id = listing['id']
                listing_url = listing['shareLink']
                listing_gps_coordinate = {
                    'Latitude': listing['address']['lat'],
                    'Longitude': listing['address']['lng']
                }

                if listing['address']['lat'] is None or listing['address']['lng'] is None:
                    print('Skipped:', listing_url, file=log, flush=True)
                    print('Reason: Invalid GPS Coordinates', listing_gps_coordinate, file=log, flush=True)
                    continue

                # crawl POIs by listing
                poi_categories = ['education', 'healthcare', 'transportation']

                for category in poi_categories:
                    poi_list = list()
                    response = crawl_poi(listing_gps_coordinate, category, listing_url)
                    try:
                        poi_list = poi_list + response['data']['pois']['items']
                    except:
                        e = str(sys.exc_info()[0]) + str(sys.exc_info()[1]) + str(sys.exc_info()[2])
                        print('Error:', e, file=log, flush=True)
                        print('Error: Skipped and proceed for next POI category', file=log, flush=True)
                        continue

                    with open(data_directory + 'poi/' + listing_id + '_' + category + '_' +
                              str(session_datetime) + '.json', 'w') as json_file:
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

        os.rename(os.path.join(listing_dir, listing_file), os.path.join(crawled_listing_dir, listing_file))

except:
    print('Terminated.', file=log, flush=True)

finally:
    print(file=log, flush=True)
    program_end_time = datetime.datetime.now()
    print('Time Elapsed:', str(program_end_time - program_start_time), file=log, flush=True)
    print('Program End:', program_end_time, file=log, flush=True)
