import time
import requests

import csv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from helper_classes.SeleniumBase import SeleniumBase

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class Scraper(SeleniumBase):
    data_info = ['title', 'content']
    data = []

    def __init__(self):
        super().__init__()

    def parse(self):
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), chrome_options=self.options)
        driver.get('http://www.prienai.lt/go.php/lit/img/79')
        time.sleep(1)

        # get all links
        links = driver.find_elements(By.XPATH, '//div[@class="arch_news_title"]/a')

        for link in links:
            link_href = link.get_attribute('href')

            # if href is not clickable
            if 'javascript' in link_href or len(link_href) <= 0:
                continue

            # go to link
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            driver.get(link_href)
            time.sleep(3)

            # get title
            title = driver.find_element(By.XPATH, '//div[@class="middle-title"]').text

            # get text
            texts = []
            contents = driver.find_elements(By.XPATH, '//div[@class="article"]/*[not(contains(@class, "back_print")) and not(contains(@class, "middle-title"))]')
            for content in contents:
                # # clean
                # content_text = self.clean_html(content.text.strip())
                # if len(content_text) <= 0:
                #     continue
                #
                # texts.append(f'<h1>{content_text}</h1>')

                texts.append(content.get_attribute('innerHTML'))


            contents_a = driver.find_elements(By.XPATH, '//div[@class="article"]/*[not(contains(@class, "back_print")) and not(contains(@class, "middle-title"))]//a')
            for content_a in contents_a:
                contents_a_href = content_a.get_attribute('href')

            if title or texts:
                self.data.append({'title': title, 'content': texts})

            # close window link
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        print("DATA")
        print(self.data)
        with open('test4.csv', 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.data_info)
            writer.writeheader()
            writer.writerows(self.data)

    def clean_html(self, html_str):
        html_str = html_str.replace('&nbsp;', ' ')
        html_str = html_str.replace('&', '&amp;')
        return html_str

    def handle_pdf_parse(self):
        pass


test = Scraper()
test.parse()
