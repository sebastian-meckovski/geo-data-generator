import pandas as pd
from pymongo import MongoClient

cluster_name = ''
username = ''
password = ''

def import_dataframe_to_mongo(df, language_code):

    # MongoDB connection string
    connection_string = f"mongodb+srv://{username}:{password}@{cluster_name}.crjcc.mongodb.net/test?retryWrites=true&w=majority"
    
    # Connect to MongoDB
    client = MongoClient(connection_string)
    
    # Specify the database and collection
    db = client["cities_collection"]
    collection = db[f"cities_{language_code}"]
    
    # Drop the collection if it exists
    collection.drop()
    
    # Convert DataFrame to a list of dictionaries
    data = df.to_dict(orient='records')
    
    # Insert data into MongoDB
    collection.insert_many(data)
    
    print(f"Data imported successfully into cities_{language_code}!")
