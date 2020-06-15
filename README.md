# Image-Scrapper
Scrape specified images from Google and download them in parallel to create datasets efficiently for training your neural networks. 

## Requirments
Install the required dependencies:

`pip install -r requirements.txt`

Also, download the Selenium webdriver for Chrome https://sites.google.com/a/chromium.org/chromedriver/download and select the compatible driver for your Chrome version. 

## RUN

`python scrapper.py --search-query "cars" --driver-path "path-to-driver" --target-path "path-to-save-images" --n-images 10 --n-threads 4` 

Your dataset is ready!
