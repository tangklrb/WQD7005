import os
import sys
import json
import pymongo
import datetime
import traceback
from pathlib import Path

mongo_host = "mongodb://localhost:27017/"
mongo_client = pymongo.MongoClient(mongo_host)
db = mongo_client.WQD7005
poi_table = db.iproperty_pois

data_directory = '../data/'
log = open('../data/iproperty_ingestion.log', 'a+')

program_start_time = datetime.datetime.now()
print('Program Start:', program_start_time, file=log, flush=True)

try:
    poi_dir = data_directory + 'new/iproperty/poi/'
    ingested_poi_dir = data_directory + 'ingested/iproperty/poi/'
    error_poi_dir = data_directory + 'error/iproperty/poi/'

    Path(ingested_poi_dir).mkdir(parents=True, exist_ok=True)
    Path(error_poi_dir).mkdir(parents=True, exist_ok=True)

    # read all json files crawled in milestone 1
    for filename in sorted(os.listdir(poi_dir)):
        if filename == 'README.md':
            continue

        poi_path = os.path.join(poi_dir, filename)
        poi_ingested_path = os.path.join(ingested_poi_dir, filename)
        poi_error_path = os.path.join(error_poi_dir, filename)

        try:
            with open(poi_path) as json_file:
                pois = json.load(json_file)

            # for each relevant poi, insert to mongodb if not exist and add into listing
            for poi in pois:
                poi_name = poi['name']
                poi_category = poi['category']
                poi_lat = poi['geometry']['location']['lat']
                poi_lng = poi['geometry']['location']['lng']

                # find if poi existed in mongodb
                existing_poi = poi_table.find_one({
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
                    print('Skipped, Existing Object ID', poi_id, file=log, flush=True)
                else:
                    # otherwise, insert as new POI
                    # remove distance as it's relevant to the listing but not a general information
                    del poi['distance']
                    del poi['distanceFloat']
                    poi_inserted_id = poi_table.insert_one(poi).inserted_id
                    print('Inserted, Object ID', poi_inserted_id, file=log, flush=True)

        except KeyboardInterrupt:
            print('Interrupted by user.', file=log, flush=True)
            exit(0)

        except:
            e = str(sys.exc_info()[0]) + str(sys.exc_info()[1]) + str(sys.exc_info()[2])
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print('Error:', filename, file=log, flush=True)
            print('Error:', e, file=log, flush=True)
            print('Error: Failed to ingest township information', file=log, flush=True)
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
            os.rename(poi_path, poi_error_path)
            continue

        # if successful, move the townships list json file to ingested folder
        os.rename(poi_path, poi_ingested_path)

except:
    print('Terminated.', file=log, flush=True)

finally:
    print(file=log, flush=True)
    program_end_time = datetime.datetime.now()
    print('Time Elapsed:', str(program_end_time - program_start_time), file=log, flush=True)
    print('Program End:', program_end_time, file=log, flush=True)
