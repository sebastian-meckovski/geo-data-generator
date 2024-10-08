import pandas as pd

# Paths to data files
places_file_path = 'cities15000.txt'  # GeoNames city data
admin_file_path = 'admin1CodesASCII.txt'  # GeoNames admin division data
alt_names_file = 'alternateNamesV2.txt'  # Alternate names file with languages

# Define column names for both files
places_columns = [
    'geonameid', 'name', 'asciiname', 'alternatenames', 'latitude', 'longitude',
    'feature_class', 'feature_code', 'country_code', 'cc2', 'admin1_code', 'admin2_code',
    'admin3_code', 'admin4_code', 'population', 'elevation', 'dem', 'timezone', 'modification_date'
]
admin_columns = ['key', 'admin1name', 'ascii_name', 'geonameid']
alt_names_columns = ['alternateNameId', 'geonameid', 'isoLanguage', 'alternateName']

# Load datasets
admin_df = pd.read_csv(admin_file_path, sep='\t', header=None, names=admin_columns, low_memory=False, encoding='utf-8')
places_df = pd.read_csv(places_file_path, sep='\t', header=None, names=places_columns, low_memory=False, encoding='utf-8')
alt_names_df = pd.read_csv(alt_names_file, sep='\t', header=None, names=alt_names_columns, usecols=[0, 1, 2, 3], encoding='utf-8')

# Ensure 'geonameid' and 'admin1_code' columns are strings for all DataFrames
admin_df['geonameid'] = admin_df['geonameid'].astype(str)
places_df['geonameid'] = places_df['geonameid'].astype(str)
alt_names_df['geonameid'] = alt_names_df['geonameid'].astype(str)
places_df['admin1_code'] = places_df['admin1_code'].astype(str)

# Create a key in places_df to match with admin_df['key']
places_df['admin1_key'] = places_df['country_code'] + '.' + places_df['admin1_code']

# Merge the main GeoNames place data with the alternate names (for cities)
df_with_alt_names = places_df.merge(alt_names_df, on='geonameid', how='left')

# Merge admin names with the places data to get the 'admin1name' (using 'admin1_key')
df_with_admin_info = df_with_alt_names.merge(admin_df[['key', 'admin1name']],
                                             left_on='admin1_key',
                                             right_on='key',
                                             how='left')

# Step 1: Extract only alternate names for admin divisions
admin_alt_names = alt_names_df[alt_names_df['geonameid'].isin(admin_df['geonameid'])]

# Step 2: Merge these alternate admin names into the DataFrame
df_with_admin_info = df_with_admin_info.merge(admin_alt_names[['geonameid', 'alternateName', 'isoLanguage']],
                                              left_on='admin1_key',
                                              right_on='geonameid',
                                              how='left',
                                              suffixes=('', '_admin_alt'))

# Rename the 'alternateName_admin_alt' to 'alternateAdmin1Name'
df_with_admin_info.rename(columns={'alternateName_admin_alt': 'alternateAdmin1Name'}, inplace=True)

# Filter for specific languages: English (en), Polish (pl), Lithuanian (lt), and Russian (ru)
filtered_languages = ['en', 'pl', 'lt', 'ru']
df_filtered = df_with_admin_info[df_with_admin_info['isoLanguage'].isin(filtered_languages)]

# Adjust pandas settings to show all columns and rows (optional)
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.expand_frame_repr', False)  # Prevent column wrapping
pd.set_option('display.max_rows', None)  # Show all rows

# Display the records with the desired columns
print(df_filtered[['geonameid', 'name', 'alternateName', 'isoLanguage', 'admin1name', 'alternateAdmin1Name']].head(5000))
