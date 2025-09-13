from sqlalchemy import Column, Integer, String, Text, ARRAY, Enum, Float
from sqlalchemy.dialects.postgresql import ARRAY
from database import Base
import enum


class DifficultyLevel(str, enum.Enum):
    easy = "легкая"
    medium = "средняя"
    hard = "сложная"


class Recipe(Base):
    __tablename__ = "recipe"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    ingredients = Column(ARRAY(Text), nullable=False)
    instructions = Column(Text, nullable=False)
    cooking_times = Column(Integer, nullable=False)
    difficulty = Column(Enum(DifficultyLevel), nullable=False)
    cuisine = Column(String(100), nullable=False, index=True)
    tags = Column(ARRAY(String), default=[])  # ['вегетарианский', 'десерт', 'здоровый', 'любая иная важная пометка']
    author = Column(String(100), default="Анонимный автор рецепта")

    embedding = Column(ARRAY(Float))

