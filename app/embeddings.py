import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer
from sqlalchemy import Float

model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')


def generate_embedding(text: str) -> List[Float]:
    if not text:
        return None
    embedding = model.encode([text], covert_to_numpy=True)[0]
    return embedding.tolist()


def generate_recipe_embedding(recipe_data: dict) -> List[Float]:
    text_representation = f"""
        Название: {recipe_data.get('title', '')}
        Ингредиенты: {', '.join(recipe_data.get('ingredients', []))}
        Инструкция: {recipe_data.get('instructions', '')}
        Кухня: {recipe_data.get('cuisine', '')}
        Теги: {', '.join(recipe_data.get('tags', ''))}
        """
    return generate_embedding(text_representation)
