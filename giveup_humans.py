import random
import threading
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


def giveup_human(number):
    """Tries a few wrong passwords, then gives up and leaves."""
    username = random.choice(list(USERS))
    password = USERS[username]
    headers = make_headers(f"human-giveup-{number}")
    guesses = [password[:-1], password + "1", password.upper(), password[1:]]
    random.shuffle(guesses)
    for guess in guesses[: random.randint(1, 3)]:
        login(username, guess, headers)
        time.sleep(random.uniform(3, 8))


def wrongname_human(number):
    """Mistypes the username once or twice, then gets it right."""
    username = random.choice(list(USERS))
    password = USERS[username]
    headers = make_headers(f"human-wrongname-{number}")
    for _ in range(random.randint(1, 2)):
        login(username[:-1], password, headers)
        time.sleep(random.uniform(3, 8))
    login(username, password, headers)


def office_network(number):
    """Several coworkers behind one shared network ID."""
    client_id = f"human-office-{number + 100}"
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
    threads = []
    for i in range(1, how_many + 1):
        t = threading.Thread(target=action, args=(i,))
        t.start()
        threads.append(t)
        time.sleep(random.uniform(0.2, 1.0))
    for t in threads:
        t.join()
    print(f"{kind} group finished")


run("human-giveup", 40, giveup_human)
run("human-wrongname", 15, wrongname_human)
run("human-office", 12, office_network)

print("Done!")
