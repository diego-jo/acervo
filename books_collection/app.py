from fastapi import FastAPI
from fastapi.responses import JSONResponse

from books_collection.account import router as account
from books_collection.auth import router as auth
from books_collection.book import router as book
from books_collection.common.exception.exception_handler import (
    exception_handlers,
)
from books_collection.novelist import router as novelist

app = FastAPI(exception_handlers=exception_handlers)

app.include_router(account.router)
app.include_router(auth.router)
app.include_router(book.router)
app.include_router(novelist.router)


@app.get('/health')
def healch_check():
    return JSONResponse(content={'status': 'Up'})
