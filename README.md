# Library

## Tech stack

- FastAPI for API serving
- Pydantic for schema validation
- SQLite db for data storage
- SQLModel/SQLAlchemy as orm and db access
- PyTest for unit testing

## Usage

- Clone the repository `git clone https://github.com/domeniconappo/books_exercise`
- Install UV `curl -LsSf https://astral.sh/uv/install.sh | sh`
- cd `books`
- Build the environment with `make build`
- Copy the env file `cp .env.example .env`
- Start the app in a terminal with `make run`
- Find the open api docs UI at `http://localhost:8000/docs`
- API root `http://localhost:8000/api/v1/books`

You can run tests with `make test`

## API endpoints

Base path: `/api/v1/books`

### Create a book
- `POST /`
- Adds a new book to the library.
- Returns the created book.

### List books
- `GET /`
- Returns all books grouped by genre.
- Includes a total count across all genres.

### Get a single book
- `GET /{book_id}`
- Returns one book by its ID.

### Delete a book
- `DELETE /{book_id}`
- Deletes a book by ID.
- If the book is the last one in its genre, deletion is prevented.

### Bulk update books
- `PATCH /`
- Updates multiple books in one request.
- Only existing books are updated; missing IDs are skipped.

### Search books
- `POST /search`
- Searches books by filters such as title and author.
- Supports pagination with page and page size.
