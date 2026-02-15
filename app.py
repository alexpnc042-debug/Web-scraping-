from flask import Flask, render_template_string, send_file, redirect, url_for, session
import requests
from bs4 import BeautifulSoup
import pandas as pd
import io

app = Flask(__name__)
app.secret_key = "demo_secret"

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Scraper Dashboard</title>

<style>

body {
    background: linear-gradient(135deg, #0f172a, #020617);
    font-family: Arial, sans-serif;
    text-align: center;
    margin: 0;
    padding: 20px;
}

h1 {
    color: #22c55e;
    text-shadow: 0 0 8px rgba(34,197,94,0.6);
}

button {
    background: transparent;
    color: #22c55e;
    border: 2px solid #22c55e;
    padding: 12px 18px;
    font-size: 15px;
    cursor: pointer;
    margin: 10px;
    border-radius: 12px;
}

button:hover {
    background: #22c55e;
    color: black;
}

.table-container {
    background: white;
    margin: 25px auto;
    padding: 15px;
    width: 95%;
    border-radius: 18px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    overflow-x: auto;
}

table {
    border-collapse: collapse;
    width: 100%;
}

th {
    background: #f3f4f6;
    color: black;
    padding: 10px;
}

td {
    color: black;
    padding: 8px;
}

tr:nth-child(even) {
    background: #f9fafb;
}

</style>
</head>

<body>

<h1>⚡ Scraper Dashboard ⚡</h1>

<a href="/scrape"><button>▶ Ejecutar Scraping</button></a>
<a href="/download"><button>⬇ Descargar Excel</button></a>

{% if books %}
<div class="table-container">
<table>
<tr>
<th>Título</th>
<th>Precio</th>
<th>Disponibilidad</th>
</tr>

{% for b in books %}
<tr>
<td>{{b.title}}</td>
<td>{{b.price}}</td>
<td>{{b.availability}}</td>
</tr>
{% endfor %}
</table>
</div>
{% endif %}

</body>
</html>
"""

def run_scraper():

    url = "https://books.toscrape.com/"
    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    books = []

    for book in soup.find_all("article", class_="product_pod"):
        books.append({
            "title": book.h3.a["title"],
            "price": book.find("p", class_="price_color").text.replace("Â", ""),
            "availability": book.find("p", class_="instock availability").text.strip()
        })

    return books


@app.route("/")
def home():
    books = session.pop("books", None)
    return render_template_string(HTML, books=books)


@app.route("/scrape")
def scrape():
    session["books"] = run_scraper()
    return redirect(url_for("home"))


@app.route("/download")
def download():

    books = run_scraper()
    df = pd.DataFrame(books)

    output = io.BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    return send_file(output,
                     download_name="scraping_demo.xlsx",
                     as_attachment=True)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)