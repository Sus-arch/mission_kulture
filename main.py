from flask import Flask, render_template
from data.users import User
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = 'NJwadok12LMKF3KMlmcd232v_key'


@app.route('/')
def main_page():
    pass


def main():
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, host='0.0.0.0')