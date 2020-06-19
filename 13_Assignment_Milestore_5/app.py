import json
import pickle
import numpy as np
import pandas as pd
from geopy.distance import distance
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.compose import make_column_transformer
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression
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


@app.route('/nearby-townships/', methods=['GET'])
def nearby_townships():
  target_coordinate = (request.args.get('lat'), request.args.get('lng'))

  townships = pd.read_csv('../data/processed/edgeprop_townships_preprocessed.csv')
  townships['coordinates'] = list(zip(townships['latitude'], townships['longitude']))

  townships['distance'] = townships['coordinates'].apply(
    lambda x: calc_distance(x, target_coordinate)
  )

  # return all townships within 2km
  nearby_townships_2km = townships[townships['distance'] <= 2000][
    ['project_id', 'township', 'distance']
  ].groupby('project_id').min().reset_index().sort_values('distance')

  return (json.dumps(nearby_townships_2km.to_dict('records')))


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

@app.route('/predict-price/', methods=['POST'])
def predict_price():
  if request.method == "POST":
    data = request.form
    error_messages = list()

    if not is_float(data['area_sqft']):
      error_messages.append("Please enter a valid number for Area (sqft)")

    # if len(data['city']) == 0:
    #   error_messages.append("Coverage: Kuala Lumpur, Selangor, Penang & Johor only. Please pick the property location from map and select the nearest city")

    if len(data['project_id']) == 0:
      error_messages.append("Coverage: Kuala Lumpur, Selangor, Penang & Johor only. Please pick the property location from map and select the nearest city")

    if len(error_messages) > 0:
      return (json.dumps({
        "status": "Error",
        "message": "<br/>".join(error_messages)
      }))

    input_features = pd.DataFrame([data])
    input_features['state'] = input_features['project_id'].apply(state_lookup)
    input_features['city'] = input_features['project_id'].apply(city_lookup)
    input_features['project_id'] = input_features['project_id'].astype('int')

    print(input_features)

    model = pickle.load(open('../data/model.pkl', 'rb'))
    predicted_price = model.predict(input_features)

    return ({
      "status": "Predicted Price",
      "message": '{:,.2f}'.format(predicted_price[0])
    })
  else:
    return ('{ "status": "Error", "message": "No data are posted"}')


def state_lookup(township_id):
  township_id = int(township_id)
  townships = pd.read_csv('../data/processed/edgeprop_townships_preprocessed.csv').drop_duplicates(
    subset='project_id', keep="first"
  )

  results = townships[townships['project_id'] == township_id]

  return results['state'].iloc[0]


def city_lookup(township_id):
  township_id = int(township_id)
  townships = pd.read_csv('../data/processed/edgeprop_townships_preprocessed.csv').drop_duplicates(
    subset='project_id', keep="first"
  )

  results = townships[townships['project_id'] == township_id]

  return results['area'].iloc[0]


def is_float(n):
  try:
    float(n)
    return True
  except ValueError:
    return False


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8888, debug=True)
