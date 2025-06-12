"""
Websites: rumahonetwothree.it
This module provides a website route handler for the Crawlee library, 
enabling efficient crawling of websites through their website. 
The website route handler is designed to parse HTML websites, extract URLs, 
and define crawling strategies based on the website structure. 
This approach helps to ensure comprehensive and structured web scraping, 
adhering to the website"s guidelines.
"""

from crawlee.crawlers import BeautifulSoupCrawlingContext
from crawlee.router import Router

from functions.crawlee_helper.crawl import (
    # get_attr_value_from_element,
    get_table,
    # get_text_from_element,
    save_table_to_json,
    LAST_WEEK,
)

rumahonetwothree_sitemap_router = Router[BeautifulSoupCrawlingContext]()
rumahonetwothree_router = Router[BeautifulSoupCrawlingContext]()

DATASET_NAME = "www.rumah123.com"


@rumahonetwothree_sitemap_router.default_handler
async def sitemap_request_handler(
    context: BeautifulSoupCrawlingContext,
) -> None:
    """This is a fallback route which will handle the www.rumah123.com sitemap URL."""
    context.log.info(f'Navigating to {context.request.url} ...')

    # table_data = get_table(context=context, limit=LAST_5_YEAR)
    if context.request.url == "https://www.rumah123.com/sitemap-v3/sitemap-ldp-jual.xml":
        table_data = get_table(context=context)
        new_sitemap_url = [row["URL"] for row in table_data if "/sitemap-ldp-jual-" in row["URL"]]
        await context.add_requests(new_sitemap_url)
    # elif "/sitemap-ldp-jual-" in context.request.url:
    #     table_data = get_table(context=context, limit=LAST_5_YEAR)
        # new_sitemap_url = [row["URL"] for row in table_data if "sitemap-" in row["URL"]]
        # await context.add_requests(new_sitemap_url)
    else:
        table_data = get_table(context=context, limit=LAST_WEEK)
        dataset_name = "sitemap_" + DATASET_NAME
        await save_table_to_json(context, table_data, dataset_name)

# @rumahonetwothree_router.default_handler
# async def request_handler(context: BeautifulSoupCrawlingContext) -> None:
#     """This is a fallback route which will handle the www.rumah123.com Website."""
#     context.log.info(f"Processing {context.request.url}")
#     context.log.info(
#         f"Proxy for the current request: {context.proxy_info.username}"
#     )

#     # Find title of the post
#     title = get_attr_value_from_element(
#         context=context, key="content", name="meta", attrs={"property":"og:title"}
#     )

#     # Find description of the post
#     description = get_attr_value_from_element(
#         context=context, key="content", name="meta", attrs={"property":"og:description"}
#     )

#     # Find content of the post
#     content = get_text_from_element(
#         context=context, name="div", attrs={"class":"text-content"}
#     )

#     # Find published date of the post
#     published_at = get_attr_value_from_element(
#         context=context, key="content", name="meta", attrs={"property":"article:published_time"}
#     )

#     # Find source of the post
#     source = get_attr_value_from_element(
#         context=context, key="content", name="meta", attrs={"property":"og:site_name"}
#     )
#     if source is None:
#         source = "rumahonetwothree"

#     # Find author of the post
#     author = get_attr_value_from_element(
#         context=context, key="content", name="meta", attrs={"name":"author"}
#     )

#     # Find language of the post
#     language = get_attr_value_from_element(
#         context=context, key="lang", name="html"
#     )

#     data = {
#         "url": context.request.url,
#         "title": title,
#         "description": description,
#         "content": content,
#         "publishedAt": published_at,
#         "source": source,
#         "author": author,
#         "language": language,
#     }

#     await context.push_data(data, dataset_name=DATASET_NAME)
