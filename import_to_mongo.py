import pandas as pd
from pymongo import MongoClient
import requests
from requests.auth import HTTPDigestAuth

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


def create_atlas_search_index(public_key, private_key, group_id, cluster_name, database, collection, index_name, config):
    """
    Creates an Atlas Search index using digest authentication.
    """
    url = f"https://cloud.mongodb.com/api/atlas/v2/groups/{group_id}/clusters/{cluster_name}/search/indexes?pretty=true"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/vnd.atlas.2024-05-30+json"
    }

    payload = {
        "collectionName": collection,
        "database": database,
        "name": index_name,
        "definition": {
            "mappings": config["mappings"],
            "analyzers": config["analyzers"]
        }
    }

    # Use HTTPDigestAuth for digest authentication
    auth = HTTPDigestAuth(public_key, private_key)

    response = requests.post(url, headers=headers, auth=auth, json=payload)

    if response.status_code == 201:
        print(f"Index {index_name} created successfully.")
    else:
        print(f"Failed to create index: {response.status_code}")
        print(response.json())


def generate_language_fields(languages):
    """
    Generates language-specific fields for the Atlas Search index configuration.
    """
    language_fields = {}
    for lang in languages:
        print(f"Generating config for {lang} search")
        language_fields[lang] = {
            "type": "document",
            "fields": {
                "country": {"analyzer": "diacriticFolder", "type": "string"},
                "admin1": {"analyzer": "diacriticFolder", "type": "string"},
                "city": {"analyzer": "diacriticFolder", "type": "string"}
            }
        }
    return language_fields

# TODO: Update API to search by index
# TODO: Update logic to override/remove old index when generating new one