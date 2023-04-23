
import pyodbc
from selenium import webdriver
from selenium.webdriver.common.by import By

class SeleniumConnection:
    def __init__(self, headless=True):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
            options.add_experimental_option("detach", True)
            options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(options=options)
        
    def get_url(self,url):
        self.driver.get(url)
       

    def find_element(self, by, selector):
        return self.driver.find_element(by, selector)

    def find_elements(self, by, selector):
        return self.driver.find_elements(by, selector)

    def close(self):
        self.driver.close()

