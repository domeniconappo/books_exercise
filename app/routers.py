import typing as tp

from fastapi import APIRouter, HTTPException
from starlette import status

from . import services as book_service
from .database import DB
from .schemas import (
    BookBulkUpdateItem,
    BookBulkUpdateResponse,
    BookCreate,
    BookListResponse,
    BookResponse,
    BookSearchFilters,
    BookSearchResponse,
)

router = APIRouter(prefix="/books", tags=["Books"])


async def _get_book_or_404(db: DB, book_id: int):
    book = await book_service.get_book_by_id(db, book_id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )
    return book


@router.post("/", response_model=BookResponse, status_code=201)
async def create_book(db: DB, payload: BookCreate) -> tp.Any:
    book = await book_service.add_book(db, payload)
    return book


@router.get("/", response_model=BookListResponse, status_code=200)
async def get_books(db: DB) -> tp.Any:
    books_by_genre = await book_service.list_books(db)
    books = BookListResponse(
        items=books_by_genre.values(),
        total=sum(books_by_genre[genre]["count"] for genre in books_by_genre),
    )
    return books


@router.get("/{book_id}", response_model=BookResponse, status_code=200)
async def get_book(book_id: int, db: DB) -> tp.Any:
    book = await _get_book_or_404(db, book_id)
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    book_id: int,
    db: DB,
) -> None:
    book = await _get_book_or_404(db, book_id)
    await book_service.delete_book(db, book)


@router.patch("/", response_model=BookBulkUpdateResponse)
async def update_books(db: DB, items: list[BookBulkUpdateItem]) -> tp.Any:
    res = await book_service.update_books(db, items)
    return res


@router.post("/search", response_model=BookSearchResponse)
async def search(db: DB, payload: BookSearchFilters) -> tp.Any:
    res = await book_service.search(db, payload)
    return res
