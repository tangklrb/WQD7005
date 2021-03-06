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


@app.route('/nearby-townships/', methods=['GET'])
def nearby_townships():
  target_coordinate = (request.args.get('lat'), request.args.get('lng'))

  townships = pd.read_csv('../data/processed/edgeprop_townships_preprocessed.csv')
  transactions = pd.read_csv('../data/processed/edgeprop_transactions_processed.csv')

  townships = pd.merge(
    townships,
    transactions.drop_duplicates(subset=['project_id']),
    on='project_id',
    how='inner',
    suffixes=('', '_2')
  )

  townships['coordinates'] = list(zip(townships['latitude'], townships['longitude']))

  townships['distance'] = townships['coordinates'].apply(
    lambda x: calc_distance(x, target_coordinate)
  )

  # return all townships within 2km, limit to 15 options only
  nearby_townships_2km = townships[townships['distance'] <= 2000][
    ['project_id', 'township', 'distance']
  ].groupby('project_id').min().reset_index().sort_values('distance')

  return (json.dumps(nearby_townships_2km.head(15).to_dict('records')))


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

    if len(data['project_id']) == 0:
      error_messages.append("Coverage: Kuala Lumpur, Selangor, Penang & Johor only. Please pick the property location from map and select the nearest city")

    if len(error_messages) > 0:
      return (json.dumps({
        "status": "Error",
        "message": "<br/>".join(error_messages)
      }))

    input_features = pd.DataFrame([data])
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


def is_float(n):
  try:
    float(n)
    return True
  except ValueError:
    return False


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8888, debug=True)
