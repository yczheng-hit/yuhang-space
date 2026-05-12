"""菜谱模块测试 — CRUD 操作。"""

from httpx import AsyncClient

from tests.conftest import auth_headers, register_and_login


class TestRecipeCRUD:
    """菜谱增删改查测试。"""

    async def _create_recipe(self, client: AsyncClient, headers: dict, title: str = "测试菜谱") -> dict:
        """辅助方法：创建一个菜谱。"""
        resp = await client.post("/api/v1/recipes", json={
            "title": title,
            "description": "美味佳肴",
            "ingredients": [
                {"name": "鸡蛋", "amount": "2", "unit": "个"},
                {"name": "番茄", "amount": "1", "unit": "个"},
            ],
            "instructions": ["打蛋", "切番茄", "翻炒"],
            "prep_time_min": 10,
            "cook_time_min": 15,
            "servings": 2,
            "tags": ["家常菜"],
        }, headers=headers)
        assert resp.status_code == 200
        return resp.json()

    async def test_create_recipe(self, client: AsyncClient):
        """创建菜谱。"""
        tokens = await register_and_login(client, "recipe_user1", "Pass123")
        headers = auth_headers(tokens["access_token"])

        data = await self._create_recipe(client, headers)
        assert data["title"] == "测试菜谱"
        assert len(data["ingredients"]) == 2
        assert len(data["instructions"]) == 3
        assert "id" in data

    async def test_list_recipes(self, client: AsyncClient):
        """列出菜谱。"""
        tokens = await register_and_login(client, "recipe_user2", "Pass123")
        headers = auth_headers(tokens["access_token"])

        await self._create_recipe(client, headers, "菜谱1")
        await self._create_recipe(client, headers, "菜谱2")

        resp = await client.get("/api/v1/recipes", headers=headers)
        assert resp.status_code == 200
        recipes = resp.json()
        assert len(recipes) == 2

    async def test_get_recipe(self, client: AsyncClient):
        """获取单个菜谱。"""
        tokens = await register_and_login(client, "recipe_user3", "Pass123")
        headers = auth_headers(tokens["access_token"])

        created = await self._create_recipe(client, headers)
        resp = await client.get(f"/api/v1/recipes/{created['id']}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["title"] == "测试菜谱"

    async def test_update_recipe(self, client: AsyncClient):
        """更新菜谱。"""
        tokens = await register_and_login(client, "recipe_user4", "Pass123")
        headers = auth_headers(tokens["access_token"])

        created = await self._create_recipe(client, headers)
        resp = await client.patch(f"/api/v1/recipes/{created['id']}", json={
            "title": "更新后的菜谱",
            "servings": 4,
        }, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["title"] == "更新后的菜谱"
        assert resp.json()["servings"] == 4

    async def test_update_recipe_ingredients(self, client: AsyncClient):
        """更新菜谱食材。"""
        tokens = await register_and_login(client, "recipe_user5", "Pass123")
        headers = auth_headers(tokens["access_token"])

        created = await self._create_recipe(client, headers)
        resp = await client.patch(f"/api/v1/recipes/{created['id']}", json={
            "ingredients": [
                {"name": "牛肉", "amount": "500", "unit": "克"},
            ],
        }, headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()["ingredients"]) == 1
        assert resp.json()["ingredients"][0]["name"] == "牛肉"

    async def test_delete_recipe(self, client: AsyncClient):
        """删除菜谱。"""
        tokens = await register_and_login(client, "recipe_user6", "Pass123")
        headers = auth_headers(tokens["access_token"])

        created = await self._create_recipe(client, headers)
        resp = await client.delete(f"/api/v1/recipes/{created['id']}", headers=headers)
        assert resp.status_code == 200

        # 确认已删除
        resp = await client.get(f"/api/v1/recipes/{created['id']}", headers=headers)
        assert resp.status_code == 404

    async def test_recipe_not_found(self, client: AsyncClient):
        """获取不存在的菜谱应返回 404。"""
        tokens = await register_and_login(client, "recipe_user7", "Pass123")
        headers = auth_headers(tokens["access_token"])

        fake_id = "00000000-0000-0000-0000-000000000000"
        resp = await client.get(f"/api/v1/recipes/{fake_id}", headers=headers)
        assert resp.status_code == 404

    async def test_recipe_unauthorized(self, client: AsyncClient):
        """未登录访问菜谱应返回 401。"""
        resp = await client.get("/api/v1/recipes")
        assert resp.status_code in (401, 422)

    async def test_recipe_user_isolation(self, client: AsyncClient):
        """用户只能看到自己的菜谱。"""
        tokens_a = await register_and_login(client, "recipe_iso_a", "Pass123")
        tokens_b = await register_and_login(client, "recipe_iso_b", "Pass123")

        await self._create_recipe(client, auth_headers(tokens_a["access_token"]), "A的菜谱")

        resp = await client.get("/api/v1/recipes", headers=auth_headers(tokens_b["access_token"]))
        assert resp.status_code == 200
        assert len(resp.json()) == 0
