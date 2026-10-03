import random
import time
import requests

URL = "http://127.0.0.1:5000/login"

USERS = {
    "alice": "alice123",
    "bob": "bobpass",
    "carol": "carol2024",
}

BROWSERS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
]

LANGUAGES = ["en-US,en;q=0.9", "en-GB,en;q=0.8", "en-IN,en;q=0.9"]


def make_headers(client_id):
    return {
        "X-Client-ID": client_id,
        "User-Agent": random.choice(BROWSERS),
        "Accept-Language": random.choice(LANGUAGES),
    }


def login(username, password, headers):
    requests.post(URL, data={"username": username, "password": password}, headers=headers)


def normal_human(number):
    """One login, sometimes a typo first."""
    username = random.choice(list(USERS))
    password = USERS[username]
    headers = make_headers(f"human-normal-{number}")
    if random.random() < 0.15:
        login(username, password[:-1], headers)
        time.sleep(random.uniform(3, 8))
    login(username, password, headers)


def forgetful_human(number):
    """Cannot remember the password: several wrong tries, then success."""
    username = random.choice(list(USERS))
    password = USERS[username]
    headers = make_headers(f"human-forgetful-{number}")
    guesses = [password[:-1], password + "1", password.upper(), password.capitalize(), password[1:], password + "!"]
    random.shuffle(guesses)
    for guess in guesses[: random.randint(3, 6)]:
        login(username, guess, headers)
        time.sleep(random.uniform(2, 6))
    login(username, password, headers)


def repeat_human(number):
    """Logs in, logs out, logs in again, a few times."""
    username = random.choice(list(USERS))
    password = USERS[username]
    headers = make_headers(f"human-repeat-{number}")
    for _ in range(random.randint(2, 4)):
        login(username, password, headers)
        time.sleep(random.uniform(4, 12))


def office_network(number):
    """Several coworkers behind one shared network ID."""
    client_id = f"human-office-{number}"
    for _ in range(random.randint(4, 7)):
        username = random.choice(list(USERS))
        password = USERS[username]
        headers = make_headers(client_id)
        if random.random() < 0.2:
            login(username, password[:-1], headers)
            time.sleep(random.uniform(2, 5))
        login(username, password, headers)
        time.sleep(random.uniform(2, 15))


def run(kind, how_many, action):
    for i in range(1, how_many + 1):
        action(i)
        print(f"{kind}-{i} finished")
        time.sleep(random.uniform(1, 3))


run("human-normal", 25, normal_human)
run("human-forgetful", 8, forgetful_human)
run("human-repeat", 8, repeat_human)
run("human-office", 3, office_network)

print("Done!")