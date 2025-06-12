"""
This module provides functionality for crawling and extracting sitemap.
The siteamap crawler is designed to navigate through sitemap.xml, parse table content, 
and retrieve specific data such as urls, and last_modified. The crawler can handle 
multiple web pages, follow links to other pages, and filter content based on user-defined criteria.
"""

import uuid
from datetime import datetime, timedelta

import pandas as pd

from crawlee.crawlers import BeautifulSoupCrawler
from crawlee.configuration import Configuration
from crawlee.http_clients import CurlImpersonateHttpClient
from crawlee.proxy_configuration import ProxyConfiguration

from functions.crawlee_helper.router import sitemap_router
from functions.logger.logger import get_logger

logger = get_logger(__name__)

class SitemapCrawler:
    """Class to crawl content of the website."""

    def __init__(self, proxy_urls:list):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
                            "AppleWebKit/537.36 (KHTML, like Gecko) " +
                            "Chrome/91.0.4472.124 Safari/537.36"
        }
        self.apify_proxy = proxy_urls[0]
        self.proxy_config = ProxyConfiguration(proxy_urls=proxy_urls)

        self.now = datetime.now()
        last_5_year = self.now.year - 5
        self.starting_date = self.now.date().replace(year=last_5_year).strftime("%Y-%m-%d")

    async def crawl_sitemap_table( self, start_urls:list, dataset_name:str) -> None:
        """Crawl table data from sitemap with Crawlee"""
        config = Configuration.get_global_configuration()
        config.internal_timeout = timedelta(minutes=0.25)
        config.persist_storage = False
        config.write_metadata = False
        config.default_request_queue_id = uuid.uuid4().hex

        http_client = CurlImpersonateHttpClient(
            timeout=15, impersonate="chrome124"
        )

        crawler = BeautifulSoupCrawler(
            http_client=http_client,
            parser="xml",
            proxy_configuration=self.proxy_config,
            request_handler=sitemap_router[dataset_name]
        )

        await crawler.run(start_urls)

        await crawler.export_data(
            f"data/Crawlee/sitemap/{dataset_name}.csv", dataset_name=dataset_name
        )

    async def crawl_sitemap(self, sitemap_url):
        """Crawl website data & store in GCS"""
        columns = ["URL", "Last Modified"]
        sitemap_metadata = []
        list_df_post_urls = []

        logger.info(f"Navigating to {sitemap_url} ...")
        dataset_name = "sitemap_" + sitemap_url.split("/")[2].strip("/")
        sitemap_filename = f"data/Crawlee/sitemap/{dataset_name}.pq"

        await self.crawl_sitemap_table([sitemap_url], dataset_name)

        sitemap_df = pd.read_csv(f"data/Crawlee/sitemap/{dataset_name}.csv")
        table_data = []
        for _, row in sitemap_df.iterrows():
            table_data += eval(row["table_data"])
        df_post_urls = pd.DataFrame(data=table_data)
        post_urls_count = len(df_post_urls)
        logger.info(f"{len(df_post_urls)} URLs collected from {sitemap_url}")
        df_post_urls.to_csv(sitemap_filename.replace("pq", "csv"), index=False)
        df_post_urls.to_parquet(sitemap_filename, index=False)

        df_post_urls = df_post_urls[columns]
        list_df_post_urls += [df_post_urls]

        sitemap_metadata += [{
            "url": sitemap_url,
            "post_urls_count": post_urls_count
        }]

        df_post_urls_combined = pd.concat(list_df_post_urls)
        sitemap_metadata = pd.DataFrame(data=sitemap_metadata)
        return df_post_urls_combined, sitemap_metadata
