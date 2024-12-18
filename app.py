from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
import json

app = Flask(__name__)

BOOKS_FILE = 'books.json'
USERS_FILE = 'users.json'

# Load books and users from JSON files
def load_books():
    try:
        with open(BOOKS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def load_users():
    try:
        with open(USERS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Save books and users to JSON files
def save_books(books):
    with open(BOOKS_FILE, 'w') as file:
        json.dump(books, file, indent=4)

def save_users(users):
    with open(USERS_FILE, 'w') as file:
        json.dump(users, file, indent=4)

# Routes for the Flask application
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_book', methods=['POST'])
def add_book():
    title = request.form['title']
    author = request.form['author']
    isbn = request.form['isbn']

    books = load_books()
    if any(book['isbn'] == isbn for book in books):
        return 'Book already exists!', 400

    book = {'isbn': isbn, 'title': title, 'author': author, 'available': True}
    books.append(book)
    save_books(books)

    return redirect(url_for('index'))

@app.route('/remove_book', methods=['POST'])
def remove_book():
    isbn = request.form['isbn']
    books = load_books()
    books = [book for book in books if book['isbn'] != isbn]
    save_books(books)
    
    return redirect(url_for('index'))

@app.route('/search_books', methods=['POST'])
def search_books():
    search_term = request.form['search_term'].lower()
    books = load_books()

    found_books = [book for book in books if (search_term in book['title'].lower()) or 
                   (search_term in book['author'].lower()) or 
                   (search_term in book['isbn'])]

    return render_template('index.html', found_books=found_books)

@app.route('/borrow_book', methods=['POST'])
def borrow_book():
    user_id = request.form['user_id']
    isbn = request.form['isbn']

    users = load_users()
    books = load_books()

    user = next((u for u in users if u['user_id'] == user_id), None)
    book = next((b for b in books if b['isbn'] == isbn), None)

    if not user or not book:
        return 'User or book not found!', 400

    if not book['available']:
        return 'Book is currently unavailable!', 400

    book['available'] = False
    due_date = datetime.now().strftime("%Y-%m-%d")
    user['borrowed_books'].append({'isbn': isbn, 'due_date': due_date})
    
    save_books(books)
    save_users(users)

    return redirect(url_for('index'))

@app.route('/return_book', methods=['POST'])
def return_book():
    user_id = request.form['user_id']
    isbn = request.form['isbn']

    users = load_users()
    books = load_books()

    user = next((u for u in users if u['user_id'] == user_id), None)
    if not user:
        return 'User not found!', 400

    borrowed_book = next((b for b in user['borrowed_books'] if b['isbn'] == isbn), None)
    if not borrowed_book:
        return 'This book was not borrowed by the user.', 400

    book = next((b for b in books if b['isbn'] == isbn), None)
    book['available'] = True
    user['borrowed_books'] = [b for b in user['borrowed_books'] if b['isbn'] != isbn]

    save_books(books)
    save_users(users)

    return redirect(url_for('index'))

@app.route('/view_users')
def view_users():
    users = load_users()
    return render_template('index.html', users=users)

if __name__ == '__main__':
    app.run(debug=True)
