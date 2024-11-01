import pandas as pd
from pymongo import MongoClient
import json

def import_dataframe_to_mongo(json_file_path, connection_string, database, collection_name):

    # Connect to MongoDB
    client = MongoClient(connection_string)
    
    # Specify the database and collection
    db = client[database]
    collection = db[collection_name]
    
    # Drop the collection if it exists
    collection.drop()
    
    # Load the JSON data from the file
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Insert data into MongoDB
    collection.insert_many(data)
    
    print(f"Data imported successfully into {collection_name}!")