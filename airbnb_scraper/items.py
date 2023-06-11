import scrapy

class Listing(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    num_bedroom = scrapy.Field()
    num_bathroom = scrapy.Field()
    num_bed = scrapy.Field()
    total_accomodation = scrapy.Field()
    amenities = scrapy.Field()
    host_name = scrapy.Field()
    host_id = scrapy.Field()
    room_type = scrapy.Field()
    picture_url = scrapy.Field()
    rating = scrapy.Field()
    city = scrapy.Field()
    state = scrapy.Field()
    country = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    longitude = scrapy.Field()

class Rating(scrapy.Item):
    accuracy = scrapy.Field()
    check_in = scrapy.Field()
    cleanliness = scrapy.Field()
    communication = scrapy.Field()
    location = scrapy.Field()
    value = scrapy.Field()
    overall = scrapy.Field()
    review_count = scrapy.Field()

