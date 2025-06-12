"""Crawlee helper functions for web crawling tasks."""


import json

from datetime import datetime

from crawlee.crawlers import BeautifulSoupCrawlingContext, PlaywrightCrawlingContext


now = datetime.now()
LAST_WEEK = now.day - 7
LAST_WEEK = now.date().replace(day=LAST_WEEK).strftime('%Y-%m-%d')



def get_attr_value_from_element(
        context: BeautifulSoupCrawlingContext, key: str, name: str, attrs: dict={}
):
    """Returns attribute value the element on the page from its name and atrributes"""
    try:
        element = context.soup.find(name=name, attrs=attrs)
        text = element.get(key)
        return text
    except Exception as e:
        context.log.warning(f"Can't get attr value of `{key}` inside element='{name}, {attrs}'.")
        context.log.warning(f"URL: '{context.request.url}'")
        return None

def get_json_ld_from_soup(context: BeautifulSoupCrawlingContext):
    """Fetches and returns the JSON-LD data from a webpage."""
    json_ld_element = context.soup.find_all(name="script", attrs={"type":"application/ld+json"})
    try:
        json_ld = [
            json.loads(json_ld_string.get_text())
            for json_ld_string in json_ld_element
        ]
        return json_ld
    except Exception as e:
        context.log.warning("Can't retrieve JSON-LD")
        context.log.warning(f"URL: '{context.request.url}'")
        return None

def find_value_from_key(key, var):
    """Recursively finds and yields values associated with the given key in a dictionary or list."""
    if hasattr(var,'items'):
        for k, v in var.items():
            if k == key:
                yield v
            if isinstance(v, dict):
                for result in find_value_from_key(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in find_value_from_key(key, d):
                        yield result

async def get_text_from_locator(context: PlaywrightCrawlingContext, selector: str):
    """Removes all tags from HTML string keeping only inner texts"""
    try:
        locator = context.page.locator(selector=selector)
        text = await locator.inner_text(timeout=5000)
        if text in (None, ""):
            context.log.warning(f"Can't get inner text inside selector='{selector}'")
            context.log.warning(f"URL: '{context.request.url}'")
            return None
        return text
    except Exception as e:
        context.log.warning(f"Can't get inner text inside selector='{selector}'")
        context.log.warning(f"URL: '{context.request.url}'")
        return None

async def get_attr_value_from_locator(context: PlaywrightCrawlingContext, selector: str, key: str):
    """Returns attribute value the element on the page from its name and atrributes"""
    try:
        locator = context.page.locator(selector=selector)
        text = await locator.get_attribute(key, timeout=5000)
        if text in (None, ""):
            context.log.warning(f"Can't get attr value of `{key}` inside selector='{selector}'")
            context.log.warning(f"URL: '{context.request.url}'")
            return None
        return text
    except Exception as e:
        context.log.warning(f"Can't get attribute value of `{key}` inside selector='{selector}'")
        context.log.warning(f"URL: '{context.request.url}'")
        return None

async def get_json_ld_from_page(context: PlaywrightCrawlingContext):
    """Fetches and returns the JSON-LD data for a NewsArticle from a webpage."""
    json_ld_element = await context.page.query_selector_all('script[type="application/ld+json"]')
    try:
        json_ld = [
            json.loads(await json_ld_string.inner_text())
            for json_ld_string in json_ld_element
        ]
        return json_ld
    except Exception as e:
        context.log.warning("Can't retrieve JSON-LD")
        context.log.warning(f"URL: '{context.request.url}'")
        return None

# async def random_scroll(page: Page, intensifier: float = 1.0):
#     """Scrolls the page randomly by a factor of intensifier, based on viewport height."""
#     size = page.viewport_size
#     scroll_to = int(size["height"] * (1.0 - (random.randrange(5, 8) / 10)))
#     await page.mouse.wheel(0, scroll_to * intensifier)


# async def random_mouse_move(page: Page, max_height: int, max_width: int):
#     """Moves the mouse to a random position within the specified width and height bounds."""
#     y = random.randint(0, max_height)
#     x = random.randint(0, max_width)
#     await page.mouse.move(x, y)


# async def random_activity(
#     page: Page, page_height: int = 0, page_width: int = 0, intensifier: float = 1.0
# ):
#     """Simulates user activity on page"""
#     size = page.viewport_size
#     page_height = page_height if page_height != 0 else size["height"]
#     page_width = page_width if page_width != 0 else size["height"]

#     await random_scroll(page, intensifier=intensifier)
#     time.sleep(random.randint(0, 1000) / 1000.0)
#     await random_mouse_move(page, page_height, page_width)
#     time.sleep(random.randint(0, 1000) / 1000.0)
#     await random_mouse_move(page, page_height, page_width)
#     time.sleep(random.randint(0, 1000) / 1000.0)
#     await random_mouse_move(page, page_height, page_width)
#     time.sleep(random.randint(0, 1000) / 1000.0)

def get_table(context: BeautifulSoupCrawlingContext, limit: str=None, exclude: list=[]):
    """
    Extracts URLs and their last modified dates from the sitemap context
    and returns them as a list of dictionaries.
    """

    urlset = context.soup.find_all("sitemap")
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(str(context.soup.prettify()))
    if not urlset:
        urlset = context.soup.find_all("url")
    if not urlset:
        context.log.error("No URL elements found.")
        context.log.error(f"URL: {context.request.url}")
    table_data = []
    for url in urlset:
        new_sitemap_url = url.find('loc').get_text(strip=True)
        lastmod = url.find('lastmod').get_text(strip=True) if url.find('lastmod') else None
        if any([exclude_url in new_sitemap_url for exclude_url in exclude]):
            continue
        else:
            if limit:
                # try:
                if lastmod >= limit:
                    table_data.append({
                        'URL': new_sitemap_url,
                        'Last Modified': lastmod,
                    })
                # except Exception as e:
                #     context.log.error(f"URL: {context.request.url}")
                #     context.log.error(f"Child URL: {new_sitemap_url}")
            else:
                table_data.append({
                    'URL': new_sitemap_url,
                    'Last Modified': lastmod,
                })

    return table_data

async def save_table_to_json(
        context: BeautifulSoupCrawlingContext, table_data: list, dataset_name: str
):
    """
    Asynchronously saves the given table data along with the request URL
    to a specified dataset in JSON format.
    """
    data = {
        'url': context.request.url,
        'table_data': table_data,
    }
    await context.push_data(data, dataset_name=dataset_name)
