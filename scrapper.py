import csv
import numpy as np
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

from time import sleep

START_URL = 'https://www.timeanddate.com/weather/'
CITIES = ['Los Angeles', 'Houston', 'New York']
CITY_NAME = 'Los Angeles'
DRIVER = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

def get_city_link(city: str=CITY_NAME):
    body = DRIVER.find_element(By.CSS_SELECTOR, 'body[class="tpl-fluid "]')
    if body:
        weather_table = body.find_element(By.CSS_SELECTOR, 'table[class="zebra fw tb-theme"]')
        try: 
            city_link = weather_table.find_element(By.XPATH, f'.//td/a[text()="{city}"]').get_attribute('href')
        except NoSuchElementException:
            print('City name error, no such city exist.')
        # print(f'{city} weather page link: {city_link}') # For debug
    return city_link

def get_weather_links(city: str=CITY_NAME):
    nav_bar = DRIVER.find_element(By.CSS_SELECTOR, 'nav[class="nav-3"]')
    if nav_bar:
        nav_div = nav_bar.find_element(By.CSS_SELECTOR, 'div[class="fixed"]')
        forecast_link = nav_div.find_element(By.XPATH, './/a[text()="14 Day Forecast"]').get_attribute('href')
        past_link = nav_div.find_element(By.XPATH, './/a[text()="Yesterday/Past Weather"]').get_attribute('href')
        climate_link = nav_div.find_element(By.XPATH, './/a[text()="Climate (Averages)"]').get_attribute('href')
        # print(f'{city} Past Weather Link: {past_link}') # For debug

    return forecast_link, past_link, climate_link

def get_date_columns():
    weather_graph = DRIVER.find_element(By.CSS_SELECTOR, 'div[id="weather"]')
    columns = weather_graph.find_elements(By.CSS_SELECTOR, 'div[id^="ws_"]') # ^= means start with
    return columns

def get_forecast_weather_data(div_block):
    weather_data = {}
    # Get the date
    full_date = div_block.find_element(By.CSS_SELECTOR, 'div[class="date"]').get_attribute('textContent').split(', ')
    weather_data['Weekday'] = full_date[0]
    weather_data['Date'] = full_date[1]
    # print(weather_data['Date']) # For debug

    # Get to the blocks
    inner_block = div_block.find_element(By.CSS_SELECTOR, 'div[class="inner__block"]')
    blocks = inner_block.find_elements(By.XPATH, './div')
    left_block = blocks[0]
    middle_block = blocks[1]
    right_block = blocks[2]

    # Get left block info
    temp = left_block.find_element(By.CSS_SELECTOR, 'div[class="temp"]').get_attribute('textContent').rstrip(' °F').split(' / ')
    weather_data['Temp High'] = float(temp[0])
    weather_data['Temp Low'] = float(temp[1])
    weather_data['Condition'] = left_block.find_element(By.CSS_SELECTOR, 'div[class="wdesc"]').get_attribute('textContent').rstrip('.')

    # Get middle block info
    mid_data = middle_block.find_elements(By.CSS_SELECTOR, 'div')
    weather_data['Feels Like'] = float(mid_data[0].get_attribute('textContent').split(':')[1].rstrip('°F').strip())
    weather_data['Humidity'] = float(mid_data[1].get_attribute('textContent').split(':')[1].rstrip('%').strip())
    precipitation = mid_data[2].get_attribute('textContent').split(':')
    weather_data['Precipitation_Rain'] = float(precipitation[2].strip().split(' ')[0])
    weather_data['Precipitation_Snow'] = float(precipitation[3].strip())
    weather_data['Precipitation Chance'] = float(mid_data[3].get_attribute('textContent').split(':')[1].rstrip('%').strip())

    # Get right block info
    wind_dir_block = right_block.find_element(By.CSS_SELECTOR, 'div[class="windDirection"]')
    weather_data['Wind Direction'] = wind_dir_block.get_attribute('textContent')
    rotation = (right_block
        .find_element(By.CSS_SELECTOR, 'canvas[id="tt-wind"]')
        .get_attribute('style'))
    if rotation:
        weather_data['Wind Degree'] = float(
            rotation
            .split('(')[1]
            .split('deg')[0]
            )
    else:
        weather_data['Wind Degree'] = np.nan
    weather_data['Wind Speed'] = float(
        wind_dir_block.find_element(By.XPATH, 'following-sibling::div')
        .get_attribute('textContent')
        .split(':')[1]
        .rstrip('mph')
        .strip()
    )

    return weather_data

def get_past_weather_data(div_block):
    weather_data = {}

    # Get the date
    full_date = div_block.find_element(By.CSS_SELECTOR, 'div[class="date"]').get_attribute('textContent').split(', ')
    weather_data['Weekday'] = full_date[0]
    weather_data['Date'] = ', '.join([full_date[1], full_date[2]])
    weather_data['Time'] = full_date[3]
    # print(weather_data['Date'] + ' ' + weather_data['Time']) # For debug

    # Get to the blocks
    inner_block = div_block.find_element(By.CSS_SELECTOR, 'div[class="inner__block"]')
    blocks = inner_block.find_elements(By.XPATH, './div')
    left_block = blocks[0]
    middle_block = blocks[1]
    right_block = blocks[2]

    # Check if data is available, if not, assign NaN to all the fields and return
    if 'No weather data available' in left_block.get_attribute('textContent'):
        weather_data['Temp High'] = np.nan
        weather_data['Temp Low'] = np.nan
        weather_data['Condition'] = np.nan
        weather_data['Humidity'] = np.nan
        weather_data['Barometer'] = np.nan
        weather_data['Wind Direction'] = np.nan
        weather_data['Wind Degree'] = np.nan
        weather_data['Wind Speed'] = np.nan
        return weather_data

    # Get left block info
    temp = left_block.find_element(By.CSS_SELECTOR, 'div[class="temp"]').get_attribute('textContent').rstrip(' °F').split(' / ')
    weather_data['Temp High'] = float(temp[0])
    weather_data['Temp Low'] = float(temp[1])
    weather_data['Condition'] = left_block.find_element(By.CSS_SELECTOR, 'div[class="wdesc"]').get_attribute('textContent').rstrip('.')

    # Get middle block info
    mid_data = middle_block.find_elements(By.CSS_SELECTOR, 'div')
    weather_data['Humidity'] = float(mid_data[0].get_attribute('textContent').split(':')[1].rstrip('%').strip())
    weather_data['Barometer'] = float(mid_data[1].get_attribute('textContent').split(':')[1].rstrip('"Hg').strip())

    # Get right block info
    wind_dir_block = right_block.find_element(By.CSS_SELECTOR, 'div[class="windDirection"]')
    weather_data['Wind Direction'] = wind_dir_block.get_attribute('textContent')
    rotation = (right_block
        .find_element(By.CSS_SELECTOR, 'canvas[id="tt-wind"]')
        .get_attribute('style'))
    if rotation:
        weather_data['Wind Degree'] = float(
            rotation
            .split('(')[1]
            .split('deg')[0]
            )
    else:
        weather_data['Wind Degree'] = np.nan
    weather_data['Wind Speed'] = float(
        wind_dir_block.find_element(By.XPATH, 'following-sibling::div')
        .get_attribute('textContent')
        .split(':')[1]
        .rstrip('mph')
        .strip()
    )
    
    return weather_data

def get_climate_data(div_block):
    weather_data = {}
    # Get the month
    weather_data['Month'] = div_block.get_attribute('class').split('--')[1].capitalize()
    data = div_block.find_elements(By.CSS_SELECTOR, 'p')
    for p in data:
        full_text = p.get_attribute('textContent')
        split_text = full_text.split(': ')
        title = split_text[0]
        split_text[1] = split_text[1].strip()
        if '°F' in split_text[1] or 'mi' in split_text[1] :
            value = float(split_text[1].split('\xa0')[0])
        elif 'mph' in split_text[1] or '"Hg' in split_text[1]:
            value = float(split_text[1].split(' ')[0])
        else:
            value = float(split_text[1][:-1])
        weather_data[title] = value
    return weather_data


def get_forecast_weather(city: str=CITY_NAME):
    columns = get_date_columns()
    div_block = DRIVER.find_element(By.CSS_SELECTOR, 'div[class="weatherTooltip"]')
    actions = ActionChains(DRIVER)
    forecast_weather = []
    for col in columns:
        actions.move_to_element(col).perform()  # Move cursor to columns to update Tooltip
        WebDriverWait(DRIVER, 5).until(lambda d: div_block.text.strip() != "") # Wait for Tooltip to update
        weather_data = get_forecast_weather_data(div_block)
        forecast_weather.append(weather_data)
        forecast_weather_df = pd.DataFrame(forecast_weather, columns=[
        'Weekday', 'Date', 'Temp High', 'Temp Low', 
        'Condition', 'Feels Like', 'Humidity', 'Precipitation_Rain', 'Precipitation_Snow', 'Precipitation Chance', 'Wind Direction', 
        'Wind Degree', 'Wind Speed'])
        forecast_weather_df['City'] = city
    return forecast_weather_df

def get_past_weather(city: str=CITY_NAME):
    months = ['2026-05', '2026-04', '2026-03', '2026-02', '2026-01']
    past_weather_dfs = []    
    for month in months: 
        month_dropdown = DRIVER.find_element(By.CSS_SELECTOR, 'select[id="month"]')
        select = Select(month_dropdown)
        select.select_by_value(month) # Select months one by one to get the months weather data

        columns = get_date_columns()
        div_block = DRIVER.find_element(By.CSS_SELECTOR, 'div[class="weatherTooltip"]')
        actions = ActionChains(DRIVER)
        past_weather = []
        for col in columns:
            actions.move_to_element(col).perform()  # Move cursor to columns to update Tooltip
            WebDriverWait(DRIVER, 5).until(lambda d: div_block.text.strip() != "") # Wait for Tooltip to update
            weather_data = get_past_weather_data(div_block)
            past_weather.append(weather_data)
        past_weather_dfs.append(
            pd.DataFrame(past_weather, columns=[
            'Weekday', 'Date', 'Time', 'Temp High', 'Temp Low', 
            'Condition', 'Humidity', 'Barometer', 'Wind Direction', 
            'Wind Degree', 'Wind Speed']))
    past_weather_df = pd.concat(past_weather_dfs, ignore_index=True)
    past_weather_df['City'] = city
    return past_weather_df

def get_climate(city: str=CITY_NAME):
    months = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
    div_blocks = [DRIVER.find_element(By.CSS_SELECTOR, f'div[class="climate-month climate-month--{m}"]') for m in months]
    climate = []
    for block in div_blocks:
        climate_data = get_climate_data(block)
        climate.append(climate_data)
        climate_df = pd.DataFrame(climate, columns=[
        'Month', 'High Temp', 'Low Temp', 'Mean Temp', 'Precipitation', 
        'Humidity', 'Dew Point', 'Wind', 'Pressure', 'Visibility'])
    climate_df['City'] = city
    return climate_df

def save(data: pd.DataFrame, filename: str, filetype: str):
    if filetype == 'csv':
        if filename[-4:] != '.csv':
            filename += '.csv'
        data.to_csv('csv/' + filename, index=False)
    elif filetype == 'json':
        if filename[-5:] != '.json':
            filename += '.json'
        data.to_json('json/' + filename, index=False) 
    else:
        raise TypeError('Only support saving to csv or json files.')

def main():
    forecast_data_list = []
    past_data_list = []
    climate_data_list = []

    for city in CITIES:
        # Loading the starting webpage    
        sleep(2)
        DRIVER.get(START_URL)

        # Get city weather url
        city_link = get_city_link(city)
        
        # Get Past Weather link
        sleep(2)
        DRIVER.get(city_link)
        forecast_link, past_link, climate_link = get_weather_links(city)

        # Get forecast weather data
        sleep(2)
        DRIVER.get(forecast_link)
        print('Scrapping Weather Forecast...')
        forecast_data_list.append(get_forecast_weather(city))

        # Get past weather data
        sleep(2)
        DRIVER.get(past_link)
        print('Scrapping Weather History...')
        past_data_list.append(get_past_weather(city))

        # Get climate data
        sleep(2)
        DRIVER.get(climate_link)
        print('Scrapping climate data...')
        climate_data_list.append(get_climate(city))

    # Close session
    DRIVER.quit()

    # Join the dfs
    forecast_data = pd.concat(forecast_data_list, ignore_index=True)
    past_data = pd.concat(past_data_list, ignore_index=True)
    climate_data = pd.concat(climate_data_list, ignore_index=True)

    # Save the data
    print('Saving data...')
    save(forecast_data, 'forecast_weather_data.csv', 'csv')
    save(forecast_data, 'forecast_weather_data.json', 'json')
    save(past_data, 'past_weather_data.csv', 'csv')
    save(past_data, 'past_weather_data.json', 'json')
    save(climate_data, 'climate_data.csv', 'csv')
    save(climate_data, 'climate_data.json', 'json')
    print('Data saved.')

if __name__ == "__main__":
    main()