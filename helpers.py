import requests
import zipfile
import io
import geohash
from pyproj import CRS, Transformer
from shapely.geometry import Point
from shapely.ops import transform

def download_and_extract(url, file_path):
  print(f'Downloading {file_path} from {url}')
  """Downloads a zip file from a URL and extracts the specified file."""
  response = requests.get(url, stream=True)
  response.raise_for_status()

  try:
    # Attempt to extract from zip file (for global_cities and alternate_names)
    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
      zip_ref.extract(file_path)
  except zipfile.BadZipFile:
    # If it's not a zip file (for admin1_codes), write the content directly
    with open(file_path, 'wb') as f:
      f.write(response.content)

def calculate_radius(population):
  if 0 <= population < 50000:
    return 400
  elif 50000 <= population < 100000:
    return 800
  elif 100000 <= population < 500000:
    return 2000
  elif 500000 <= population < 1000000:
    return 4000
  elif 1000000 <= population < 5000000:
    return 6000
  elif 5000000 <= population < 10000000:
    return 14000
  else: 
    return 16000

def add_geohash(row):
  """Calculates the geohash for a given latitude and longitude."""
  return geohash.encode(row['latitude'], row['longitude'], precision=12)

def geodesic_point_buffer(lat, lon, distance):
    # Azimuthal equidistant projection
    aeqd_proj = CRS.from_proj4(
        f"+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0")
    tfmr = Transformer.from_proj(aeqd_proj, aeqd_proj.geodetic_crs)
    buf = Point(0, 0).buffer(distance)  # distance in metres
    return transform(tfmr.transform, buf)

def determine_priority(row):
    if row['is_preferred_name'] == True and row['is_short_name'] == False and row['is_colloquial'] == False and row['is_historic'] == False:
        return 1
    elif row['is_preferred_name'] == False and row['is_short_name'] == False and row['is_colloquial'] == False and row['is_historic'] == False:
        return 2
    elif row['is_preferred_name'] == False and row['is_short_name'] == True and row['is_colloquial'] == False and row['is_historic'] == False:
        return 3
    else:
        return 4
    
def check_names_city_country(row):
    name = str(row['alternate_name_city']).lower().strip()
    country = str(row['alternate_name_country']).lower().strip()
    return country in name

def check_names_city_admin1(row):
    name = str(row['alternate_name_city']).lower().strip()
    admin1 = str(row['alternate_name_admin1']).lower().strip()
    return name in admin1 or admin1 in name
