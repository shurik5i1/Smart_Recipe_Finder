from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from embeddings import generate_recipe_embedding
from datetime import datetime
import models
import schemas
import json


# Вспомогательные функции для работы с JSON-полями
def _dump_json(data):
    """Конвертирует данные в JSON-строку."""
    return json.dumps(data, ensure_ascii=False) if data else "[]"


def _load_json(data):
    """Загружает данные из JSON-строки."""
    return json.loads(data) if data else []


# Создает новый рецепт в базе данных.
async def create_recipe(db: AsyncSession, recipe: schemas.RecipeCreate):
    recipe_data = recipe.model_dump()

    recipe_data["ingredients"] = _dump_json(recipe_data["ingredients"])
    recipe_data["tags"] = _dump_json(recipe_data["tags"])

    embedding = generate_recipe_embedding(recipe.model_dump())
    recipe_data["embedding"] = _dump_json(embedding) if embedding else None

    current_time = datetime.now().isoformat()
    recipe_data["created_at"] = current_time
    recipe_data["updated_at"] = current_time

    # Создаем объект модели SQLAlchemy
    db_recipe = models.Recipe(**recipe_data)
    db.add(db_recipe)
    await db.commit()
    await db.refresh(db_recipe)

    # Конвертируем обратно для ответа
    db_recipe.ingredients = _load_json(db_recipe.ingredients)
    db_recipe.tags = _load_json(db_recipe.tags)
    db_recipe.embedding = _load_json(db_recipe.embedding) if db_recipe.embedding else None

    return db_recipe


# Получает один рецепт по его ID
async def get_recipe(db: AsyncSession, recipe_id: int):
    query = select(models.Recipe).where(models.Recipe.id == recipe_id)
    result = await db.execute(query)
    db_recipe = result.scalar_one_or_none()
    if db_recipe:
        # Конвертируем JSON-строки обратно в списки
        db_recipe.ingredients = _load_json(db_recipe.ingredients)
        db_recipe.tags = _load_json(db_recipe.tags)
        db_recipe.embedding = _load_json(db_recipe.embedding) if db_recipe.embedding else None

    return db_recipe


# Получает список рецептов с пагинацией.
async def get_recipes(db: AsyncSession, skip: int = 0, limit: int = 100):
    query = select(models.Recipe).offset(skip).limit(limit)
    result = await db.execute(query)
    recipes = result.scalars().all()
    for recipe in recipes:
        recipe.ingredients = _load_json(recipe.ingredients)
        recipe.tags = _load_json(recipe.tags)
        if recipe.embedding:
            recipe.embedding = _load_json(recipe.embedding)

    return recipes


# Обновляет существующий рецепт.
async def update_recipe(db: AsyncSession, recipe_id: int, recipe: schemas.RecipeUpdate):
    db_recipe = await get_recipe(db, recipe_id)
    if db_recipe is None:
        return None

    update_data = recipe.model_dump(exclude_unset=True)

    if update_data:
        update_data["updated_at"] = datetime.now().isoformat()

        if "ingredients" in update_data:
            update_data["ingredients"] = _dump_json(update_data["ingredients"])
        if "tags" in update_data:
            update_data["tags"] = _dump_json(update_data["tags"])

        if any(key in update_data for key in ["title", "ingredients", "instructions", "cuisine", "tags"]):
            current_data = {
                'title': update_data.get("title", db_recipe.title),
                'ingredients': (_load_json(update_data["ingredients"]) if "ingredients" in update_data else db_recipe.ingredients),
                'instructions': update_data.get("instructions", db_recipe.instructions),
                'cuisine': update_data.get("cuisine", db_recipe.cuisine),
                'tags': (_load_json(update_data["tags"]) if "tags" in update_data else db_recipe.tags)
            }

            embedding = generate_recipe_embedding(current_data)
            update_data["embedding"] = _dump_json(embedding) if embedding else None

        for key, value in update_data.items():
            setattr(db_recipe, key, value)

        await db.commit()
        await db.refresh(db_recipe)

        if hasattr(db_recipe, "ingredients") and isinstance(db_recipe.ingredients, str):
            db_recipe.ingredients = _load_json(db_recipe.ingredients)
        if hasattr(db_recipe, "tags") and isinstance(db_recipe.tags, str):
            db_recipe.tags = _load_json(db_recipe.tags)
        if hasattr(db_recipe, "embedding") and db_recipe.embedding and isinstance(db_recipe.embedding, str):
            db_recipe.embedding = _load_json(db_recipe.embedding)

    return db_recipe


# Удаляет существующий рецепт по ID.
async def delete_recipe(db: AsyncSession, recipe_id: int):
    query = delete(models.Recipe).where(models.Recipe.id == recipe_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount > 0


