import json
import numpy as np
import pandas as pd
from geopy.distance import distance
from flask import Flask, render_template, request
app = Flask(__name__)

@app.route("/")
def map():
  return render_template('main.html')


@app.route('/nearby-cities/', methods=['GET'])
def nearby_cities():
  target_coordinate = (request.args.get('lat'), request.args.get('lng'))

  townships = pd.read_csv('../data/processed/edgeprop_townships_preprocessed.csv')
  townships['coordinates'] = list(zip(townships['latitude'], townships['longitude']))

  townships['distance'] = townships['coordinates'].apply(
    lambda x: calc_distance(x, target_coordinate)
  )

  # return all cities within 15km
  nearby_cities = townships[townships['distance'] <= 5000][
    ['area', 'distance']
  ].groupby('area').min().reset_index().sort_values('distance')

  return (json.dumps(list(nearby_cities['area'])))


# calculate distance between two points
def calc_distance(source, target):
  return (distance(source, target).m)


@app.route('/nearest-poi/', methods=['GET'])
def nearest_poi():
  target_coordinate = (request.args.get('lat'), request.args.get('lng'))

  pois = pd.read_csv('../data/processed/iproperty_pois_preprocessed.csv')
  pois['coordinates'] = list(zip(pois['latitude'], pois['longitude']))

  pois['distance'] = pois['coordinates'].apply(
    lambda x: calc_distance(x, target_coordinate)
  )

  return(json.dumps({
    'nearest_poi': pois['distance'].min()
  }))


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8899, debug=True)
