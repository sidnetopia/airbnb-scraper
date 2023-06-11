# Airbnb Listing Scraper

Due to Airbnb's dynamic nature and heavy reliance on JavaScript for content loading, two approaches were available to address this issue.

The first option involved using frameworks like scrapy Splash or Selenium to fully load the Airbnb site and execute the JavaScript code. However, this method had the drawback of requiring the setup of these frameworks, which added significant weight and complexity to the system.

The alternative approach I chose was to identify the endpoint to which the JavaScript sent its requests and directly scrape the data from that source.

I decided to go with the second approach as it is easier and faster.

## Thought process

1. Conducted research on how Airbnb retrieves data
   - Cannot determine how Airbnb obtains the data solely using browser tools.
   - Discovered a useful [GitHub repository](https://github.com/tecnosam/airbnb-scraper) that utilizes the [Airbnb API](https://www.airbnb.com/api/v2/explore_tabs)
2. Noticed an assumption made by the original poster (OP) 
    - listing's city is always the same as the searched city.
       - Corrected this by incorporating the retrieved listing city, which limited the data to approximately 540 records for the three cities.
    - some values are text instead of float and integer.
       - Typecasted to their desired type.

3. Observed that the names of some listing owners were left blank.
4. Realized that additional information, specifically ratings, could be scraped from the Airbnb website.
   - However, this extended beyond scrapy's capabilities, leading me to utilize playwright.
   - Unfortunately, the use of [Scrapy Playwright](https://github.com/scrapy-plugins/scrapy-playwright) was limited to Linux, causing delays due to working on different systems.

## How to run

1. Clone this repository.
2. Create a virtual environment with `python -m venv env` or `python -m virtualenv env`.
3. Activate the virtual environment with `source ./env/bin/activate` for Linux or `.\env\Scripts\activate` for Windows.
4. Run `pip install -r requirements.txt`.
5. Install the required browser: `playwright install`.
6. Create a `.env` file and add `MONGO_URI=<your-mongodb-connection-string>`.
7. Run `scrapy crawl listings`.

Sample data can be found in `listing.json` and `listing.csv`. For amenities ID mapping, refer to `airbnb_scraper --> models --> amenities.py`.

Modify the `PLAYWRIGHT_LAUNCH_OPTIONS = {"headless": False}` to `True` if you want to hide the browser.