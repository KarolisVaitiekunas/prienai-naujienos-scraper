import mimetypes
import time
import uuid
import csv
import cgi
import pathlib

import re

import requests

from selenium.webdriver.common.by import By

from helper_classes.SeleniumBase import SeleniumBase

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class Scraper(SeleniumBase):
    data_info = ['title', 'content', "post_date", 'files']
    data = []
    title = None
    texts = None
    files = []

    IMAGE = 'IMAGE'
    OTHER = 'OTHER'
    image_types = ["jpg", 'png', 'jpeg', 'gif', ".jpg", '.png', '.jpeg', '.gif']




    def __init__(self):
        super().__init__()
        self.driver.get('http://www.prienai.lt/go.php/lit/Sausis/18')



    def start_pagination_requests(self):
        availible_pagination_months_links = []
        availible_pagination_months = self.driver.find_elements(By.XPATH, "//table[@class='m_news_archive_c_table']/tbody/tr/td/a")
        for avalible_pagination_month in availible_pagination_months:
            availible_pagination_months_links.append(avalible_pagination_month.get_attribute('href'))

        for link in availible_pagination_months_links:
            self.driver.get(link)
            time.sleep(1)
            self.parse()

        try:
            next_arrow = self.driver.find_element(By.XPATH, '//*[@id="page"]/div[3]/div[2]/div[2]/div[2]/div[1]/table/tbody/tr[1]/td/b/a[2]')
            print("ARROW:")
            print(next_arrow.get_attribute("outerHTML"))
            next_arrow.click()
            time.sleep(10)
            self.start_pagination_requests()
        except Exception as e:
            print("MAY ERROR")
            print(e)
            print("NO MORE ARROWS >:)")



    def parse(self):
        # get all links
        links = self.driver.find_elements(By.XPATH, '//div[@class="arch_news_title"]/a')

        for index, link in enumerate(links):
            link_href = link.get_attribute('href')

            # if href is not clickable
            if 'javascript' in link_href or len(link_href) <= 0:
                continue

            # go to link
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[1])
            self.driver.get(link_href)
            time.sleep(5)

            self.files = []

            # get title
            self.title = self.driver.find_element(By.XPATH, '//div[@class="middle-title"]').text

            # get text
            contents = self.driver.find_elements(By.XPATH,
                                            '//div[@class="article"]/*[not(contains(@class, "back_print")) and not(contains(@class, "middle-title"))]')

            temp_text = ''
            for content in contents:
                temp_text = temp_text + content.get_attribute("outerHTML")

            try:
                table_exists = self.driver.find_element(By.XPATH, '//div[@class="article"]/table/tbody')
            except:
                table_exists = None

            if table_exists:
                temp_text = self.handle_regex_element_clean('<(?!\/a>|a|\/img>|img|\/table>|table|\/tbody>|tbody|\/td>|td|\/tr>|tr)[^>]+>', temp_text)
            else:
                temp_text = self.handle_regex_element_clean('<(?!\/a>|a|\/img>|img| )[^>]+>', temp_text)


            # p = re.compile('<(?!\/a>|a|\/img>|img| )[^>]+>')
            # temp_text = p.sub('', temp_text)
            # temp_text = self.clean_html(temp_text)

            # select all non images content
            non_image_contents_a = self.driver.find_elements(By.XPATH,
                                                        '//div[@class="article"]/*[not(contains(@class, "back_print")) and not(contains(@class, "middle-title"))]//a[not(img)][normalize-space()]')

            for non_image_content_a in non_image_contents_a:
                non_image_content_href = non_image_content_a.get_attribute('href')
                print("SENDING 1")
                print(non_image_content_href)
                if non_image_content_href:
                    [downloadable, location, file_type] = self.handleFileDownload(non_image_content_href)
                    if downloadable:
                        # if file is not an image
                        if file_type == self.OTHER:
                            # replace old a tag with an updated one with href to storage
                            non_image_content_a_html = self.handle_regex_element_clean(
                                '<(?!\/a>|a|\/img>|img| )[^>]+>', non_image_content_a.get_attribute('outerHTML'))

                            temp_text = temp_text.replace(non_image_content_a_html,
                                                           f'<a href={location}>{non_image_content_a.text}</a>')

                        else:
                            non_image_content_a_html = self.handle_regex_element_clean(
                                '<(?!\/a>|a|\/img>|img| )[^>]+>', non_image_content_a.get_attribute('outerHTML'))

                            temp_text = temp_text.replace(non_image_content_a_html,
                                                           f'<a href={location} target="_blank">{non_image_content_a.text}</a>')
                            # raise ValueError(
                            #     f'non_image_contents file_type must be "OTHER" but got {non_image_content_href} ')
                    else:
                        pass
                        # print("FILE IS NOT DOWNLOADABLE")

            # select all images content
            image_contents_img = self.driver.find_elements(By.XPATH,
                                                      '//div[@class="article"]/*[not(contains(@class, "back_print")) and not(contains(@class, "middle-title"))]//img')

            for image_content_img in image_contents_img:
                image_content_img_src = image_content_img.get_attribute('src')
                print("SENDING 2")
                print(image_content_img_src)

                if image_content_img_src:
                    [downloadable, location, file_type] = self.handleFileDownload(image_content_img_src)

                    if downloadable:
                        # if file is not an image
                        if file_type == self.IMAGE:

                            # get element parent
                            image_content_img_parent = image_content_img.find_element(By.XPATH, 'parent::*')
                            image_content_img_parent_html = self.handle_regex_element_clean(
                                '<(?!\/a>|a|\/img>|img| )[^>]+>', image_content_img_parent.get_attribute('outerHTML'))

                            # replace old a tag with an updated one with href to storage
                            if "</a>" in image_content_img_parent_html:

                                temp_text = temp_text.replace(image_content_img_parent_html,
                                                              f'<img src={location}/>')
                            else:

                                image_content_img_html = self.handle_regex_element_clean(
                                    '<(?!\/a>|a|\/img>|img| )[^>]+>', image_content_img.get_attribute('outerHTML'))

                                temp_text = temp_text.replace(image_content_img_html,
                                                              f'<img src={location}/>')

                        else:
                            raise ValueError(
                                f'image_contents_img file_type must be "IMAGE", but got {image_content_img_src} ')
                    else:
                        pass
                        # print("FILE IS NOT DOWNLOADABLE")

            self.texts = temp_text
            self.data.append({'title': self.title, 'content': self.texts, "files": self.files})

            # close window link
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            # if index == 8:
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

        print("HREF IS")
        print(href)

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

        if 'text/html' in content_type:
            downloadable = False
            return [downloadable, location, file_type]

        if extension:
            file_name_generated_url = uuid.uuid4().hex + extension

        else:
            if file.headers.get('Content-Disposition'):
                params = cgi.parse_header(file.headers.get('Content-Disposition'))
                file_name_generated_url = uuid.uuid4().hex + str(pathlib.Path(params[1]['filename']).suffix)
                print("YO BRO")
                print(file.headers)
                print(file_name_generated_url)

                # download
                real_location = self.temp_storage + file_name_generated_url
                location = "storage/" + file_name_generated_url
                open(real_location, 'wb').write(file.content)
                self.files.append(location)

                downloadable = True
                return [downloadable, location,
                        self.handle_check_file_type(str(pathlib.Path(params[1]['filename']).suffix))]
            else:
                downloadable = False
                return [downloadable, location, file_type]

        # download
        real_location = self.temp_storage + file_name_generated_url
        location = "storage/" + file_name_generated_url
        open(real_location, 'wb').write(file.content)
        self.files.append(location)


        downloadable = True
        return [downloadable, location, self.handle_check_file_type(extension)]

    def handle_pdf_parse(self):
        pass

    def handle_check_file_type(self, file_extension):
        print("FILE EXTENSION IS " + file_extension)
        if file_extension in self.image_types:
            # print("FILE_EXTENSION IS " + self.IMAGE)
            return self.IMAGE
        else:
            # print("FILE_EXTENSION IS " + self.OTHER)
            return self.OTHER

    def handle_regex_element_clean(self, regex, text):
        p = re.compile(regex)
        some_text = p.sub('', text)
        some_text = self.clean_html(some_text)
        return some_text


test = Scraper()
test.start_pagination_requests()
