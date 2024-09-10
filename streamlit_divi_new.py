import streamlit as st
import pandas as pd
import altair as alt
import sqlite3
import numpy as np
import re
import pandas as pd
from datetime import datetime
import yfinance as yf
import plotly.express as px
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import os

####

from sqlalchemy import create_engine

# Získanie environmentálnej premenné
DATABASE_URL = os.getenv("DATABASE_URL")

# Vytvorenie pripojenia k PostgreSQL databáze
engine = create_engine(DATABASE_URL)

# Pripojenie k PostgreSQL
#database_url = 'postgresql://lubza_ib:Jfd3cNeULsuufDEqSQ1yGbWELzgCCNCb@dpg-crg1meg8fa8c73ak3960-a.frankfurt-postgres.render.com:5432/ib_db'

#postgres_engine = create_engine(database_url)

# Načítanie dát z tabuľky 'dividends' do pandas DataFrame
try:
    query = "SELECT * FROM dividends"
    #df = pd.read_sql(query, postgres_engine)
    df = pd.read_sql(query, engine)
    print("Data successfully loaded into DataFrame.")
except Exception as e:
    print("Error loading data:", e)

# Zobrazenie prvých niekoľkých riadkov DataFrame
#print(df.head())

####


# Pripojenie k SQLite databáze
#conn = sqlite3.connect(r'C:\Users\Lubos\Dropbox\xFlexQueryTest\ib_flex_query_divi.db')

# Načítanie údajov z tabuľky 'dividends' do DataFrame
#df = pd.read_sql_query("SELECT * FROM dividends", conn)

# Zatvorenie pripojenia k databáze
#conn.close()

# Get the current date
current_date = datetime.now()

st.set_page_config(page_title="Dividends overview",
                    page_icon=":money_with_wings:",
                    layout="wide"
)

# Create pivot table
overview = pd.pivot_table(df, values='Amount', index='Year', columns='Qtr', aggfunc='sum', margins=True, margins_name='Total', fill_value=0)

# Streamlit app
#st.title('Dividends overview')

# Split layout into two columns
col1, col2 = st.columns(2)

with col1:

    # Display overview table
    st.write('### Overview Table')
    st.dataframe(overview)

    # Create pivot table
    ccy_overview = pd.pivot_table(df, values='Amount', index='Currency', columns='Year', aggfunc='sum', margins=True, margins_name='Total', fill_value=0)

    # Display overview table
    st.write('### Overview by currency')
    st.dataframe(ccy_overview)

    # Filter for top 5 tickers in 2024
    df_2024 = df[df['Year'] == 2024]
    top_5_tickers = df_2024.groupby('Ticker')['Amount'].sum().nlargest(5).reset_index().set_index('Ticker')

    # Display overview table
    st.write('### Top 5 contributors this year')
    st.dataframe(top_5_tickers)

    # Streamlit app to display the Yearly Totals with Change
    st.write('### Dividend overview of selected ticker')

    sorted_tickers = sorted(df['Ticker'].unique())
    # Ticker filter
    ticker_filter = st.selectbox('Select Ticker', options=sorted_tickers, index=0)

    # Filter DataFrame based on selected ticker
    filtered_df_ticker = df[df['Ticker'] == ticker_filter]

    # Create pivot table for yearly total amounts for the selected ticker
    yearly_totals = filtered_df_ticker.groupby('Year')['Amount'].sum().reset_index()
    yearly_totals.columns = ['Year', 'Total']

    # Convert 'Year' to string from integer to eliminate commas separator of tousands
    yearly_totals['Year'] = yearly_totals['Year'].astype(str)

    # Calculate change from the previous year
    yearly_totals['Change'] = yearly_totals['Total'].diff()

    # Replace NaN values in the 'Change' column with 0 for the first year
    yearly_totals['Change'] = yearly_totals['Change'].fillna(0)

    # Set 'Year' as the index
    yearly_totals.set_index('Year', inplace=True)

    # Sort the index (Year) in descending order
    yearly_totals = yearly_totals.sort_index(ascending=False)

    # Calculate the total sum of the 'Total' column
    total_sum = yearly_totals['Total'].sum()

    # Append the total sum as a new row
    total_row = pd.DataFrame({'Total': total_sum, 'Change': 0}, index=['Total'])
    yearly_totals = pd.concat([yearly_totals, total_row])

    st.dataframe(yearly_totals)

with col2:

    # Year filter
    year_filter = st.selectbox('Select Year', options=df['Year'].unique(), index=0)

    # Filter DataFrame based on selected year
    filtered_df = df[df['Year'] == year_filter]

    # Create the Altair chart
    chart = alt.Chart(filtered_df).mark_bar().encode(
        x='Qtr',
        y='Amount',
        color='Qtr'
    ).properties(
        width=600,
        height=400
    )

    # Display the chart in Streamlit
    st.write()
    st.altair_chart(chart)

    # Sector filter
    sector_filter = st.selectbox('Select Sector', options=df['Sector'].unique(), index=0)

    # Filter DataFrame based on selected sector
    filtered_df_sector = df[df['Sector'] == sector_filter]

    # Create the Altair chart
    chart_sector = alt.Chart(filtered_df_sector).mark_bar().encode(
        x='Year:O',
        y='Amount',
        color='Year:N'
    ).properties(
        width=600,
        height=400
    )

    # Display the chart in Streamlit
    st.write()
    st.altair_chart(chart_sector)
    