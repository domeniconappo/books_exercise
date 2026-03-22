import pytest
from httpx import AsyncClient

from app.schemas import RESTRICTED_GENRES

API = "/api/v1/books/"

BOOK_PAYLOAD = {
    "title": "My Book",
    "publication_year": 2006,
    "author": "Domenico Nappo",
    "genre": "Fantasy",
}


@pytest.mark.asyncio
class TestBooks:
    async def test_create_success(self, client: AsyncClient) -> None:
        resp = await client.post(API, json=BOOK_PAYLOAD)
        assert resp.status_code == 201
        body = resp.json()
        assert "id" in body
        assert body["title"] == "My Book"
        assert body["publication_year"] == 2006
        assert body["author"] == "Domenico Nappo"
        assert body["genre"] == "Fantasy"

    async def test_create_fail(self, client: AsyncClient) -> None:
        BOOK_PAYLOAD["genre"] = "Horror"
        resp = await client.post(API, json=BOOK_PAYLOAD)
        assert resp.status_code == 422
        body = resp.json()
        assert body["detail"][0]["msg"] == "Value error, Genre 'Horror' is not allowed."

    async def test_list(self, client: AsyncClient, populate: None) -> None:
        resp = await client.get(API)
        assert resp.status_code == 200
        body = resp.json()
        assert body["items"]
        assert body["total"] == 10
        restricted_books = [
            book
            for i in body["items"]
            for book in i["books"]
            if i["genre"] in RESTRICTED_GENRES
        ]
        assert all(b["title"] == "**** MASKED ****" for b in restricted_books)

    async def test_delete(self, client: AsyncClient, populate: None) -> None:
        resp = await client.delete(f"{API}1")
        assert resp.status_code == 204
        resp = await client.get(f"{API}1")
        assert resp.status_code == 404
        resp = await client.delete(f"{API}6")
        assert resp.status_code == 409
        body = resp.json()
        assert body == {"detail": "Cannot delete the last book in genre 'Mystery'."}

    async def test_bulk_update(self, client: AsyncClient, populate: None) -> None:
        payload = [{"id": 1, "title": "New Title"}, {"id": 5, "author": "Anonymous"}]
        resp = await client.patch(API, json=payload)
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["updated"]) == 2
        assert body["updated"][0] == {
            "author": "F. Scott",
            "genre": "Fiction",
            "id": 1,
            "publication_year": 1925,
            "title": "New Title",  # updated
        }
        assert body["updated"][1] == {
            "author": "Anonymous",  # updated
            "genre": "18+",
            "id": 5,
            "publication_year": 2011,
            "title": "Fifty Shades of Grey",
        }

    async def test_search(self, client: AsyncClient, populate: None) -> None:
        filters = {"title": "great"}
        resp = await client.post(f"{API}search", json=filters)
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["items"]) == body["total"] == 1
        assert body["items"][0]["title"] == "The Great Gatsby"
        filters = {"author": "scott"}
        resp = await client.post(f"{API}search", json=filters)
        body = resp.json()
        assert len(body["items"]) == body["total"] == 1
        assert body["items"][0]["title"] == "The Great Gatsby"
        filters = {"title": "shades"}
        resp = await client.post(f"{API}search", json=filters)
        body = resp.json()
        assert len(body["items"]) == body["total"] == 0
