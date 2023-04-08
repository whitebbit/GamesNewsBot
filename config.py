import os

from dotenv import load_dotenv
headers = {
    "cache-control": "max-age=2592000",
    "accept-encoding": "gzip, deflate, br",
    "accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 OPR/93.0.0.0"
}
load_dotenv()
token = os.environ.get('TOKEN', 'None')
chat_id = os.environ.get('CHAT_ID', 'None')
