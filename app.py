from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    books_borrowed = db.relationship('Borrow', back_populates='member')

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    available = db.Column(db.Boolean, default=True)
    borrows = db.relationship('Borrow', back_populates='book')

class Borrow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    member = db.relationship('Member', back_populates='books_borrowed')
    book = db.relationship('Book', back_populates='borrows')

@app.route('/')
def index():
    books = Book.query.all()
    return render_template('index.html', books=books)

@app.route('/members')
def members():
    members = Member.query.all()
    return render_template('members.html', members=members)

@app.route('/add_member', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        if Member.query.filter_by(email=email).first():
            flash('Email already exists!')
            return redirect(url_for('add_member'))
        member = Member(name=name, email=email)
        db.session.add(member)
        db.session.commit()
        flash('Member added successfully!')
        return redirect(url_for('members'))
    return render_template('add_member.html')

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        book = Book(title=title, author=author)
        db.session.add(book)
        db.session.commit()
        flash('Book added successfully!')
        return redirect(url_for('index'))
    return render_template('add_book.html')

@app.route('/borrow', methods=['GET', 'POST'])
def borrow():
    members = Member.query.all()
    books = Book.query.filter_by(available=True).all()
    if request.method == 'POST':
        member_id = request.form['member_id']
        book_id = request.form['book_id']
        borrow = Borrow(member_id=member_id, book_id=book_id)
        book = Book.query.get(book_id)
        book.available = False
        db.session.add(borrow)
        db.session.commit()
        flash('Book borrowed successfully!')
        return redirect(url_for('index'))
    return render_template('borrow.html', members=members, books=books)

@app.route('/return/<int:borrow_id>')
def return_book(borrow_id):
    borrow = Borrow.query.get(borrow_id)
    book = Book.query.get(borrow.book_id)
    book.available = True
    db.session.delete(borrow)
    db.session.commit()
    flash('Book returned successfully!')
    return redirect(url_for('index'))

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    books = []
    if query:
        books = Book.query.filter(
            (Book.title.ilike(f'%{query}%')) | (Book.author.ilike(f'%{query}%'))
        ).all()
    return render_template('search_results.html', books=books, query=query)

@app.route('/member_history/<int:member_id>')
def member_history(member_id):
    member = Member.query.get_or_404(member_id)
    borrows = Borrow.query.filter_by(member_id=member_id).all()
    return render_template('member_history.html', member=member, borrows=borrows)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
