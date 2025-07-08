from fastapi import FastAPI

from books_collection.account import router as account
from books_collection.auth import router as auth
from books_collection.book import router as book
from books_collection.novelist import router as novelist

app = FastAPI()

app.include_router(account.router)
app.include_router(auth.router)
app.include_router(book.router)
app.include_router(novelist.router)
