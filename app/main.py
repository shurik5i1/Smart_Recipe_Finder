from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from starlette.middleware.cors import CORSMiddleware
import models
import schemas
import crud
import search
from database import engine, get_db


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


# Описание API
description = """
Smart Recipe Finder API помогает вам найти идеальный рецепт. 🍳

## Рецепты

Вы можете:
* **Создать новый рецепт** (POST /recipes/)
* **Получить список всех рецептов** (GET /recipes/)
* **Получить один рецепт** (GET /recipes/{recipe_id})
* **Обновить рецепт** (PUT /recipes/{recipe_id})
* **Удалить рецепт** (DELETE /recipes/{recipe_id})

## Поиск

Вы можете искать рецепты двумя способами:
* **Фильтрация по ингредиентам** (GET /search/filter/)
* **Семантический поиск на естественном языке** (GET /search/semantic/)
"""


app = FastAPI(
    title="Smart Recipe Finder",
    description=description,
    version="0.0.1",
    openapi_tags=[
        {
            "name": "Recipes",
            "description": "Операции CRUD с рецептами.",
        },
        {
            "name": "Search",
            "description": "Поиск и фильтрация рецептов.",
        },
        {
            "name": "Health",
            "description": "Проверка работоспособности API.",
        },
    ]
)


# Настройка CORS (разрешить запросы с фронтенда)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # URL вашего фронтенд-приложения
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Event handler: создает таблицы при запуске приложения
@app.on_event("startup")
async def on_startup():
    await create_tables()
    print("Таблицы в БД созданы (если не существовали)")


# Эндпоинт для создания нового рецепта
@app.post("/recipes/", response_model=schemas.Recipe, tags=["Recipes"], status_code=status.HTTP_201_CREATED)
async def create_new_recipe(recipe: schemas.RecipeCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_recipe(db=db, recipe=recipe)


# Эндпоинт для выбора списка рецептов
@app.get("/recipes/", response_model=List[schemas.Recipe], tags=["Recipes"])
async def read_recipes(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    recipes = await crud.get_recipes(db=db, skip=skip, limit=limit)
    return recipes


# Эндпоинт для выбора рецепта по его ID
@app.get("/recipe/{recipe_id}", response_model=schemas.Recipe, tags=["Recipes"])
async def read_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    db_recipe = await crud.get_recipe(db=db, recipe_id=recipe_id)
    if db_recipe is None:
        raise HTTPException(status_code=404, detail="Рецепт не найден")
    return db_recipe


# Эндпоинт для редактирования существующего рецепта
@app.put("/recipes/{recipes}", response_model=schemas.Recipe, tags=["Recipes"])
async def update_existing_recipe(recipe_id: int, recipe: schemas.RecipeUpdate, db: AsyncSession = Depends(get_db)):
    db_recipe = await crud.update_recipe(db=db, recipe_id=recipe_id, recipe=recipe)
    if db_recipe is None:
        raise HTTPException(status_code=400, detail="Рецепт не найден")
    return db_recipe


# Эндпоинт для удаления рецепта по его ID
@app.delete("/recipe/{recipe_id}", tags=["Recipes"])
async def delete_existing_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    success = await crud.delete_recipe(db=db, recipe_id=recipe_id)
    if not success:
        raise HTTPException(status_code=404, detail="Рецепт не найден")
    return {"message": f"Рецепт с ID {recipe_id} успешно удален"}


# Эндпоинт для поиска рецепта по ингридиентам
@app.get("/search/filter/", response_model=List[schemas.Recipe], tags=["Search"])
async def search_recipes_by_ingredients(
        include: Optional[List[str]] = Query(None, description="Ингредиенты, которые ДОЛЖНЫ быть в рецепте (например, `include=картофель&include=сыр`)"),
        exclude: Optional[List[str]] = Query(None, description="Ингредиенты, которых НЕ ДОЛЖНО быть в рецепте (например, `exclude=лук`)"),
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db)
):
    ingredient_filter = schemas.IngredientFilter(include=include, exclude=exclude)
    recipe = await search.filter_recipes_by_ingredients(
        db=db,
        ingredient_filter=ingredient_filter,
        skip=skip,
        limit=limit
    )
    return recipe


# Эндпоинт для поиска рецепта на естественном языке
@app.get("/search/semantic/", response_model=List[schemas.Recipe], tags=["Search"])
async def search_recipes_by_natural_language(
        query: str = Query(..., description="Поисковый запрос на естественном языке (например, 'Вегетарианские рецепты с картофелем')"),
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db)
):
    if not query:
        raise HTTPException(status_code=400, detail="Поисковый запрос не может быть пустым")

    recipes = await search.semantic_search_recipes(
        db=db,
        natural_language_query=query,
        skip=skip,
        limit=limit
    )
    return recipes

