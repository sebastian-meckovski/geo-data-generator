import pandas as pd

# 1. Load allCountries.txt, admin1CodesASCII.txt and alternateNamesV2.txt as DataFrame objects
cities_input_file = "allCountries.txt"
alternate_names_file = "alternateNamesV2.txt"
admin_file_path = "admin1CodesASCII.txt"
language = "fr"

def determine_priority(row):
    if (
        row["isPreferredName"]
        and not row["isShortName"]
        and not row["isColloquial"]
        and not row["isHistoric"]
    ):
        return 1
    elif (
        not row["isPreferredName"]
        and not row["isShortName"]
        and not row["isColloquial"]
        and not row["isHistoric"]
    ):
        return 2
    elif (
        not row["isPreferredName"]
        and row["isShortName"]
        and not row["isColloquial"]
        and not row["isHistoric"]
    ):
        return 3
    else:
        return 4


# define column names
cities_column_names = [
    "geonameId",
    "name",
    "asciiname",
    "alternatenames",
    "latitude",
    "longitude",
    "feature_class",
    "feature_code",
    "country_code",
    "cc2",
    "admin1_code",
    "admin2_code",
    "admin3_code",
    "admin4_code",
    "population",
    "elevation",
    "dem",
    "timezone",
    "modification_date",
]
alternate_names_columns = [
    "alternateNameId",
    "geonameId",
    "isoLanguage",
    "alternateName",
    "isPreferredName",
    "isShortName",
    "isColloquial",
    "isHistoric",
    "from",
    "to",
]
admin_columns = ["key", "admin1name", "ascii_name", "geonameId"]

# Define data types for the columns
cities_dtype = {
    "geonameId": "int64",
    "name": "str",
    "asciiname": "str",
    "alternatenames": "str",
    "latitude": "float64",
    "longitude": "float64",
    "feature_class": "str",
    "feature_code": "str",
    "country_code": "str",
    "cc2": "str",
    "admin1_code": "str",
    "admin2_code": "str",
    "admin3_code": "str",
    "admin4_code": "str",
    "population": "int64",
    "elevation": "float64",
    "dem": "int64",
    "timezone": "str",
    "modification_date": "str",
}

# List of feature codes to filter by
feature_codes = [
    "PPLA",
    "PPLC",
    "PPL",
    "PPLW",
    "PPLG",
    "PPLL",
    "PPLS",
    "PPLF",
    "PPLR",
]

# Read the data into a pandas DataFrame objects
df_cities = pd.read_csv(
    cities_input_file,
    sep="\t",
    header=None,
    names=cities_column_names,
    dtype=cities_dtype,
    low_memory=False,
    keep_default_na=False,
    na_values="",
    encoding="utf-8",
)
df_alternate_names = pd.read_csv(
    alternate_names_file,
    sep="\t",
    header=None,
    names=alternate_names_columns,
    dtype=str,
    keep_default_na=False,
    na_values="",
    encoding="utf-8",
)
admin_df = pd.read_csv(
    admin_file_path,
    sep="\t",
    header=None,
    names=admin_columns,
    low_memory=False,
    encoding="utf-8",
)



# Filter the DataFrame for rows with the specified feature codes and population > 15000, then create a copy
filtered_df_by_population = df_cities[
    df_cities["feature_code"].isin(feature_codes) & (df_cities["population"] >= 15000)
].copy()

# 3. Update allCountries dataset to contain country geonameId (add column at the end)
# Get the DataFrame for countries (feature_code == 'PCLI')
pcli_df = df_cities[df_cities["feature_code"] == "PCLI"]
country_geonameId_map = pcli_df.set_index("country_code")["geonameId"].to_dict()

# Add the country_geonameId column to the filtered DataFrame using .loc
filtered_df_by_population.loc[:, "country_geonameId"] = (
    filtered_df_by_population["country_code"].map(country_geonameId_map).astype("Int64")
)

# 4. Clean alternateNames table to contain only one alternateName per geonameId per languageIsoCode
## for loop start
df_lang = df_alternate_names[df_alternate_names["isoLanguage"] == language].copy()

df_lang[["isPreferredName", "isShortName", "isColloquial", "isHistoric"]] = df_lang[
    ["isPreferredName", "isShortName", "isColloquial", "isHistoric"]
].fillna(0)

df_lang["priority"] = df_alternate_names.apply(determine_priority, axis=1)

df_lang.sort_values(by=["priority", "geonameId"], inplace=True)

# Select the first row for each geonameId in the filtered DataFrame
df_lang = df_lang.groupby("geonameId").first()

df_lang = df_lang.reset_index()
# Reorder the columns (excluding 'priority')
df_lang = df_lang[
    [
        "alternateNameId",
        "geonameId",
        "isoLanguage",
        "alternateName",
        "isPreferredName",
        "isShortName",
        "isColloquial",
        "isHistoric",
        "from",
        "to",
    ]
]  # Removed 'priority'

print(df_lang)

# 5. Merge allCountries with admin1CodesASCII with alternateNamesV2. If language not available - use original from allCountries

# 6. Remove duplicates per country

## for loop ends


# Adjust pandas settings to show all columns and rows (optional)
# pd.set_option('display.max_columns', None)  # Show all columns
# pd.set_option('display.expand_frame_repr', False)  # Prevent column wrapping
# pd.set_option('display.max_rows', None)  # Show all rows
