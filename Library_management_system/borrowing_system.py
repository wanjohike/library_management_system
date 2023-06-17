import tkinter as tk
from tkinter import messagebox
from sqlalchemy import create_engine, Column, String, Integer, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import date, timedelta

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
window.title("Library Management System")

# Functions
def clear_entries():
    book_id_entry.delete(0, tk.END)
    patron_id_entry.delete(0, tk.END)

def check_out_book():
    book_id = book_id_entry.get()
    patron_id = patron_id_entry.get()
    
    if book_id and patron_id:
        book = session.query(Book).filter(Book.id == book_id).first()
        patron = session.query(Patron).filter(Patron.id == patron_id).first()
        
        if book and patron:
            if book.borrowed_by:
                messagebox.showerror("Error", "Book is already checked out.")
            else:
                book.borrowed_by = patron.id
                session.commit()
                messagebox.showinfo("Success", "Book checked out successfully.")
                clear_entries()
        else:
            messagebox.showerror("Error", "Invalid book or patron ID.")
    else:
        messagebox.showerror("Error", "Please fill in all the fields.")

def check_in_book():
    book_id = book_id_entry.get()
    
    if book_id:
        book = session.query(Book).filter(Book.id == book_id).first()
        
        if book:
            if book.borrowed_by:
                book.borrowed_by = None
                session.commit()
                calculate_fine(book)
                messagebox.showinfo("Success", "Book checked in successfully.")
                clear_entries()
            else:
                messagebox.showerror("Error", "Book is already checked in.")
        else:
            messagebox.showerror("Error", "Invalid book ID.")
    else:
        messagebox.showerror("Error", "Please fill in all the fields.")

def calculate_fine(book):
    due_date = book.publication_date + timedelta(weeks=2)
    today = date.today()
    
    if today > due_date:
        days_overdue = (today - due_date).days
        fine_amount = days_overdue * 10
        
        patron = session.query(Patron).filter(Patron.id == book.borrowed_by).first()
        patron.contact += f"\nFine: {fine_amount} KES"
        
        session.commit()
        messagebox.showinfo("Fine", f"A fine of {fine_amount} KES has been added to the patron's account.")
        notify_patron(patron, book)
    else:
        messagebox.showinfo("No Fine", "No fine is due for this book.")

def notify_patron(patron, book):
    messagebox.showinfo("Notification", f"Dear {patron.name},\n\nThis is a reminder that the book '{book.title}' is overdue. Please return it as soon as possible to avoid further fines.\n\nThank you!")

# UI
book_id_label = tk.Label(window, text="Book ID:")
book_id_label.grid(row=0, column=0, sticky=tk.E)

book_id_entry = tk.Entry(window)
book_id_entry.grid(row=0, column=1)

patron_id_label = tk.Label(window, text="Patron ID:")
patron_id_label.grid(row=1, column=0, sticky=tk.E)

patron_id_entry = tk.Entry(window)
patron_id_entry.grid(row=1, column=1)

check_out_button = tk.Button(window, text="Check Out", command=check_out_book)
check_out_button.grid(row=2, column=0, pady=10)

check_in_button = tk.Button(window, text="Check In", command=check_in_book)
check_in_button.grid(row=2, column=1, pady=10)

window.mainloop()

