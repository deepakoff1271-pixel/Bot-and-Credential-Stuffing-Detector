import random
import time
from concurrent.futures import ThreadPoolExecutor
import requests

URL = "http://127.0.0.1:5000/login"

# The attacker has a leaked list, so every username is real
USERS = {
    "alice": "alice123",
    "bob": "bobpass",
    "carol": "carol2024",
}

OLD_PASSWORDS = ["Password1", "welcome123", "summer2023", "letmein1", "qwerty123", "iloveyou2"]

BROWSERS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
]

LANGUAGES = ["en-US,en;q=0.9", "en-GB,en;q=0.8", "en-IN,en;q=0.9"]


def valid_bot(number):
    """Real usernames, old leaked passwords, one throwaway identity."""
    headers = {
        "X-Client-ID": f"bot-small-{number}",
        "User-Agent": random.choice(BROWSERS),
        "Accept-Language": random.choice(LANGUAGES),
    }
    username = random.choice(list(USERS))
    for _ in range(random.randint(2, 3)):
        # about 1 in 20 leaked passwords still works
        if random.random() < 0.05:
            password = USERS[username]
        else:
            password = random.choice(OLD_PASSWORDS)
        requests.post(URL, data={"username": username, "password": password}, headers=headers)
        time.sleep(random.uniform(3, 10))


def safe_bot(number):
    try:
        valid_bot(number)
        return True
    except Exception as error:
        print("Bot", number, "failed:", error)
        return False


print("Starting...")
with ThreadPoolExecutor(max_workers=30) as pool:
    results = list(pool.map(safe_bot, range(1, 21)))

print("Bots that worked:", sum(results), "out of", len(results))
print("Done!")