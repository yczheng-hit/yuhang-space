"""日程模块测试 — CRUD 操作。"""

import pytest
from httpx import AsyncClient

from tests.conftest import auth_headers, register_and_login


class TestScheduleCRUD:
    """日程增删改查测试。"""

    async def _create_schedule(self, client: AsyncClient, headers: dict, title: str = "测试日程") -> dict:
        """辅助方法：创建一个日程。"""
        resp = await client.post("/api/v1/schedules", json={
            "title": title,
            "description": "测试描述",
            "start_time": "2025-06-01T10:00:00Z",
            "end_time": "2025-06-01T11:00:00Z",
            "priority": 0,
            "status": "pending",
            "tags": ["测试"],
        }, headers=headers)
        assert resp.status_code == 200
        return resp.json()

    async def test_create_schedule(self, client: AsyncClient):
        """创建日程。"""
        tokens = await register_and_login(client, "sched_user1", "Pass123")
        headers = auth_headers(tokens["access_token"])

        data = await self._create_schedule(client, headers)
        assert data["title"] == "测试日程"
        assert data["status"] == "pending"
        assert "id" in data

    async def test_list_schedules(self, client: AsyncClient):
        """列出日程。"""
        tokens = await register_and_login(client, "sched_user2", "Pass123")
        headers = auth_headers(tokens["access_token"])

        await self._create_schedule(client, headers, "日程1")
        await self._create_schedule(client, headers, "日程2")

        resp = await client.get("/api/v1/schedules", headers=headers)
        assert resp.status_code == 200
        schedules = resp.json()
        assert len(schedules) == 2

    async def test_get_schedule(self, client: AsyncClient):
        """获取单个日程。"""
        tokens = await register_and_login(client, "sched_user3", "Pass123")
        headers = auth_headers(tokens["access_token"])

        created = await self._create_schedule(client, headers)
        resp = await client.get(f"/api/v1/schedules/{created['id']}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["title"] == "测试日程"

    async def test_update_schedule(self, client: AsyncClient):
        """更新日程。"""
        tokens = await register_and_login(client, "sched_user4", "Pass123")
        headers = auth_headers(tokens["access_token"])

        created = await self._create_schedule(client, headers)
        resp = await client.patch(f"/api/v1/schedules/{created['id']}", json={
            "title": "更新后的日程",
            "status": "completed",
        }, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["title"] == "更新后的日程"
        assert resp.json()["status"] == "completed"

    async def test_delete_schedule(self, client: AsyncClient):
        """删除日程。"""
        tokens = await register_and_login(client, "sched_user5", "Pass123")
        headers = auth_headers(tokens["access_token"])

        created = await self._create_schedule(client, headers)
        resp = await client.delete(f"/api/v1/schedules/{created['id']}", headers=headers)
        assert resp.status_code == 200

        # 确认已删除
        resp = await client.get(f"/api/v1/schedules/{created['id']}", headers=headers)
        assert resp.status_code == 404

    async def test_schedule_not_found(self, client: AsyncClient):
        """获取不存在的日程应返回 404。"""
        tokens = await register_and_login(client, "sched_user6", "Pass123")
        headers = auth_headers(tokens["access_token"])

        fake_id = "00000000-0000-0000-0000-000000000000"
        resp = await client.get(f"/api/v1/schedules/{fake_id}", headers=headers)
        assert resp.status_code == 404

    async def test_schedule_unauthorized(self, client: AsyncClient):
        """未登录访问日程应返回 401。"""
        resp = await client.get("/api/v1/schedules")
        assert resp.status_code in (401, 422)

    async def test_schedule_user_isolation(self, client: AsyncClient):
        """用户只能看到自己的日程。"""
        tokens_a = await register_and_login(client, "sched_iso_a", "Pass123")
        tokens_b = await register_and_login(client, "sched_iso_b", "Pass123")

        await self._create_schedule(client, auth_headers(tokens_a["access_token"]), "A的日程")

        resp = await client.get("/api/v1/schedules", headers=auth_headers(tokens_b["access_token"]))
        assert resp.status_code == 200
        assert len(resp.json()) == 0
