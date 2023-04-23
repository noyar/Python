#!/usr/bin/env python
# coding: utf-8

# In[ ]:



import os
import time
import pyodbc
import pandas as pd
from zipfile import ZipFile
import schedule
from datetime import datetime
from selcon import SeleniumConnection
from selenium.webdriver.common.by import By


def job():
    site  = SeleniumConnection(False)
    site.get_url('https://www.cftc.gov/files/dea/history/deacot2023.zip')
    time.sleep(3)
    site.close()

    txt = r'C:\Users\rayon\Downloads\annual.txt'
    zip = r'C:\Users\rayon\Downloads\deacot2023.zip'

    with ZipFile(zip, 'r') as Object:
        Object.extractall(r'C:\Users\rayon\Downloads')  
    os.remove(zip)

    dff = pd.read_csv(txt)
    os.remove(txt)

    df = dff.copy()

    df = df[['Market and Exchange Names', 'As of Date in Form YYYY-MM-DD', 'Noncommercial Positions-Long (All)',
             'Noncommercial Positions-Short (All)', 'Change in Noncommercial-Long (All)', 'Change in Noncommercial-Short (All)']]
    df.columns = ['currency', 'date', 'long' ,'short', 'long_change', 'short_change' ]

    df['long_change'], df['short_change'] = df['long_change'].replace('.' ,0), df['short_change'].replace('.' ,0)

    for r in ['long_change', 'short_change']:
        df[r] = df[r].astype(int)

    df.date  =pd.to_datetime(df.date)   


    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=TRADE4SUCCESS;DATABASE=TRADE_DATA;')
    cursor = conn.cursor()
    cursor.execute("truncate table cot_data")

    for index, row in df.iterrows():
         cursor.execute("INSERT INTO cot_data (currency, date, long, short, long_change, short_change ) values(?,?,?,?,?,?)", 
                        row.currency, row.date, row.long, row.short, row.long_change, row.short_change )

    cursor.execute("delete from jobs where job_name = 'cot data'")
    cursor.execute("INSERT INTO jobs (job_name,refreshed_time, row_count) values(?,?,?)", 'cot data', datetime.now(), len(df))

    conn.commit()
    conn.close()

# schedule.every(25).minutes.do(job)
# schedule.every().hour.do(job)
# schedule.every().day.at("10:30").do(job)
# schedule.every().monday.do(job)
schedule.every().saturday.at("11:00").do(job)
# schedule.every().day.at("12:42", "Europe/Amsterdam").do(job)
# schedule.every().minute.at(":17").do(job)

while True:
    schedule.run_pending()
    #time.sleep(1)

