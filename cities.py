import pandas as pd

# Path to the GeoNames data file (unzip if necessary)
# Example: 'allCountries.txt' for all countries or 'AD.txt' for Andorra
file_path = 'cities15000.txt'  # Change to your file path
admin1_mapping = pd.read_csv('admin1CodesASCII.txt', sep='\t', header=None, names=['key', 'name', 'ascii_name', 'geonameid'])

# Specify column names according to GeoNames.org documentation
columns = [
    'geonameid', 'name', 'asciiname', 'alternatenames', 'latitude', 'longitude', 'feature_class',
    'feature_code', 'country_code', 'cc2', 'admin1_code', 'admin2_code', 'admin3_code', 'admin4_code',
    'population', 'elevation', 'dem', 'timezone', 'modification_date'
]

# Load the data into a pandas DataFrame
df = pd.read_csv(file_path, sep='\t', header=None, names=columns, low_memory=False)
# Adjust pandas settings to show all columns
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.expand_frame_repr', False)  # Prevent column wrapping
pd.set_option('display.max_rows', None)  # Show all rows


# Display the first 10 records
print(df.head(100))
