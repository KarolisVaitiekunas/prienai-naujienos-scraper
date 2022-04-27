import mimetypes
import time
import uuid
import csv
import cgi
import pathlib

import re

import requests

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
    data_info = ['title', 'texts', 'files']
    data = []
    title = None
    texts = None
    files = []

    IMAGE = 'IMAGE'
    OTHER = 'OTHER'
    image_types = ["jpg", 'png', 'jpeg', ".jpg", '.png', '.jpeg']

    def __init__(self):
        super().__init__()

    def parse(self):
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), chrome_options=self.options)
        driver.get('http://www.prienai.lt/go.php/lit/img/57')
        time.sleep(1)

        # get all links
        links = driver.find_elements(By.XPATH, '//div[@class="arch_news_title"]/a')

        for index, link in enumerate(links):
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
            self.title = driver.find_element(By.XPATH, '//div[@class="middle-title"]').text

            # get text
            contents = driver.find_elements(By.XPATH,
                                            '//div[@class="article"]/*[not(contains(@class, "back_print")) and not(contains(@class, "middle-title"))]')

            temp_text = ''
            for content in contents:
                temp_text = temp_text + content.get_attribute("innerHTML")

            p = re.compile('<(?!\/a>|a|\/img>|img| )[^>]+>')
            temp_text = p.sub('', temp_text)
            temp_text = self.clean_html(temp_text)

            # select all non images content
            non_image_contents_a = driver.find_elements(By.XPATH,
                                              '//div[@class="article"]/*[not(contains(@class, "back_print")) and not(contains(@class, "middle-title"))]//a[not(img)]')

            for non_image_content_a in non_image_contents_a:
                non_image_content_href = non_image_content_a.get_attribute('href')
                [downloadable, location, file_type] = self.handleFileDownload(non_image_content_href)

                if downloadable:
                    # if file is not an image
                    if file_type == self.OTHER:
                        # replace old a tag with an updated one with href to storage
                        self.texts = temp_text.replace(non_image_content_a.get_attribute('outerHTML'),
                                                       f'<a href={location}>{non_image_content_a.text}</a>')
                    else:
                        raise ValueError(f'non_image_contents file_type must be "OTHER" but got {non_image_content_href} ')
                else:
                    print("FILE IS NOT DOWNLOADABLE")


            # select all images content
            image_contents_img = driver.find_elements(By.XPATH,
                                              '//div[@class="article"]/*[not(contains(@class, "back_print")) and not(contains(@class, "middle-title"))]//img')


            for image_content_img in image_contents_img:
                image_content_img_src = image_content_img.get_attribute('src')
                [downloadable, location, file_type] = self.handleFileDownload(image_content_img_src)

                if downloadable:
                    # if file is not an image
                    if file_type == self.IMAGE:


                        # get element parent
                        image_content_img_parent = image_content_img.find_element(By.XPATH,
                                                                                  'parent::*')
                        # replace old a tag with an updated one with href to storage
                        if "</a>" in image_content_img_parent.get_attribute('outerHTML'):
                            temp_text = temp_text.replace(image_content_img_parent.get_attribute('outerHTML'),
                                                           f'<img src={location}/>')
                        else:
                            temp_text = temp_text.replace(image_content_img.get_attribute('outerHTML'),
                                                       f'<img src={location}/>')

                        self.texts = temp_text
                    else:
                        raise ValueError(f'image_contents_img file_type must be "IMAGE", but got {image_content_img_src} ')
                else:
                    print("FILE IS NOT DOWNLOADABLE")





            # contents_a = driver.find_elements(By.XPATH,
            #                                   '//div[@class="article"]/*[not(contains(@class, "back_print")) and not(contains(@class, "middle-title"))]//a')
            # for content_a in contents_a:
            #     contents_a_href = content_a.get_attribute('href')
            #     [downloadable, location, file_type] = self.handleFileDownload(contents_a_href)
            #
            #     if downloadable:
            #         print("FILE IS DOWNLOADABLE")
            #
            #         # if file is an image
            #         if file_type == self.IMAGE:
            #             # replace old img tag with an updated one with src to storage
            #             self.texts = temp_text.replace(content_a.get_attribute('innerHTML'),
            #                                            f'<img src={location}/>')
            #
            #         # if file is not an image
            #         elif file_type == self.OTHER:
            #             self.texts = temp_text.replace(content_a.get_attribute('innerHTML'),
            #                                            f'<a href={location}>{content_a.text}</a>')
            #         else:
            #             raise ValueError('file_type cannot be anything else besides "OTHER" AND "IMAGE" ')
            #     else:
            #         print("FILE IS NOT DOWNLOADABLE")


            self.data.append({'title': self.title, 'texts': self.texts, "files": self.files})


            # close window link
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            # if index == 1:
            #     break

        with open('test.csv', 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.data_info)
            writer.writeheader()
            writer.writerows(self.data)

    def clean_html(self, html_str):
        html_str = html_str.replace('&nbsp;', ' ')
        html_str = html_str.replace('&', '&amp;')
        return html_str

    def handleFileDownload(self, href):
        downloadable = False
        location = None
        file_type = self.OTHER

        # determine url schema
        if "http" in href:
            file_url = href
        elif "www." in href:
            file_url = 'http://' + href
        else:
            file_url = 'http://www.prienai.lt' + href

        # send request
        try:
            file = requests.get(file_url, allow_redirects=True, verify=False, timeout=5)
        except:
            return [downloadable, location, file_type]

        # try to guess file extension, generate file url
        content_type = file.headers['content-type']
        extension = mimetypes.guess_extension(content_type)

        if extension:
            file_name_generated_url = uuid.uuid4().hex + extension

        else:
            if file.headers.get('Content-Disposition'):
                params = cgi.parse_header(file.headers.get('Content-Disposition'))
                file_name_generated_url = uuid.uuid4().hex + str(pathlib.Path(params[1]['filename']).suffix)

                downloadable = True
                return [downloadable, location,
                        self.handle_check_file_type(str(pathlib.Path(params[1]['filename']).suffix))]
            else:
                downloadable = False
                return [downloadable, location, file_type]

        # download
        location = self.temp_storage + file_name_generated_url
        open(location, 'wb').write(file.content)
        self.files.append(location)

        downloadable = True
        return [downloadable, location, self.handle_check_file_type(extension)]

    def handle_pdf_parse(self):
        pass

    def handle_check_file_type(self, file_extension):
        print("CHECKING " + file_extension)
        if file_extension in self.image_types:
            print("FILE_EXTENSION IS " + self.IMAGE)
            return self.IMAGE
        else:
            print("FILE_EXTENSION IS " + self.OTHER)
            return self.OTHER


test = Scraper()
test.parse()
