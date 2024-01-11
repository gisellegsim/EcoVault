"""
This is a prototype for other functions that can be included in the EcoVault API.
It mainly consists of various data visualisation methods to track carbon credit pricing. 
The data is sourced from World Bank and has been cleaned to better facilitate manipulation. 

The code creates a desktop app run on Streamlit (https://streamlit.io/)

To be used in conjunction with wallet.py in the XRPL-code folder.
"""

import streamlit as st
from PIL import Image
import pandas as pd
import altair as alt
import re
import plotly.express as px  # For choropleth map
import matplotlib.pyplot as plt # For stacked bar chart

path = "....../crediting_data.xlsx" # CHANGE TO USER DIRECTORY
xl_file = pd.ExcelFile(path)

st.set_page_config(layout="wide")

# Read data from each sheet
df_overall = pd.read_excel(xl_file, sheet_name='Crediting_overall')
df_detail = pd.read_excel(xl_file, sheet_name='Crediting_detail')
df_sector = pd.read_excel(xl_file, sheet_name='Crediting_sector')
df_issuances = pd.read_excel(xl_file, sheet_name='Crediting_issuances')

# Set the default page
default_page = 'Overall'

# Function to handle page selection
def select_page():
    imagepath = "....../EcoVault_logo.jpg" # CHANGE TO USER DIRECTORY
    image = Image.open(imagepath)
    st.image(image,width=200)
    
    page = st.sidebar.selectbox('Select page', ('Overall', 'Detail', 'Sector', 'Issuances'), index=0)
    return page

# Get the selected page
selected_page = select_page()

# Set query parameters for navigation
page_params = st.experimental_get_query_params()
page_params['page'] = selected_page
st.experimental_set_query_params(**page_params)

#---------------------------------#
# About
expander_bar = st.expander("About")
expander_bar.markdown("""

Data last updated 31 March 2023

*Note: Crediting mechanisms are considered to be under development if they have legislature in place
allowing for the future implementation of carbon crediting system but has currently not issued any credits
either due to missing components such as registries and protocols.*

* **Python libraries:** pandas, streamlit, PIL, altair, re, plotly, matplotlib
* **Data source:** [The World Bank](https://carbonpricingdashboard.worldbank.org/carbon_crediting).

""")

#---------------------------------#
# Functions used

# Currency converter (to USD)
def convert_to_usd(price_range):
    if 'US$' in price_range: # If the price range is already in USD, return the original value
        return float(re.search(r'US\$(\d+\.\d+)', price_range).group(1))
    elif 'CAN$' in price_range: # Convert CAN$ to USD using the exchange rate
        exchange_rate = 0.75 
        price_usd = float(re.search(r'US\$(\d+\.\d+)', price_range).group(1))
        return price_usd * exchange_rate
    elif 'A$' in price_range:
        exchange_rate = 0.67
        price_usd = float(re.search(r'US\$(\d+\.\d+)', price_range).group(1))
        return price_usd * exchange_rate
    elif 'CNY' in price_range:
        exchange_rate = 0.14
        price_usd = float(re.search(r'US\$(\d+\.\d+)', price_range).group(1))
        return price_usd * exchange_rate
    elif 'JPY' in price_range:
        exchange_rate = 0.0069 
        price_usd = float(re.search(r'US\$(\d+\.\d+)', price_range).group(1))
        return price_usd * exchange_rate
    elif 'KRW' in price_range:
        exchange_rate = 0.00076
        price_usd = float(re.search(r'US\$(\d+\.\d+)', price_range).group(1))
        return price_usd * exchange_rate
    elif 'EUR' in price_range:
        exchange_rate = 1.09
        price_usd = float(re.search(r'US\$(\d+\.\d+)', price_range).group(1))
        return price_usd * exchange_rate
    elif 'CHF' in price_range:
        exchange_rate = 1.18
        price_usd = float(re.search(r'US\$(\d+\.\d+)', price_range).group(1))
        return price_usd * exchange_rate

    # If the currency is not available, return NaN
    return None

df_detail['Price range USD'] = df_detail['Price range'].apply(convert_to_usd)
#print(df_detail[~df_detail['Price range USD'].isna()][['Price range', 'Price range USD']])


#---------------------------------#

# Display selected page content
if selected_page == 'Overall':
    st.title('Overall Carbon Crediting Data')

    # Bar chart of Jurisdiction Type
    st.write("""
        ## Count Carbon Credit Mechanism Jurisdiction Type
        """)
    bar_chart_data = df_overall['Type of jurisdiction covered'].value_counts().reset_index()
    bar_chart_data.columns = ['Jurisdiction Type', 'Count']
    bar_chart = alt.Chart(bar_chart_data).mark_bar().encode(
        x='Count:Q',
        y=alt.Y('Jurisdiction Type:N', sort='-x'),
        color='Jurisdiction Type:N'
    ).properties(
        width=500,
        height=300
    )
    st.altair_chart(bar_chart, use_container_width=True)

    # Map of implemented mechanisms
    st.write("""
        ## Map of Implemented Mechanisms
        """)
    fig = px.choropleth(df_overall,
                        locations='Jurisdiction covered',
                        locationmode='country names',
                        color='Status',
                        title='Mechanism Status by Country',
                        labels={'Status': 'Mechanism Status'}
                        )
    fig.update_layout(height=800,width=1000)
    st.plotly_chart(fig)

    # Line chart of implemented mechanisms over the years
    st.write("""
        ## Implemented Mechanisms Over The Years
        """)
    line_chart_data = df_overall[df_overall['Status'] == 'Implemented']['Year of implementation'].value_counts().reset_index()
    line_chart_data.columns = ['Year', 'Count']
    line_chart = alt.Chart(line_chart_data).mark_line().encode(
        x='Year:N',
        y='Count:Q',
        tooltip=['Year', 'Count']
    ).properties(
        width=600,
        height=300
    )
    st.altair_chart(line_chart, use_container_width=True)
    
    # Insert full table for reference 
    st.write("""
        ## Full Table
        """)
    st.dataframe(df_overall)
    
elif selected_page == 'Detail':
    st.title('Detailed Carbon Crediting Data')
    
    # Bar chart for credits issued by mechanism
    st.write("""
        ## Credits Issued by Mechanism
        """)
    bar_chart = alt.Chart(df_detail, height=400).mark_bar().encode(
        x=alt.X('Credits issued (MtCO2e):Q', title='Credits Issued (MtCO2e)'),
        y=alt.Y('Name of the mechanism:N', title='Mechanism'),
        color='Status of the mechanism:N',
        tooltip=['Name of the mechanism', 'Credits issued (MtCO2e)']
        )
    st.altair_chart(bar_chart, use_container_width=True)

    # Bar chart for credits retired by mechanism
    st.write("""
        ## Credits Retired or Cancelled by Mechanism
        """)
    bar_chart = alt.Chart(df_detail, height=400).mark_bar().encode(
        x=alt.X('Credits retired or cancelled (MtCO2e):Q', title='Credits retired or cancelled (MtCO2e)'),
        y=alt.Y('Name of the mechanism:N', title='Mechanism'),
        color='Status of the mechanism:N',
        tooltip=['Name of the mechanism', 'Credits retired or cancelled (MtCO2e)']
        )
    st.altair_chart(bar_chart, use_container_width=True)

    # Table showing Carbon Credit Mechanism and respective Price Range
    st.write("""
        ## Table of Carbon Credit Mechanism by Price in USD
        """)
    df_filtered = df_detail[df_detail['Price range USD'] != None]
    df_table = df_filtered[['Name of the mechanism', 'Price range USD']]
    st.dataframe(df_table)

    # Bar chart for Price Range in USD
    st.write("""
        ## Carbon Credit Mechanism by Price in USD
        """)
    chart = alt.Chart(df_detail).mark_bar().encode(
        x=alt.X('Price range USD:Q', title='Price Range (USD)'),
        y=alt.Y('Name of the mechanism:N', title='Mechanism'),
        tooltip=['Price range USD', 'Name of the mechanism']
    ).properties(
        title='Price Range of Carbon Credits in USD'
    )
    st.altair_chart(chart, use_container_width=True)

    # Line chart for trend of credits issued over years
    st.write("""
        ## Trend of Credits Issued Over The Years
        """)
    line_chart = alt.Chart(df_detail, height=400).mark_line().encode(
        x=alt.X('Year of implementation:N', title='Year of Implementation'),
        y=alt.Y('Credits issued (MtCO2e):Q', title='Credits Issued (MtCO2e)'),
        color='Status of the mechanism:N',
        tooltip=['Year of implementation:N', 'Credits issued (MtCO2e)']
    )
    st.altair_chart(line_chart, use_container_width=True)

    # Insert full table for reference 
    st.write("""
        ## Full Table
        """)
    st.dataframe(df_detail)
    
elif selected_page == 'Sector':
    st.title('Industry Sector')

    # Stacked bar chart -- Year as legend
    df = df_sector.set_index('Sectors')
    plt.figure(figsize=(12, 8))
    left = [0] * len(df)

    for year in df.columns[1:]:
        plt.barh(df.index, df[year], left=left, label=year)
        left = [sum(x) for x in zip(left, df[year])]

    plt.xlabel('Total Contribution')
    plt.ylabel('Sectors')
    plt.title('Stacked Horizontal Bar Chart of Contributions by Sector Over the Years')
    plt.legend(title='Year', bbox_to_anchor=(1, 1))
    st.pyplot(plt)

    # Stacked bar chart -- Sector as Legend
    df = df.T
    fig, ax = plt.subplots(figsize=(12, 8))
    df.plot(kind='barh', stacked=True, ax=ax)
    plt.xlabel('Year')
    plt.ylabel('Total Contribution')
    plt.title('Stacked Bar Chart of Contributions by Year and Sector')
    plt.legend(title='Sector', bbox_to_anchor=(1.05, 1), loc='upper left')
    st.pyplot(fig)

    # Insert full table for reference 
    st.write("""
        ## Full Table
        """)
    st.dataframe(df_sector)
    
elif selected_page == 'Issuances':
    st.title('Carbon Credit Issuances')

    # Insert full table for reference 
    st.write("""
        ## Full Table
        """)
    st.dataframe(df_issuances)
