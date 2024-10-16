import pandas as pd

# Read data from text files with specified dtypes
admin1_df = pd.read_csv('admin1_codes.txt', sep=' ', header=None, names=['admin_code', 'admin_name'],
                        dtype={'admin_code': int, 'admin_name': str})
alternate_names_df = pd.read_csv('alternate_names.txt', sep='\t', header=None, names=['geoname_id', 'lang', 'name'],
                                 dtype={'geoname_id': int, 'lang': str, 'name': str})
cities_df = pd.read_csv('cities.txt', sep=' ', header=None,
                        names=['city_geoname_id', 'city_name', 'admin_code', 'country_code'],
                        dtype={'city_geoname_id': int, 'city_name': str, 'admin_code': int, 'country_code': int})

# Create a DataFrame for country codes (replace with your actual data if you have a country_codes.txt file)
country_codes_df = pd.DataFrame({
    "country_code": [3401, 3402, 3403],
    "country_name": ["United Kingdom", "United States", "Germany"]
})


def join_and_localize(language_code):
    """
    Joins the three DataFrames and localizes the city, admin area,
    and country names based on the given language code using merge operations.
    """

    # Merge cities_df with alternate_names_df on city_geoname_id
    merged_df = pd.merge(cities_df, alternate_names_df[alternate_names_df['lang'] == language_code],
                         left_on='city_geoname_id', right_on='geoname_id', how='left')

    # Fill missing city names with original values
    merged_df['city_name'] = merged_df['name'].fillna(merged_df['city_name'])

    # Merge with admin1_df and fill missing admin names
    merged_df = pd.merge(merged_df, admin1_df, on='admin_code', how='left')
    merged_df = pd.merge(merged_df, alternate_names_df[alternate_names_df['lang'] == language_code],
                         left_on='admin_code', right_on='geoname_id', how='left')
    merged_df['admin_name'] = merged_df['name_y'].fillna(merged_df['admin_name'])

    # Merge with country_codes_df and fill missing country names
    merged_df = pd.merge(merged_df, country_codes_df, on='country_code', how='left')
    merged_df = pd.merge(merged_df, alternate_names_df[alternate_names_df['lang'] == language_code],
                         left_on='country_code', right_on='geoname_id', how='left')
    merged_df['country_name'] = merged_df['name'].fillna(merged_df['country_name'])

    # Select and rename columns
    result_df = merged_df[['city_geoname_id', 'city_name', 'admin_name', 'country_name']]
    result_df = result_df.rename(columns={'admin_name': 'admin_area', 'country_name': 'country'})

    return result_df


# Get the data in English
en_data = join_and_localize("en")
print("Data in English:")
print(en_data.to_markdown(index=False, numalign="left", stralign="left"))

# Get the data in French
fr_data = join_and_localize("fr")
print("\nData in French:")
print(fr_data.to_markdown(index=False, numalign="left", stralign="left"))

# Save the results to text files
en_data.to_csv('joined_data_en.txt', sep='\t', index=False, header=True)
fr_data.to_csv('joined_data_fr.txt', sep='\t', index=False, header=True)