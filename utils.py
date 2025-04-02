import os

import requests
import tiktoken
from dotenv import load_dotenv
from firecrawl import FirecrawlApp

load_dotenv()


def firecrawl_scrape(url):
    app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
    d = app.scrape_url(url, params={"formats": ["markdown"]})
    return truncate_text(d["markdown"], 2000)


def validate_email(email):
    url = f"https://apilayer.net/api/check?access_key={os.getenv('MAIL_API_KEY')}&email={email}"

    try:
        response = requests.get(url)
        data = response.json()
        print(data)
        return data

    except Exception as e:
        return False


def truncate_text(text, max_tokens=8000, model="gpt-4"):
    tokenizer = tiktoken.encoding_for_model(model)
    tokens = tokenizer.encode(text)
    truncated_tokens = tokens[:max_tokens]
    return tokenizer.decode(truncated_tokens)
