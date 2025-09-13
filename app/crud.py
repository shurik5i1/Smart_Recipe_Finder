from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import models
import schemas

from embeddings import generate_recipe_embedding


# Получает один рецепт по его ID
async def get_recipe(db: AsyncSession, recipe_id: int):
    query = select(models.Recipe).where(models.Recipe.id == recipe_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


# Получает список рецептов с пагинацией.
async def get_recipes(db: AsyncSession, skip: int = 0, limit: int = 100):
    query = select(models.Recipe).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


# Создает новый рецепт в базе данных.
async def create_recipe(db: AsyncSession, recipe: schemas.RecipeCreate):
    recipe_data = recipe.model_dump()
    embedding = generate_recipe_embedding(recipe_data)

    db_recipe = models.Recipe(**recipe_data, embedding=embedding)
    db.add(db_recipe)
    await db.commit()
    await db.refresh(db_recipe)
    return db_recipe


# Обновляет существующий рецепт.
async def update_recipe(db: AsyncSession, recipe_id: int, recipe: schemas.RecipeUpdate):
    db_recipe = await get_recipe(db, recipe_id)
    if db_recipe is None:
        return None

    update_data = recipe.model_dump(exclude_unset=True)

    if update_data:
        combined_data = db_recipe.__dict__.copy()
        combined_data.update(update_data)
        combined_data = {k: v for k, v in combined_data.items() if not k.startswith("_")}
        update_data["embedding"] = generate_recipe_embedding(combined_data)

        query = (
            update(models.Recipe)
            .where(models.Recipe.id == recipe_id)
            .values(**update_data)
            .execution_options(synchronize_session="fetch")
        )
        await db.execute(query)
        await db.commit()

        await db.refresh(db_recipe)

    return db_recipe


# Удаляет существующий рецепт по ID.
async def delete_recipe(db: AsyncSession, recipe_id: int):
    query = delete(models.Recipe).where(models.Recipe.id == recipe_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount > 0


