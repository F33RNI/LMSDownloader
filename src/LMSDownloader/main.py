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
import argparse
import logging
import sys

from LMSDownloader import LMSDownloader


def logging_setup() -> None:
    """
    Sets up logging format and level
    :return:
    """
    # Create logs formatter
    log_formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    # Setup logging into console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)

    # Add all handlers and setup level
    root_logger = logging.getLogger()
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.INFO)

    # Log test message
    logging.info("logging setup is complete")


def main():
    # Generate and parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l",
        "--login",
        help="LMS account login",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-p",
        "--password",
        help="LMS account password",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-link",
        "--link-to-download",
        help="LMS link to download",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-path",
        "--save-to",
        help="Path to the dir where to save downloaded PDF and TXT",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--login-link",
        help="link to LMS login page",
        type=str,
        required=False,
        default="https://online.mospolytech.ru/login/index.php"
    )
    parser.add_argument(
        "--wait-between-pages",
        help="how long to wait after going to next page",
        type=float,
        required=False,
        default=1.
    )
    parser.add_argument(
        "--link-check-regex",
        help="regex expression to check link_to_download (replace to \"^\" to bypass link check)",
        type=str,
        required=False,
        default="^(http|https):\\/\\/online\\.mospolytech\\.ru\\/mod\\/(scorm|hvp)\\/view\\.php\\?id="
    )
    parser.add_argument(
        "--headless",
        help="specify to open Chrome in headless mode",
        action="store_true",
        required=False
    )
    parser.add_argument(
        "--no-logging-init",
        help="specify to bypass logging initialization",
        action="store_true",
        required=False
    )
    args = parser.parse_args()

    # Initialize logging
    if not args.no_logging_init:
        logging_setup()

    # Initialize class
    lms_downloader = LMSDownloader.LMSDownloader(args.login, args.password, args.link_to_download,
                                                 args.login_link,
                                                 args.wait_between_pages,
                                                 args.link_check_regex,
                                                 args.headless)

    # Download
    try:
        logging.info("Saved as: {}".format(", ".join(lms_downloader.download(args.save_to))))
        sys.exit(0)
    except KeyboardInterrupt:
        logging.warning("KeyboardInterrupt! Exiting")
    except Exception as e:
        logging.error("Error download data", exc_info=e)
    sys.exit(-1)


if __name__ == "__main__":
    main()
