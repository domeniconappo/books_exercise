from pydantic import Field, field_validator
from sqlmodel import SQLModel

from app.models import Book

BLOCKED_GENRES = ("Horror",)
RESTRICTED_GENRES = ("18+",)


class BookCreate(SQLModel):
    title: str
    author: str
    genre: str
    publication_year: int

    @field_validator("genre")
    @classmethod
    def allowed_genre(cls, v: str) -> str:
        if v in BLOCKED_GENRES:
            raise ValueError(f"Genre '{v}' is not allowed.")
        return v


class BookResponse(SQLModel):
    id: int
    title: str
    publication_year: int
    author: str
    genre: str

    @classmethod
    def from_book(cls, book: Book) -> "BookResponse":
        return cls(
            id=book.id,
            title=book.title,
            publication_year=book.publication_year,
            author=book.author,
            genre=book.genre,
        )


class BooksByGenreList(SQLModel):
    books: list[BookResponse]
    genre: str
    count: int


class BookListResponse(SQLModel):
    items: list[BooksByGenreList]
    total: int


class BookBulkUpdateItem(SQLModel):
    id: int
    title: str | None = None
    author: str | None = None
    genre: str | None = None
    publication_year: int | None = None


class BookBulkUpdateResponse(SQLModel):
    updated: list["BookResponse"]


class BookSearchFilters(SQLModel):
    title: str | None = None
    author: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class BookSearchResponse(SQLModel):
    items: list[Book]
    total: int
    page: int
    page_size: int
    pages: int
