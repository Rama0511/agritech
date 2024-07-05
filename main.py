import requests
import json
import mysql.connector
import time
from datetime import datetime, timedelta
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd

# Database configuration
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'agritech'
}

# URLs and file paths
url = 'https://myapplication-2d043.firebaseio.com/SOILL.json'
geojson_file = 'map.geojson'
stations_file = 'stations.json'

# Define utility functions
def load_geojson(geojson_file):
    try:
        return gpd.read_file(geojson_file)
    except Exception as e:
        print(f"Error loading GeoJSON file: {e}")
        return None

def get_location(gdf, lat, lon):
    try:
        point = Point(lon, lat)
        for idx, row in gdf.iterrows():
            if row['geometry'].contains(point):
                return row['name']  
        return "Location not found"
    except Exception as e:
        return f"Error during location search: {e}"

def load_stations(stations_file):
    try:
        with open(stations_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading stations file: {e}")
        return None

def get_nearest_station(location, stations):
    for station in stations:
        if station['lokasi'] == location:
            return station['stasiun_terdekat']
    return "Station not found"

def fetch_and_update_data():
    response = requests.get(url)
    print("URL Didapat")
    if response.status_code == 200:
        print("DB Request")
        data = response.json()
        cnx = mysql.connector.connect(**db_config)
        print("DB Didapat")
        cursor = cnx.cursor()
        gdf = load_geojson(geojson_file)
        stations = load_stations(stations_file)
        for device_id, device_info in data.items():
            iddevice = device_info.get('iddevice', 'NULL')
            nama = device_info.get('nama', 'NULL')
            komoditi = device_info.get('komoditi', 'NULL')
            jenis = device_info.get('jenis', 'NULL')
            wilayah = device_info.get('wilayah', 'NULL')
            lat = device_info.get('lat', 'NULL')
            long = device_info.get('long', 'NULL')
            baterai = device_info.get('baterai', 'NULL')
            soilec = device_info.get('soilec', 'NULL')
            suhutanah = device_info.get('suhutanah', 'NULL')
            nilai = device_info.get('nilai', 'NULL')
            nomoriot = device_info.get('nomoriot', 'NULL')
            ket = device_info.get('ket', 'NULL')
            tanggal = device_info.get('tanggal', 'NULL')
            waktu = device_info.get('waktu', 'NULL')
            tanggalupdate = device_info.get('tanggalupdate', 'NULL')
            waktuupdate = device_info.get('waktuupdate', 'NULL')
            location = get_location(gdf, float(lat), float(long))
            stasiun = get_nearest_station(location, stations)
            check_query = ("SELECT * FROM device_data WHERE iddevice = %s")
            cursor.execute(check_query, (iddevice,))
            result = cursor.fetchone()
            if result:
                update_query = ("""
                    UPDATE device_data
                    SET nama=%s, komoditi=%s, jenis=%s, wilayah=%s, lat=%s, longt=%s, baterai=%s, soilec=%s, suhutanah=%s, nilai=%s, nomoriot=%s, ket=%s, tanggal=%s, waktu=%s, tanggalupdate=%s, waktuupdate=%s, stasiun=%s
                    WHERE iddevice=%s
                """)
                cursor.execute(update_query, (nama, komoditi, jenis, wilayah, lat, long, baterai, soilec, suhutanah, nilai, nomoriot, ket, tanggal, waktu, tanggalupdate, waktuupdate, stasiun, iddevice))
            else:
                insert_query = ("""
                    INSERT INTO device_data (iddevice, nama, komoditi, jenis, wilayah, lat, longt, baterai, soilec, suhutanah, nilai, nomoriot, ket, tanggal, waktu, tanggalupdate, waktuupdate, stasiun)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """)
                cursor.execute(insert_query, (iddevice, nama, komoditi, jenis, wilayah, lat, long, baterai, soilec, suhutanah, nilai, nomoriot, ket, tanggal, waktu, tanggalupdate, waktuupdate, stasiun))
        cnx.commit()
        cursor.close()
        cnx.close()
        print("Sukses update data device form firebase")
    else:
        print(f"Failed to retrieve data: {response.status_code}")

sensor_companies = [
    ("e652946f-41bb-4796-a7ed-f3d583c16ced", "OP 1"),
    ("7e10d82c-6bac-41b0-a5a3-230f99f89a89", "Kijung"),
    ("f2dca796-17a1-416b-a7fd-2bdf2da27968", "Lakop"),
    ("e637a3d4-f3d8-48af-986a-1bf738b1af91", "RnD"),
    ("cd80d441-747d-43e1-8e2c-26f3472168ac", "Divisi 4"),
    ("271fc161-b3cd-403d-8bf8-f6fc27da6145", "OP 2"),
    ("b598f938-e154-4140-8aef-28062e1e4063", "PG 3 Central"),
    ("d77f1ab5-b779-47ca-8d0e-83b6c79643b0", "Paris"),
    ("84cd3fd0-51cb-4424-b51b-f83d6e5ce0b3", "Traknus"),
    ("829abc49-16cc-497e-bd2d-0c526873ac37", "Taru"),
    ("24a3567c-48c5-4691-a04b-d02187b2bd45", "PH"),
    ("0b49974a-6560-4bc0-81c7-865332659550", "PG 4 Central")
]

bulan_dict = {
    "Jan": "Jan", "Feb": "Feb", "Mar": "Mar", "Apr": "Apr", "Mei": "May", "Jun": "Jun",
    "Jul": "Jul", "Agu": "Aug", "Sep": "Sep", "Okt": "Oct", "Nov": "Nov", "Des": "Dec"
}

def convert_bulan(bulan):
    for indo, eng in bulan_dict.items():
        bulan = bulan.replace(indo, eng)
    return bulan

def get_token():
    url = "https://data.mertani.co.id/users/login"
    data = {
        "strategy": "web",
        "email": "reza26pahlevi@gmail.com",
        "password": "divisi02"
    }
    response = requests.post(url, json=data)
    data = json.loads(response.content)
    access_token = data["data"]["accessToken"]
    # print(access_token)
    return access_token

def fetch_sensor_data(api_url, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: Unable to fetch data. Status code: {response.status_code}")
        return None

def run_datamic_script():
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    start_date = '2024-01-01'
    try:
        final_df = pd.DataFrame()

        for sensor_company_id, sensor_company_name in sensor_companies:
            api_url = f"https://data.mertani.co.id/sensors/records?sensor_company_id={sensor_company_id}&start={start_date}&end={current_date}"
            token = get_token()
            api_response = fetch_sensor_data(api_url, token)

            if api_response and 'data' in api_response and 'data' in api_response['data']:
                data_list = api_response['data']['data'][0]['sensor_records']
                labels = [entry['datetime'] for entry in data_list]
                values = [entry['value_calibration'] for entry in data_list]

                df = pd.DataFrame({'Date': labels, f'{sensor_company_name}': values})

                if final_df.empty:
                    final_df = df
                else:
                    final_df = pd.merge(final_df, df, on='Date', how='outer')

        final_df = final_df.fillna(0)
        final_df['Date'] = pd.to_datetime(final_df['Date'], format='%Y-%m-%d %H:%M:%S')
        final_df['Time'] = final_df['Date'].dt.time
        final_df['Date'] = final_df['Date'].dt.date
        print(final_df)

        cnx = mysql.connector.connect(user='root', password='', host='localhost', database='agritech')
        cursor = cnx.cursor()

        for row in final_df.itertuples(index=False):
            date = row.Date
            time = row.Time

            check_query = "SELECT Date FROM rainfalldata_microlimate WHERE Date = %s AND Time = %s"
            cursor.execute(check_query, (date, time))
            result = cursor.fetchone()

            if result:
                update_query = """UPDATE rainfalldata_microlimate
                                  SET `OP 1`=%s, Kijung=%s, Lakop=%s, RnD=%s, `Divisi 4`=%s, `OP 2`=%s, `PG 3 Central`=%s, Paris=%s, Traknus=%s, Taru=%s, PH=%s, `PG 4 Central`=%s
                                  WHERE Date=%s AND Time=%s"""
                cursor.execute(update_query, (*row[2:], date, time))
            else:
                insert_query = """INSERT INTO rainfalldata_microlimate (Date, Time, `OP 1`, Kijung, Lakop, RnD, `Divisi 4`, `OP 2`, `PG 3 Central`, Paris, Traknus, Taru, PH, `PG 4 Central`)
                                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(insert_query, (date, time, *row[2:]))

            # print(cursor.rowcount, "record(s) affected")

        cnx.commit()
        cursor.close()
        cnx.close()

        print("Data updated successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

def fetch_data_from_api(device_name):
    try:
        today = datetime.today()
        start_date = today - timedelta(days=29)
        end_date = today
        
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        print(f"Request API {device_name}")
        api_url = f"http://lebungapi.gg-foods.com/api?startDate={start_date_str}&endDate={end_date_str}&source={device_name}"
        response = requests.get(api_url, timeout=10) 
        print(f"Sukses Request API {device_name}")
        response.raise_for_status()
        data = response.json()
        return data['data']
    except requests.exceptions.Timeout:
        print(f"Timeout occurred for device {device_name}. Moving to the next device.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for device {device_name}: {e}")
        return None

def save_data_to_db(data):
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()
    for entry in data:
        entry_id = entry.get('entry_id')
        object_id = entry.get('object_id')
        sensor_id = entry.get('sensor_id')
        value = entry.get('value')
        date = entry.get('date')
        time = entry.get('time')
        trans_id = entry.get('trans_id') or None
        insert_query = """
        INSERT INTO api_data (entry_id, object_id, sensor_id, value, date, time, trans_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        object_id = VALUES(object_id),
        sensor_id = VALUES(sensor_id),
        value = VALUES(value),
        date = VALUES(date),
        time = VALUES(time),
        trans_id = VALUES(trans_id)
        """
        cursor.execute(insert_query, (entry_id, object_id, sensor_id, value, date, time, trans_id))
        cnx.commit()
    cursor.close()
    cnx.close()

def update_all_devices():
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()
    query = "SELECT nama FROM device_data"
    cursor.execute(query)
    device_names = cursor.fetchall()
    cursor.close()
    cnx.close()
    for device_name in device_names:
        device_name = device_name[0]
        print(f"Fetching data for device: {device_name}")
        data = fetch_data_from_api(device_name)
        if data:
            print(f"Saving data for {device_name}")
            save_data_to_db(data)
        time.sleep(5)

def main_loop():
    while True:
        print("Starting getdata.py script")
        fetch_and_update_data()
        print("Sleeping for 10 second...")
        time.sleep(10)

        print("Starting getdatamic.py script")
        run_datamic_script()
        print("Sleeping for 10 second...")
        time.sleep(10)

        print("Starting gethistory.py script")
        update_all_devices()
        print("Sleeping for 1 hours...")
        time.sleep(1 * 60 * 60)

if __name__ == "__main__":
    main_loop()
