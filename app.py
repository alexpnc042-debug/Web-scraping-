from flask import Flask, render_template_string, request, send_file, redirect, url_for
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

app = Flask(__name__)

DATA_FILE = "books.xlsx"

# ------------------------
# SCRAPER
# ------------------------
def scrape_books():
    url = "https://books.toscrape.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")

    books = []

    for book in soup.select(".product_pod"):
        title = book.h3.a["title"]
        price = book.select_one(".price_color").text
        availability = book.select_one(".availability").text.strip()

        books.append([title, price, availability])

    df = pd.DataFrame(books, columns=["Title", "Price", "Availability"])
    df.to_excel(DATA_FILE, index=False)

    return df


# ------------------------
# HTML TEMPLATE
# ------------------------
HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Scraper Demo</title>
<style>
body {
    background: #0f172a;
    color: white;
    font-family: Arial;
    text-align: center;
}

button {
    padding: 12px 20px;
    border-radius: 10px;
    border: none;
    cursor: pointer;
    margin: 10px;
    font-size: 16px;
}

.scrap {
    background: #22c55e;
    color: black;
}

.download {
    background: #38bdf8;
    color: black;
}

.table-box {
    background: white;
    color: black;
    border-radius: 20px;
    padding: 20px;
    margin: 20px auto;
    width: 90%;
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th, td {
    padding: 10px;
    border-bottom: 1px solid #ddd;
}
</style>
</head>

<body>

<h1>Web Scraping Demo</h1>

<form method="post">
<button class="scrap">Scrapear</button>
</form>

{% if table %}
<a href="/download">
<button class="download">Descargar Excel</button>
</a>

<div class="table-box">
{{ table|safe }}
</div>
{% endif %}

</body>
</html>
"""


# ------------------------
# ROUTES
# ------------------------
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        df = scrape_books()
        table = df.to_html(classes="table", index=False)
        return render_template_string(HTML, table=table)

    return render_template_string(HTML, table=None)


@app.route("/download")
def download():
    if os.path.exists(DATA_FILE):
        return send_file(DATA_FILE, as_attachment=True)
    return redirect(url_for("home"))


# ------------------------
# SERVER (Render compatible)
# ------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
