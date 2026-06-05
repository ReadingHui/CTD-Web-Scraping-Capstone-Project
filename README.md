# CTD Web Scraping Capstone Project: Major US City Weather
In partial completion of the CTD Python Essential Course requirement, a project on web scraping for data, perform data cleaning, and present them in a Streamlit webapp.

## Project Structure
```
├── csv/                    # Scraped csv files
├── db/                     # SQLite3 DB
├── json/                   # Scraped json files
├── pages/                  # Pages in the streamlit web app
├── current.py              # Help py for getting current weather
├── data_cleaning.ipynb     # Data Cleaning Jupyter Notebook
├── Front_Page.py           # Landing page of streamlit app
├── scaper.py               # Scraping logic
├── README.md
└── requirements.txt
```

## Methodology
- Web scraping: Selenium for dynamic website scraping.
- Data Cleaning: Fill the empty entries by `np.nan`.
- Data Augmentation: Added features like `Average Temp` and `Temp Diff`, also decomposed date & time into date, time, week, month, day etc..
- Database Incorportation: Saved the scraped data in SQLite database.
- Dashboard: Applied Streamlit library to create dashboard for presentation of the weather data.

## Installation
1. **Prerequisites**: ChromeDriver, Python
2. **Installation**: 
```Bash
pip install -r requirements.txt
```
3. **Scraping**:
```Bash
python scaper.py
```
4. **Data Cleaning**:
Open and run the `data_cleaning.ipynb` notebook for data cleaning.

5. **Local deployment**:
```Bash
streamlit run Front_Page.py
```
6. **Web App**:
[Weather Dashboard](https://ctd-web-scraping-capstone-project-reading-hui.streamlit.app/Weather_Dashboard)

