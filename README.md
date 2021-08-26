# Scrapy - Postgres pipeline
This is a web crawler built with Scrapy to store shipping container information from [msc](https://https://www.msc.com/track-a-shipment)

## Installation
First clone the repository

```bash
git clone https://github.com/PremanJeyabalan/scrapy_postgres.git
```

When inside the root folder, run the following:

```bash
docker-compose up -d
```

Once finished, to run the scraper for a given id, run the following:
```bash
docker exec -it portcast_scrapy_1 scrapy crawl msc -a id="your_id_here"
```
replacing your_id_here with the specific id to test. Below is an example:

```bash
docker exec -it portcast_scrapy_1 scrapy crawl msc -a id="MEDUJ1581977"
```
