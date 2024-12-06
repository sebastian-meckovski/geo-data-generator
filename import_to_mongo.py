from pymongo import MongoClient
from requests.auth import HTTPDigestAuth
from pymongo.mongo_client import MongoClient
from pymongo.operations import SearchIndexModel

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


def create_atlas_search_index(connection_string, database_name, collection_name, index_name, languages):
    """
    Creates an Atlas Search index using pymongo's SearchIndexModel.
    """
    # Connect to your Atlas deployment
    client = MongoClient(connection_string)

    # Access the specified database and collection
    database = client[database_name]
    collection = database[collection_name]

    # Define the search index model
    search_index_model = SearchIndexModel(
        definition={
            "mappings": {
                "fields": {
                    "name": {
                        "type": "document",
                        "fields": generate_language_fields(languages)
                    }
                }
            },
            "analyzers": [
                {
                    "name": "diacriticFolder",
                    "charFilters": [],
                    "tokenizer": {"type": "keyword"},
                    "tokenFilters": [{"type": "icuFolding"}]
                }
            ]
        },
        name=index_name
    )

    # Create the search index
    try:
        result = collection.create_search_index(model=search_index_model)
        print(f"Index {index_name} created successfully: {result}")
    except Exception as e:
        print(f"Failed to create index: {e}")
    finally:
        client.close()


def delete_atlas_search_index(connection_string, database_name, collection_name, index_name):
    """
    Deletes an Atlas Search index using pymongo's dropSearchIndex method.
    """
    # Connect to your Atlas deployment
    client = MongoClient(connection_string)

    try:
        # Access the specified database and collection
        database = client[database_name]
        collection = database[collection_name]

        # Drop the search index
        collection.drop_search_index(index_name)
        print(f"Index {index_name} deleted successfully")
    except Exception as e:
        print(f"Failed to delete index {index_name}: {e}")
    finally:
        # Close the connection
        client.close()


def does_search_index_exist(connection_string, database_name, collection_name, index_name):
    """
    Checks if a specific Atlas Search index exists in a collection.

    Parameters:
    - connection_string: MongoDB Atlas connection string.
    - database_name: Name of the database.
    - collection_name: Name of the collection.
    - index_name: Name of the search index to check.

    Returns:
    - True if the index exists, False otherwise.
    """
    # Connect to your Atlas deployment
    client = MongoClient(connection_string)

    try:
        # Access the specified database and collection
        database = client[database_name]
        collection = database[collection_name]

        # Get a list of the collection's search indexes
        cursor = collection.list_search_indexes()

        # Check if the index name exists
        for index in cursor:
            if index["name"] == index_name:
                return True

        return False

    except Exception as e:
        print(f"Error checking search index existence: {e}")
        return False

    finally:
        # Close the client connection
        client.close()


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
