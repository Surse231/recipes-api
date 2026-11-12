from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src import models, schemas
from src.database import Base, engine, get_session


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="Кулинарная книга",
    description=(
        "API кулинарной книги. Рецепты в списке отсортированы по популярности: "
        "сначала с наибольшим числом просмотров, при равенстве — по времени готовки. "
        "Каждое открытие детальной страницы рецепта увеличивает его счётчик просмотров."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


@app.get(
    "/recipes",
    response_model=list[schemas.RecipeListItem],
    summary="Список рецептов",
    description=(
        "Возвращает все рецепты для экрана со списком. Сортировка: по количеству просмотров "
        "по убыванию, при равенстве — по времени готовки по возрастанию. "
        "Сам запрос просмотры не увеличивает."
    ),
    tags=["recipes"],
)
async def list_recipes(
    session: AsyncSession = Depends(get_session),
) -> list[models.Recipe]:
    result = await session.execute(
        select(models.Recipe).order_by(
            models.Recipe.views.desc(),
            models.Recipe.cooking_time.asc(),
        )
    )
    return list(result.scalars().all())


@app.get(
    "/recipes/{recipe_id}",
    response_model=schemas.RecipeDetail,
    summary="Детальная информация о рецепте",
    description=(
        "Возвращает название, время готовки, описание и ингредиенты рецепта. "
        "Каждый вызов увеличивает счётчик просмотров рецепта на 1."
    ),
    responses={404: {"description": "Рецепт с таким ID не найден"}},
    tags=["recipes"],
)
async def get_recipe(
    recipe_id: int,
    session: AsyncSession = Depends(get_session),
) -> models.Recipe:
    recipe = await session.get(models.Recipe, recipe_id)
    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe {recipe_id} not found",
        )
    recipe.views += 1
    await session.commit()
    return recipe


@app.post(
    "/recipes",
    response_model=schemas.RecipeDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Создать рецепт",
    description=(
        "Создаёт рецепт вместе со списком ингредиентов. Счётчик просмотров у нового рецепта "
        "равен 0. Возвращает созданный рецепт с его ID."
    ),
    responses={
        422: {
            "description": (
                "Неверные данные: пустое название, время не больше нуля, "
                "пустой список ингредиентов"
            ),
        },
    },
    tags=["recipes"],
)
async def create_recipe(
    data: schemas.RecipeIn,
    session: AsyncSession = Depends(get_session),
) -> models.Recipe:
    recipe = models.Recipe(
        title=data.title,
        description=data.description,
        cooking_time=data.cooking_time,
        views=0,
        ingredients=[
            models.Ingredient(name=item.name, amount=item.amount) for item in data.ingredients
        ],
    )
    session.add(recipe)
    await session.commit()
    return recipe
