import random
import threading
import time
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


def try_login(headers):
    data = {
        "username": random.choice(FAKE_USERNAMES),
        "password": random.choice(COMMON_PASSWORDS),
    }
    requests.post(URL, data=data, headers=headers)


def fast_bot(name, attempts):
    """No costume, no waiting."""
    headers = {"X-Client-ID": name, "User-Agent": "python-requests/2.31.0"}
    for _ in range(attempts):
        try_login(headers)
    print(f"{name} finished")


def disguised_bot(name, attempts):
    """Browser costume, but waits exactly 0.5 seconds every time."""
    headers = {
        "X-Client-ID": name,
        "User-Agent": BROWSERS[0],
        "Accept-Language": "en-US,en;q=0.9",
    }
    for _ in range(attempts):
        try_login(headers)
        time.sleep(0.5)
    print(f"{name} finished")


def slow_bot(name, attempts):
    """Browser costume plus random human-looking waits."""
    headers = {
        "X-Client-ID": name,
        "User-Agent": random.choice(BROWSERS),
        "Accept-Language": random.choice(LANGUAGES),
    }
    for _ in range(attempts):
        try_login(headers)
        time.sleep(random.uniform(2, 12))
    print(f"{name} finished")


for i in range(1, 21):
    fast_bot(f"bot-fast-{i}", 100)

for i in range(1, 11):
    disguised_bot(f"bot-disguised-{i}", 40)

# The slow bots run at the same time (threads) so this doesn't take forever
threads = []
for i in range(1, 9):
    t = threading.Thread(target=slow_bot, args=(f"bot-slow-{i}", 15))
    t.start()
    threads.append(t)
for t in threads:
    t.join()

print("Done!")