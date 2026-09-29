"""
Declarative base for all ORM models.

Every model in app/models/ inherits from `Base`. Keeping this in its own
module (rather than in database.py) avoids circular imports: models need
to import `Base`, and `database.py` will eventually need to import models
for Alembic autogeneration.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
