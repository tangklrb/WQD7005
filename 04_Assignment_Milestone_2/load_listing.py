import os
import sys
import json
import pymongo
import datetime
import traceback

mongo_host = "mongodb://localhost:27017/"
mongo_client = pymongo.MongoClient(mongo_host)
db_name = 'wqd7005_iproperty_listing'
listing_tbl_name = 'listings'
poi_tbl_name = 'pois'
db = mongo_client.wqd7005_iproperty_listing
listing_tbl = db.listings
poi_tbl = db.pois

data_directory = '../data/crawl_listing_search/'
log = open('load_listing_search.log', 'a+')

program_start_time = datetime.datetime.now()
print('Program Start:', program_start_time, file=log, flush=True)

try:
    poi_dir = data_directory + 'poi'
    listing_dir = data_directory + 'listing'
    loaded_poi_dir = data_directory + 'loaded/poi'
    loaded_listing_dir = data_directory + 'loaded/listing'
    not_loaded_poi_dir = data_directory + 'not_loaded/poi'
    not_loaded_listing_dir = data_directory + 'not_loaded/listing'

    # read all json files crawled in milestone 1
    for listing_file in os.listdir(listing_dir):
        with open(os.path.join(listing_dir, listing_file)) as json_file:
            current_listing = json.load(json_file)

        print('Preparing to load Listings into Data Lake', listing_file, file=log, flush=True)
        filename = listing_file.replace('.json', '').split('_')
        session_postfix = filename[2]

        # load each listing and the relevant pois into mongo db
        for listing in current_listing:
            try:
                listing_id = listing['id']
                print('Loading Listing:', listing_id, file=log, flush=True)

                # include poi summary into listing
                listing_poi = {}
                poi_categories = ['education', 'healthcare', 'transportation']

                # link the listing to the relevant poi crawled previously
                for category in poi_categories:
                    try:
                        listing_poi_list = list()
                        poi_filename = listing_id + '_' + category + '_' + str(session_postfix) + '.json'
                        poi_path = os.path.join(poi_dir, poi_filename)
                        if os.path.isfile(poi_path):
                            with open(poi_path) as json_file:
                                pois = json.load(json_file)

                            # for each relevant poi, insert to mongodb if not exist and add into listing
                            for poi in pois:
                                poi_name = poi['name']
                                poi_category = poi['category']
                                poi_lat = poi['geometry']['location']['lat']
                                poi_lng = poi['geometry']['location']['lng']
                                poi_distance = poi['distanceFloat']

                                # find if poi existed in mongodb
                                existing_poi = poi_tbl.find_one({
                                    'name': poi_name,
                                    'category': poi_category,
                                    'geometry': {
                                        'location': {
                                            'lat': poi_lat,
                                            'lng': poi_lng,
                                            '__typename': 'Location'
                                        },
                                        '__typename': 'Geometry'
                                    }
                                })

                                if existing_poi:
                                    # if exist, get the existing object ID
                                    poi_id = existing_poi.get('_id')
                                else:
                                    # otherwise, insert as new POI
                                    # remove distance as it's relative to the listing but not a general information
                                    del poi['distance']
                                    del poi['distanceFloat']
                                    poi_id = poi_tbl.insert_one(poi).inserted_id

                                # add attributes in listing to store poi information and the distance to the poi
                                listing_poi_list.append({
                                    'name': poi['name'],
                                    'distance': poi_distance,
                                    'id': str(poi_id)
                                })
                            listing_poi[category] = listing_poi_list

                            # move the poi json file to success folder
                            os.rename(poi_path, os.path.join(loaded_poi_dir, poi_filename))
                        else:
                            print('No Poi found', file=log, flush=True)
                    except:
                        # if error, move the poi json file to error folder
                        if os.path.isfile(poi_path):
                            os.rename(poi_path, os.path.join(not_loaded_poi_dir, poi_filename))
                        e = str(sys.exc_info()[0]) + str(sys.exc_info()[1]) + str(sys.exc_info()[2])
                        print('Error:', e, file=log, flush=True)
                        print('Error: Unable to insert/update POI details, proceed for next category', file=log, flush=True)
                        continue

                # add the poi information to the listing
                listing['poi'] = listing_poi
                # insert or update the listing into mongodb
                listing_inserted_id = listing_tbl.replace_one({'id': listing_id}, listing, upsert=True).upserted_id
                if listing_inserted_id is not None:
                    print('Inserted, Object ID', listing_inserted_id, file=log, flush=True)
                else:
                    existing_listing = listing_tbl.find_one({'id': listing_id})
                    listing_updated_id = existing_listing.get('_id')
                    print('Updated, Object ID', listing_updated_id, file=log, flush=True)

            except KeyboardInterrupt:
                print('Interrupted by user.', file=log, flush=True)
                exit(0)

            except:
                e = str(sys.exc_info()[0]) + str(sys.exc_info()[1]) + str(sys.exc_info()[2])
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print('Error:', e, file=log, flush=True)
                print('Error: Failed to load listing information', file=log, flush=True)
                traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
                # move the listings json file to error folder
                os.rename(os.path.join(listing_dir, listing_file), os.path.join(not_loaded_listing_dir, listing_file))
                continue

        # if successful, move the listings json file to success folder
        os.rename(os.path.join(listing_dir, listing_file), os.path.join(loaded_listing_dir, listing_file))

except:
    print('Terminated.', file=log, flush=True)

finally:
    print(file=log, flush=True)
    program_end_time = datetime.datetime.now()
    print('Time Elapsed:', str(program_end_time - program_start_time), file=log, flush=True)
    print('Program End:', program_end_time, file=log, flush=True)
