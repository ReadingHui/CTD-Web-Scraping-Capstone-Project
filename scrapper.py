import csv
import numpy as np
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

from time import sleep

START_URL = 'https://www.timeanddate.com/weather/'
CITY_NAME = 'Los Angeles'
DRIVER = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

def get_city_link():
    body = DRIVER.find_element(By.CSS_SELECTOR, 'body[class="tpl-fluid "]')
    if body:
        weather_table = body.find_element(By.CSS_SELECTOR, 'table[class="zebra fw tb-theme"]')
        try: 
            city_link = weather_table.find_element(By.XPATH, f'.//td/a[text()="{CITY_NAME}"]').get_attribute('href')
        except NoSuchElementException:
            print('City name error, no such city exist.')
        # print(f'{CITY_NAME} weather page link: {city_link}') # For debug
    return city_link

def get_past_weather_link():
    nav_bar = DRIVER.find_element(By.CSS_SELECTOR, 'nav[class="nav-3"]')
    if nav_bar:
        nav_div = nav_bar.find_element(By.CSS_SELECTOR, 'div[class="fixed"]')
        past_link = nav_div.find_element(By.XPATH, './/a[text()="Yesterday/Past Weather"]').get_attribute('href')
        # print(f'{CITY_NAME} Past Weather Link: {past_link}') # For debug
    return past_link

def get_date_columns():
    weather_graph = DRIVER.find_element(By.CSS_SELECTOR, 'div[id="weather"]')
    columns = weather_graph.find_elements(By.CSS_SELECTOR, 'div[id^="ws_"]') # ^= means start with
    return columns

def get_weather_data(div_block):
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

def get_past_weather():
    columns = get_date_columns()
    div_block = DRIVER.find_element(By.CSS_SELECTOR, 'div[class="weatherTooltip"]')
    actions = ActionChains(DRIVER)
    past_weather = []
    for col in columns:
        actions.move_to_element(col).perform()  # Move cursor to columns to update Tooltip
        WebDriverWait(DRIVER, 5).until(lambda d: div_block.text.strip() != "") # Wait for Tooltip to update
        weather_data = get_weather_data(div_block)
        past_weather.append(weather_data)
        past_weather_df = pd.DataFrame(past_weather, columns=[
        'Weekday', 'Date', 'Time', 'Temp High', 'Temp Low', 
        'Condition', 'Humidity', 'Barometer', 'Wind Direction', 
        'Wind Degree', 'Wind Speed'])
    return past_weather_df

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
    # Loading the webpage    
    sleep(2)
    DRIVER.get(START_URL)

    # Get Los Angeles weather url
    city_link = get_city_link()
    
    # Get Past Weather link
    sleep(2)
    DRIVER.get(city_link)
    past_link = get_past_weather_link()


    # Get all date ids
    sleep(2)
    DRIVER.get(past_link)
    data = get_past_weather()

    # Save the data
    save(data, CITY_NAME.replace(' ', '_') + '_past_weather_data.csv', 'csv')
    save(data, CITY_NAME.replace(' ', '_') + '_past_weather_data.json', 'json')

    # Close session
    DRIVER.quit()

if __name__ == "__main__":
    main()