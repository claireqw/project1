import os

from flask import Flask, session, render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", display=False)


@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/submit", methods=["POST"])
def submit():
    username = request.form.get("username")
    password = request.form.get("password")
    if username == "" or password == "":
        return render_template("signup.html", display=True, message="Please fill out both fields")
    account = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
    if account is None:
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
            {"username": username, "password": password})
        db.commit()
        return render_template("index.html", display=True, message="Account created")
    return render_template("signup.html", display=True, message="Username taken; please pick another username")

@app.route("/search", methods=["POST", "GET"])
def search():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        account = db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username": username, "password": password}).fetchone()
        if account is None:
            return render_template("index.html", display=True, message="Log in failed")
        session["user_id"] = account.id
        return render_template("search.html")
    else:
        if session["user_id"] is None:
            return render_template("index.html", display=True, message="Please log in to access this page")
        return render_template("search.html")

@app.route("/search/results", methods=["POST"])
def results():
    category = request.form.get("category")
    if category is None:
        return render_template("status.html", headline="Search failed", message="Please select search type (by title, author, or ISBN number)")
    keyword = request.form.get("keyword")
    if keyword == "":
        return render_template("status.html", headline="Search failed", message="Please enter the keyword you want to search")
    command = "SELECT * FROM books WHERE " + category + " LIKE \'%" + keyword  + "%\'"
    books = db.execute(command).fetchall()
    # print(f"cat {category}  key {keyword}")
    # print(books)
    return render_template("search.html", books=books, display=True)

@app.route("/logout")
def logout():
    session["user_id"] = None
    return render_template("index.html", display=True, message="Logged out")


@app.route("/book/<int:book_id>")
def book(book_id):
    if session["user_id"] is None:
        return render_template("index.html", display=True, message="Please log in to access this page")
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    reviews = db.execute("SELECT * FROM reviews WHERE book_id = :id", {"id": book_id}).fetchall()
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "Sf34sMQk988J7HsUiEYg", "isbns": book.isbn})
    if res.status_code != 200:
        return render_template("book.html", book=book, reviews=reviews)
    data = res.json()
    return render_template("book.html", book=book, reviews=reviews, data=data)

@app.route("/review/<int:book_id>", methods=["POST"])
def review(book_id):
    if session["user_id"] is None:
        return render_template("index.html", display=True, message="Please log in to access this page")
    review = db.execute("SELECT * FROM reviews WHERE book_id = :book_id AND user_id = :user_id", {"book_id": book_id, "user_id": session["user_id"]}).fetchone()
    if review is None:
        rating = request.form.get("rating")
        content = request.form.get("content")
        if rating == "":
            return render_template("status.html", headline="Unsuccesful", message="Please select a rating for the book.")
        db.execute("INSERT INTO reviews (rating, content, book_id, user_id) VALUES (:rating, :content, :book_id, :user_id)",
            {"rating": rating, "content": content, "book_id": book_id, "user_id": session["user_id"]})
        db.commit()
        return render_template("status.html", headline="Success", message="Review submitted")
    return render_template("status.html", headline="Unsuccesful", message="You have already submitted a review for this book.")

@app.route("/api/<string:isbn>")
def api(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if book is None:
        return jsonify({"error: no book with that isbn number"}), 422
    print(book)
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "Sf34sMQk988J7HsUiEYg", "isbns": book.isbn})
    data = res.json()
    return jsonify({
        "title": book.title,
        "author": book.author,
        "year": book.author,
        "isbn": book.isbn,
        "review_count": data["books"][0]["work_ratings_count"],
        "average_score": data["books"][0]["average_rating"]
    })
