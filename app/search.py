from sqlalchemy import select, func, or_, and_, not_
from sqlalchemy.ext.asyncio import AsyncSession
import models
from embeddings import generate_embedding
import numpy as np


# Фильтрует рецепты по наличию или отсутствию ингредиентов.
async def filter_recipes_by_ingredients(
        db: AsyncSession,
        ingredient_filter,
        skip: int = 0,
        limit: int = 100
):
    query = select(models.Recipe)
    conditions = []

    # Условие ВКЛЮЧЕНИЯ: каждый ингредиент из списка "include" должен быть в рецепте
    if ingredient_filter.include:
        for ingredient in ingredient_filter.include:
            conditions.append(
                func.array_to_string(models.Recipe.ingredients, ', ').ilike(f'%{ingredient}%')
            )

    # Условие ИСКЛЮЧЕНИЯ: каждый ингредиент из списка "include" должен быть в рецепте
    if ingredient_filter.exclude:
        for ingredient in ingredient_filter.exclude:
            conditions.append(
                not_(func.array_to_string(models.Recipe.ingredients, ', ').ilike(f'%{ingredient}%'))
            )

    if conditions:
        query = query.where(and_(*conditions))

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


async def semantic_search_recipes(
        db: AsyncSession,
        natural_language_query: str,
        threshold: float = 0.5,
        skip: int = 0,
        limit: int = 100
):
    query_embedding = generate_embedding(natural_language_query)
    if query_embedding is None:
        return []

    all_recipes_query = select(models.Recipe)
    result = await db.execute(all_recipes_query)
    all_recipes = result.scalars().all()

    recipes_with_similarity = []
    for recipe in all_recipes:
        if recipe.embedding:
            recipe_embedding = np.array(recipe.embedding)
            similarity = np.dot(query_embedding, recipe_embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(recipe_embedding))
            if similarity >= threshold:
                recipes_with_similarity.append(recipe, similarity)

    recipes_with_similarity.sort(key=lambda x: x[1], reverse=True)

    paginated_recipes = [recipe for recipe, sim in recipes_with_similarity[skip:skip + limit]]
    return paginated_recipes


