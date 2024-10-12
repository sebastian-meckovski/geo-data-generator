import pandas as pd

columns = ['rowId','geonameId', 'isPreferredName', 'isShortName', 'isColloquial', 'isHistoric']

# Read the dataset from the file without headers
df = pd.read_csv('preferential_data_test.txt',
                 sep='\t',
                 header=None,
                 names=columns,
                 dtype=str,
                 low_memory=False)

# Fill missing values with 0 (or another appropriate value)
df[['isPreferredName', 'isShortName', 'isColloquial', 'isHistoric']] = df[['isPreferredName', 'isShortName', 'isColloquial', 'isHistoric']].fillna(0)

def determine_priority(row):
    if row['isPreferredName'] and not row['isShortName'] and not row['isColloquial'] and not row['isHistoric']:
        return 1
    elif not row['isPreferredName'] and not row['isShortName'] and not row['isColloquial'] and not row['isHistoric']:
        return 2
    elif not row['isPreferredName'] and row['isShortName'] and not row['isColloquial'] and not row['isHistoric']:
        return 3
    else:
        return 4

# Add a priority column to the DataFrame
df['priority'] = df.apply(determine_priority, axis=1)

# Sort the DataFrame by priority and geonameId
df.sort_values(by=['priority', 'geonameId'], inplace=True)

# Select the first row for each geonameId
result_df = df.groupby('geonameId').first()
# Log the dataset
print(result_df)