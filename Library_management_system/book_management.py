import tkinter as tk
from tkinter import messagebox
from sqlalchemy import create_engine, Column, String, Integer, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLAlchemy setup
engine = create_engine('sqlite:///books.db', echo=True)
Base = declarative_base()

# Define the Book model
class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    isbn = Column(String)
    publication_date = Column(Date)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Tkinter setup
window = tk.Tk()
window.title("Book Management System")

# Functions
def clear_entries():
    title_entry.delete(0, tk.END)
    author_entry.delete(0, tk.END)
    isbn_entry.delete(0, tk.END)
    pub_date_entry.delete(0, tk.END)

def add_book():
    title = title_entry.get()
    author = author_entry.get()
    isbn = isbn_entry.get()
    pub_date = pub_date_entry.get()
    
    if title and author and isbn and pub_date:
        book = Book(title=title, author=author, isbn=isbn, publication_date=pub_date)
        session.add(book)
        session.commit()
        messagebox.showinfo("Success", "Book added successfully.")
        clear_entries()
    else:
        messagebox.showerror("Error", "Please fill in all the fields.")

def search_books():
    query = search_entry.get()
    books = session.query(Book).filter(Book.title.like(f"%{query}%") |
                                       Book.author.like(f"%{query}%") |
                                       Book.isbn.like(f"%{query}%") |
                                       Book.publication_date.like(f"%{query}%")).all()
    
    if books:
        search_result.delete(0, tk.END)
        for book in books:
            search_result.insert(tk.END, f"{book.title} by {book.author} (ISBN: {book.isbn})")
    else:
        messagebox.showinfo("Not Found", "No books found.")

def delete_book():
    selected_book = search_result.get(tk.ACTIVE)
    
    if selected_book:
        book_title = selected_book.split("by")[0].strip()
        book = session.query(Book).filter(Book.title == book_title).first()
        
        if book:
            confirmation = messagebox.askyesno("Confirm", f"Do you want to delete {book.title}?")
            
            if confirmation:
                session.delete(book)
                session.commit()
                search_books()
        else:
            messagebox.showinfo("Not Found", "Book not found.")
    else:
        messagebox.showinfo("No Selection", "Please select a book to delete.")

# tkinter user interface
title_label = tk.Label(window, text="Title:")
title_label.grid(row=0, column=0, sticky=tk.E)

title_entry = tk.Entry(window)
title_entry.grid(row=0, column=1)

author_label = tk.Label(window, text="Author:")
author_label.grid(row=1, column=0, sticky=tk.E)

author_entry = tk.Entry(window)
author_entry.grid(row=1, column=1)

isbn_label = tk.Label(window, text="ISBN:")
isbn_label.grid(row=2, column=0, sticky=tk.E)

isbn_entry = tk.Entry(window)
isbn_entry.grid(row=2, column=1)

pub_date_label = tk.Label(window, text="Publication Date:")
pub_date_label.grid(row=3, column=0, sticky=tk.E)

pub_date_entry = tk.Entry(window)
pub_date_entry.grid(row=3, column=1)

add_button = tk.Button(window, text="Add Book", command=add_book)
add_button.grid(row=4, column=0, columnspan=2, pady=10)

search_label = tk.Label(window, text="Search:")
search_label.grid(row=5, column=0, sticky=tk.E)

search_entry = tk.Entry(window)
search_entry.grid(row=5, column=1)

search_button = tk.Button(window, text="Search", command=search_books)
search_button.grid(row=6, column=0, columnspan=2, pady=10)

search_result = tk.Listbox(window)
search_result.grid(row=7, column=0, columnspan=2)

delete_button = tk.Button(window, text="Delete", command=delete_book)
delete_button.grid(row=8, column=0, columnspan=2, pady=10)

window.mainloop()
