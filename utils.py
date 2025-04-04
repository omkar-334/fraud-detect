import asyncio
import os

import requests
import tiktoken
from bs4 import BeautifulSoup
from firecrawl import FirecrawlApp
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright


def scrape(url, p=True):
    try:
        if p:
            content = asyncio.run(playwright_scrape_async(url))
            content = extract_text(content)
    except:
        content = ""

    try:
        content = firecrawl_scrape(url)
    except:
        content = ""

    return content


def extract_text(content):
    soup = BeautifulSoup(content, "html.parser")
    # Return text content of the page
    content = soup.get_text()
    # Remove extra whitespace and newlines
    content = " ".join(content.split())
    content = content[:2000].strip()
    return content


# added this since firecrawl probably has rate limits (have to handle that then add this as fallback)
def playwright_scrape(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto(url)

        page.wait_for_selector("body")

        content = page.content()

        context.close()
        browser.close()

    return content


async def playwright_scrape_async(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url)

        await page.wait_for_selector("body")

        content = await page.content()

        await context.close()
        await browser.close()

    return content


def firecrawl_scrape(url):
    app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
    d = app.scrape_url(url, params={"formats": ["markdown"]})
    return truncate_text(d["markdown"], 2000)


# Mailboxlayer only allows 100 requests per month for free
def validate_email(email):
    return {}
    url = f"https://apilayer.net/api/check?access_key={os.getenv('MAIL_API_KEY')}&email={email}"

    try:
        response = requests.get(url)
        data = response.json()
        if data.get("error"):
            print("EMAIL ERROR:", data["error"]["info"])
            data = {}
    except:
        data = {}

    return data


def truncate_text(text, max_tokens=8000, model="gpt-4"):
    tokenizer = tiktoken.encoding_for_model(model)
    tokens = tokenizer.encode(text)
    truncated_tokens = tokens[:max_tokens]
    return tokenizer.decode(truncated_tokens)
