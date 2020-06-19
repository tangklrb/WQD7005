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
township_table = db.edgeprop_townships
transaction_table = db.edgeprop_transactions

data_directory = '../data/'
log = open('../data/edgeprop_ingestion.log', 'a+')

program_start_time = datetime.datetime.now()
print('Program Start:', program_start_time, file=log, flush=True)

try:
    township_dir = data_directory + 'new/edgeprop/townships/'
    transaction_dir = data_directory + 'new/edgeprop/transactions/'
    ingested_township_dir = data_directory + 'ingested/edgeprop/townships/'
    ingested_transaction_dir = data_directory + 'ingested/edgeprop/transactions/'
    error_township_dir = data_directory + 'error/edgeprop/townships/'
    error_transaction_dir = data_directory + 'error/edgeprop/transactions/'

    Path(ingested_township_dir).mkdir(parents=True, exist_ok=True)
    Path(ingested_transaction_dir).mkdir(parents=True, exist_ok=True)
    Path(error_township_dir).mkdir(parents=True, exist_ok=True)
    Path(error_transaction_dir).mkdir(parents=True, exist_ok=True)

    # read all township lists crawled in milestone 1
    for filename in sorted(os.listdir(township_dir)):
        if filename == 'README.md':
            continue
        
        township_path = os.path.join(township_dir, filename)
        township_ingested_path = os.path.join(ingested_township_dir, filename)
        township_error_path = os.path.join(error_township_dir, filename)

        try:
            with open(township_path) as json_file:
                townships = json.load(json_file)

            print('Preparing to ingest townships into Document Data Store', filename, file=log, flush=True)

            for township in townships:
                # insert or update the township into mongodb
                township_inserted_id = township_table.replace_one(
                    {'id': township['projectid']}, township, upsert=True
                ).upserted_id
                if township_inserted_id is not None:
                    print('Inserted, Object ID', township_inserted_id, file=log, flush=True)
                else:
                    existing_township = township_table.find_one({'id': township['projectid']})
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
            os.rename(township_path, township_error_path)
            continue

        # if successful, move the townships list json file to ingested folder
        os.rename(township_path, township_ingested_path)

    # read all transaction lists crawled in milestone 1
    for filename in sorted(os.listdir(transaction_dir)):
        if filename == 'README.md':
            continue

        transaction_path = os.path.join(transaction_dir, filename)
        transaction_ingested_path = os.path.join(ingested_transaction_dir, filename)
        transaction_error_path = os.path.join(error_transaction_dir, filename)

        try:
            with open(transaction_path) as json_file:
                transactions = json.load(json_file)

            print('Preparing to ingest transactions into Document Data Store', filename, file=log, flush=True)

            for transaction in transactions:
                # insert the transaction into mongodb
                transaction_inserted_id = transaction_table.insert_one(transaction).inserted_id
                print('Inserted, Object ID', transaction_inserted_id, file=log, flush=True)

        except KeyboardInterrupt:
            print('Interrupted by user.', file=log, flush=True)
            exit(0)

        except:
            e = str(sys.exc_info()[0]) + str(sys.exc_info()[1]) + str(sys.exc_info()[2])
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print('Error:', filename, file=log, flush=True)
            print('Error:', e, file=log, flush=True)
            print('Error: Failed to ingest transaction information', file=log, flush=True)
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
            os.rename(transaction_path, transaction_error_path)
            continue

        # if successful, move the transaction list json file to ingested folder
        os.rename(transaction_path, transaction_ingested_path)

except:
    print('Terminated.', file=log, flush=True)

finally:
    print(file=log, flush=True)
    program_end_time = datetime.datetime.now()
    print('Time Elapsed:', str(program_end_time - program_start_time), file=log, flush=True)
    print('Program End:', program_end_time, file=log, flush=True)
