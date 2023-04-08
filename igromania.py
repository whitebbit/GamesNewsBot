import re
from datetime import datetime
from functools import lru_cache

import requests
import config
from bs4 import BeautifulSoup


url = "https://www.igromania.ru/news/"


def get_news():
    news = {}
    try:
        res = requests.get(url, headers=config.headers)
        soup = BeautifulSoup(res.text, "lxml")

        news_items = soup.find_all("div", class_="aubli_data")

        for item in news_items:
            try:
                title = item.find("a")
                link = "https://www.igromania.ru" + title.get("href")
                news[title.text] = link
            except Exception as e:
                print(f"igromania - {e}: {datetime.now()}")
    except Exception as e:
        print(f"igromania - {e}: {datetime.now()}")
    return news


def get_images(content, global_content=None):
    images = []
    if content.find("img"):
        img = content.find_all("img")
        for image in img:
            images.append(image.get("src"))
    if global_content:
        if global_content.find("img"):
            img = global_content.find_all("img")
            for image in img:
                images.append(image.get("src"))
    return images


def get_text(content):
    text = ""
    for item in content.contents:
        if item != "\n":
            if str(item).startswith("<div>"):
                if str(item).find('''<div class="uninote console">''') != -1 or str(item).find('''<div class="video_block">''') \
                        != -1 or str(item).find('''<div class="grayblock_nom">''') != -1 or \
                        str(item).find('''<div class="pic_container">''') != -1 or \
                        str(item).find('''<div class="container_wide1">''') != -1:
                    continue
                if str(item).find('''<div class="opinion_text">''') != -1:
                    s = item.text.strip()
                    caption = s[s.find("»."):].replace("».", "").strip()
                    text += re.sub("^\s+|\n|\r|\s+$", '', (item.text.strip().replace(caption, "")) + f""" — {caption.strip()}""") + "\n\n"
                elif str(item).find('''<div class="live_schedule">''') != -1:
                    s = str(item)
                    titles_index = [m.start() for m in re.finditer('<div class="schedule_ttl">', str(item))]
                    titles = [s[i:s.find("</strong>", i)].replace('<div class="schedule_ttl"><strong>', "") for i in titles_index]
                    top_list = []
                    for i, t in enumerate(titles):
                        l = item.text[item.text.find(t): item.text.find(titles[i + 1])].replace(t, "") if t != titles[-1] else item.text[item.text.find(t):].replace(t, "")
                        top_list.append(l)
                    for i, t in enumerate(titles):
                        text += f"{t}:" + top_list[i] + "\n"
                else:
                    text += item.text.strip() + "\n\n"
            elif str(item).startswith("<h3>"):
                text += item.text.strip() + "\n"
            elif str(item).startswith("<ol"):
                ulist = item.text.strip().split(";")
                for index, u in enumerate(ulist):
                    if u.strip() == "":
                        continue
                    text += f"{index + 1}. " + u.strip() + "\n" if u != ulist[-1] else f"{index + 1}. " + u.strip() + "\n\n"
            elif str(item).startswith("<ul"):
                sep = ";" if item.text.strip().find(";") != -1 else "\n"
                ulist = item.text.strip().split(sep)
                for u in ulist:
                    if u.strip() == "":
                        continue
                    text += f"◉ " + u.strip() + "\n" if u != ulist[-1] else f"◉ " + u.strip() + "\n\n"

    return text.strip()


def get_news_content(url):
    res = requests.get(url, headers=config.headers)
    soup = BeautifulSoup(res.text, "lxml")

    content = soup.find("div", class_="universal_content clearfix")
    global_content = soup.find("div", class_="main_pic_container")
    data = {
        "Text": get_text(content),
        "Images": get_images(content, global_content)
    }
    return data

