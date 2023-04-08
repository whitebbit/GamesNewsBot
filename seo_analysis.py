import string
import time
import pymorphy3

from math import sqrt
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from nltk.corpus import stopwords
from nltk.stem.snowball import RussianStemmer
from fuzzywuzzy import process

_options = Options()
# _options.headless = True
# _options.add_argument("--headless")
_options.binary_location = r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
stopwords = stopwords.words("russian")


def get_seo_analysis(text):
    browser = webdriver.Firefox(
        executable_path=r"D:/Yang/projects/GamesNews/venv/WebDriverManager/gecko/v0.32.0/geckodriver-v0.32.0-win64/geckodriver.exe",
        options=_options)
    browser.get("https://advego.com/text/seo/")
    time.sleep(2)

    textarea = browser.find_element(By.ID, "job_text_seo")
    button = browser.find_element(By.XPATH, """//*[@id="text_spell_check"]/a[1]""")
    textarea.send_keys(f"""{text}""")
    time.sleep(2)

    button.click()
    time.sleep(2)

    # classic_nausea = browser.find_element(By.XPATH, """//*[@id="text_check_results_form"]/table/tbody/tr[10]/td[2]""")
    academic_nausea = browser.find_element(By.XPATH, """//*[@id="text_check_results_form"]/table/tbody/tr[11]/td[2]""")

    analysis = {
        # "Classic": float(classic_nausea.text) if classic_nausea.text != "" else float("inf"),
        "Academic": float(academic_nausea.text[:-1]) if academic_nausea.text != "" else float("inf")
    }
    browser.close()
    return analysis


def calculate_academic_nausea(text):
    morph = pymorphy3.MorphAnalyzer(lang='ru')
    stemmer = RussianStemmer()

    clean_text = clean_string(text)
    words = sorted(clean_text.split())
    normalized_words = [morph.parse(w)[0].normal_form for w in words]
    stemmer_words = [stemmer.stem(x) for x in normalized_words]
    words = []
    for i in stemmer_words:
        l = stemmer_words[:]
        singles = [i]
        l.remove(i)
        extract_one = process.extractOne(i, l)
        if extract_one[1] > 70:
            singles.append(extract_one[0])
            stemmer_words.remove(extract_one[0])
        words.append(singles)
    words = [w for w in words if len(w) > 1]
    if len(text.split()) > 0:
        academic_nausea = (sqrt(sum([len(s) ** 2 for s in words])) / len(text.split())) * 100
        academic_nausea = round(academic_nausea, 2)
    else:
        academic_nausea = float("inf")
    return academic_nausea


def clean_string(text):
    text = "".join([word for word in text if word not in string.punctuation])
    text = text.replace("—", " ")
    text = text.replace("◉", " ")
    text = text.replace("●", " ")
    text = text.replace("–", " ")
    text = text.replace("»", " ")
    text = text.lower()
    text = " ".join([word for word in text.split() if word not in stopwords])
    return text

