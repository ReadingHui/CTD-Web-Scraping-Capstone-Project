import streamlit as st  
import pandas as pd     # Used to work with tabular data
import numpy as np      # Helps generate random numbers
import plotly.express as px  # For interactive charts
import plotly.graph_objects as go
import sqlite3 # For accessing DB
import current # Helper function to get current info
from zoneinfo import ZoneInfo

from datetime import datetime, timedelta

# Setting page title
st.set_page_config(page_title="Cross Info Dashboard")

# Global variables
CITIES = ['Los Angeles', 'Houston', 'New York']
FLAGS = {
    'Los Angeles': 'https://upload.wikimedia.org/wikipedia/commons/8/85/Flag_of_Los_Angeles%2C_California.svg',
    'Houston': 'https://upload.wikimedia.org/wikipedia/commons/7/7f/Flag_of_Houston%2C_Texas.svg',
    'New York': 'https://upload.wikimedia.org/wikipedia/commons/b/ba/Flag_of_New_York_City.svg'
}
WEATHER_FEATURES = [
        'Temp High', 
        'Temp Low', 
        'Average Temp',
        'Condition',
        'Humidity',
        'Air Pressure',
        'Wind Direction',
        'Wind Speed'
        ]

# ===============
# Sidebar filters
# ===============
st.sidebar.header('Major US Cities')  # Sidebar title
city = st.sidebar.radio('Select Cities', CITIES)  # Dropdown to choose a product
st.sidebar.subheader('Select weather info')
start_date = st.sidebar.date_input('Select Starting Date', '2026-03-01', min_value='2026-03-01', max_value='2026-05-31')
end_date = st.sidebar.date_input('Select Ending Date', '2026-05-31', min_value=start_date, max_value='2026-05-31') + timedelta(days=1)
first_data = st.sidebar.selectbox('Select first data (x-axis)', WEATHER_FEATURES, index=None, placeholder='Select your first data...')
second_data = st.sidebar.selectbox('Select second data (y-axis)', WEATHER_FEATURES, index=None, placeholder='Select your second data...')
if not first_data or not second_data:
    error_flag = True
    st.sidebar.warning("Select two different data above to start.")
elif first_data == second_data:
    error_flag = True
    st.sidebar.warning("Select two different data above.")
else:
    error_flag = False

# Build query to database
query = f"""
        SELECT `{first_data}`, `{second_data}`, `Month` FROM Past_Weather
        WHERE City = ? AND
        Date >= ? AND
        Date <= ?
        """

# Connect to the database
try:
    with sqlite3.connect("db/weather.db") as conn:
        cursor = conn.cursor()
        if not error_flag:
            cursor.execute(query, (city, start_date, end_date))
            columns = [description[0] for description in cursor.description]
            weather_df = pd.DataFrame(cursor.fetchall(), columns=columns)
            weather_dtype = weather_df.dtypes.to_list()

except sqlite3.Error as e:
    print(f"An error occurred while connecting to the database: {e}")

# ============================
# Main app content starts here
# ============================
st.title(f'{city} Weather Analysis')  # Big title for the dashboard
if not error_flag:
    if weather_dtype[0] == np.float64 and weather_dtype[1] == np.float64:
        plot = px.scatter(weather_df, x=first_data, y=second_data, title=f'Scatter plot of {first_data} against {second_data}', color='Month')
        st.plotly_chart(plot)
        st.metric('Correlation coefficient', f"{weather_df[first_data].corr(weather_df[second_data]):.2f}")
    elif isinstance(weather_dtype[0], pd.StringDtype) and weather_dtype[1] == np.float64:
        plot = px.box(weather_df, x=first_data, y=second_data, title=f'Box plot of {first_data} against {second_data}', color=first_data)
        plot.update_layout(showlegend=False)
        st.plotly_chart(plot)
    elif weather_dtype[0] == np.float64 and isinstance(weather_dtype[1], pd.StringDtype):
        plot = px.box(weather_df, x=first_data, y=second_data, title=f'Box plot of {first_data} against {second_data}', color=second_data, orientation='h')
        plot.update_layout(showlegend=False)
        st.plotly_chart(plot)
    else:
        plot = px.histogram(weather_df, x=first_data, color=second_data, barmode='group')
        st.plotly_chart(plot)
else:
    st.write("Select data on the left to begin.")