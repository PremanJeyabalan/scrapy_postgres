FROM python:3.6
ADD scrape .
RUN pip install scrapy psycopg2 pytz

