"""
 Copyright (C) 2023 Fern Lane, LMSDownloader

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 See the License for the specific language governing permissions and
 limitations under the License.

 IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR
 OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
 ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 OTHER DEALINGS IN THE SOFTWARE.
"""
import base64
import json
import logging
import os
import re
import tempfile
import time
from urllib.parse import urljoin

from PIL import Image
from PyPDF2 import PdfReader, PdfMerger
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.support.wait import WebDriverWait

# Print to PDF settings
PRINT_SETTINGS = {
    "recentDestinations": [{
        "id": "Save as PDF",
        "origin": "local",
        "account": "",
    }],
    "selectedDestinationId": "Save as PDF",
    "version": 2,
    "isHeaderFooterEnabled": True,
    "isLandscapeEnabled": True
}

# Content types
CONTENT_TYPE_SCORM_PRESENTATION = 0
CONTENT_TYPE_SCORM_BOOK = 1
CONTENT_TYPE_H5P_PRESENTATION = 2

# Default user agent
USER_AGENT_DEFAULT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " \
                     "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

# Default regex to check link_to_download
LINK_CHECK_REGEX_DEFAULT = "^(http|https):\\/\\/online\\.mospolytech\\.ru\\/mod\\/(scorm|hvp)\\/view\\.php\\?id="


class LMSDownloader:
    def __init__(self, lms_login: str, lms_password: str, link_to_download: str,
                 login_link: str = "https://online.mospolytech.ru/login/index.php",
                 wait_between_pages: float = 1.,
                 link_check_regex: str = LINK_CHECK_REGEX_DEFAULT,
                 user_agent: str = USER_AGENT_DEFAULT,
                 window_size: str = "960,1080",
                 headless: bool = True) -> None:
        """
        Initializes LMSDownloader class (just copies fields)
        :param lms_login: LMS account login
        :param lms_password: LMS account password
        :param link_to_download: LMS link to download
        :param login_link: Link to LMS login page
        :param wait_between_pages: How long to wait after going to next page
        :param link_check_regex: Regex expression to check link_to_download, replace to "^" to bypass link check
        :param user_agent: Browser's user agent to prevent mobile version
        :param window_size: Default browser's window size
        :param headless: Set True to open Chrome in headless mode
        """
        self._lms_login = lms_login
        self._lms_password = lms_password
        self._link_to_download = link_to_download
        self._login_link = login_link
        self._wait_between_pages = wait_between_pages
        self._link_check_regex = link_check_regex
        self._user_agent = user_agent
        self._window_size = window_size
        self._headless = headless

        self.browser = None

    def download(self, save_to_directory: str = "") -> list[str]:
        """
        Downloads pages into PDF (and TXT for SCORM book)
        :param save_to_directory: Path to the dir where to save downloaded PDF and TXT
        :return: Paths to downloaded files
        """
        # Test link using regex
        logging.info("Checking link using regex")
        if re.search(self._link_check_regex, self._link_to_download) is None:
            raise Exception("Invalid link to download from! The link must satisfy the expression: {}"
                            .format(self._link_check_regex))

        # Start browser and log into LMS
        self._start_browser()
        self._login()

        # Open link
        logging.info("Redirecting to {}".format(self._link_to_download))
        self.browser.get(self._link_to_download)

        # Enter button
        enter_btn_xpath = "//input[@class='btn btn-primary'][@type='submit']"

        # Wait for page to load
        logging.info("Waiting for page to load")
        WebDriverWait(self.browser, 60).until(expected_conditions.any_of(
            presence_of_element_located((By.XPATH, enter_btn_xpath)),
            presence_of_element_located((By.ID, "scorm_object")),
            presence_of_element_located((By.CLASS_NAME, "h5p-iframe"))))

        # Click button if needed to enter the page
        enter_buttons = self.browser.find_elements(By.XPATH, enter_btn_xpath)
        for enter_button in enter_buttons:
            enter_button.click()

        # Wait for page to load again
        WebDriverWait(self.browser, 60).until(expected_conditions.any_of(
            presence_of_element_located((By.XPATH, enter_btn_xpath)),
            presence_of_element_located((By.ID, "scorm_object")),
            presence_of_element_located((By.CLASS_NAME, "h5p-iframe"))))

        # SCORM
        if self.browser.find_elements(By.ID, "scorm_object"):
            logging.info("Switching to the iframe")
            iframe_src = self.browser.find_element(By.ID, "scorm_object").get_attribute("src")
            if iframe_src.lower().startswith("http"):
                self.browser.get(iframe_src)
            else:
                self.browser.get(urljoin(self._link_to_download, iframe_src))

            # Wait until loaded
            WebDriverWait(self.browser, 60).until(expected_conditions.any_of(
                presence_of_element_located((By.ID, "playerView")),
                presence_of_element_located((By.XPATH, "//div[@class='viewer bookViewer']")),
                presence_of_element_located((By.XPATH, "//div[@class='viewer pageViewer']"))))
            logging.info("Subject page opened")
            time.sleep(1)

            # Check for No button
            message_box_buttons = self.browser.find_elements(By.CLASS_NAME, "message-box-buttons-panel__window-button")
            if message_box_buttons:
                logging.info("Clicking {} button".format(message_box_buttons[-1].text))
                message_box_buttons[-1].click()

            # Wait
            logging.info("Waiting 10s for loading")
            time.sleep(10)
            logging.info("Subject page loaded successfully")

            # Handle book mode
            book_btn_xpath = "//button[@class='btn']/div[@class='icon viewMode book']"
            book_btn = self.browser.find_elements(By.XPATH, book_btn_xpath)
            if book_btn:
                book_btn_ = book_btn[0].find_elements(By.XPATH, "./..")
                if book_btn_:
                    logging.info("Fixing book mode")
                    book_btn_[0].click()
                    time.sleep(1)

        # H5P
        elif self.browser.find_elements(By.CLASS_NAME, "h5p-iframe"):
            # Open iframe's src
            logging.info("Switching to the iframe")
            self.browser.switch_to.frame(self.browser.find_element(By.CLASS_NAME, "h5p-iframe"))

            # Wait until loaded
            WebDriverWait(self.browser, 60).until(presence_of_element_located((By.CLASS_NAME, "h5p-wrapper")))
            logging.info("Subject page opened. Waiting 1 second")
            time.sleep(1)

            # Go to the first page
            logging.info("Going to the first page")
            previous_slide_btn_xpath = "//div[@class='h5p-footer-button h5p-footer-previous-slide']"
            previous_slide_btn = self.browser.find_element(By.XPATH, previous_slide_btn_xpath)
            while previous_slide_btn.get_attribute("aria-disabled") == "false":
                previous_slide_btn.click()
                previous_slide_btn = self.browser.find_element(By.XPATH, previous_slide_btn_xpath)
                time.sleep(self._wait_between_pages)

        # Something else
        else:
            raise ValueError("Wrong content type! Unsupported link")

        # Determine content type
        if self.browser.find_elements(By.ID, "playerView"):
            logging.info("Detected content type as SCORM presentation")
            content_type = CONTENT_TYPE_SCORM_PRESENTATION
        elif self.browser.find_elements(By.XPATH, "//div[@class='viewer pageViewer']"):
            logging.info("Detected content type as SCORM book")
            content_type = CONTENT_TYPE_SCORM_BOOK
        elif self.browser.find_elements(By.CLASS_NAME, "h5p-iframe"):
            logging.info("Detected content type as H5P presentation")
            content_type = CONTENT_TYPE_H5P_PRESENTATION
        else:
            raise ValueError("Wrong content type! Unsupported link")

        # Create directory for downloads
        temp_dir = tempfile.TemporaryDirectory()
        logging.info("Downloading into {}".format(temp_dir.name))

        # Disable landscape for SCORM book
        print_settings = PRINT_SETTINGS.copy()
        if content_type == CONTENT_TYPE_SCORM_BOOK:
            logging.info("Disabling landscape mode")
            print_settings["isLandscapeEnabled"] = False
        else:
            logging.info("Enabling landscape mode")
            print_settings["isLandscapeEnabled"] = True

        # Download all pages
        pdfs = []
        page_counter = 0
        while True:
            # Set path
            pdf_path = os.path.join(temp_dir.name, "{}.pdf".format(page_counter))
            png_path = os.path.join(temp_dir.name, "{}.png".format(page_counter))

            if content_type == CONTENT_TYPE_SCORM_PRESENTATION or content_type == CONTENT_TYPE_SCORM_BOOK:
                # Print into PDF
                logging.info("Downloading page as: {}".format(pdf_path))
                self.browser.execute_script("window.print();")
                pdf_data = self.browser.execute_cdp_cmd("Page.printToPDF", print_settings)
                with open(pdf_path, "wb") as file:
                    file.write(base64.b64decode(pdf_data["data"]))
                pdfs.append(pdf_path)
            elif content_type == CONTENT_TYPE_H5P_PRESENTATION:
                # Save as image and convert to PDF
                logging.info("Downloading page as: {}".format(png_path))
                self.browser.find_element(By.CLASS_NAME, "h5p-iframe").screenshot(png_path)
                logging.info("Converting into RGB and saving as PDF")
                image = Image.open(png_path).convert("RGB")
                image.save(pdf_path)
                image.close()
                pdfs.append(pdf_path)

            # Find next button
            next_slide_btn = None
            if content_type == CONTENT_TYPE_SCORM_PRESENTATION:
                next_slide_btn_xpath = "//button[@aria-label='next slide']"
                next_slide_btn = self.browser.find_element(By.XPATH, next_slide_btn_xpath)
            elif content_type == CONTENT_TYPE_SCORM_BOOK:
                next_slide_btn_xpath = "//button[@class='btn']/div[@class='icon next down']"
                next_slide_btn = self.browser.find_element(By.XPATH, next_slide_btn_xpath).find_element(By.XPATH,
                                                                                                        "./..")
            elif content_type == CONTENT_TYPE_H5P_PRESENTATION:
                next_slide_btn_xpath = "//div[@class='h5p-footer-button h5p-footer-next-slide']"
                next_slide_btn = self.browser.find_element(By.XPATH, next_slide_btn_xpath)

            # Finish or next
            if not next_slide_btn.is_enabled() or next_slide_btn.get_attribute("aria-disabled") == "true":
                logging.info("Downloading done")
                break
            else:
                logging.info("Moving to the next slide and waiting {:.2f} seconds".format(self._wait_between_pages))
                next_slide_btn.click()
                time.sleep(self._wait_between_pages)

            # Increment counter
            page_counter += 1

        downloaded_paths = []

        # Extract text for SCORM book
        if content_type == CONTENT_TYPE_SCORM_BOOK:
            logging.info("Extracting text")
            soup = BeautifulSoup(self.browser.page_source, "html.parser")
            text = soup.get_text("\n")
            txt_file_path = os.path.join(save_to_directory, self.browser.title + ".txt")
            with open(txt_file_path, "w", encoding="utf-8") as txt_file:
                logging.info("Saving text as {}".format(txt_file_path))
                txt_file.write(text)
                downloaded_paths.append(txt_file_path)

        # Merge them
        logging.info("Merging PDF files")
        merger = PdfMerger()
        for filename in pdfs:
            pdf_file = open(filename, "rb")
            merger.append(PdfReader(pdf_file))
            pdf_file.close()
        pdf_file_path = os.path.join(save_to_directory, self.browser.title + ".pdf")
        logging.info("Saving final PDF as {}".format(pdf_file_path))
        merger.write(pdf_file_path)
        downloaded_paths.append(pdf_file_path)
        merger.close()

        # Delete temp dir
        logging.info("Cleaning up temp files")
        temp_dir.cleanup()

        # Exit and close broser
        logging.info("Exiting browser")
        self.browser.quit()

        # Done!
        logging.info("Done!")
        return downloaded_paths

    def _login(self) -> None:
        """
        Logs in into LMS account
        :return:
        """
        logging.info("Logging in...")
        # Find elements
        username_filed = self.browser.find_element(By.ID, "username")
        password_filed = self.browser.find_element(By.ID, "password")

        # Fill with login and password
        username_filed.send_keys(self._lms_login)
        password_filed.send_keys(self._lms_password)

        # Click login button
        login_button = self.browser.find_element(By.ID, "loginbtn")
        login_button.click()

        # Wait for usertext or loginerrors element to make sure page is loaded
        WebDriverWait(self.browser, 60).until(expected_conditions.any_of(
            presence_of_element_located((By.CLASS_NAME, "usertext")),
            presence_of_element_located((By.CLASS_NAME, "loginerrors"))))

        # Check login
        if self.browser.find_elements(By.CLASS_NAME, "loginerrors"):
            raise Exception("Login error! Check login / password")
        logging.info("Logged in successfully")

    def _start_browser(self) -> None:
        """
        Starts browser and opens login page
        :return:
        """
        logging.info("Starting browser{}... Please wait".format(" in headless mode" if self._headless else ""))
        chrome_options = webdriver.ChromeOptions()
        if self._headless:
            chrome_options.add_argument("--headless=old")
        chrome_options.add_argument(f"--user-agent={self._user_agent}")
        chrome_options.add_argument(f"--window-size={self._window_size}")
        # chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--ignore-ssl-errors=yes")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-window")
        chrome_options.add_argument("--kiosk-printing")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_experimental_option("prefs", {
            "printing.print_preview_sticky_settings.appState": json.dumps(PRINT_SETTINGS),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "profile.default_content_setting_values.automatic_downloads": 1
        })

        # Start browser and open login link
        self.browser = webdriver.Chrome(options=chrome_options)
        logging.info("Loading {}".format(self._login_link))
        self.browser.get(self._login_link)

        # Wait for login button element to make sure page is loaded
        WebDriverWait(self.browser, 60).until(presence_of_element_located((By.ID, "loginbtn")))
        logging.info(self._login_link + " loaded successfully")
