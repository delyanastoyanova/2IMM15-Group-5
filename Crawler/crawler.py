from selenium import webdriver
import time
import urllib.request
import random
import csv
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from socket import timeout
from urllib.error import HTTPError
from urllib.error import URLError

image_number = 0  # counter for creating unique file names
hashed_src = []  # list saving unique hash values from src
## settings of the webdriver
pause_time = 15
last_height = 0
 #open file or create file in the same directory as this python file in order to save urls
f = csv.writer(open('data.csv', 'w',newline=''))
f.writerow(['Image number', 'url'])
try:
    chrome_path = r"chromedriver.exe"
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(chrome_path, options=chrome_options)
    driver.get("https://www.instagram.com/8fact/")
    while True:
        try:
            #scroll to the end of the page
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            articles = driver.find_elements_by_xpath('//*[@class="v1Nh3 kIKUG  _bz0w"]//child::img')
            number_art = len(articles)
            for i in range(number_art):
                print(image_number)
                #append the hash value of the resul
                hashed_src.append(hash(articles[i].get_attribute('src')))
                if len(hashed_src) == len(set(hashed_src)):
                    #hashed_src has only unique elements,set()function returns only unique elements
                    f.writerow([image_number,articles[i].get_attribute('src')])
                    print('unique element saved')
                    image_number += 1
                    if image_number % 200 == 0:
                        #delete old hashed values in order to maintain smaller data structure
                        hashed_src = hashed_src[100:]
                else:
                    print('skip')
                    #unique element is not found, hence update the data structure with only unique elements
                    hashed_src = list(set(hashed_src))
        except StaleElementReferenceException as Exception:
            print('StaleElementReferenceException')
        time.sleep(pause_time)
except KeyboardInterrupt:
    print('Interrupted')
    print('Process time')
    print(time.process_time())
