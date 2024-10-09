pip install flask
from flask import Flask, request, redirect, render_template, url_for
import string
import random
import sqlite3

app = Flask(__name__)

# Database setup
DATABASE = 'url_shortener.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS urls
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         original_url TEXT NOT NULL,
                         short_url TEXT NOT NULL UNIQUE);''')

# Function to shorten the URL
def generate_short_url():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))

# Function to store a new URL mapping in the database
def store_url_mapping(original_url, short_url):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('INSERT INTO urls (original_url, short_url) VALUES (?, ?)', (original_url, short_url))
        conn.commit()

# Function to retrieve the original URL based on the shortened URL
def get_original_url(short_url):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute('SELECT original_url FROM urls WHERE short_url = ?', (short_url,))
        row = cursor.fetchone()
        return row[0] if row else None

# Route for the home page with form to shorten URL
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['original_url']
        short_url = generate_short_url()

        # Store the mapping between original and short URL
        store_url_mapping(original_url, short_url)

        # Provide the short URL to the user
        short_url_link = request.host_url + short_url
        return render_template('index.html', short_url=short_url_link)

    return render_template('index.html')

# Route to redirect short URL to the original URL
@app.route('/<short_url>')
def redirect_to_original(short_url):
    original_url = get_original_url(short_url)
    if original_url:
        return redirect(original_url)
    else:
        return 'URL not found', 404

# Initialize the database when the app starts
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
