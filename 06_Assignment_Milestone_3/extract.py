import pymongo
import pandas as pd
from pathlib import Path

mongo_host = "mongodb://localhost:27017/"
mongo_client = pymongo.MongoClient(mongo_host)
db = mongo_client.WQD7005

data_directory = '../data/processed'
Path(data_directory).mkdir(parents=True, exist_ok=True)

# extract townships data into csv files
# column to be extracted
# 'projectid', 'asset_id', 'lat', 'lon', 'project_name', 'state', 'area', 'street_name',
# 'fieldtransactions', 'psf', 'price'
# column to be ignored
# '_id', 'transacted_price', 'unit_price_psf', 'contract_date', 'propsubtype', 'tenure', 'floor', 'area_sqft',
# 'non_landed'
townships = pd.DataFrame(list(
    db.edgeprop_townships.aggregate([
        {
            '$project': {
                '_id': 0,
                'asset_id': 0,
                'project_name': 0,
                'street_name': 0,
                'transacted_price': 0,
                'unit_price_psf': 0,
                'contract_date': 0,
                'propsubtype': 0,
                'tenure': 0,
                'floor': 0,
                'area_sqft': 0,
                'fieldtransactions': 0,
                'non_landed': 0
            }
        }
    ])
))
townships.columns = [
    'project_id', 'latitude', 'longitude', 'state', 'area', 'median_psf', 'median_price'
]

# extract pois data into csv files
townships.to_csv(data_directory + '/edgeprop_township_extracted.csv', encoding='utf-8', index=False)

pois = pd.DataFrame(list(
    db.iproperty_pois.aggregate([
        {
            '$addFields': {
                'latitude': '$geometry.location.lat',
                'longitude': '$geometry.location.lng'
            }
        }, {
            '$project': {
                '_id': 0,
                'name': 1,
                'category': 1,
                'type': 1,
                'subType': 1,
                'lineName': 1,
                'latitude': 1,
                'longitude': 1
            }
        }
    ])
))
pois.columns = [
    'name', 'sub_type', 'category', 'line_name', 'type', 'latitude', 'longitude'
]

pois.to_csv(data_directory + '/iproperty_poi_extracted.csv', encoding='utf-8', index=False)

# extract transactions data into csv files
# columns to be extracted
# 'projectid', 'project_name', 'transacted_price', 'unit_price_psf', 'date',
# 'proptype', 'tenure', 'floor', 'area_sqft', 'non_landed', 'bedrooms',
# 'street_name', 'psf', 'price', 'state', 'planning_region'
transactions = pd.DataFrame(list(
    db.edgeprop_transactions.aggregate([
        {
            '$project': {
                '_id': 0,
                'project_name': 0,
                'street_name': 0
            }
        }
    ])
))
transactions.columns = [
    'project_id', 'transacted_price', 'unit_price_psf', 'date', 'property_type', 'tenure', 'floor', 'area_sqft',
    'non_landed', 'bedrooms', 'psf', 'price', 'state', 'planning_region'
]

transactions.to_csv(data_directory + '/edgeprop_transaction_extracted.csv', encoding='utf-8', index=False)

# print(transactions['planning_region'].value_counts())
# print(transactions['planning_region'].describe())
# print(transactions['planning_region'].isnull().sum())
