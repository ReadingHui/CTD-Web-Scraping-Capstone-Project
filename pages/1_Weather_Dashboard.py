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
st.set_page_config(page_title="Weather Dashboard")

# Global variables
CITIES = ['Los Angeles', 'Houston', 'New York']
FLAGS = {
    'Los Angeles': 'https://upload.wikimedia.org/wikipedia/commons/8/85/Flag_of_Los_Angeles%2C_California.svg',
    'Houston': 'https://upload.wikimedia.org/wikipedia/commons/7/7f/Flag_of_Houston%2C_Texas.svg',
    'New York': 'https://upload.wikimedia.org/wikipedia/commons/b/ba/Flag_of_New_York_City.svg'
}

@st.fragment(run_every='1s')
def live_clock(tz):
    now = datetime.now(tz=tz)
    date = now.date()
    time = now.time().strftime('%H:%M:%S')
    st.metric('Date', f"{date}")
    st.metric('Time', f"{time}")

# ===============
# Sidebar filters
# ===============
st.sidebar.header('Major US Cities')  # Sidebar title
city = st.sidebar.radio('Select Cities', CITIES)  # Dropdown to choose a product
st.sidebar.subheader('Past Weather')
past_weather_plot = st.sidebar.toggle("Show Past Weather Info", value=True)
if past_weather_plot:
    start_date = st.sidebar.date_input('Select Starting Date', '2026-03-01', min_value='2026-03-01', max_value='2026-05-31')
    end_date = st.sidebar.date_input('Select Ending Date', start_date, min_value=start_date, max_value='2026-05-31') + timedelta(days=1)
    past_temp_plot_data = st.sidebar.multiselect('Select temperature data', [
        'Temp High', 
        'Temp Low', 
        'Average Temp'
        ],
        'Average Temp')
    past_weather_plot_data = st.sidebar.multiselect('Select other weather data', [
        'Humidity',
        'Air Pressure',
        'Wind Speed'
    ],
    [
        'Humidity',
        'Air Pressure',
        'Wind Speed'
    ])
st.sidebar.subheader('Climate')
climate_plot = st.sidebar.toggle("Show Average Climate Info", value=True)
if climate_plot:
    climate_plot_data = st.sidebar.multiselect('Select data',[
        'High Temp',
        'Mean Temp',
        'Low Temp',
        'Precipitation',
        'Humidity',
        'Dew Point',
        'Wind',
        'Pressure',
        'Visibility'
    ], [
        'High Temp',
        'Low Temp',
        'Mean Temp'
    ])

# Build query to database
past_temp_query = f"""
        SELECT * FROM Past_Weather
        WHERE City = ? AND
        Date >= ? AND
        Date <= ?
        """

climate_query = f"""
        SELECT * FROM Climate
        WHERE City = ?
        """

# Connect to the database
try:
    with sqlite3.connect("db/weather.db") as conn:
        cursor = conn.cursor()
        if past_weather_plot:
            cursor.execute(past_temp_query, (city, start_date, end_date))
            columns = [description[0] for description in cursor.description]
            past_df = pd.DataFrame(cursor.fetchall(), columns=columns)
        if climate_plot:
            cursor.execute(climate_query, (city,))        
            columns = [description[0] for description in cursor.description]
            climate_df = pd.DataFrame(cursor.fetchall(), columns=columns)

except sqlite3.Error as e:
    print(f"An error occurred while connecting to the database: {e}")

# ============================
# Main app content starts here
# ============================
st.title(f'{city} Weather Dashboard')  # Big title for the dashboard
st.subheader('Current Weather')

# Current weather info (API call)
current_info = current.getCurrentWeather(city)

city_col, dt_col = st.columns(2)  # Create two columns for layout

with city_col:
    st.metric('City', f"{city}") 
    st.image(FLAGS[city], width=100)
with dt_col:
    live_clock(ZoneInfo(current_info['timezone']))

c_temp_col, c_weather_col = st.columns(2)

with c_temp_col:
    st.metric('Temperature', f"{current_info['temp']} °F")
with c_weather_col:
    st.metric(f'Current Weather', f"{current_info['weather_desc']} ![Weather Icon]({current_info['wicon']})")

c_hum_col, c_wspeed_col, c_wdir_col = st.columns(3)

with c_hum_col:
    st.metric('Relative Humidity', f"{current_info['humidity']}%")
with c_wspeed_col:
    st.metric('Wind Speed', f"{current_info['wind_speed']} mph")
with c_wdir_col:
    st.metric('Wind Direction', f"{current_info['wind_direction']}°")
if past_weather_plot:
    st.divider()
    # Past temp info
    st.subheader(f'Past Weather Graph from {start_date} to {end_date}')  # Subheading for the chart
    past_df['Temp High'] = past_df.groupby('Date')['Temp High'].transform('max')
    past_df['Temp Low'] = past_df.groupby('Date')['Temp Low'].transform('min')
    past_df['Average Temp'] = past_df.groupby('Date')['Average Temp'].transform('mean')
    if end_date - start_date == timedelta(days=1):
        past_temp_graph = px.scatter(past_df, x='Date', y=past_temp_plot_data, title='Past Temperature Graph')  # Just the point
    else:
        past_temp_graph = px.line(past_df.sort_values('Date'), x='Date', y=past_temp_plot_data, title='Past Temperature Graph')  # Line graph
    past_temp_graph.update_traces(mode="markers+lines", hovertemplate=None)
    past_temp_graph.update_layout(hovermode="x unified")
    if past_temp_plot_data:
        st.plotly_chart(past_temp_graph, key='past_temp_graph')  # Render the chart in the app

    # Past other info
    past_df['Humidity'] = past_df.groupby('Date')['Humidity'].transform('mean')
    past_df['Air Pressure'] = past_df.groupby('Date')['Air Pressure'].transform('min')
    past_df['Wind Speed'] = past_df.groupby('Date')['Wind Speed'].transform('mean')
    if past_weather_plot_data:
        if end_date - start_date == timedelta(days=1):
            past_weather_graph = px.scatter(past_df, x='Date', y=[f for f in past_weather_plot_data if f != 'Wind Speed'], title='Past Other Info Graph')  # Just the point
            
        else:
            past_weather_graph = px.line(past_df.sort_values('Date'), x='Date', y=[f for f in past_weather_plot_data if f != 'Wind Speed'], title='Past Other Info Graph')  # Line graph
        if 'Wind Speed' in past_weather_plot_data:
            past_weather_graph.add_trace(go.Scatter(
                x=past_df['Date'],
                y=past_df['Wind Speed'],
                mode='lines',
                name='Wind Speed',
                customdata=past_df['Wind Direction'],
                hovertemplate='Date: %{x}<br>' + 
                'Wind Speed: %{y}<br>' + 
                'Wind Direction: %{customdata}<br><extra></extra>',

            ))
        past_weather_graph.update_traces(mode='lines+markers')
        st.plotly_chart(past_weather_graph)  # Render the chart in the app

    # Past Wind Directions and Conditions
    st.markdown('#### Pie charts of Wind Directions and Weather Conditions')
    p_wdir_col, p_cond_col = st.columns(2)
    with p_wdir_col:
        past_wdir = pd.DataFrame((past_df['Wind Direction'].value_counts() / 4).reset_index())
        past_wdir_graph = px.pie(past_wdir, names='Wind Direction', values='count', title='Wind Directions')
        st.plotly_chart(past_wdir_graph, key='past_wdir_graph')
    with p_cond_col:
        past_cond = pd.DataFrame((past_df['Condition'].value_counts() / 4).reset_index())
        past_cond_graph = px.pie(past_cond, names='Condition', values='count', title='Conditions')
        st.plotly_chart(past_cond_graph, key='past_cond_graph')

# Climate info
climate_temp = {'High Temp', 'Mean Temp', 'Low Temp'}
if climate_plot:
    st.divider()
    st.subheader('Average Climate Info during 1992 - 2021')
    if set(climate_plot_data).intersection(climate_temp):
        climate_temp_graph = px.line(climate_df, x='Month', y=[f for f in climate_plot_data if f in climate_temp], title='Climate Temperature Graph')
        climate_temp_graph.update_traces(mode="markers+lines", hovertemplate=None)
        climate_temp_graph.update_layout(hovermode='x unified')
        st.plotly_chart(climate_temp_graph)
    if set(climate_plot_data) - climate_temp:
        climate_other_graph = px.line(climate_df, x='Month', y=[f for f in climate_plot_data if f not in climate_temp], title='Other Climate Info Graph')
        climate_other_graph.update_traces(mode="markers+lines")
        st.plotly_chart(climate_other_graph)