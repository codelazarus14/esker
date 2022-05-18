# Taken from online version on Repl.it - needed to keep the session active
# ...so probably unnecessary for a locally-run bot
from flask import Flask
from threading import Thread

app = Flask('')


@app.route('/')
def home():
    return "I'm alive"


def run():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()
