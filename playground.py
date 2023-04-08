from datetime import datetime
from functools import lru_cache

import requests
import config
from bs4 import BeautifulSoup

url = "https://www.playground.ru/news"


def get_news():
    news = {}
    try:
        res = requests.get(url, headers=config.headers)
        soup = BeautifulSoup(res.text, "lxml")

        news_items = soup.find_all("div", class_="post")
        for item in news_items:
            try:
                title = item.find("div", class_="post-title").find("a")
                link = title.get("href")
                news[title.text] = link
            except Exception as e:
                print(f"playground - {e}: {datetime.now()}")
    except Exception as e:
        print(f"playground - {e}: {datetime.now()}")
    return news


def get_images(content):
    return [item.get("src") for item in content.find_all("img")] if content.find("img") else []


def get_text(content):
    text = ""
    for item in content.contents:
        if item != "\n":
            if "<p>" in str(item):
                text += item.text.strip() + "\n\n"
            elif "<ul>" in str(item):
                ulist = item.text.strip().split("\n")
                for u in ulist:
                    text += "◉ " + u + "\n" if u != ulist[-1] else "◉ " + u + "\n\n"
            elif "<ol>" in str(item):
                ulist = item.text.strip().split("\n")
                for index, u in enumerate(ulist):
                    text += f"{index + 1}. " + u + "\n" if u != ulist[-1] else f"{index + 1}. " + u + "\n\n"
            elif "<blockquote>" in str(item):
                text += f"«{item.text.strip()}»" + "\n\n"
    return text.strip()


def get_news_content(url):
    res = requests.get(url, headers=config.headers, timeout=5)
    soup = BeautifulSoup(res.text, "lxml")

    content = soup.find("div", class_="article-content js-post-item-content")

    data = {
        "Text": get_text(content),
        "Images": get_images(content)
    }
    return data


