from fastapi import HTTPException


class LastInGenre(HTTPException):
    def __init__(self, genre: str):
        super().__init__(
            detail=f"Cannot delete the last book in genre '{genre}'.", status_code=409
        )
