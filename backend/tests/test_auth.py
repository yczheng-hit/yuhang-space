"""认证模块测试 — 注册、登录、刷新 Token。"""

from httpx import AsyncClient

from tests.conftest import auth_headers, register_and_login


class TestRegister:
    """注册接口测试。"""

    async def test_register_success(self, client: AsyncClient):
        """正常注册。"""
        resp = await client.post("/api/v1/auth/register", json={
            "username": "newuser",
            "password": "Pass123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "newuser"
        assert "user_id" in data

    async def test_register_duplicate_username(self, client: AsyncClient):
        """重复用户名注册应返回 409。"""
        await client.post("/api/v1/auth/register", json={
            "username": "dupuser",
            "password": "Pass123",
        })
        resp = await client.post("/api/v1/auth/register", json={
            "username": "dupuser",
            "password": "Pass456",
        })
        assert resp.status_code == 409
        assert "已被注册" in resp.json()["detail"]

    async def test_register_weak_password_no_digit(self, client: AsyncClient):
        """缺少数字的弱密码应返回 400。"""
        resp = await client.post("/api/v1/auth/register", json={
            "username": "weakuser",
            "password": "abcdef",
        })
        assert resp.status_code == 400

    async def test_register_weak_password_no_letter(self, client: AsyncClient):
        """缺少字母的弱密码应返回 400。"""
        resp = await client.post("/api/v1/auth/register", json={
            "username": "weakuser2",
            "password": "123456",
        })
        assert resp.status_code == 400

    async def test_register_short_password(self, client: AsyncClient):
        """过短密码应返回 422（Pydantic 校验）。"""
        resp = await client.post("/api/v1/auth/register", json={
            "username": "shortpw",
            "password": "Ab1",
        })
        assert resp.status_code == 422

    async def test_register_short_username(self, client: AsyncClient):
        """过短用户名应返回 422。"""
        resp = await client.post("/api/v1/auth/register", json={
            "username": "a",
            "password": "Pass123",
        })
        assert resp.status_code == 422

    async def test_register_username_case_insensitive(self, client: AsyncClient):
        """用户名应统一转小写存储。"""
        await client.post("/api/v1/auth/register", json={
            "username": "CaseUser",
            "password": "Pass123",
        })
        resp = await client.post("/api/v1/auth/login", json={
            "username": "caseuser",
            "password": "Pass123",
        })
        assert resp.status_code == 200


class TestLogin:
    """登录接口测试。"""

    async def test_login_success(self, client: AsyncClient):
        """正常登录应返回 access_token 和 refresh_token。"""
        await client.post("/api/v1/auth/register", json={
            "username": "loginuser",
            "password": "Pass123",
        })
        resp = await client.post("/api/v1/auth/login", json={
            "username": "loginuser",
            "password": "Pass123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client: AsyncClient):
        """错误密码应返回 401。"""
        await client.post("/api/v1/auth/register", json={
            "username": "wrongpw",
            "password": "Pass123",
        })
        resp = await client.post("/api/v1/auth/login", json={
            "username": "wrongpw",
            "password": "WrongPass123",
        })
        assert resp.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """不存在的用户应返回 401。"""
        resp = await client.post("/api/v1/auth/login", json={
            "username": "nobody",
            "password": "Pass123",
        })
        assert resp.status_code == 401

    async def test_login_empty_username(self, client: AsyncClient):
        """空用户名应返回 422。"""
        resp = await client.post("/api/v1/auth/login", json={
            "username": "",
            "password": "Pass123",
        })
        assert resp.status_code == 422


class TestRefreshToken:
    """刷新 Token 测试。"""

    async def test_refresh_success(self, client: AsyncClient):
        """使用有效 refresh_token 获取新 access_token。"""
        tokens = await register_and_login(client, "refreshuser", "Pass123")
        resp = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": tokens["refresh_token"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_refresh_invalid_token(self, client: AsyncClient):
        """无效 refresh_token 应返回 401。"""
        resp = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": "invalid.token.here",
        })
        assert resp.status_code == 401

    async def test_refresh_with_access_token(self, client: AsyncClient):
        """用 access_token 当 refresh_token 应返回 401。"""
        tokens = await register_and_login(client, "badrefresh", "Pass123")
        resp = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": tokens["access_token"],
        })
        assert resp.status_code == 401
