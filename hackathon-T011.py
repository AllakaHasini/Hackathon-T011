import openmeteo_requests
import requests_cache
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from retry_requests import retry
import html

# Setup API client with caching and retries
cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# API URL and parameters
url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": 52.52,
    "longitude": 13.41,
    "start_date": "2025-02-16",
    "end_date": "2025-03-02",
    "hourly": ["temperature_2m", "rain", "wind_speed_10m"],
    "daily": ["temperature_2m_max", "temperature_2m_min", "wind_speed_10m_max"]
}

# Fetch weather data
responses = openmeteo.weather_api(url, params=params)
response = responses[0]

# Process Hourly Data
hourly = response.Hourly()
hourly_data = {
    "date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    ),
    "temperature_2m": hourly.Variables(0).ValuesAsNumpy(),
    "rain": hourly.Variables(1).ValuesAsNumpy(),
    "wind_speed_10m": hourly.Variables(2).ValuesAsNumpy(),
}

hourly_df = pd.DataFrame(hourly_data)

# Process Daily Data
daily = response.Daily()
daily_data = {
    "date": pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s", utc=True),
        end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=daily.Interval()),
        inclusive="left"
    ),
    "temperature_2m_max": daily.Variables(0).ValuesAsNumpy(),
    "temperature_2m_min": daily.Variables(1).ValuesAsNumpy(),
    "wind_speed_10m_max": daily.Variables(2).ValuesAsNumpy(),
}

daily_df = pd.DataFrame(daily_data)

# Set Seaborn style
sns.set_style("darkgrid")

# 📌 Temperature Trend (Hourly)
plt.figure(figsize=(10, 5))
sns.lineplot(data=hourly_df, x="date", y="temperature_2m", label="Temperature (°C)", color="red")
plt.xlabel("Date")
plt.ylabel("Temperature (°C)")
plt.title("Hourly Temperature Trend")
plt.xticks(rotation=45)
plt.legend()
plt.show()

# 📌 Rainfall Trend (Hourly)
plt.figure(figsize=(10, 5))
sns.lineplot(data=hourly_df, x="date", y="rain", label="Rain (mm)", color="blue")
plt.xlabel("Date")
plt.ylabel("Rain (mm)")
plt.title("Hourly Rainfall Trend")
plt.xticks(rotation=45)
plt.legend()
plt.show()

# 📌 Wind Speed (Daily Max)
plt.figure(figsize=(10, 5))
sns.barplot(data=daily_df, x="date", y="wind_speed_10m_max", color="purple")
plt.xlabel("Date")
plt.ylabel("Max Wind Speed (m/s)")
plt.title("Daily Max Wind Speed")
plt.xticks(rotation=45)

plt.show()
