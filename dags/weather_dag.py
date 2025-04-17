from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import requests
import pandas as pd
from sqlalchemy import create_engine

cities = [
    {"name": "Paris", "latitude": 48.85, "longitude": 2.35},
    {"name": "Nouakchott", "latitude": 18.08, "longitude": -15.98},
    {"name": "Tokyo", "latitude": 35.68, "longitude": 139.69}
]

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'weather_data_pipeline',
    default_args=default_args,
    description='A DAG to fetch and store weather data',
    schedule_interval=timedelta(days=1),
)

def fetch_weather_data():
    all_weather_data = []
    for city in cities:
        try:
            # Add current date parameter to get fresh forecasts
            current_date = datetime.now().date()
            url = (
                "https://api.open-meteo.com/v1/forecast"
                f"?latitude={city['latitude']}&longitude={city['longitude']}"
                "&hourly=temperature_2m,precipitation,windspeed_10m"
                f"&start_date={current_date}&end_date={current_date + timedelta(days=7)}"
                "&timezone=auto"
            )
            print(f"Fetching data for {city['name']} from URL: {url}")
            
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            data = response.json()
            print(f"Data received for {city['name']}: {data.keys()}")
            
            if 'hourly' not in data:
                raise ValueError(f"No hourly data found for {city['name']}")
                
            all_weather_data.append({
                "city": city["name"],
                "times": data["hourly"]["time"],
                "temperature": data["hourly"]["temperature_2m"],
                "precipitation": data["hourly"]["precipitation"],
                "windspeed": data["hourly"]["windspeed_10m"]
            })
            print(f"Successfully processed data for {city['name']}")
            
        except requests.RequestException as e:
            print(f"Error fetching data for {city['name']}: {str(e)}")
            raise
        except (KeyError, ValueError) as e:
            print(f"Error processing data for {city['name']}: {str(e)}")
            raise
        except Exception as e:
            print(f"Unexpected error for {city['name']}: {str(e)}")
            raise
            
    if not all_weather_data:
        raise ValueError("No weather data was collected for any city")
        
    return all_weather_data

def transform_weather_data(**context):
    weather_data_list = context['task_instance'].xcom_pull(task_ids='fetch_weather')
    transformed_data = []
    
    for city_data in weather_data_list:
        for i in range(len(city_data["times"])):
            transformed_data.append({
                'city': city_data['city'],
                'time': city_data['times'][i],
                'temperature': city_data['temperature'][i],
                'precipitation': city_data['precipitation'][i],
                'windspeed': city_data['windspeed'][i],
                'extraction_timestamp': datetime.now()
            })
    
    return transformed_data

def store_weather_data(**context):
    data = context['task_instance'].xcom_pull(task_ids='transform_weather')
    df = pd.DataFrame(data)
    
    engine = create_engine('postgresql+psycopg2://airflow:airflow@postgres/airflow')
    
    # Drop existing table to ensure correct schema
    with engine.connect() as connection:
        connection.execute("DROP TABLE IF EXISTS weather_data")
        connection.execute("""
            CREATE TABLE weather_data (
                id SERIAL PRIMARY KEY,
                city VARCHAR(255),
                time TIMESTAMP,
                temperature FLOAT,
                precipitation FLOAT,
                windspeed FLOAT,
                extraction_timestamp TIMESTAMP
            )
        """)
    
    # Store data
    df.to_sql('weather_data', engine, if_exists='append', index=False)

fetch_weather = PythonOperator(
    task_id='fetch_weather',
    python_callable=fetch_weather_data,
    dag=dag,
)

transform_weather = PythonOperator(
    task_id='transform_weather',
    python_callable=transform_weather_data,
    dag=dag,
)

store_weather = PythonOperator(
    task_id='store_weather',
    python_callable=store_weather_data,
    dag=dag,
)

fetch_weather >> transform_weather >> store_weather