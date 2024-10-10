import pandas as pd
# Path to the GeoNames data file (unzip if necessary)
file_path = 'cities15000.txt'  # Change to your file path
admin1_mapping_file = 'admin1CodesASCII.txt'  # Path to admin1CodesASCII.txt

# Specify column names according to GeoNames.org documentation
columns = [
    'geonameid', 'name', 'asciiname', 'alternatenames', 'latitude', 'longitude', 'feature_class',
    'feature_code', 'country_code', 'cc2', 'admin1_code', 'admin2_code', 'admin3_code', 'admin4_code',
    'population', 'elevation', 'dem', 'timezone', 'modification_date'
]

admin_codes_columns = ['key', 'name', 'ascii_name', 'geonameid']

# Load the Admin1CodesASCII.txt file to map admin1 codes to names
admin1_mapping = pd.read_csv(admin1_mapping_file, sep='\t', header=None, names=admin_codes_columns)

# Create a dictionary to map 'country_code.admin1_code' to the admin1 name
admin1_dict = admin1_mapping.set_index('key')['name'].to_dict()

# Load the GeoNames data into a pandas DataFrame
df = pd.read_csv(file_path, sep='\t', header=None, names=columns, low_memory=False)

# Create the 'country_code.admin1_code' key to map admin1 names
df['admin1_key'] = df['country_code'] + '.' + df['admin1_code']  # Create mapping key like 'US.CA'

# Map the admin1_code to its human-readable name using the dictionary
df['admin1_name'] = df['admin1_key'].map(admin1_dict)

# Adjust pandas settings to show all columns and rows (optional)
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.expand_frame_repr', False)  # Prevent column wrapping
pd.set_option('display.max_rows', None)  # Show all rows

# Display the first 100 records with the mapped admin1 names
print(df[['geonameid', 'name', 'admin1_code', 'admin1_name', 'feature_class', 'feature_code']].head(9999))
