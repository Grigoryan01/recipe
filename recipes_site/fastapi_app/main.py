from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, select
from sqlalchemy.orm import sessionmaker
import os

# Получаем абсолютный путь к файлу базы данных db.sqlite3 из Django проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'db.sqlite3')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata = MetaData()

recipes = Table(
    "recipes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String, index=True),
    Column("description", Text),
    Column("steps", Text),
    Column("cooking_time", Integer),
    Column("author_id", Integer),
)

SessionLocal = sessionmaker(bind=engine)
app = FastAPI()


class Recipe(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    steps: Optional[str] = None
    cooking_time: Optional[int] = None
    author_id: Optional[int] = None


class RecipeCreate(BaseModel):
    title: str
    description: Optional[str] = None
    steps: Optional[str] = None
    cooking_time: Optional[int] = None
    author_id: Optional[int] = None


@app.get("/recipes/by-title/{title}", response_model=List[Recipe])
def get_recipe_by_title(title: str):
    session = SessionLocal()
    query = select(recipes).where(recipes.c.title.ilike(f"%{title}%"))
    result = session.execute(query).fetchall()
    session.close()
    if not result:
        raise HTTPException(status_code=404, detail="Recipes not found")
    return [Recipe(**dict(row)) for row in result]


@app.get("/recipes/", response_model=List[Recipe])
def get_all_recipes():
    session = SessionLocal()
    query = select(recipes)
    result = session.execute(query).fetchall()
    session.close()
    return [Recipe(**dict(row)) for row in result]


@app.post("/recipes/", response_model=Recipe)
def create_recipe(recipe: RecipeCreate):
    session = SessionLocal()
    new_recipe = recipes.insert().values(
        title=recipe.title,
        description=recipe.description,
        steps=recipe.steps,
        cooking_time=recipe.cooking_time,
        author_id=recipe.author_id,
    )
    session.execute(new_recipe)
    session.commit()
    session.close()
    return recipe
