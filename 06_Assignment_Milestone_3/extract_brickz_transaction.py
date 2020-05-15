import pymongo
import pandas as pd
from pathlib import Path

mongo_host = "mongodb://localhost:27017/"
mongo_client = pymongo.MongoClient(mongo_host)
db = mongo_client.WQD7005_Assignment

data_directory = '../data/brickz_transaction/'
extract_township_dir = data_directory + 'extract/township'
Path(extract_township_dir).mkdir(parents=True, exist_ok=True)

townships = pd.DataFrame(list(
    db.brickz_townships.aggregate([
        {
            '$addFields': {
                'latitude': '$coordinate.lat',
                'longitude': '$coordinate.lng'
            }
        }, {
            '$project': {
                '_id': 0,
                'name': 0,
                'url': 0,
                'map_url': 0,
                'coordinate': 0,
                'id': 0,
                'transaction': 0
            }
        }
    ])
))

townships.to_csv(extract_township_dir + '/brickz_township.csv', encoding='utf-8', index=False)
