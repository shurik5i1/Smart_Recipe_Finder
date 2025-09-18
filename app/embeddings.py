from typing import List, Optional
from sentence_transformers import SentenceTransformer
from sqlalchemy import Float

# model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
#
#
# def generate_embedding(text: str) -> List[Float]:
#     if not text:
#         return None
#     embedding = model.encode([text], covert_to_numpy=True)[0]
#     return embedding.tolist()
#
#
# def generate_recipe_embedding(recipe_data: dict) -> List[Float]:
#     text_representation = f"""
#         Название: {recipe_data.get('title', '')}
#         Ингредиенты: {', '.join(recipe_data.get('ingredients', []))}
#         Инструкция: {recipe_data.get('instructions', '')}
#         Кухня: {recipe_data.get('cuisine', '')}
#         Теги: {', '.join(recipe_data.get('tags', ''))}
#         """
#     return generate_embedding(text_representation)


model = SentenceTransformer("intfloat/multilingual-e5-large")


def generate_embedding(query: str) -> Optional[List[Float]]:
    """
    Генерирует эмбеддинг для пользовательского запроса (natural language query).
    Добавляем префикс 'query:' как рекомендуют авторы модели E5.
    """
    if not query:
        return None
    emb = model.encode(
        [f"query: {query}"],
        convert_to_numpy=True,
        normalize_embeddings=True,  # сразу нормируем (косинус = dot product)
    )[0]
    return emb.tolist()


def generate_recipe_embedding(recipe_data: dict) -> Optional[List[Float]]:
    """
    Генерирует эмбеддинг для рецепта (passage/document).
    Добавляем префикс 'passage:'.
    """
    text_representation = f"""
    Название: {recipe_data.get('title', '')}
    Ингредиенты: {', '.join(recipe_data.get('ingredients', []))}
    Инструкция: {recipe_data.get('instructions', '')}
    Кухня: {recipe_data.get('cuisine', '')}
    Теги: {', '.join(recipe_data.get('tags', []))}
    """
    emb = model.encode(
        [f"passage: {text_representation}"],
        convert_to_numpy=True,
        normalize_embeddings=True,
    )[0]
    return emb.tolist()
