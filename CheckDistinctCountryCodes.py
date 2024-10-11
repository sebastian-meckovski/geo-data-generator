import pandas as pd

def find_anomaly(file_path):
    # Define column names based on the provided data structure
    column_names = [
        'geonameid', 'name', 'asciiname', 'alternatenames', 'latitude', 'longitude',
        'feature_class', 'feature_code', 'country_code', 'cc2', 'admin1_code',
        'admin2_code', 'admin3_code', 'admin4_code', 'population', 'elevation',
        'dem', 'timezone', 'modification_date'
    ]

    # Read the data into a pandas DataFrame
    df = pd.read_csv(file_path, sep='\t', header=None, names=column_names, low_memory=False, keep_default_na=False, na_values='')

    # Check for duplicate rows
    duplicate_rows = df[df.duplicated(keep=False)]

    # Check for any missing or empty country codes
    missing_country_codes = df[df['country_code'].isnull() | (df['country_code'] == '')]

    # Get the total number of records
    record_count = len(df)

    return duplicate_rows, missing_country_codes, record_count

# Path to the pcli_records.txt file
file_path = 'pcli_records.txt'

# Find the anomaly and print the duplicate rows, missing country codes, and record count
duplicate_rows, missing_country_codes, record_count = find_anomaly(file_path)
print(f"Total number of records in the file: {record_count}")
print("\nDuplicate rows in the file are:")
print(duplicate_rows)
print("\nRows with missing or empty country codes are:")
print(missing_country_codes)
