import pandas as pd

# Load the data from text files
cities = pd.read_csv('cities.txt', sep=' ', header=None, names=['cityId', 'city', 'regionId'])
regions = pd.read_csv('admin1_codes.txt', sep=' ', header=None, names=['regionId', 'region'])
alt_names = pd.read_csv('alternate_names.txt', sep=' ', header=None, names=['id', 'lang', 'name'])

# Merge cities with regions to get the region names
cities = cities.merge(regions, on='regionId', how='left')

# Separate city and region alternate names
city_alt_names = alt_names[alt_names['id'].isin(cities['cityId'])]
region_alt_names = alt_names[alt_names['id'].isin(cities['regionId'])]

# Set the language filter (change this to 'fr' for French)
language_filter = 'en'

# Create the final dataframe
final_data = []

for _, row in cities.iterrows():
    cityId = row['cityId']

    # Get alternate names for the city
    city_alts = city_alt_names[(city_alt_names['id'] == cityId) & (city_alt_names['lang'] == language_filter)]
    if city_alts.empty:
        city_alts = pd.DataFrame([{'id': cityId, 'lang': language_filter, 'name': row['city']}])

    # Get alternate names for the region
    region_alts = region_alt_names[
        (region_alt_names['id'] == row['regionId']) & (region_alt_names['lang'] == language_filter)]
    if region_alts.empty:
        region_alts = pd.DataFrame([{'id': row['regionId'], 'lang': language_filter, 'name': row['region']}])

    for _, city_alt in city_alts.iterrows():
        for _, region_alt in region_alts.iterrows():
            final_data.append({
                'id': cityId,
                'city': city_alt['name'],
                'region': region_alt['name']
            })

# Convert the final data to a DataFrame
final_df = pd.DataFrame(final_data)

# Save the final DataFrame to a CSV file
final_df.to_csv('final_data.csv', index=False)

print(final_df)
