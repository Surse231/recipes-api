from pydantic import BaseModel, ConfigDict, Field


class IngredientIn(BaseModel):
    name: str = Field(
        min_length=1, max_length=100, description="Название ингредиента", examples=["Мука"]
    )
    amount: str = Field(
        min_length=1,
        max_length=50,
        description="Количество с единицей измерения",
        examples=["200 г"],
    )


class IngredientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(description="Название ингредиента")
    amount: str = Field(description="Количество с единицей измерения")


class RecipeIn(BaseModel):
    title: str = Field(
        min_length=1, max_length=200, description="Название рецепта", examples=["Блины"]
    )
    description: str = Field(
        min_length=1,
        description="Текстовое описание приготовления",
        examples=["Смешать ингредиенты и жарить на сковороде"],
    )
    cooking_time: int = Field(gt=0, description="Время готовки в минутах", examples=[30])
    ingredients: list[IngredientIn] = Field(min_length=1, description="Список ингредиентов")


class RecipeListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Идентификатор рецепта")
    title: str = Field(description="Название рецепта")
    views: int = Field(description="Сколько раз открыли детальную страницу рецепта")
    cooking_time: int = Field(description="Время готовки в минутах")


class RecipeDetail(RecipeListItem):
    description: str = Field(description="Текстовое описание приготовления")
    ingredients: list[IngredientOut] = Field(description="Список ингредиентов")
