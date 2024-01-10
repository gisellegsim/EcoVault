"""
Credits to Data Professor:
    https://github.com/dataprofessor/streamlit-12
and Quinton Pang:
    https://github.com/QuintonPang/Cryptocurrency-Analyse-Web
"""

import streamlit as st
import pandas as pd 
from PIL import Image
import base64
import seaborn as sns 
import numpy as np
from bs4 import BeautifulSoup
import requests
import json
import time
import matplotlib.pyplot as plt

# set page to expand to full width
st.set_page_config(layout="wide")

# title
st.title('Cryto Price Analyse Web')

# description
st.markdown("""
This app retrieves cryptocurrency prices for the top 100 crytocurrency from the **CoinMarketCap**!
""")

# About expander
expander_bar = st.expander("About")
expander_bar.markdown("""
* **Python libraries used:** base64, streamlit, numpy, pandas, BeautifulSoup, matplotlib, requests, json, time
* **Data source:** [CoinMarketCap](https://www.wikipedia.org/)
* **Credit:** One of the youtube videos by Youtuber Data Professor
""")

### Page layout ###
### Divide page to 3 columns (col1=sidebar,col2=tables,col3=graph)
col1 = st.sidebar
col2,col3 = st.columns((2,1))

# Header of sidebar
col1.header('Input options')

# select currency for price
currency_price_unit = col1.selectbox('Select currency for price',('USD','BTC','ETH'))

### web scraping of CoinMarketCap data ###
@st.cache
def load_data():
    # sends get request
    url = 'https://coinmarketcap.com'
    # cmc = requests.get('https://coinmarketcap.com')
    # makes the fetching faster
    session_object = requests.Session()
    page_obj = session_object.get(url)
    # gets whole html
    soup = BeautifulSoup(page_obj.content,'html.parser')
    # look for script tag
    data = soup.find('script',id='__NEXT_DATA__',type='application/json')
    coins = {}
    coin_data = json.loads(data.contents[0])
    # returns array of arrays
    listings = json.loads(coin_data['props']['initialState'])['cryptocurrency']['listingLatest']['data']
    # returns an array
    attributes = listings[0]["keysArr"]
    # gets index of id
    index_of_id = attributes.index("id")
     # gets index of slug
    index_of_slug = attributes.index("slug")

    # insert into coins
    for i in listings[1:]:
        coins[str(i[index_of_id])] = i[index_of_slug]

    # initialize variables of array type to store data of coins
    coin_name = []
    coin_symbol = []
    market_cap = []
    percent_change_1h = []
    percent_change_24h = []
    percent_change_7d = []
    price = []
    volume_24h = []

    # gets index of all info needed
    index_of_symbol = attributes.index("symbol")

    index_of_quote_currency_price = attributes.index(
        f"quote.{currency_price_unit}.price"
    )
    index_of_quote_currency_percent_change_1h = attributes.index(
        f"quote.{currency_price_unit}.percentChange1h"
    )
    index_of_quote_currency_percent_change_24h = attributes.index(
        f"quote.{currency_price_unit}.percentChange24h"
    )
    index_of_quote_currency_percent_change_7d = attributes.index(
        f"quote.{currency_price_unit}.percentChange7d"
    )
    index_of_quote_currency_market_cap = attributes.index(
        f"quote.{currency_price_unit}.marketCap"
    )
    index_of_quote_currency_volume_24h = attributes.index(
        f"quote.{currency_price_unit}.volume24h"
    )
    
    # add info to the arrays
    for i in listings[1:]:
        coin_name.append(i[index_of_slug])
        coin_symbol.append(i[index_of_symbol])
        price.append(i[index_of_quote_currency_price])
        percent_change_1h.append(i[index_of_quote_currency_percent_change_1h])
        percent_change_24h.append(i[index_of_quote_currency_percent_change_24h])
        percent_change_7d.append(i[index_of_quote_currency_percent_change_7d])
        market_cap.append(i[index_of_quote_currency_market_cap])
        volume_24h.append(i[index_of_quote_currency_volume_24h])

    # convert into dataframe
    df = pd.DataFrame(
    columns=[
        "coin_name",
        "coin_symbol",
        "market_cap",
        "percent_change_1h",
        "percent_change_24h",
        "percent_change_7d",
        "price",
        "volume_24h",
        ]
    )

    # assign to table columns
    df["coin_name"] = coin_name
    df["coin_symbol"] = coin_symbol
    df["price"] = price
    df["percent_change_1h"] = percent_change_1h
    df["percent_change_24h"] = percent_change_24h
    df["percent_change_7d"] = percent_change_7d
    df["market_cap"] = market_cap
    df["volume_24h"] = volume_24h
    # change index to start from 1
    df.index = np.arange(1, len(df) + 1)
    return df

# call the function
df = load_data()

# sort available coins
sorted_coin = sorted( df['coin_symbol'] )
# choices of coins, third argument is default value(which is all coins in this case)
selected_coin = col1.multiselect('Cryptocurrency', sorted_coin, sorted_coin)

# Filtering data according to selected coin symbol
df_selected_coin = df[(df["coin_symbol"].isin(selected_coin))] 

# inside sidebar, choose number of coins to display
num_coin = col1.slider("Display Top N Coins", 1, 100, 100)
# slice till selected number of coins
df_coins = df_selected_coin[:num_coin]

# inside sidebar - Percent change timeframe
# choices of timeframe
percent_timeframe = col1.selectbox('Percent change time frame',
                                    ['7d','24h', '1h'])
# assign values to choices
percent_dict = {"7d":'percentChange7d',"24h":'percentChange24h',"1h":'percentChange1h'}
# extract selected value
selected_percent_timeframe = percent_dict[percent_timeframe]

## Sidebar - Sorting values
# select if sort values or not for bar chart
sort_values = col1.selectbox('Sort values?', ['Yes', 'No'])

### tables ###
col2.subheader('Price Data of Selected Cryptocurrency')
col2.write('Data Dimension: ' + str(df_selected_coin.shape[0]) + ' rows and ' + str(df_selected_coin.shape[1]) + ' columns.')

# print dataframe of filtred coins data
col2.dataframe(df_coins)

# Download CSV data
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="crypto.csv">Download CSV File</a>'
    return href

# output hyperlink to download CSV data
col2.markdown(filedownload(df_selected_coin), unsafe_allow_html=True)

### Preparing data for Bar plot of % Price change ###

## table of price change ##
# title of table
col2.subheader('Table of % Price Change')

# table
df_change = pd.concat([df_coins.coin_symbol, df_coins.percent_change_1h, df_coins.percent_change_24h, df_coins.percent_change_7d], axis=1)
df_change = df_change.set_index('coin_symbol')
# check if positive change or not
# and assign boolean to positive_percent_change_** field
df_change['positive_percent_change_1h'] = df_change['percent_change_1h'] > 0
df_change['positive_percent_change_24h'] = df_change['percent_change_24h'] > 0
df_change['positive_percent_change_7d'] = df_change['percent_change_7d'] > 0
# output table
col2.dataframe(df_change)

## Conditional creation of Bar plot (time frame) ##
# title of bar plot
col3.subheader('Bar plot of % Price Change')

# if 7d timeframe is choosen
if percent_timeframe == '7d':
    if sort_values == 'Yes':
        df_change = df_change.sort_values(by=['percent_change_7d'])
    # title
    col3.write('*7 days period*')
    # figsize specifies width and height of a figure in unit inches
    plt.figure(figsize=(5,25))
    # Adjust the subplot layout parameters.
    plt.subplots_adjust(top = 1, bottom = 0)
    #kind: The kind of plot to produce
    # color: green if true, red if false based on if it is positive change
    df_change['percent_change_7d'].plot(kind='barh', color=df_change.positive_percent_change_7d.map({True: 'g', False: 'r'}))
    # plot the graph on column 3
    col3.pyplot(plt)
# if 24h timeframe is choosen
elif percent_timeframe == '24h':
    if sort_values == 'Yes':
        # sort data by percentage change value
        df_change = df_change.sort_values(by=['percent_change_24h'])
    col3.write('*24 hour period*')
    plt.figure(figsize=(5,25))
    plt.subplots_adjust(top = 1, bottom = 0)
    df_change['percent_change_24h'].plot(kind='barh', color=df_change.positive_percent_change_24h.map({True: 'g', False: 'r'}))
    col3.pyplot(plt)
    
# if 1h timeframe is choosen
else:
    if sort_values == 'Yes':
        df_change = df_change.sort_values(by=['percent_change_1h'])
    col3.write('*1 hour period*')
    plt.figure(figsize=(5,25))
    plt.subplots_adjust(top = 1, bottom = 0)
    df_change['percent_change_1h'].plot(kind='barh', color=df_change.positive_percent_change_1h.map({True: 'g', False: 'r'}))
    col3.pyplot(plt)
