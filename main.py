import asyncio
import os

from fastapi import FastAPI, status
from dotenv import load_dotenv
from pydantic import BaseModel

from functions.crawler.sitemap_crawler import SitemapCrawler

load_dotenv()
app = FastAPI()


class SitemapURL(BaseModel):
    """Model for scraping a new sitemap."""
    sitemap_url: str


@app.post("/sitemap", status_code=status.HTTP_201_CREATED)
def scrape_sitemap(data: SitemapURL):
    """Scrape url list from sitemap URL."""

    proxy_urls = [os.environ["APIFY_PROXY"]]

    crawler = SitemapCrawler(proxy_urls=proxy_urls)
    df_post_urls, sitemap_metadata = asyncio.run(crawler.crawl_sitemap(data.sitemap_url))
    print(sitemap_metadata)

    return df_post_urls.to_json(orient="records")
