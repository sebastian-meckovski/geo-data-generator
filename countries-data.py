import pandas as pd
import numpy as np
import requests
import geohash
import zipfile
from math import radians, cos, sin, asin, sqrt
import io

# Define output languages
languages = ['pl', 'lt', 'ru', 'hu', 'en', 'fr']

# Define the file paths (these will be the extracted file names)
global_cities_path = 'allCountries.txt'
alternate_names_path = 'alternateNamesV2.txt'
admin1_codes_path = 'admin1CodesASCII.txt'

# Define the URLs of the files
print(f'Downloading files')
global_cities_url = 'http://download.geonames.org/export/dump/allCountries.zip'
alternate_names_url = 'http://download.geonames.org/export/dump/alternateNamesV2.zip'
admin1_codes_url = 'https://download.geonames.org/export/dump/admin1CodesASCII.txt'

def download_and_extract(url, file_path):
  """Downloads a zip file from a URL and extracts the specified file."""
  response = requests.get(url, stream=True)
  response.raise_for_status()  # Raise an exception for bad status codes

  try:
    # Attempt to extract from zip file (for global_cities and alternate_names)
    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
      zip_ref.extract(file_path)
  except zipfile.BadZipFile:
    # If it's not a zip file (for admin1_codes), write the content directly
    with open(file_path, 'wb') as f:
      f.write(response.content)

# Download and extract the files
download_and_extract(global_cities_url, global_cities_path)
download_and_extract(alternate_names_url, alternate_names_path)
download_and_extract(admin1_codes_url, admin1_codes_path)
languages = ['pl', 'lt', 'ru', 'hu', 'en', 'fr']

# Define the file paths
global_cities_path = 'allCountries.txt'
alternate_names_path = 'alternateNamesV2.txt'
admin1_codes_path = 'admin1CodesASCII.txt'

# Define the column headers for the global cities file
global_cities_headers = [
    'geoname_id', 'name', 'ascii_name', 'alternate_names', 'latitude', 'longitude',
    'feature_class', 'feature_code', 'country_code', 'cc2', 'admin1_code',
    'admin2_code', 'admin3_code', 'admin4_code', 'population', 'elevation',
    'dem', 'timezone', 'modification_date'
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

# Define the data types for the columns in the alternate names file
alternate_names_dtype = {
    'alternate_name_id': 'Int64', 'geoname_id': 'Int64', 'iso_language': str, 'alternate_name': str,
    'is_preferred_name': 'boolean', 'is_short_name': 'boolean', 'is_colloquial': 'boolean', 'is_historic': 'boolean',
    'from': str, 'to': str
}

# Define the column headers for the admin1 codes file
admin1_codes_headers = [
    'code', 'name', 'name_ascii', 'geoname_id_admin1'
]

# Define the data types for the columns in the admin1 codes file
admin1_codes_dtype = {
    'code': str, 'name': str, 'name_ascii': str, 'geoname_id_admin1': 'Int64'
}

# Read the files 'Int64'o pandas DataFrames
print(f'Reading file: {alternate_names_path}')
alternate_names_df = pd.read_csv(alternate_names_path, sep='\t', header=None, names=alternate_names_headers, dtype=alternate_names_dtype, low_memory=False, keep_default_na=False, na_values='', encoding='utf-8')
print(f'Reading file: {global_cities_path}')
cities_df = pd.read_csv(global_cities_path, sep='\t', header=None, names=global_cities_headers, dtype=global_cities_dtype, low_memory=False, keep_default_na=False, na_values='', encoding='utf-8').drop('alternate_names', axis=1)
print(f'Reading file: {admin1_codes_path}')
admin1_codes_df = pd.read_csv(admin1_codes_path, sep='\t', header=None, names=admin1_codes_headers, dtype=admin1_codes_dtype, low_memory=False, keep_default_na=False, na_values='', encoding='utf-8')

# Fill <NA> values with False for the specified columns
alternate_names_df[['is_preferred_name', 'is_short_name', 'is_colloquial', 'is_historic']] = \
    alternate_names_df[['is_preferred_name', 'is_short_name', 'is_colloquial', 'is_historic']].fillna(False)

# Generate countries dataset
countries_df = cities_df[cities_df['feature_code'].isin(['PCLI', 'PCLS', 'PCLIX', 'TERR', 'PCLD', 'PCL', 'PCLF'])].rename(columns={'name': 'name_country'})

feature_codes = [
    'PPLA2', 'PPLA', 'PPLC', 'PPL', 'PPLW',
    'PPLG', 'PPLL', 'PPLS', 'PPLF', 'PPLR'
]

filtered_cities_df = cities_df[cities_df['feature_code'].isin(feature_codes) & (cities_df['population'] >= 20000)]

# Merge the DataFrames on the country code
cities_with_country = pd.merge(filtered_cities_df, countries_df[['geoname_id', 'name_country', 'country_code']], on='country_code', how='left', suffixes=('_city', '_country'))

# Include first-order administrative division in cities_with_country_table
cities_with_country['admin1_geocode'] = cities_with_country['country_code'] + '.' + cities_with_country['admin1_code']

cities_with_country_admin1_geocodes = pd.merge(cities_with_country, admin1_codes_df[['code', 'name', 'geoname_id_admin1']], right_on='code',
                                               left_on='admin1_geocode', how='left',  suffixes=('_city', '_admin1')).drop('code', axis=1)

# Remove the admin_area column if the city name is unique within a country. Keep it if multiple cities have the same name in the country.
cities_with_country_admin1_geocodes["city_count"] = cities_with_country_admin1_geocodes.groupby(["geoname_id_country", "name_city"])["geoname_id_city"].transform("count")
cities_with_country_admin1_geocodes["geoname_id_admin1"] = cities_with_country_admin1_geocodes.apply(lambda row: row["geoname_id_admin1"] if row["city_count"] > 1 else np.nan, axis=1)

def calculate_radius(population):
  if 0 <= population < 50000:
    return 500
  elif 50000 <= population < 100000:
    return 1000
  elif 100000 <= population < 500000:
    return 2000
  elif 500000 <= population < 1000000:
    return 7500
  elif 1000000 <= population < 5000000:
    return 12000
  elif 5000000 <= population < 10000000:
    return 16000
  else: 
    return 20000

cities_with_country_admin1_geocodes['estimated_radius'] = cities_with_country_admin1_geocodes['population'].apply(calculate_radius)

def add_geohash(row):
  """Calculates the geohash for a given latitude and longitude."""
  return geohash.encode(row['latitude'], row['longitude'], precision=12)

cities_with_country_admin1_geocodes['geohash'] = cities_with_country_admin1_geocodes.apply(add_geohash, axis=1) 

def haversine(lat1, lon1, lat2, lon2):
  """
  Calculate the great circle distance between two points 
  on the earth (specified in decimal degrees) in meters.
  """
  # Convert decimal degrees to radians 
  lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

  # Haversine formula 
  dlon = lon2 - lon1 
  dlat = lat2 - lat1 
  a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
  c = 2 * asin(sqrt(a)) 
  r = 6371000  # Radius of earth in meters.
  return c * r

def remove_intersecting_circles_grouped(df):
  def _remove_intersecting_circles_for_country(df_country):
    """Helper function to remove intersections within a single country."""
    indices_to_remove = set()
    for i in range(len(df_country)):
      for j in range(i + 1, len(df_country)):
        distance = haversine(df_country['latitude'].iloc[i], df_country['longitude'].iloc[i],
                            df_country['latitude'].iloc[j], df_country['longitude'].iloc[j])
        if distance < df_country['estimated_radius'].iloc[i] + df_country['estimated_radius'].iloc[j]:
          if df_country['population'].iloc[i] < df_country['population'].iloc[j]:
            indices_to_remove.add(df_country.index[i]) 
          else:
            indices_to_remove.add(df_country.index[j])
    return indices_to_remove

  all_indices_to_remove = set()
  for country_code in df['country_code'].unique():
    df_country = df[df['country_code'] == country_code]
    indices_to_remove = _remove_intersecting_circles_for_country(df_country)
    all_indices_to_remove.update(indices_to_remove)

  new_df = df.drop(index=all_indices_to_remove)
  return new_df

print('removing intersecting circles')
cities_with_country_admin1_geocodes = remove_intersecting_circles_grouped(cities_with_country_admin1_geocodes)


def determine_priority(row):
    if row['is_preferred_name'] == True and row['is_short_name'] == False and row['is_colloquial'] == False and row['is_historic'] == False:
        return 1
    elif row['is_preferred_name'] == False and row['is_short_name'] == False and row['is_colloquial'] == False and row['is_historic'] == False:
        return 2
    elif row['is_preferred_name'] == False and row['is_short_name'] == True and row['is_colloquial'] == False and row['is_historic'] == False:
        return 3
    else:
        return 4
    
def check_names_city_country(row):
    name = str(row['alternate_name_city']).lower().strip()
    country = str(row['alternate_name_country']).lower().strip()
    return country in name

def check_names_city_admin1(row):
    name = str(row['alternate_name_city']).lower().strip()
    admin1 = str(row['alternate_name_admin1']).lower().strip()
    return name in admin1 or admin1 in name

for language in languages:
    filtered_alternate_names = alternate_names_df[alternate_names_df['iso_language'] == language].copy()
    # Add a priority column to the filtered DataFrame
    filtered_alternate_names['priority'] = filtered_alternate_names.apply(determine_priority, axis=1)

    # Sort the filtered DataFrame by priority and geoname_id
    filtered_alternate_names.sort_values(by=['priority', 'geoname_id'], inplace=True)

    # Select the first row for each geoname_id in the filtered DataFrame
    filtered_alternate_names = filtered_alternate_names.groupby('geoname_id').first().reset_index()
    # Add alternate city names
    cities_with_country_admin1_alternates = pd.merge(cities_with_country_admin1_geocodes, filtered_alternate_names[['geoname_id', 'alternate_name']], 
                                                how='left', left_on='geoname_id_city', right_on='geoname_id').drop('geoname_id', axis=1)

    # Fill missing city names with original values
    cities_with_country_admin1_alternates['alternate_name'] = cities_with_country_admin1_alternates['alternate_name'].fillna(
        cities_with_country_admin1_alternates['ascii_name']
    )

    # Add alternate admin1 names 
    cities_with_country_admin1_alternates = pd.merge(cities_with_country_admin1_alternates, filtered_alternate_names[['geoname_id', 'alternate_name']], 
                                                    how='left', left_on='geoname_id_admin1', right_on='geoname_id', suffixes=('_city','_admin1')).drop('geoname_id', axis=1)

    # Add alternate country names 
    cities_with_country_admin1_alternates = pd.merge(cities_with_country_admin1_alternates, filtered_alternate_names[['geoname_id', 'alternate_name']], 
                                                    how='left', left_on='geoname_id_country', right_on='geoname_id').drop('geoname_id', axis=1).rename(columns={'alternate_name': 'alternate_name_country'})
    
    # Fill missing country names with original values
    cities_with_country_admin1_alternates['alternate_name_country'] = cities_with_country_admin1_alternates['alternate_name_country'].fillna(
        cities_with_country_admin1_alternates['name_country']
    )

    # Get the indices where the condition is met (using the original DataFrame)
    indices_to_remove = cities_with_country_admin1_alternates[
        cities_with_country_admin1_alternates.apply(check_names_city_country, axis=1)
    ].index

    # Remove the 'alternate_name_admin1' values at those indices in the original DataFrame
    cities_with_country_admin1_alternates.loc[indices_to_remove, 'alternate_name_country'] = np.nan

    # Get the indices where the condition is met (using the copy)
    indices_to_remove = cities_with_country_admin1_alternates[
        cities_with_country_admin1_alternates.apply(check_names_city_admin1, axis=1)
    ].index  # Get the indices

    # Remove the 'alternate_name_admin1' values at those indices in the ORIGINAL
    cities_with_country_admin1_alternates[['geoname_id_city', 'latitude', 'longitude', 'geohash', 'country_code', 'population', 'estimated_radius', 'alternate_name_city', 'alternate_name_admin1', 'alternate_name_country']].to_csv(f'cities_with_alternates_{language}.csv', index=False, sep=',', header=True) 

