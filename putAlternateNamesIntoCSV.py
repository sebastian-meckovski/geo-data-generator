import pandas as pd

# Define column names
columns = ['alternateNameId', 'geonameId', 'isoLanguage', 'alternateName', 'isPreferredName', 'isShortName',
           'isColloquial', 'isHistoric', 'from', 'to']

# Define data types for the columns
dtype = {
    'alternateNameId': 'str',
    'geonameId': 'str',
    'isoLanguage': 'str',
    'alternateName': 'str',
    'isPreferredName': 'str',
    'isShortName': 'str',
    'isColloquial': 'str',
    'isHistoric': 'str',
    'from': 'str',
    'to': 'str'
}

# Read the data into a pandas DataFrame
df = pd.read_csv('alternateNamesV2.txt', sep='\t', header=None, names=columns, dtype=dtype,
                 keep_default_na=False, na_values='') # Filter for French language names first
pd.set_option('display.expand_frame_repr', False)  # Prevent column wrapping
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.max_rows', None)  # Show all rows


df_fr = df[df['isoLanguage'] == 'fr'].copy()
df_fr[['isPreferredName', 'isShortName', 'isColloquial', 'isHistoric']] = df_fr[['isPreferredName', 'isShortName', 'isColloquial', 'isHistoric']].infer_objects(copy=False)

unique_geoname_id_count = df_fr['geonameId'].nunique()

print(f"Number of unique geonameIds in df_fr: {unique_geoname_id_count}")
# Fill missing values in the filtered DataFrame

def determine_priority(row):
    if row['isPreferredName'] and not row['isShortName'] and not row['isColloquial'] and not row['isHistoric']:
        return 1
    elif not row['isPreferredName'] and not row['isShortName'] and not row['isColloquial'] and not row['isHistoric']:
        return 2
    elif not row['isPreferredName'] and row['isShortName'] and not row['isColloquial'] and not row['isHistoric']:
        return 3
    else:
        return 4

# Add priority column to the filtered DataFrame
df_fr['priority'] = df_fr.apply(determine_priority, axis=1)

# Sort the filtered DataFrame
df_fr.sort_values(by=['priority', 'geonameId'], ascending=True, inplace=True)

# Select the first row for each geonameId in the filtered DataFrame
result_df_fr = df_fr.groupby('geonameId').first()

result_df_fr = result_df_fr.reset_index()

# Reorder the columns (excluding 'priority')
result_df_fr = result_df_fr[['alternateNameId', 'geonameId', 'isoLanguage', 'alternateName',
                            'isPreferredName', 'isShortName', 'isColloquial', 'isHistoric',
                            'from', 'to']]  # Removed 'priority'

result_df_fr.to_csv('preferred_names_fr.csv', sep=',', index=False, encoding='utf-8')

print("Preferred names for French language saved to preferred_names_fr.csv")
