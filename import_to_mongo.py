import pandas as pd
from pymongo import MongoClient

def import_dataframe_to_mongo(df, language_code, connection_string, database):

    # Connect to MongoDB
    client = MongoClient(connection_string)
    
    # Specify the database and collection
    db = client[database]
    collection = db[f"cities-{language_code}"]
    
    # Drop the collection if it exists
    collection.drop()
    
    # Convert DataFrame to a list of dictionaries
    data = df.to_dict(orient='records')
    
    # Insert data into MongoDB
    collection.insert_many(data)
    
    print(f"Data imported successfully into cities_{language_code}!")
