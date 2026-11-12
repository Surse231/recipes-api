from typing import Any

from fastapi.testclient import TestClient


def _recipe_payload(title: str, cooking_time: int) -> dict[str, Any]:
    return {
        "title": title,
        "description": f"Описание: {title}",
        "cooking_time": cooking_time,
        "ingredients": [{"name": "Яйца", "amount": "2 шт"}],
    }


def test_create_recipe_returns_201_with_zero_views(client: TestClient) -> None:
    response = client.post("/recipes", json=_recipe_payload("Омлет", 10))
    assert response.status_code == 201
    body = response.json()
    assert body["views"] == 0
    assert body["ingredients"] == [{"name": "Яйца", "amount": "2 шт"}]


def test_create_recipe_rejects_invalid_data(client: TestClient) -> None:
    response = client.post(
        "/recipes",
        json={"title": "", "description": "x", "cooking_time": 0, "ingredients": []},
    )
    assert response.status_code == 422


def test_list_recipes_is_sorted_by_views_then_cooking_time(client: TestClient) -> None:
    first = client.post("/recipes", json=_recipe_payload("Борщ", 90)).json()
    second = client.post("/recipes", json=_recipe_payload("Блины", 30)).json()
    client.get(f"/recipes/{first['id']}")
    client.get(f"/recipes/{first['id']}")

    response = client.get("/recipes")
    assert response.status_code == 200
    titles = [item["title"] for item in response.json()]
    assert titles.index("Борщ") < titles.index("Блины")
    assert second["id"] is not None


def test_get_recipe_increments_views(client: TestClient) -> None:
    created = client.post("/recipes", json=_recipe_payload("Суп", 45)).json()
    first = client.get(f"/recipes/{created['id']}")
    assert first.status_code == 200
    assert first.json()["views"] == 1
    second = client.get(f"/recipes/{created['id']}")
    assert second.json()["views"] == 2


def test_get_missing_recipe_returns_404(client: TestClient) -> None:
    response = client.get("/recipes/999999")
    assert response.status_code == 404
