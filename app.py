from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from common import *
import cli


def create_app():
    app = Flask(__name__)
    Bootstrap(app)

    return app

app = create_app()

@app.route("/")
def home():
    # cli.main()
    euro_data = process_json_data(download_json_data(PAGE_EURO))
    referendum_data = process_json_data(download_json_data(PAGE_REFERENDUM))
    difference_data = euro_data - referendum_data

    return render_template("index.html", refresh_seconds=60,\
        euro_data=euro_data, \
        difference_data=difference_data, referendum_data=referendum_data, \
        url_euro=PAGE_EURO, url_referendum=PAGE_REFERENDUM)

if __name__ == "__main__":
    app.run(debug=True)
