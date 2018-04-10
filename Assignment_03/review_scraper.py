from selenium import webdriver
from selenium.webdriver.support.select import Select

import time
import random
import pandas as pd
import json
import csv

normal_delay = random.normalvariate(3, 0.5)
normal_delay_2 = random.normalvariate(5, 0.5)

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

titles = []
dates = []
ratings = []
reviews = []
comments = []


def extract_reviews(driver):
    title_links = driver.find_elements_by_css_selector(".a-size-base.a-link-normal.review-title.a-color-base.a-text-bold")
    date_links = driver.find_elements_by_css_selector(".a-size-base.a-color-secondary.review-date")
    review_links = driver.find_elements_by_css_selector(".a-size-base.review-text")
    rating_links = driver.find_elements_by_xpath(".//a[contains(@title,  'out of 5 stars')]")
    comment_links = driver.find_elements_by_xpath("//*[contains(text(), 'Was this review helpful to you?')]")

    titles = [title_link.text for title_link in title_links]
    dates = [date_link.text.strip('on').replace((','),'') for date_link in date_links]
    ratings = [rating_link.get_attribute("title") for rating_link in rating_links]
    reviews = [review_link.text for review_link in review_links]
    comments = [comment_link.text for comment_link in comment_links]

    del dates[0:2]

    return pd.DataFrame({'Title': titles, 'Date': dates, 'Ratings': ratings, 'Reviews': reviews, 'Comments': comments})


df = extract_reviews(driver)
while True:
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
    time.sleep(normal_delay)


time.sleep(normal_delay_2)
driver.close()

data = pd.DataFrame.from_dict(df, orient='columns', dtype=None)
data.to_csv('review_scraper.csv')

data = df.reset_index()
data.to_json('review_scraper.json')

