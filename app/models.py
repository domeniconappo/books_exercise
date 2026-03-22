from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, DateTime, text
from sqlmodel import Field, Relationship, SQLModel


class Book(SQLModel, table=True):
    __tablename__ = "books"
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    title: str = Field(max_length=200, nullable=False, index=True)
    author: str = Field(max_length=200, nullable=False, index=True)
    genre: str = Field(max_length=200, nullable=False, index=True)
    publication_year: int = Field(nullable=False, ge=1)
