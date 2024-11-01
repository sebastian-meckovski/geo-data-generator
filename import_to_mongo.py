import pandas as pd
from pymongo import MongoClient
import json

def import_dataframe_to_mongo(data, connection_string, database, collection_name):

    # Connect to MongoDB
    client = MongoClient(connection_string)
    
    # Specify the database and collection
    db = client[database]
    collection = db[collection_name]
    
    # Drop the collection if it exists
    collection.drop()
    
    # Insert data into MongoDB
    collection.insert_many(data)
    
    print(f"Data imported successfully into {collection_name}!")