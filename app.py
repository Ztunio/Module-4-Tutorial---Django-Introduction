from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

app = Flask(__name__)


basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'books.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)



class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    publisher = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<Book {self.book_name}>"



class BookSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Book
        load_instance = True

    id = ma.auto_field()
    book_name = ma.auto_field()
    author = ma.auto_field()
    publisher = ma.auto_field()


book_schema = BookSchema()
books_schema = BookSchema(many=True)




# Create a Book
@app.route("/book", methods=["POST"])
def add_book():
    book_name = request.json.get("book_name")
    author = request.json.get("author")
    publisher = request.json.get("publisher")

    new_book = Book(book_name=book_name, author=author, publisher=publisher)

    db.session.add(new_book)
    db.session.commit()

    return book_schema.jsonify(new_book)


# Get all Books
@app.route("/books", methods=["GET"])
def get_books():
    all_books = Book.query.all()
    result = books_schema.dump(all_books)
    return jsonify(result)


# Get a single Book
@app.route("/book/<int:id>", methods=["GET"])
def get_book(id):
    book = Book.query.get_or_404(id)
    return book_schema.jsonify(book)


# Update a Book
@app.route("/book/<int:id>", methods=["PUT"])
def update_book(id):
    book = Book.query.get_or_404(id)

    book.book_name = request.json.get("book_name", book.book_name)
    book.author = request.json.get("author", book.author)
    book.publisher = request.json.get("publisher", book.publisher)

    db.session.commit()
    return book_schema.jsonify(book)


# Delete a Book
@app.route("/book/<int:id>", methods=["DELETE"])
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted"})


# ----- Init DB & Run -----
if __name__ == "__main__":
    with app.app_context():
        db.create_all()   # creates books.db with Book table if it doesn't exist
    app.run(debug=True)
