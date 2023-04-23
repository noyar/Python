#!/usr/bin/env python
# coding: utf-8

# In[1]:


#forex news

import os
import time
import pyodbc
import numpy as np
import pandas as pd
from zipfile import ZipFile
import schedule
from datetime import datetime
from selcon import SeleniumConnection
from selenium.webdriver.common.by import By

def job():
    site  = SeleniumConnection(False)
    site.get_url('https://www.forexfactory.com/calendar')
#     time.sleep(4)

    rows = site.find_element(By.CLASS_NAME, 'calendar__table  ').find_elements(By.TAG_NAME, 'tr')[1:]
    rowCon = []
    for row in rows:
        if row.text != '':
            date = row.find_element(By.CLASS_NAME, 'date').text
            time = row.find_element(By.CSS_SELECTOR,'.calendar__cell.calendar__time.time').text
            currency = row.find_element(By.CSS_SELECTOR,'.calendar__cell.calendar__currency.currency').text 
            event= row.find_element(By.CSS_SELECTOR,'.calendar__cell.calendar__event.event').text 
            actual = row.find_element(By.CSS_SELECTOR,'.calendar__cell.calendar__actual.actual').text
            forecast = row.find_element(By.CSS_SELECTOR,'.calendar__cell.calendar__forecast.forecast').text
            previous = row.find_element(By.CSS_SELECTOR,'.calendar__cell.calendar__previous.previous').text
            rowCon.append({'date_':date, 'time':time, 'currency': currency, 'event':event, 'actual':actual, 'forecast':forecast, 'previous':previous})
#     time.sleep(4)
    site.close()
    dff = pd.DataFrame(rowCon)

    df = dff.copy()

    df['date'] = df.date_.replace('', np.nan).ffill().str.split('\n', expand=True)[1]
    df['day'] = df.date_.replace('', np.nan).ffill().str.split('\n', expand=True)[0]
    df['date'] = pd.to_datetime('2023'+'-'+df.date.str[:3]+'-'+df.date.str[4:])

    df.time = df.time.replace('Tentative', '12:00 am').replace('All Day', '12:00 am').replace('', np.nan).ffill()
    in_time = [datetime.strptime(i[:-2]+' '+i[-2:],"%I:%M %p") for i in df.time]
    df.time = [datetime.strftime(i, "%H:%M") for i in in_time]

    df = df[['date', 'day', 'time', 'currency', 'event', 'actual', 'forecast', 'previous']]


    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=TRADE4SUCCESS;DATABASE=TRADE_DATA;')
    cursor = conn.cursor()
    cursor.execute("truncate table calendar_news")

    for index, row in df.iterrows():
         cursor.execute("INSERT INTO calendar_news (date, day, time, currency ,event, actual ,forecast ,previous) values(?,?,?,?,?,?,?,?)", 
                                                  row.date, row.day ,row.time, row.currency,row.event, row.actual, row.forecast, row.previous)

    cursor.execute("delete from jobs where job_name = 'calendar news'")
    cursor.execute("INSERT INTO jobs (job_name,refreshed_time, row_count) values(?,?,?)", 'calendar news', datetime.now(), len(df))

    conn.commit()
    conn.close()

#schedule.every(25).minutes.do(job)
# schedule.every().hour.do(job)
# schedule.every().day.at("10:30").do(job)
schedule.every().sunday.at("13:35").do(job)
# schedule.every().wednesday.at("13:15").do(job)
# schedule.every().day.at("12:42", "Europe/Amsterdam").do(job)
# schedule.every().minute.at(":17").do(job)

while True:
    schedule.run_pending()
    #time.sleep(1)

