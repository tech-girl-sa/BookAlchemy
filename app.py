import json
import os
from datetime import datetime
import requests
from dotenv import load_dotenv

from data_models import db, Author, Book
from flask import Flask, request, render_template, redirect, url_for



load_dotenv()

# Now you can access your environment variables using os.environ
rapid_api_key = os.getenv('RAPID-API-KEY')




basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'data', 'library.sqlite')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
db.init_app(app)



@app.route("/",  methods=["GET"])
def home():
    success_message = request.args.get('success_message')
    sort = request.args.get("sort")
    search = request.args.get("search")
    books = db.session.query(Book)
    if search:
        books = books.filter(Book.title.like(f"%{search}%"))
    if sort == "title":
        books = books.order_by(Book.title)
    if sort == "author":
        books = books.join(Author).order_by(Author.name)
    return render_template("home.html", books=books.all(), success_message=success_message,book_rating=2)


@app.route('/add_author', methods=["GET", "POST"])
def add_author():
    if request.method == "GET":
        success_message = request.args.get('success_message')
        return render_template("add_author.html", success_message=success_message)
    else:
        data = dict(request.form)
        try:
            data["birth_date"] = datetime.strptime(data["birth_date"], "%Y-%m-%d").date()
        except ValueError:
            data["birth_date"] = None
        try:
            data["death_date"] = datetime.strptime(data["death_date"], "%Y-%m-%d").date()
        except ValueError:
            data["death_date"] = None

        author=Author(**data)
        db.session.add(author)
        db.session.commit()
        success_message = "Author added successfully."
        return redirect(url_for('add_author', success_message=success_message))


@app.route('/add_book', methods=["GET", "POST"])
def add_book():
    if request.method == "GET":
        authors = db.session.query(Author).all()
        success_message = request.args.get('success_message')
        return render_template("add_book.html", success_message=success_message, authors=authors)
    else:
        data = dict(request.form)
        book =Book(**data)
        db.session.add(book)
        db.session.commit()
        success_message="Book added successfully."
        return redirect(url_for('home', success_message=success_message))


@app.route("/book/<int:book_id>/delete", methods=["post"])
def delete_book(book_id):
    db.session.query(Book) \
        .filter(Book.id == book_id) \
        .delete()
    db.session.commit()
    success_message = "Book deleted successfully."
    return redirect(url_for('home', success_message=success_message))

@app.route("/book/<int:book_id>/details", methods=["get"])
def book_details(book_id):
    book=db.session.query(Book) \
        .filter(Book.id == book_id) \
        .one()
    empty_star="☆"
    star="★"
    book_rating = f"{book.rating*star}{(10-book.rating)*empty_star}"
    return render_template("book_details.html", book=book, book_rating=book_rating)

@app.route("/book/<int:book_id>/rate", methods=["post"])
def rate_book(book_id):
    book=db.session.query(Book) \
        .filter(Book.id == book_id) \
        .one()
    rating= request.form.get("rating")
    book.rating = rating
    db.session.commit()
    empty_star="☆"
    star="★"
    book_rating = f"{book.rating*star}{(10-book.rating)*empty_star}"
    return render_template("book_details.html", book=book, book_rating=book_rating)


@app.route("/book_recommendation",  methods=["GET"])
def book_recommendation():
    preferences = request.args.get("preferences")
    books = db.session.query(Book).all()
    rapid_api_url = "https://chatgpt-42.p.rapidapi.com/chatgpt"
    books_list=[(book.title, book.rating) for book in books]
    content = f"""
    those are list of books in the database with their ratings {books_list}  rating 0 means the rating was not
    entered yet what book do you recommend to read and why. 
    please provide the response in the following format: book_name // justification
    """
    if preferences:
        content += f"those are the reader preferences: {preferences} please prioritize those preferences over ratings"
    headers = {
        'content-type': 'application/json',
        'x-rapidapi-host': 'chatgpt-42.p.rapidapi.com' ,
        'x-rapidapi-key': rapid_api_key
         }
    data = {
        "messages": [{"role": "user", "content": content}],
        "web_access": False
    }
    response = requests.post(rapid_api_url, data= json.dumps(data), headers=headers)
    error = False
    if response.ok:
        title, justification = response.json().get("result", "//").split("//")
    else:
        error = True
        title, justification = response.status_code, response.json().get("message",
                                                                         "There was an issue fetching data from API")
    return render_template("book_recommendation.html",
                           title=title, justification=justification, error=error)

if __name__ == '__main__':

    app.run(host="0.0.0.0", port=5000, debug=True)