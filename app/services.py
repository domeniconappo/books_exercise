import typing as tp
from collections import defaultdict
from math import ceil
from pathlib import Path

from sqlalchemy import func, text
from sqlmodel import SQLModel, select

from .database import DB, engine
from .exceptions import LastInGenre
from .models import Book
from .schemas import (
    RESTRICTED_GENRES,
    BookBulkUpdateItem,
    BookBulkUpdateResponse,
    BookCreate,
    BookSearchFilters,
    BookSearchResponse,
)


async def populate() -> None:
    dataset = Path("./dataset.sql")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        if not dataset.exists():
            return
        sql = text(dataset.read_text())
        await conn.execute(sql)
        await conn.commit()


async def add_book(db: DB, payload: BookCreate) -> Book:
    book = Book(
        title=payload.title,
        publication_year=payload.publication_year,
        author=payload.author.title(),
        genre=payload.genre.title(),
    )
    db.add(book)
    await db.flush()
    await db.commit()
    await db.refresh(book)
    return book


async def list_books(db: DB) -> dict[str, dict[str, tp.Any]]:
    query = select(Book).order_by(Book.genre)
    res = await db.execute(query)
    books = res.scalars().all()

    out = defaultdict(list)
    for book in books:
        if book.genre in RESTRICTED_GENRES:
            book.title = "**** MASKED ****"
        out[book.genre].append(book)
    return {
        genre: {"genre": genre, "count": len(books), "books": books}
        for genre, books in out.items()
    }


async def delete_book(db: DB, book: Book) -> None:
    stmt = select(func.count(Book.id)).where(Book.genre == book.genre)
    count = await db.scalar(stmt)
    if count == 1:
        # last book for the genre, prevent deletion
        raise LastInGenre(book.genre)
    await db.delete(book)
    await db.commit()


async def update_books(db: DB, payload: list[BookBulkUpdateItem]):
    updated = []
    for item in payload:
        book = await get_book_by_id(db, item.id)
        if not book:
            continue

        patch = item.model_dump(exclude_none=True)
        for field, value in patch.items():
            setattr(book, field, value)

        db.add(book)
        updated.append(book)

    await db.commit()
    for book in updated:
        await db.refresh(book)

    return BookBulkUpdateResponse(updated=updated)


async def get_book_by_id(db: DB, book_id: int) -> Book | None:
    result = await db.execute(select(Book).where(Book.id == book_id))
    return result.scalar_one_or_none()


async def search(db: DB, filters: BookSearchFilters) -> BookSearchResponse:
    query = (
        select(Book)
        .where(Book.genre.notin_(RESTRICTED_GENRES))
        .order_by(Book.publication_year)
    )
    if filters.title:
        # allow substring lookup
        query = query.where(func.lower(Book.title).contains(filters.title.lower()))
    if filters.author:
        # look for exact match
        query = query.where(func.lower(Book.author).contains(filters.author.lower()))
    # --- total count before pagination ---
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar_one()
    # --- pagination ---
    offset = (filters.page - 1) * filters.page_size
    query = query.offset(offset).limit(filters.page_size)
    result = await db.execute(query)
    books = result.scalars().all()
    return BookSearchResponse(
        items=books,
        total=total,
        page=filters.page,
        page_size=filters.page_size,
        pages=ceil(total / filters.page_size) if total else 0,
    )
