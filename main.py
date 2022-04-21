from flask import Flask
import os


app = Flask(__name__)


def main():
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, host='0.0.0.0')