from sqlalchemy import Column, Text
from canvas.models import Base, TimestampMixin


class ThesisCategory(Base, TimestampMixin):
    __tablename__ = "thesis_categories"

    name = Column(Text, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    color = Column(Text, nullable=True)
