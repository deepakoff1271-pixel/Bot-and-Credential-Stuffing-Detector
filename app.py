import json
from datetime import datetime
from flask import Flask, request, render_template

app = Flask(__name__)

# Our pretend customers: username and password
USERS = {
    "alice": "alice123",
    "bob": "bobpass",
    "carol": "carol2024",
}


def write_in_notebook(username, success):
    note = {
        "time": datetime.now().isoformat(),
        "visitor": request.headers.get("X-Client-ID", "unknown"),
        "username_tried": username,
        "got_in": success,
        "browser": request.headers.get("User-Agent", ""),
        "language": request.headers.get("Accept-Language", ""),
    }
    with open("logs/notebook.txt", "a") as f:
        f.write(json.dumps(note) + "\n")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username", "")
    password = request.form.get("password", "")

    if USERS.get(username) == password:
        write_in_notebook(username, True)
        return render_template("welcome.html")

    write_in_notebook(username, False)
    return render_template("login.html", error="Wrong username or password"), 401


app.run(port=5000)