import pandas as pd

def filter_specific_feature_codes(input_file, output_file):
    # Define column names based on the provided data structure
    column_names = [
        'geonameid', 'name', 'asciiname', 'alternatenames', 'latitude', 'longitude',
        'feature_class', 'feature_code', 'country_code', 'cc2', 'admin1_code',
        'admin2_code', 'admin3_code', 'admin4_code', 'population', 'elevation',
        'dem', 'timezone', 'modification_date'
    ]

    # Define data types for the columns
    dtype = {
        'geonameid': 'int64', 'name': 'str', 'asciiname': 'str', 'alternatenames': 'str',
        'latitude': 'float64', 'longitude': 'float64', 'feature_class': 'str', 'feature_code': 'str',
        'country_code': 'str', 'cc2': 'str', 'admin1_code': 'str', 'admin2_code': 'str',
        'admin3_code': 'str', 'admin4_code': 'str', 'population': 'int64', 'elevation': 'float64',
        'dem': 'int64', 'timezone': 'str', 'modification_date': 'str'
    }

    # List of feature codes to filter
    feature_codes = [
        'PPLA', 'PPLC', 'PPL', 'PPLW',
        'PPLG', 'PPLL', 'PPLS', 'PPLF', 'PPLR',
    ]

    # Read the data into a pandas DataFrame
    df = pd.read_csv(input_file, sep='\t', header=None, names=column_names, dtype=dtype, low_memory=False,
                     keep_default_na=False, na_values='')

    # Filter the DataFrame for rows with the specified feature codes and population > 15000
    filtered_df = df[df['feature_code'].isin(feature_codes) & (df['population'] >= 15000)]

    # Drop any records that don't contain country code
    filtered_df = filtered_df[filtered_df['country_code'].notnull() & (filtered_df['country_code'] != '')]

    # Get the DataFrame for countries (feature_code == 'PCLI')
    pcli_df = df[df['feature_code'] == 'PCLI']

    # Create a dictionary to map country codes to their geonameid
    country_geonameid_map = pcli_df.set_index('country_code')['geonameid'].to_dict()

    # Add the country_geonameid column to the filtered DataFrame as integer
    filtered_df['country_geonameid'] = filtered_df['country_code'].map(country_geonameid_map).astype('Int64')

    # Save the filtered DataFrame to a new file
    filtered_df.to_csv(output_file, sep='\t', index=False)

    print(f"Filtered records have been saved to {output_file}")

# Path to the allCountries.txt file
input_file = 'allCountries.txt'
output_file = 'filtered_records15000.txt'
filter_specific_feature_codes(input_file, output_file)
