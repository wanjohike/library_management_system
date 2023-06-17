from datetime import date, timedelta
import tkinter as tk
from tkinter import ttk
from sqlalchemy import create_engine, Column, String, Integer, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# SQLAlchemy setup
engine = create_engine('sqlite:///library.db', echo=True)
Base = declarative_base()

# Define the Book model
class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    isbn = Column(String)
    publication_date = Column(Date)
    borrowed_by = Column(Integer, ForeignKey('patrons.id'))

# Define the Patron model
class Patron(Base):
    __tablename__ = 'patrons'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    contact = Column(String)
    membership_status = Column(Integer)
    borrowed_books = relationship("Book", backref="patron")

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Tkinter setup
window = tk.Tk()
window.title("Library Reports")

# Functions
def generate_available_books_report():
    books = session.query(Book).filter(Book.borrowed_by == None).all()
    generate_report(books, "Available Books")

def generate_borrowed_books_report():
    books = session.query(Book).filter(Book.borrowed_by != None).all()
    generate_report(books, "Borrowed Books")

def generate_fines_report():
    patrons = session.query(Patron).all()
    report_data = []

    for patron in patrons:
        total_fines = 0
        borrowed_books = session.query(Book).filter(Book.borrowed_by == patron.id).all()

        for book in borrowed_books:
            due_date = book.publication_date + timedelta(weeks=2)
            today = date.today()

            if today > due_date:
                days_overdue = (today - due_date).days
                fine_amount = days_overdue * 10
                total_fines += fine_amount

        if total_fines > 0:
            report_data.append((patron.name, total_fines))

    generate_report(report_data, "Fines Report", column1_name="Patron Name", column2_name="Total Fines (KES)")

def generate_report(data, title, column1_name="Title", column2_name="Author"):
    report_window = tk.Toplevel(window)
    report_window.title(title)

    tree = ttk.Treeview(report_window)
    tree["columns"] = (column1_name, column2_name)
    tree.column(column1_name, width=200)
    tree.column(column2_name, width=200)
    tree.heading(column1_name, text=column1_name)
    tree.heading(column2_name, text=column2_name)

    for item in data:
        tree.insert("", tk.END, values=item)

    tree.pack()

# UI
available_books_button = tk.Button(window, text="Available Books Report", command=generate_available_books_report)
available_books_button.pack(pady=10)

borrowed_books_button = tk.Button(window, text="Borrowed Books Report", command=generate_borrowed_books_report)
borrowed_books_button.pack(pady=10)

fines_report_button = tk.Button(window, text="Fines Report", command=generate_fines_report)
fines_report_button.pack(pady=10)

window.mainloop()

