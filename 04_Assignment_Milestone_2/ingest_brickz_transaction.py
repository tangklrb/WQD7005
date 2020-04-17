import os
import sys
import json
import pymongo
import datetime
import traceback
from pathlib import Path

mongo_host = "mongodb://localhost:27017/"
mongo_client = pymongo.MongoClient(mongo_host)
db = mongo_client.WQD7005_Assignment
township_tbl = db.brickz_townships

data_directory = '../data/brickz_transaction/'
log = open('../data/ingest_brickz_transaction.log', 'a+')

program_start_time = datetime.datetime.now()
print('Program Start:', program_start_time, file=log, flush=True)

try:
    township_dir = data_directory + 'new/township'
    transaction_dir = data_directory + 'new/transaction'
    ingested_township_dir = data_directory + 'ingested/township'
    ingested_transaction_dir = data_directory + 'ingested/transaction'
    error_township_dir = data_directory + 'error/township'
    error_transaction_dir = data_directory + 'error/transaction'

    Path(ingested_township_dir).mkdir(parents=True, exist_ok=True)
    Path(ingested_transaction_dir).mkdir(parents=True, exist_ok=True)
    Path(error_township_dir).mkdir(parents=True, exist_ok=True)
    Path(error_transaction_dir).mkdir(parents=True, exist_ok=True)

    # read all json files crawled in milestone 1
    for filename in sorted(os.listdir(township_dir)):
        if filename == 'README.md':
            continue
        
        township_path = os.path.join(township_dir, filename)
        township_ingested_path = os.path.join(ingested_township_dir, filename)
        township_error_path = os.path.join(error_township_dir, filename)
        transaction_path = os.path.join(transaction_dir, filename)
        transaction_ingested_path = os.path.join(ingested_transaction_dir, filename)
        transaction_error_path = os.path.join(error_transaction_dir, filename)

        try:
            with open(township_path) as json_file:
                township = json.load(json_file)

            transactions = list()
            if os.path.isfile(transaction_path):
                with open(transaction_path) as json_file:
                    transactions = json.load(json_file)
            else:
                print('No Transaction found', file=log, flush=True)

            print('Preparing to ingest transactions into Data Lake', filename, file=log, flush=True)
            # session_postfix = filename[filename.rfind('_'):].replace('.json', '')
            township_id = filename[:filename.rfind('_')].replace('.json', '')

            # add the transaction information to the township
            township['id'] = township_id
            township['transaction'] = transactions

            # insert or update the township into mongodb
            township_inserted_id = township_tbl.replace_one({'id': township_id}, township, upsert=True).upserted_id
            if township_inserted_id is not None:
                print('Inserted, Object ID', township_inserted_id, file=log, flush=True)
            else:
                existing_township = township_tbl.find_one({'id': township_id})
                township_updated_id = existing_township.get('_id')
                print('Updated, Object ID', township_updated_id, file=log, flush=True)

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
            # move the townships/transaction json file to error folder
            os.rename(township_path, township_error_path)
            os.rename(transaction_path, transaction_error_path)
            continue

        # if successful, move the townships/transaction json file to ingested folder
        os.rename(township_path, township_ingested_path)
        os.rename(transaction_path, transaction_ingested_path)

except:
    print('Terminated.', file=log, flush=True)

finally:
    print(file=log, flush=True)
    program_end_time = datetime.datetime.now()
    print('Time Elapsed:', str(program_end_time - program_start_time), file=log, flush=True)
    print('Program End:', program_end_time, file=log, flush=True)
