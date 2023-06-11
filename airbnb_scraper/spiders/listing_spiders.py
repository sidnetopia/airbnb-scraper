import scrapy
from urllib.parse import urlencode
import json
from airbnb_scraper.items import Listing, Rating
import re

class ListingSpiders(scrapy.Spider):
    name = "listing"

    cities = {}
    state_code = 'AR'
    country = 'United States'
    limit = 300

    def __init__(self):
        super().__init__()
        self.cities = {
            "Springdale": 0,
            "Fayetteville": 0,
            "Rogers": 0
        }

    def start_requests(self):
        """
        Entry point for the spider. Generates requests to scrape listings for each city.
        """
        for city in self.cities:
            listings_url = self.gen_url(city)

            yield scrapy.Request(url=listings_url, callback=self.parse_page, meta={'searched_city': city})

    def parse_page(self, response):
        """
        Parses the listings page and extracts listing information.
        """
        data = json.loads(response.body)
        listings = data.get('explore_tabs')[0].get('sections')[-1].get('listings')

        searched_city = response.meta.get('searched_city')

        for listing in listings:
            if self.cities[searched_city] == self.limit:
                break

            yield self.extract_listing_info(listing, searched_city)

        # next page on api
        pagination_metadata = data.get('explore_tabs')[0].get('pagination_metadata')
        if pagination_metadata.get('has_next_page') and self.cities[searched_city] < self.limit:
            params = {
                'items_offset': pagination_metadata.get('items_offset'),
                'section_offset': pagination_metadata.get('section_offset')
            }

            new_url = self.gen_url(searched_city, additional_params=params)
            yield scrapy.Request(url=new_url, callback=self.parse_page, meta={'searched_city': searched_city})

    def extract_listing_info(self, listing, searched_city):
        """
        Extracts listing information from the listing details and prepares a request to scrape ratings.
        """
        pricing_quote = listing['pricing_quote']
        listing_info = listing['listing']

        city, state, country = [part.strip() for part in listing_info['public_address'].split(',')]

        # Ensure that the listing is in the correct place
        if city != searched_city or state != self.state_code or country != self.country:
            return None

        self.cities[searched_city] += 1

        price = pricing_quote['structured_stay_display_price']['primary_line']['price']
        price = int(re.search(r'\d+', price).group()) if re.search(r'\d+', price) else 0.0

        data = {
            'id': listing_info['id'],
            'name': listing_info['name'],
            'city': listing_info['city'],
            'state': "Arkansas",
            'country': country,
            'num_bedroom': int(listing_info['bedrooms']),
            'num_bed': int(listing_info['beds']),
            'num_bathroom': int(listing_info['bathrooms']),
            'total_accomodation': float(price),
            'host_name': listing_info['user']['first_name'],
            'host_id': listing_info['user']['id'],
            'latitude': listing_info['lat'],
            'longitude': listing_info['lng'],
            'room_type': listing_info['room_type'],
            'picture_url': listing_info['picture_url'],
            'amenities': listing_info['amenity_ids'],
        }

        # get rating details
        listing_page_url = "https://www.airbnb.com/rooms/{}".format(listing_info['id'])
        return scrapy.Request(listing_page_url, 
                        callback=self.parse_rating,
                        meta={"playwright": True, "playwright_include_page": True, "listing": data})



    async def parse_rating(self, response):
        """
        Parses the rating information from the listing page.
        """
        rating_dict = {
            "overall": None,
            "review_count": None,
            "cleanliness": None,
            "check_in": None,
            "accuracy": None,
            "location": None,
            "value": None

        }

        try:
            page = response.meta["playwright_page"]
            rating_text = await page.inner_text('h2 .a8jt5op.dir.dir-ltr')

            if rating_text:
                overall_match = re.search(r'([\d.]+)\sout', rating_text)
                review_count_match = re.search(r'from\s(\d+)', rating_text)

                if overall_match and review_count_match:
                    rating_dict["overall"] = float(overall_match.group(1))
                    rating_dict["review_count"] = int(review_count_match.group(1))

                    elements = await page.query_selector_all('div._1s11ltsf')

                    for element in elements:
                        category_rating = await element.text_content()
                        matches = re.match(r"([^\d]+)([\d.]+)", category_rating)
                        if matches:
                            label = matches.group(1)
                            value = matches.group(2)

                            rating_dict[self.get_rating_key(label)] = float(value)
        except:
            pass

        await page.close()

        listing = response.meta["listing"]
        listing["rating"] = Rating(rating_dict)

        yield Listing(listing)

    def get_rating_key(self, label):
        """
        Maps the rating label to a corresponding key.
        """
        mapping = {
            'Cleanliness': 'cleanliness',
            'Communication': 'communication',
            'Check-in': 'check_in',
            'Accuracy': 'accuracy',
            'Location': 'location',
            'Value': 'value'
        }

        if label not in mapping:
            return ''

        return mapping[label]

    def gen_url(self, city, additional_params=None):
        """
        Generates the URL for retrieving the listings for a specific city.
        """
        base_url = "https://www.airbnb.com/api/v2/explore_tabs?"
        params = {
            "key": "d306zoyjsyarp7ifhu67rjxn52tv0t20",
            "selected_tab_id": "home_tab",
            "items_per_grid": 50,
            "max_total_count": 5000,
            "query": "{}--{}--{}"
        }
        params['query'] = params['query'].format(city, self.state_code, self.country.replace(' ', '-'))

        url = base_url + urlencode(params)
        if additional_params:
            url += '&' + urlencode(additional_params)

        return url