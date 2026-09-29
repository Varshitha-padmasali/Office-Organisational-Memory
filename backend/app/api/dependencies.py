from collections.abc import Generator

from app.db.database import get_db


def get_database() -> Generator:
    yield from get_db()