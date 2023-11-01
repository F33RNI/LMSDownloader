# 🏠 LMSDownloader
### Download presentations and lectures from LMS
<div style="width:100%;text-align:center;">
   <p align="center">
      <img src="https://badges.frapsoft.com/os/v1/open-source.png?v=103" >
   </p>
</div>
<div style="width:100%;text-align:center;">
   <p align="center">
      <a href="https://www.youtube.com/@F3RNI"><img alt="YouTube" src="https://img.shields.io/badge/-YouTube-red" ></a>
      <a href="https://f3rni.bandcamp.com"><img alt="Bandcamp" src="https://img.shields.io/badge/-Bandcamp-cyan" ></a>
      <a href="https://open.spotify.com/artist/22PQ62alehywlYiksbtzsm"><img alt="Spotify" src="https://img.shields.io/badge/-Spotify-green" ></a>
      <a href="https://soundcloud.com/f3rni"><img alt="SoundCloud" src="https://img.shields.io/badge/-SoundCloud-orange" ></a>
   </p>
</div>

----------

## 📙 Dependencies

- Google Chrome
- Python 3.9 or 3.10
- Pillow
- pypdf2
- beautifulsoup4
- selenium

----------

## ❓ Get started

### Installing using pip
```
pip install git+https://github.com/F33RNI/LMSDownloader.git
```

### Usage in terminal
```
lmsdownloader [-h] -l LOGIN -p PASSWORD -link LINK_TO_DOWNLOAD -path SAVE_TO [--login-link LOGIN_LINK] [--wait-between-pages WAIT_BETWEEN_PAGES] [--link-check-regex LINK_CHECK_REGEX] [--headless] [--no-logging-init]

options:
  -h, --help            show this help message and exit
  -l LOGIN, --login LOGIN
                        LMS account login
  -p PASSWORD, --password PASSWORD
                        LMS account password
  -link LINK_TO_DOWNLOAD, --link-to-download LINK_TO_DOWNLOAD
                        LMS link to download
  -path SAVE_TO, --save-to SAVE_TO
                        Path to the dir where to save downloaded PDF and TXT
  --login-link LOGIN_LINK
                        link to LMS login page
  --wait-between-pages WAIT_BETWEEN_PAGES
                        how long to wait after going to next page
  --link-check-regex LINK_CHECK_REGEX
                        regex expression to check link_to_download (replace to "^" to bypass link check)
  --headless            specify to open Chrome in headless mode
  --no-logging-init     specify to bypass logging initialization
```

### Usage as python package
```python
from LMSDownloader import LMSDownloader


def main():
    lms_downloader = LMSDownloader.LMSDownloader("your_login@gmail.com",
                                                 "your_strong_password",
                                                 "https://online.mospolytech.ru/mod/scorm/view.php?id=158345",
                                                 headless=False)
    lms_downloader.download("path/to/download")


if __name__ == "__main__":
    main()
```

### LMSDownloader()
#### Initializes LMSDownloader class (just copies fields)
Params:
- `lms_login` – LMS account login
- `lms_password` – LMS account password
- `link_to_download` – LMS link to download
- `login_link` – Link to LMS login page
- `wait_between_pages` – How long to wait after going to next page
- `link_check_regex` – Regex expression to check link_to_download (replace to "^" to bypass link check)
- `headless` – Set True to open Chrome in headless mode

### LMSDownloader.download()
#### Downloads pages into PDF (and TXT for SCORM book)
Params:
- `save_to_directory` – Path to the dir where to save downloaded PDF and TXT

Returns:
- Paths to downloaded files

----------

## ✨ Contribution

- Anyone can contribute! Just create a pull request

----------

### 🚧 P.S. This project is under development!
