# import pandas as pd
# from pymongo import MongoClient
# import requests
# import json
# from create_atlas_search_index import create_atlas_search_index
# from import_to_mongo import generate_language_fields, import_dataframe_to_mongo


# # Main function
# if __name__ == "__main__":
#     # Replace with your MongoDB Atlas credentials and cluster info
#     api_key = "YOUR_PUBLIC_KEY"
#     private_key = "YOUR_PRIVATE_KEY"
#     cluster_name = "YOUR_CLUSTER_NAME"
#     connection_string = "YOUR_MONGODB_CONNECTION_STRING"
#     languages = ['pl']

#     database = "city-names-db"
#     collection_name = "cities_database"
#     index_name = "default"

#     # Sample data
#     data = [
#         {"name": {"pl": {"country": "Polska", "admin1": "Mazowieckie", "city": "Warszawa"}}},
#         {"name": {"pl": {"country": "Niemcy", "admin1": "Berlin", "city": "Berlin"}}},
#     ]
    
#     # Load data into MongoDB
#     import_dataframe_to_mongo(data, connection_string, database, collection_name)

#     # Search index configuration
#     search_index_config = {
#         "analyzer": "diacriticFolder",
#         "mappings": {
#             "fields": {
#                 "name": {
#                     "type": "document",
#                     "fields": generate_language_fields(languages)
#                 }
#             }
#         },
#         "analyzers": [
#             {
#                 "name": "diacriticFolder",
#                 "charFilters": [],
#                 "tokenizer": {"type": "keyword"},
#                 "tokenFilters": [{"type": "icuFolding"}]
#             }
#         ]
#     }

#     # Create the Atlas Search Index
#     create_atlas_search_index(api_key, private_key, cluster_name, database, collection_name, index_name, search_index_config)
