from sqlalchemy import Column, Integer, String, Text, Enum
from datetime import datetime
from database import Base
import enum


class DifficultyLevel(str, enum.Enum):
    easy = "легкая"
    medium = "средняя"
    hard = "сложная"


class Recipe(Base):
    __tablename__ = "recipe"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True, default=["название"])
    ingredients = Column(Text, nullable=False)
    instructions = Column(Text, nullable=False)
    cooking_time = Column(Integer, nullable=False)
    difficulty = Column(Enum(DifficultyLevel), nullable=False)
    cuisine = Column(String(100), nullable=False, index=True)
    tags = Column(String, default=[])  # ['вегетарианский', 'десерт', 'здоровый', 'любая иная важная пометка']
    author = Column(String(100), default="Анонимный автор рецепта")
    embedding = Column(Text, nullable=True)
    created_at = Column(Text, default=lambda: datetime.now().isoformat())
    updated_at = Column(Text, default=lambda: datetime.now().isoformat())

    def __repr__(self):
        return f"<Recipe {self.title}>"

