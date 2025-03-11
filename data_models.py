import datetime
from typing import List

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import  ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


db:SQLAlchemy = SQLAlchemy()


class Author(db.Model):
    __tablename__ = 'authors'
    id:Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    name: Mapped[str]
    birth_date: Mapped[datetime.date] = mapped_column(nullable=True)
    death_date: Mapped[datetime.date] = mapped_column(nullable=True)
    books: Mapped[List["Book"]] = relationship(back_populates="author")

    def __repr__(self):
        return f"Author(name={self.name})"

    def __str__(self):
        return f"Author({self.name})"

class Book(db.Model):
    __tablename__ = 'books'
    id :Mapped[int] = mapped_column( autoincrement=True, primary_key=True)
    isbn: Mapped[str] = mapped_column( unique=True)
    title: Mapped[str]
    publication_year: Mapped[int]
    rating : Mapped[int] = mapped_column(default=0)
    author_id :Mapped[int] = mapped_column(ForeignKey('authors.id'))
    author: Mapped["Author"] = relationship(back_populates="books")

    def __repr__(self):
        return f"Book(title={self.title})"

    def __str__(self):
        return f"Book({self.title})"




