import os
from pymongo import MongoClient
import json

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def save_product_to_db(dr, link):
    dr.get(link)
    WebDriverWait(dr, 30).until(EC.presence_of_element_located((By.XPATH, '//h1')))
    url = dr.current_url
    name = dr.find_element(By.XPATH, "//h1").text
    price = dr.find_element(By.XPATH, "//span[@class='price__main-value']").text
    properties = dr.find_elements(By.XPATH, "//div[@class='item-with-dots']")
    properties_dict = {
        pr.find_element(By.XPATH, ".//dt").text:
            pr.find_element(By.XPATH, ".//dd").text
        for pr in properties
    }
    product = {
        'name': name,
        'url': url,
        'price': price,
        'properties': properties_dict,
    }
    client = MongoClient('localhost', 27017)
    db = client['eldorado']
    collection = db['in_trend_goods']
    collection.insert_one(product)


install_dir = "/snap/firefox/current/usr/lib/firefox"
driver_loc = os.path.join(install_dir, "geckodriver")
binary_loc = os.path.join(install_dir, "firefox")

service = Service(driver_loc)
opts = webdriver.FirefoxOptions()
opts.binary_location = binary_loc

driver = webdriver.Firefox(service=service, options=opts)
driver.implicitly_wait(10)
driver.get('https://www.mvideo.ru/')
driver.maximize_window()
body_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script(f"window.scrollTo(0, {body_height});")
    body_height = driver.execute_script("return document.body.scrollHeight")
    try:
        in_trend_button = driver.find_elements(By.XPATH, "//button[contains(@class, 'tab-button')]")[-1]
        in_trend_button.click()
        break
    except Exception as e:
        print(e)
        continue
product_cards_group = driver.find_elements(By.XPATH, '//mvid-product-cards-group')[1]
goods = product_cards_group.find_elements(By.XPATH, './/img/..')
good_urls = [g.get_property('href') for g in goods]
for url in good_urls:
    save_product_to_db(driver, url)
driver.quit()
