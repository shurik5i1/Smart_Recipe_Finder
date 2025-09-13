from pydantic import BaseModel, Field, validator
from typing import List, Optional
from enum import Enum
from datetime import datetime


class DifficultyLevel(str, Enum):
    easy = "легкая"
    medium = "средняя"
    hard = "сложная"


class RecipeBase(BaseModel):
    title: str = Field(min_length=1, max_length=255, examples=["Спагетти Итальяно"])
    ingredients: List[str] = Field(..., examples=["спагетти 100гр", ",бекон 50г", "яйцо 1шт", "пармезан 30гр"])
    instructions: str = Field(examples=["Сварите спагетти ..."])
    cooking_time_minutes: int = Field(gt=0, examples=[15])
    difficulty: DifficultyLevel = Field(examples=[DifficultyLevel.medium])
    cuisine: str = Field(min_length=1, max_length=100, examples=["итальянская"])
    tags: Optional[List[str]] = Field(default=[], examples=["итальянская", "паста", "быстро"])
    author: Optional[str] = Field(default="Анонимный автор рецепта", max_length=100)


class RecipeCreate(RecipeBase):
    pass


class RecipeUpdate(RecipeBase):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    ingredients: Optional[List[str]] = None
    instructions: Optional[str] = None
    cooking_time: Optional[int] = Field(None, gt=0)
    difficulty: Optional[DifficultyLevel] = None
    cuisine: Optional[str] = Field(None, min_length=1, max_length=100)
    tags: Optional[List[str]] = None
    author: Optional[str] = Field(None, max_digits=100)


class Recipe(RecipeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IngredientFilter(BaseModel):
    include: Optional[List[str]] = Field(None, description="Список ингредиентов, которые ДОЛЖНЫ быть в рецепте")
    exclude: Optional[List[str]] = Field(None, description="Список ингредиентов, которых НЕ ДОЛЖНО быть в рецепте")

    class Config:
        json_schema_extra = {
            "example": {
                "include": ["свинина", "майонез"],
                "exclude": ["чеснок"]
            }
        }


class SearchResult(BaseModel):
    query: str
    results: List[Recipe]
