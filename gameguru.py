import re
from datetime import datetime
from functools import lru_cache

import requests
import config
from bs4 import BeautifulSoup

url = "https://gameguru.ru/articles/rubrics_news/"


def get_news():
    news = {}

    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "lxml")

        news_items = soup.find_all("div", class_="col-lg-4 col-md-6")

        for item in news_items:
            try:
                title = item.find("a", class_="area-clickable")
                link = "https://gameguru.ru" + title.get("href")
                news[title.text] = link
            except Exception as e:
                pass#print(f"gameguru - {e}: {datetime.now()}")
    except Exception as e:
        pass#print(f"gameguru - {e}: {datetime.now()}")
    return news


def get_images(content):
    images = set([f"https://gameguru.ru{item.get('src')}" for item in content.find_all("img")] if content.find("img") else [])
    gallery = set([f"https://gameguru.ru{item.get('data-src')}" for item in content.find_all("div", class_="swiper-slide")] if content.find("div", class_="swiper-slide") else [])
    return list(images.union(gallery))[1:]


def get_text(content):
    text = ""
    for item in content.contents:
        if item != "\n":
            if str(item).startswith("<p"):
                text += item.text.strip() + "\n\n" if item.text.strip() != "" else ""
            elif str(item).startswith("<blockquote"):
                s = re.sub("^\s+|\n|\r|\s+$", '', item.text.strip()) if item.text.strip() != "" else ""
                caption = s[s.find("»."):].replace("».", "").strip() if "blockquote-author" in str(item) else ""
                print(caption)
                if caption != "":
                    s = s.replace(caption, "")
                    s = re.sub("^\s+|\n|\r|\s+$", '', s)
                    s += f" — {caption}" + "\n\n"
                else:
                    s += "\n\n"
                text += s
            elif str(item).startswith("<ul"):
                ulist = item.text.strip().split("\n")
                for u in ulist:
                    text += "◉ " + u + "\n" if u != ulist[-1] else "◉ " + u + "\n\n"
            elif str(item).startswith("<ol"):
                ulist = item.text.strip().split("\n")
                for index, u in enumerate(ulist):
                    text += f"{index + 1}. " + u + "\n" if u != ulist[-1] else f"{index + 1}. " + u + "\n\n"
    return text.strip()


def get_news_content(url):
    res = requests.get(url, headers=config.headers)
    soup = BeautifulSoup(res.text, "lxml")

    content = soup.find("article", class_="news-article")

    data = {
        "Text": get_text(content),
        "Images": get_images(content)
    }
    return data

