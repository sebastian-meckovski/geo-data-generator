# 1. Load allCountries.txt, admin1CodesASCII.txt and alternateNamesV2.txt
# 2. Filter only cities > 15,000 population
# 3. Update allCountries dataset to contain country geonameId (add column at the end)
# 4. Clean alternateNames table to contain only one alternateName per geonameId per languageIsoCode
# 5. Mege allCountries with admin1CodesASCII with alternateNamesV2. If language not available - use original from allCountries
# 6. Remove duplicates per country