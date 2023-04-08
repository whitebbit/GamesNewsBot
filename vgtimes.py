from datetime import datetime
from functools import lru_cache
import requests
import config
from bs4 import BeautifulSoup
import emoji
url = "https://vgtimes.ru/news/"


def get_news():
    news = {}

    try:
        res = requests.get(url, headers=config.headers, timeout=5)
        soup = BeautifulSoup(res.text, "lxml")

        news_items = soup.find_all("div", class_="item-name type0")

        for item in news_items:
            try:
                title = item.find("a")
                link = title.get("href")
                news[title.text] = link
            except Exception as e:
                print(f"vgtimes - {e}: {datetime.now()}")
    except Exception as e:
        print(f"vgtimes - {e}: {datetime.now()}")
    return news


def get_images(content):
    images = []
    if content.find("img"):
        for item in content.find_all("img"):
            image = item.get("data-src")
            if "https" not in image or "http" not in image:
                image = "https://vgtimes.ru" + image
            images.append(image)
    return images


def get_text(content):
    text = ""
    for item in content.contents:
        if item != "\n":
            if str(item).startswith("<p>"):
                if str(item) == "<p><!--dle_list--></p>" or str(item) == "<p><!--dle_ol_1--></p>":
                    continue

                if not emoji.emoji_list(item.text.strip()):
                    text += item.text.strip() + "\n\n"

            elif str(item).startswith("<ul"):
                if 'class="relrel"' in str(item):
                    continue
                sep = ";" if item.text.strip().find(";") != -1 else "."
                ulist = item.text.strip().split(sep)
                ulist = sorted(ulist, key=lambda e: e)
                for u in ulist:
                    if u:
                        text += "◉ " + u + "\n" if u != ulist[-1] else "◉ " + u + "\n\n"
            elif str(item).startswith("<ol"):
                ulist = item.text.strip().split(";")
                for index, u in enumerate(ulist):
                    text += f"{index + 1}. " + u + "\n" if u != ulist[-1] else f"{index + 1}. " + u + "\n\n"
            elif "<blockquote" in str(item):
                s = str(item)
                caption = s[s.index("""<figcaption"""):s.index("</figcaption")].replace("""<figcaption class="favt">""", "")
                text += f"""«{item.text.strip().replace(caption, "")}» {caption}""" + "\n\n"
            elif str(item).startswith("<h2"):
                text += item.text.strip() + "\n"
    return text.strip()


def get_news_content(url):
    res = requests.get(url, headers=config.headers)
    soup = BeautifulSoup(res.text, "lxml")

    content = soup.find("div", class_="v12 text_block")

    data = {
        "Text": get_text(content),
        "Images": get_images(content)
    }
    return data

