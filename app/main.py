from fastapi import FastAPI

import models
import schemas
import crud
import search
from database import engine, get_db
from embeddings import generate_embedding


app = FastAPI(
    title="Smart Recipe Finder"
)


# Эндпоинт для создания нового рецепта
@app.post()
async def create_new_recipe():
    pass


# Эндпоинт для выбора списка рецептов
@app.get("/recipes/")
async def read_recipes():
    pass


# Эндпоинт для выбора рецепта по его ID
@app.get("/recipe/{")
async def read_recipe():
    pass


# Эндпоинт для редактирования существующего рецепта
@app.put()
async def update_existing_recipe():
    pass


# Эндпоинт для удаления рецепта по его ID
@app.delete("/recipe/")
async def delete_existing_recipe():
    pass


# Эндпоинт для поиска рецепта по ингридиентам
@app.get("/search/filter/")
async def search_recipes_by_ingredients():
    pass


# Эндпоинт для поиска рецепта на естественном языке
@app.get("/search/semantic/")
async def search_recipes_by_natural_language():
    pass

