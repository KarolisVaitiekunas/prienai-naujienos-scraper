import os
from abc import abstractmethod

from selenium.webdriver.chrome.options import Options
from user_agent import generate_user_agent, generate_navigator

userAgent = generate_user_agent()
# userAgent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.7 Safari/537.36'

temp_storage = os.getenv('TEMP_STORAGE')
root_path = os.getenv('ROOT')
image_upload_path = os.getenv('IMAGE_UPLOAD')


class SeleniumBase:
    def __init__(self):
        self.root_path = root_path

        self.options = Options()
        self.options.headless = False
        prefs = {"download.default_directory": temp_storage}
        self.options.add_experimental_option("prefs", prefs)
        self.options.add_argument(f'user-agent={userAgent}')
        self.options.add_argument("--window-size=1920,1200")
        # https://stackoverflow.com/questions/53902507/unknown-error-session-deleted-because-of-page-crash-from-unknown-error-cannot
        self.options.add_argument('--no-sandbox')
        self.options.add_argument("--disable-setuid-sandbox")
        self.options.add_argument('--disable-dev-shm-usage')

    @abstractmethod
    def parse(self):
        raise NotImplementedError

    @abstractmethod
    def handle_pdf_parse(self, *args, **kwargs):
        raise NotImplementedError
