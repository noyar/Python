import time
import pyodbc
import pandas as pd
import schedule
from datetime import datetime
from selcon import SeleniumConnection
from selenium.webdriver.common.by import By


def job():
    site = SeleniumConnection()
    site.get_url('https://www.myfxbook.com/community/outlook')

    time.sleep(4)
    site.find_element(By.CSS_SELECTOR, '.bold.color-white').click()

    rows = site.find_element(By.ID, 'outlookSymbolsTableContent').find_elements(By.CLASS_NAME, 'outlook-symbol-row')
    row=[]
    for i in range(len(rows)):
        try:
            symbol = rows[i].find_element(By.TAG_NAME, 'a').text
            short  = int(rows[i].find_element(By.CSS_SELECTOR, '.progress-bar.progress-bar-danger').get_attribute('style')[6:-2])/100
            long   = int(rows[i].find_element(By.CSS_SELECTOR, '.progress-bar.progress-bar-success').get_attribute('style')[6:-2])/100
        except:
            pass
        row.append({'symbol':symbol, 'long':long, 'short': short})

    df = pd.DataFrame(row)
    site.close()


    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=TRADE4SUCCESS;DATABASE=TRADE_DATA;')
    cursor = conn.cursor()
    cursor.execute("truncate table retail_sent")
    
    for index, row in df.iterrows():
         cursor.execute("INSERT INTO retail_sent (symbol,long, short) values(?,?,?)", row.symbol, row.long, row.short)

    cursor.execute("delete from jobs where job_name = 'retail sentiment'")
    cursor.execute("INSERT INTO jobs (job_name,refreshed_time, row_count) values(?,?,?)", 'retail sentiment', datetime.now(), len(df))

    conn.commit()
    conn.close()

    print("Job Completed")



schedule.every(30).minutes.do(job)

while True:
    schedule.run_pending()
    #time.sleep(1)

