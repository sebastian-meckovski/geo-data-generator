import os
import pandas as pd
import numpy as np
import geopandas as gpd
from helpers import add_geohash, calculate_radius, check_names_admin1_country, check_names_city_admin1, check_names_city_country, determine_priority, download_and_extract, geodesic_point_buffer
from import_to_mongo import import_dataframe_to_mongo

# Define output languages
languages = os.environ.get('LANGUAGES').split(',')
mongo_conn_string = os.environ.get('MONGO_DB_CONN_STRING')
mongo_database_name = os.environ.get('MONGO_DATABASE_NAME')
mongo_collection_name = os.environ.get('MONGO_COLLECTION_NAME')
population_threshold = int(os.environ.get('POPULATION_THRESHOLD'))

# Define the file paths (these will be the extracted file names)
global_cities_path = 'allCountries.txt'
alternate_names_path = 'alternateNamesV2.txt'
admin1_codes_path = 'admin1CodesASCII.txt'

# Define the URLs of the files
global_cities_url = 'http://download.geonames.org/export/dump/allCountries.zip'
alternate_names_url = 'http://download.geonames.org/export/dump/alternateNamesV2.zip'
admin1_codes_url = 'https://download.geonames.org/export/dump/admin1CodesASCII.txt'

# Download and extract the files
download_and_extract(global_cities_url, global_cities_path)
download_and_extract(alternate_names_url, alternate_names_path)
download_and_extract(admin1_codes_url, admin1_codes_path)

global_cities_path = 'allCountries.txt'
alternate_names_path = 'alternateNamesV2.txt'
admin1_codes_path = 'admin1CodesASCII.txt'

global_cities_headers = [
    'geoname_id', 'name', 'ascii_name', 'alternate_names', 'latitude', 'longitude',
    'feature_class', 'feature_code', 'country_code', 'cc2', 'admin1_code',
    'admin2_code', 'admin3_code', 'admin4_code', 'population', 'elevation',
    'dem', 'timezone', 'modification_date'
]

global_cities_headers_usecols = [
    'geoname_id', 'name', 'ascii_name', 'latitude', 'longitude',
    'feature_code', 'country_code', 'admin1_code', 'population'
]

# Define the data types for the columns in the global cities file
global_cities_dtype = {
    'geoname_id': 'Int64', 'name': str, 'asciiname': str, 'alternatenames': str,
    'latitude': float, 'longitude': float, 'feature_class': str, 'feature_code': str,
    'country_code': str, 'cc2': str, 'admin1_code': str, 'admin2_code': str,
    'admin3_code': str, 'admin4_code': str, 'population': 'Int64', 'elevation': float,
    'dem': float, 'timezone': str, 'modification_date': str
}

# Define the column headers for the alternate names file
alternate_names_headers = [
    'alternate_name_id', 'geoname_id', 'iso_language', 'alternate_name',
    'is_preferred_name', 'is_short_name', 'is_colloquial', 'is_historic', 
    'from', 'to'
]

alternate_names_headers_usecols = [
    'geoname_id', 'iso_language', 'alternate_name',
    'is_preferred_name', 'is_short_name', 'is_colloquial', 'is_historic'
]

alternate_names_dtype = {
    'alternate_name_id': 'Int64', 'geoname_id': 'Int64', 'iso_language': str, 'alternate_name': str,
    'is_preferred_name': 'boolean', 'is_short_name': 'boolean', 'is_colloquial': 'boolean', 'is_historic': 'boolean',
    'from': str, 'to': str
}

admin1_codes_headers = [
    'code', 'name', 'name_ascii', 'geoname_id_admin1'
]

admin1_codes_usecols = ['code', 'name', 'geoname_id_admin1']

admin1_codes_dtype = {
    'code': str, 'name': str, 'name_ascii': str, 'geoname_id_admin1': 'Int64'
}

print(f'Reading file: {alternate_names_path}')
alternate_names_df = pd.read_csv(alternate_names_path, sep='\t', header=None, names=alternate_names_headers, dtype=alternate_names_dtype, low_memory=False, keep_default_na=False, na_values='', encoding='utf-8', usecols=alternate_names_headers_usecols)
print(f'Reading file: {global_cities_path}')
cities_df = pd.read_csv(global_cities_path, sep='\t', header=None, names=global_cities_headers, dtype=global_cities_dtype, low_memory=False, keep_default_na=False, na_values='', encoding='utf-8', usecols=global_cities_headers_usecols)
print(f'Reading file: {admin1_codes_path}')
admin1_codes_df = pd.read_csv(admin1_codes_path, sep='\t', header=None, names=admin1_codes_headers, dtype=admin1_codes_dtype, low_memory=False, keep_default_na=False, na_values='', encoding='utf-8', usecols=admin1_codes_usecols)

# Fill <NA> values with False for the specified columns
alternate_names_df[['is_preferred_name', 'is_short_name', 'is_colloquial', 'is_historic']] = \
    alternate_names_df[['is_preferred_name', 'is_short_name', 'is_colloquial', 'is_historic']].fillna(False)

# Generate countries dataset
countries_df = cities_df[cities_df['feature_code'].isin(['PCLI', 'PCLS', 'PCLIX', 'TERR', 'PCLD', 'PCL', 'PCLF'])].rename(columns={'name': 'name_country'})

feature_codes = [
    'PPLA2', 'PPLA', 'PPLC', 'PPL', 'PPLW',
    'PPLG', 'PPLL', 'PPLS', 'PPLF', 'PPLR'
]

filtered_cities_df = cities_df[cities_df['feature_code'].isin(feature_codes) & (cities_df['population'] >= population_threshold)]

# Merge the DataFrames on the country code
cities_with_country = pd.merge(filtered_cities_df, countries_df[['geoname_id', 'name_country', 'country_code']], on='country_code', how='left', suffixes=('_city', '_country'))

# Include first-order administrative division in cities_with_country_table
cities_with_country['admin1_geocode'] = cities_with_country['country_code'] + '.' + cities_with_country['admin1_code']

cities_with_country_admin1_geocodes = pd.merge(cities_with_country, admin1_codes_df[['code', 'name', 'geoname_id_admin1']], right_on='code',
                                               left_on='admin1_geocode', how='left',  suffixes=('_city', '_admin1')).drop('code', axis=1)

# Remove the admin_area column if the city name is unique within a country. Keep it if multiple cities have the same name in the country.
cities_with_country_admin1_geocodes["city_count"] = cities_with_country_admin1_geocodes.groupby(["geoname_id_country", "name_city"])["geoname_id_city"].transform("count")
cities_with_country_admin1_geocodes["geoname_id_admin1"] = cities_with_country_admin1_geocodes.apply(lambda row: row["geoname_id_admin1"] if row["city_count"] > 1 else np.nan, axis=1)

print('Calculating radius')
cities_with_country_admin1_geocodes['estimated_radius'] = cities_with_country_admin1_geocodes['population'].apply(calculate_radius)

print('Adding geohash column')
cities_with_country_admin1_geocodes['geohash'] = cities_with_country_admin1_geocodes.apply(add_geohash, axis=1) 

print('removing overlapping circles')
points_df = cities_with_country_admin1_geocodes

# Convert the points to circles by buffering them
points_buffer_gdf = gpd.GeoDataFrame(
    points_df,
    geometry=points_df.apply(
        lambda row : geodesic_point_buffer(row.latitude, row.longitude, row.estimated_radius), axis=1
    ),
    crs=4326,
)

# Determine the intersecting city buffers (result includes self-intersections)
intersecting_gdf = points_buffer_gdf.sjoin(points_buffer_gdf)

intersecting_larger_population_df = intersecting_gdf.loc[
    (intersecting_gdf.population_left < intersecting_gdf.population_right) 
    & (intersecting_gdf.population_left < 2000000)
]

# Remove the city buffers that intersect with a larger population city buffer
cities_with_country_admin1_geocodes = points_buffer_gdf[
    ~points_buffer_gdf.index.isin(intersecting_larger_population_df.index) 
]

combined_data = {}

for language in languages:
    filtered_alternate_names = alternate_names_df[alternate_names_df['iso_language'] == language].copy()
    filtered_alternate_names['priority'] = filtered_alternate_names.apply(determine_priority, axis=1)
    filtered_alternate_names.sort_values(by=['priority', 'geoname_id'], inplace=True)
    filtered_alternate_names = filtered_alternate_names.groupby('geoname_id').first().reset_index()

    cities_with_country_admin1_alternates = pd.merge(cities_with_country_admin1_geocodes, filtered_alternate_names[['geoname_id', 'alternate_name']], 
                                                     how='left', left_on='geoname_id_city', right_on='geoname_id').drop('geoname_id', axis=1)
    cities_with_country_admin1_alternates['alternate_name'] = cities_with_country_admin1_alternates['alternate_name'].fillna(
        cities_with_country_admin1_alternates['ascii_name']
    )

    cities_with_country_admin1_alternates = pd.merge(cities_with_country_admin1_alternates, filtered_alternate_names[['geoname_id', 'alternate_name']], 
                                                     how='left', left_on='geoname_id_admin1', right_on='geoname_id', suffixes=('_city','_admin1')).drop('geoname_id', axis=1)
    cities_with_country_admin1_alternates = pd.merge(cities_with_country_admin1_alternates, filtered_alternate_names[['geoname_id', 'alternate_name']], 
                                                     how='left', left_on='geoname_id_country', right_on='geoname_id').drop('geoname_id', axis=1).rename(columns={'alternate_name': 'alternate_name_country'})
    cities_with_country_admin1_alternates['alternate_name_country'] = cities_with_country_admin1_alternates['alternate_name_country'].fillna(
        cities_with_country_admin1_alternates['name_country']
    )

    country_names_indices_to_remove = cities_with_country_admin1_alternates[
        cities_with_country_admin1_alternates.apply(check_names_city_country, axis=1)
    ].index
    cities_with_country_admin1_alternates.loc[country_names_indices_to_remove, 'alternate_name_country'] = np.nan

    admin1_names_indices_to_remove = cities_with_country_admin1_alternates[
        cities_with_country_admin1_alternates.apply(check_names_city_admin1, axis=1)
    ].index 
    cities_with_country_admin1_alternates.loc[admin1_names_indices_to_remove, 'alternate_name_admin1'] = np.nan

    admin1_names_vs_country_indices_to_remove = cities_with_country_admin1_alternates[
        cities_with_country_admin1_alternates.apply(check_names_admin1_country, axis=1)
    ].index 
    cities_with_country_admin1_alternates.loc[admin1_names_vs_country_indices_to_remove, 'alternate_name_admin1'] = np.nan

    # Iterate through the rows and update the combined_data dictionary
    for _, row in cities_with_country_admin1_alternates.iterrows():
        geoname_id_city = row['geoname_id_city']
        if geoname_id_city not in combined_data:
            combined_data[geoname_id_city] = {
                'geoname_id_city': geoname_id_city,
                'latitude': row['latitude'],
                'longitude': row['longitude'],
                'geohash': row['geohash'],
                'country_code': row['country_code'],
                'population': row['population'],
                'estimated_radius': row['estimated_radius'],
                'name': {}
            }
        combined_data[geoname_id_city]['name'][language] = {
            'city': row['alternate_name_city'] if pd.notna(row['alternate_name_city']) else None,
            'admin1': row['alternate_name_admin1'] if pd.notna(row['alternate_name_admin1']) else None,
            'country': row['alternate_name_country'] if pd.notna(row['alternate_name_country']) else None
        }

nested_json_list = list(combined_data.values())

import_dataframe_to_mongo(nested_json_list, mongo_conn_string, mongo_database_name, "cities_database")
