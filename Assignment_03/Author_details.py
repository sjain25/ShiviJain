'''
import re
import itertools
import pandas as pd

def cleaned_reviews(value):
    return(''.join(list(itertools.chain.from_iterable([re.sub(r'[^\w\s]',' ',x.replace(':',' ').lower().strip()).split('|')for x in value.split('.')]))).replace('\n',''))
'''

from selenium import webdriver
from selenium.webdriver.support.select import Select

import time
import random
import pandas as pd
import json
import csv
import glob

normal_delay = random.normalvariate(3, 0.5)
normal_delay_2 = random.normalvariate(5, 0.5)
normal_delay_3 = random.normalvariate(7, 0.5)

driver = webdriver.Chrome(executable_path='chromedriver.exe')
driver.get('https://www.amazon.com/RockBirds-Flashlights-Bright-Aluminum-Flashlight/product-reviews/B00X61AJYM')
time.sleep(normal_delay_2)

sort = driver.find_element_by_css_selector('#sort-order-dropdown')
most_recent = Select(sort)
most_recent.select_by_visible_text('Most recent')
time.sleep(normal_delay)

filter = driver.find_element_by_css_selector('#reviewer-type-dropdown')
verified_purchase = Select(filter)
verified_purchase.select_by_visible_text('Verified purchase only')
time.sleep(normal_delay)


def extract_reviews(driver):
    author_links = driver.find_elements_by_css_selector(".a-size-base.a-color-secondary.review-byline")
    authors = [author_link.text.strip('By') for author_link in author_links]
    del authors[0:2]

    helpful_reviews = []
    frequent_reviewer = []

    for author in authors:
        authorlink = driver.find_element_by_link_text(author)
        authorlink.click()
        time.sleep(normal_delay_3)
        helpful_reviews.append(driver.find_element_by_css_selector("#profile_v5 > div > div > div.a-section.activity-area-container > div.deck-container.main > div.desktop.padded.card.dashboard-desktop-card > div:nth-child(2) > div > div:nth-child(1) > a > div > div.dashboard-desktop-stat-value > span").text)
        frequent_reviewer.append(driver.find_element_by_css_selector("#profile_v5 > div > div > div.a-section.activity-area-container > div.deck-container.main > div.desktop.padded.card.dashboard-desktop-card > div:nth-child(2) > div > div:nth-child(2) > a > div > div.dashboard-desktop-stat-value > span").text)
        driver.back()
        time.sleep(normal_delay_3)

    return pd.DataFrame({'Author': authors, 'Frequency': frequent_reviewer, 'Helpful_reviews': helpful_reviews})


def to_csv():
    path = r'C:/Users/Shivi/PycharmProjects/ShiviJain/Assignment_03' # use your path
    allFiles = glob.glob(path + "/*.csv")
    frame = pd.DataFrame()
    list_ = []
    for file_ in allFiles:
        df = pd.read_csv(file_,index_col=None, header=0)
        list_.append(df)
    return pd.concat(list_)


df = extract_reviews(driver)
df.to_csv('0 test.csv')
for i in range(1,10):
    current_page = driver.find_element_by_css_selector(".a-selected.page-button")
    print("The reviews on page {} successfully extracted".format(current_page.text))

    next_page = driver.find_element_by_class_name("a-last")

    try:
        is_last_page = driver.find_element_by_css_selector(".a-disabled.a-last")
    except:
        is_last_page = None

    if is_last_page is not None:
        print("All the reviews extracted successfully ")
        break
    time.sleep(normal_delay)
    next_page.click()
    time.sleep(normal_delay_2)
    page_reviews = extract_reviews(driver)
    df = df.append(page_reviews)
    page_reviews.to_csv(str(i) + ' test.csv')
    time.sleep(normal_delay)

time.sleep(normal_delay_2)
driver.close()

data_frame = to_csv()

data = pd.DataFrame.from_dict(data_frame, orient='columns', dtype=None)
data.to_csv('author_details.csv')

data = df.reset_index()
data.to_json('author_details.json')