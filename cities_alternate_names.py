import pandas as pd

# Path to the GeoNames data file and alternate names file
file_path = 'cities15000.txt'  # Main GeoNames data
alt_names_file = 'alternateNamesV2.txt'  # Alternate names file with languages

# Load the GeoNames main data into a pandas DataFrame
columns = [
    'geonameid', 'name', 'asciiname', 'alternatenames', 'latitude', 'longitude', 'feature_class',
    'feature_code', 'country_code', 'cc2', 'admin1_code', 'admin2_code', 'admin3_code', 'admin4_code',
    'population', 'elevation', 'dem', 'timezone', 'modification_date'
]
df = pd.read_csv(file_path, sep='\t', header=None, names=columns, low_memory=False)

# Load the alternate names data (with languages) into another DataFrame
alt_names_columns = ['alternateNameId', 'geonameid', 'isoLanguage', 'alternateName']
alt_names_df = pd.read_csv(alt_names_file, sep='\t', header=None, names=alt_names_columns, usecols=[0, 1, 2, 3])

# Merge the main GeoNames data with the alternate names (based on geonameid)
df_with_alt_names = df.merge(alt_names_df, on='geonameid', how='left')

# Filter for specific languages: English (en), Polish (pl), Lithuanian (lt), and Russian (ru)
filtered_languages = ['en', 'pl', 'lt', 'ru']
df_filtered = df_with_alt_names[df_with_alt_names['isoLanguage'].isin(filtered_languages)]

# Adjust pandas settings to show all columns
pd.set_option('display.expand_frame_repr', False)  # Prevent column wrapping
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.expand_frame_repr', False)  # Prevent column wrapping
pd.set_option('display.max_rows', None)  # Show all rows

# Display the first 100 records with the filtered languages
print(df_filtered[['geonameid','name', 'alternateName', 'isoLanguage']].head(5000))
