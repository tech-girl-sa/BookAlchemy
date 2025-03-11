import os
from datetime import datetime
from datetime import date


from data_models import db, Author, Book
from flask import Flask, request, render_template, redirect, url_for




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
        data["birth_date"] = datetime.strptime(data["birth_date"], "%Y-%m-%d").date()
        data["death_date"] = datetime.strptime(data["death_date"], "%Y-%m-%d").date()
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


if __name__ == '__main__':
    # with app.app_context():
    #     db.create_all()
    #
    # # List of well-known authors with their birth and death dates and books
    # with app.app_context():
    #     authors_books_data = {
    #         "George Orwell": {
    #             "birth_date": date(1903, 6, 25),
    #             "death_date": date(1950, 1, 21),
    #             "books": [
    #                 {"title": "1984", "isbn": "9780451524935", "year": 1949},
    #                 {"title": "Animal Farm", "isbn": "9780451526342", "year": 1945}
    #             ]
    #         },
    #         "Jane Austen": {
    #             "birth_date": date(1775, 12, 16),
    #             "death_date": date(1817, 7, 18),
    #             "books": [
    #                 {"title": "Pride and Prejudice", "isbn": "9780141040349", "year": 1813},
    #                 {"title": "Sense and Sensibility", "isbn": "9780141439672", "year": 1811}
    #             ]
    #         },
    #         "J.K. Rowling": {
    #             "birth_date": date(1965, 7, 31),
    #             "death_date": None,  # J.K. Rowling is still alive
    #             "books": [
    #                 {"title": "Harry Potter and the Sorcerer's Stone", "isbn": "9780590353427", "year": 1997},
    #                 {"title": "Harry Potter and the Chamber of Secrets", "isbn": "9780439064873", "year": 1998}
    #             ]
    #         },
    #         "F. Scott Fitzgerald": {
    #             "birth_date": date(1896, 9, 24),
    #             "death_date": date(1940, 12, 21),
    #             "books": [
    #                 {"title": "The Great Gatsby", "isbn": "9780743273565", "year": 1925},
    #                 {"title": "Tender Is the Night", "isbn": "9780743244532", "year": 1934}
    #             ]
    #         },
    #         "Mark Twain": {
    #             "birth_date": date(1835, 11, 30),
    #             "death_date": date(1910, 4, 21),
    #             "books": [
    #                 {"title": "The Adventures of Tom Sawyer", "isbn": "9780486400778", "year": 1876},
    #                 {"title": "Adventures of Huckleberry Finn", "isbn": "9780142437179", "year": 1884}
    #             ]
    #         },
    #         "Leo Tolstoy": {
    #             "birth_date": date(1828, 9, 9),
    #             "death_date": date(1910, 11, 20),
    #             "books": [
    #                 {"title": "War and Peace", "isbn": "9781853260629", "year": 1869},
    #                 {"title": "Anna Karenina", "isbn": "9781853262715", "year": 1877}
    #             ]
    #         },
    #         "Haruki Murakami": {
    #             "birth_date": date(1949, 1, 12),
    #             "death_date": None,  # Haruki Murakami is still alive
    #             "books": [
    #                 {"title": "Norwegian Wood", "isbn": "9780375704024", "year": 1987},
    #                 {"title": "Kafka on the Shore", "isbn": "9781400079278", "year": 2002}
    #             ]
    #         },
    #         "Gabriel García Márquez": {
    #             "birth_date": date(1927, 3, 6),
    #             "death_date": date(2014, 4, 17),
    #             "books": [
    #                 {"title": "One Hundred Years of Solitude", "isbn": "9780060883287", "year": 1967},
    #                 {"title": "Love in the Time of Cholera", "isbn": "9780307389732", "year": 1985}
    #             ]
    #         },
    #         "Ernest Hemingway": {
    #             "birth_date": date(1899, 7, 21),
    #             "death_date": date(1961, 7, 2),
    #             "books": [
    #                 {"title": "The Old Man and the Sea", "isbn": "9780684801223", "year": 1952},
    #                 {"title": "A Farewell to Arms", "isbn": "9780099908401", "year": 1929}
    #             ]
    #         },
    #         "Oscar Wilde": {
    #             "birth_date": date(1854, 10, 16),
    #             "death_date": date(1900, 11, 30),
    #             "books": [
    #                 {"title": "The Picture of Dorian Gray", "isbn": "9780141441259", "year": 1890},
    #                 {"title": "The Importance of Being Earnest", "isbn": "9780486275479", "year": 1895}
    #             ]
    #         }
    #     }
    #
    #     # Create authors and books
    #     for author_name, author_data in authors_books_data.items():
    #         author = Author(
    #             name=author_name,
    #             birth_date=author_data["birth_date"],
    #             death_date=author_data["death_date"]
    #         )
    #         db.session.add(author)
    #         db.session.commit()  # Commit to get the author ID for referencing in books
    #
    #         for book_data in author_data["books"]:
    #             book = Book(
    #                 title=book_data['title'],
    #                 isbn=book_data['isbn'],
    #                 publication_year=book_data['year'],
    #                 author=author  # Associate the book with the author
    #             )
    #             db.session.add(book)
    #
    #     # Commit all the books to the database
    #     db.session.commit()
    app.run(host="0.0.0.0", port=5000, debug=True)