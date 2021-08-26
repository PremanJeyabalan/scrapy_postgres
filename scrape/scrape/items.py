# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ContainerItem(scrapy.Item):
    type = scrapy.Field()
    id_type = scrapy.Field()
    id = scrapy.Field()
    updated_at = scrapy.Field()
    final_pod = scrapy.Field()
    final_pod_eta = scrapy.Field()
    shipped_to = scrapy.Field()
    price_calculation_date = scrapy.Field()
    movements = scrapy.Field()
    pass

class MovementContainerItem(scrapy.Item):
    location = scrapy.Field()
    description = scrapy.Field()
    date = scrapy.Field()
    vessel = scrapy.Field()
    voyage = scrapy.Field()
    pass

class BOLItem(scrapy.Item):
    id_type = scrapy.Field()
    id = scrapy.Field()
    updated_at = scrapy.Field()
    bl_issuer = scrapy.Field()
    departure_date = scrapy.Field()
    vessel = scrapy.Field()
    port_of_load = scrapy.Field()
    port_of_discharge = scrapy.Field()
    transhipment = scrapy.Field()
    price_calculation_date = scrapy.Field()
    containers = scrapy.Field()
    pass