import datetime
import json
import sqlite3
import time

import telebot

import gameguru
import igromania
import playground
import seo_analysis
import text_similarity
import vgtimes
from config import token, chat_id


class Post:
    def __init__(self, title, text, images, academic_nausea):
        self.title = title
        self.text = text
        self.images = images
        self.academic_nausea = academic_nausea
        self.url = "not found url"


def get_news():
    news_dicts = [vgtimes.get_news(), gameguru.get_news(), playground.get_news(), igromania.get_news()]
    news = {}
    for item in news_dicts:
        for key, value in item.items():
            news[key] = value
    return news


def get_similarity_news(titles):
    similarity_titles = set()
    for title in titles:
        found_titles = [title]
        for i in range(len(titles)):
            if title != titles[i]:
                similarity = text_similarity.get_similarity([title, titles[i]]) * 100
                if similarity > 45:
                    found_titles.append(titles[i])

        if len(found_titles) > 1:
            found_titles = " | ".join(sorted(found_titles))
            similarity_titles.add(found_titles)

    similarity_titles = [title.split(" | ") for title in sorted(similarity_titles)]
    return similarity_titles


def get_content(url):
    function = None
    if url.startswith("https://www.igromania.ru"):
        function = igromania.get_news_content
    elif url.startswith("https://gameguru.ru"):
        function = gameguru.get_news_content
    elif url.startswith("https://www.playground.ru"):
        function = playground.get_news_content
    elif url.startswith("https://vgtimes.ru"):
        function = vgtimes.get_news_content
    return function


def add_title_to_database(title, value):
    with sqlite3.connect("D:/Yang/projects/NewsAi/data.db") as db:
        cursor = db.cursor()
        title = title.replace('"', "'")
        query = """ INSERT INTO News ('Name', 'Exit') VALUES ("{}", "{}")""".format(title, value)
        try:
            cursor.execute(query)
            db.commit()
        except Exception as e:
            query = """ UPDATE News SET 'Exit' = '{}' WHERE 'Name' = "{}" """.format(value, title)
            cursor.execute(query)
            db.commit()


def get_not_saved(themes):
    not_saved = []
    with open("saved_news.json", encoding='utf-8') as f:
        loaded_news = json.load(f)
        for item in themes:
            theme_saved = False
            for title in item:
                if title in loaded_news:
                    theme_saved = True
            if not theme_saved:
                not_saved.append(item)

    return not_saved


def save_titles(titles):
    with open("saved_news.json", encoding='utf-8') as f:
        loaded_news = json.load(f)
        loaded_news += titles
        with open("saved_news.json", "w", encoding='utf-8') as of:
            json.dump(loaded_news, of, indent=4, ensure_ascii=False)


def create_posts(news, news_data):
    created_posts = []
    for list in news:
        posts = []
        for item in list:
            try:
                url = news_data[item]
                get_content_function = get_content(url)
                content = get_content_function(url)
                text = content["Text"]
                images = content["Images"]
                academic_nausea = seo_analysis.calculate_academic_nausea(text)
                post = Post(item, text, images, academic_nausea)
                post.url = url
                posts.append(post)
            except Exception as e:
                print(e)
        created_posts.append(posts)
    return created_posts


def get_best_posts(posts):
    best_posts = []
    for item in posts:
        best_post = Post("", "", [], float("inf"))
        for post in item:
            if post.academic_nausea > best_post.academic_nausea or post.academic_nausea == 0 or len(post.text) > 4096:
                continue
            best_post = post
        best_posts.append(best_post)
    return set(best_posts)


def sort_similarity(titles):
    similarity = set()
    sort = []
    trash = []
    for item in sorted(titles):
        for i in sorted(item):
            similarity.add(i)
    for item in similarity:
        if item in trash:
            continue
        theme_list = [item]
        for title in similarity:
            if title == item:
                continue
            sim = text_similarity.get_similarity([item, title]) * 100
            if sim > 15:
                theme_list.append(title)
                trash.append(title)
        sort.append(theme_list)
    return sort


def send_telegram(bot, text, image):
    try:
        bot.send_photo(chat_id, photo=image, caption=text, parse_mode="HTML")
    except Exception as e:
        bot.send_message(chat_id, text, parse_mode="HTML")


def create_messages(posts):
    messages = []
    for post in posts:
        text = f"<b>{post.title}</b>\n\n{post.text}"
        try:
            image = post.images[0]
        except Exception:
            image = None
        message = {
            "Text": text,
            "Image": image
        }
        messages.append(message)
    return messages


def main():
    bot = telebot.TeleBot(token)
    news = get_news()
    titles = [title for title in news.keys()]
    similarity = get_similarity_news(titles)
    sort = sort_similarity(similarity)
    interest = []

    for item in sort:
        for i in item:
            interest.append(i)

    interest = set(interest)
    not_interest = set([t for t in titles if t not in interest])

    for item in not_interest:
        add_title_to_database(item, "Not interesting")
    for item in interest:
        add_title_to_database(item, "Interesting")

    not_saved = get_not_saved(sort)
    if not not_saved:
        print("Not found new titles:", datetime.datetime.now())
        return

    print(f"Found {len(not_saved)} new titles:", datetime.datetime.now())
    posts = create_posts(not_saved, news)
    best_posts = get_best_posts(posts)
    print("Posts created:", datetime.datetime.now())
    messages = create_messages(best_posts)
    print("Messages created:", datetime.datetime.now())
    for item in messages:
        send_telegram(bot, item["Text"], item["Image"])
        time.sleep(60)

    print("Messages sent:", datetime.datetime.now())
    not_saved_titles = []
    for item in not_saved:
        for i in item:
            not_saved_titles.append(i)

    save_titles(not_saved_titles)
    print("Titles saved:", datetime.datetime.now())


if __name__ == '__main__':
    while True:
        main()
        time.sleep(60 * 30)
