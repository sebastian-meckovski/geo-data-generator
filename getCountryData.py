import pandas as pd

def filter_pcli_records(input_file, output_file):
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

    # Read the data into a pandas DataFrame, ensuring 'NA' is not treated as a missing value
    df = pd.read_csv(input_file, sep='\t', header=None, names=column_names, dtype=dtype, low_memory=False,
                     keep_default_na=False, na_values='')

    # Filter the DataFrame for rows where feature_code is 'PCLI'
    pcli_df = df[df['feature_code'] == 'PCLI']

    # Save the filtered DataFrame to a new file without headers
    pcli_df.to_csv(output_file, sep='\t', index=False, header=False)

    print(f"Filtered records have been saved to {output_file}")

# Path to the allCountries.txt file
input_file = 'allCountries.txt'
output_file = 'pcli_records.txt'
filter_pcli_records(input_file, output_file)
