import pytest
from pydantic import ValidationError

from app.schemas import BookCreate


def make_book(**overrides) -> dict:
    return {
        "title": "My Book",
        "publication_year": 2006,
        "author": "Domenico Nappo",
        "genre": "Fantasy",
        **overrides,
    }


class TestBooks:
    def test_create(self):
        book = BookCreate(**make_book())
        assert book.title == "My Book"
        assert book.author == "Domenico Nappo"
        with pytest.raises(ValidationError) as exc:
            BookCreate(**make_book(**{"genre": "Horror"}))
        assert (
            str(exc.value.errors()[0]["msg"])
            == "Value error, Genre 'Horror' is not allowed."
        )
