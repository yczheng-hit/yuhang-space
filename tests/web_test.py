#!/usr/bin/env python3
"""
web-test: 全面 E2E 集成测试
用法: python tests/web_test.py [--base-url URL]
默认测试 http://localhost:8000
"""

import argparse
import json
import sys
import uuid
from urllib.request import Request, urlopen
from urllib.error import HTTPError


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    END = "\033[0m"


class WebTest:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.passed = 0
        self.failed = 0
        self.errors = []

    # ── HTTP 工具 ──────────────────────────────────────────────

    def _request(self, method: str, path: str, data: dict | None = None, headers: dict | None = None) -> tuple:
        """发送 HTTP 请求，返回 (status_code, response_body_dict_or_str)。"""
        url = f"{self.base_url}{path}"
        body = json.dumps(data).encode() if data else None
        req = Request(url, data=body, method=method)
        req.add_header("Content-Type", "application/json")
        if headers:
            for k, v in headers.items():
                req.add_header(k, v)
        try:
            with urlopen(req) as resp:
                raw = resp.read()
                try:
                    return resp.status, json.loads(raw)
                except json.JSONDecodeError:
                    return resp.status, {}
        except HTTPError as e:
            raw = e.read()
            try:
                return e.code, json.loads(raw)
            except json.JSONDecodeError:
                return e.code, {"_raw": raw.decode("utf-8", errors="replace")[:200]}

    def _auth_headers(self, token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}

    # ── 断言工具 ──────────────────────────────────────────────

    def assert_status(self, actual: int, expected: int, test_name: str):
        if actual == expected:
            self._pass(test_name)
            return True
        else:
            self._fail(test_name, f"期望状态码 {expected}，实际 {actual}")
            return False

    def assert_contains(self, body: dict, key: str, test_name: str):
        if key in body:
            self._pass(test_name)
        else:
            self._fail(test_name, f"响应缺少字段 '{key}': {body}")

    def assert_not_contains(self, body: dict, key: str, test_name: str):
        if key not in body:
            self._pass(test_name)
        else:
            self._fail(test_name, f"响应不应包含字段 '{key}'")

    def assert_value(self, actual, expected, test_name: str):
        if actual == expected:
            self._pass(test_name)
        else:
            self._fail(test_name, f"期望 '{expected}'，实际 '{actual}'")

    def assert_true(self, condition: bool, test_name: str, detail: str = ""):
        if condition:
            self._pass(test_name)
        else:
            self._fail(test_name, detail or "条件不满足")

    def _pass(self, name: str):
        self.passed += 1
        print(f"  {Colors.GREEN}✓{Colors.END} {name}")

    def _fail(self, name: str, reason: str):
        self.failed += 1
        self.errors.append((name, reason))
        print(f"  {Colors.RED}✗{Colors.END} {name} — {reason}")

    # ── 测试项 ──────────────────────────────────────────────

    def test_health(self):
        """健康检查"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}── 健康检查 ──{Colors.END}")

        status, body = self._request("GET", "/docs")
        self.assert_status(status, 200, "GET /docs 可访问")

        status, body = self._request("GET", "/openapi.json")
        self.assert_status(status, 200, "GET /openapi.json 可访问")
        self.assert_contains(body, "paths", "OpenAPI 包含 paths 字段")

    def test_register(self):
        """注册接口"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}── 注册测试 ──{Colors.END}")

        uname = f"testuser_{uuid.uuid4().hex[:8]}"

        # 正常注册
        status, body = self._request("POST", "/api/v1/auth/register", {
            "username": uname,
            "password": "Pass123",
        })
        self.assert_status(status, 200, "正常注册返回 200")
        self.assert_contains(body, "user_id", "响应包含 user_id")
        self.assert_value(body.get("username"), uname, "响应用户名匹配")

        # 重复注册
        status, body = self._request("POST", "/api/v1/auth/register", {
            "username": uname,
            "password": "Pass456",
        })
        self.assert_status(status, 409, "重复用户名返回 409")

        # 弱密码（无数字）
        status, body = self._request("POST", "/api/v1/auth/register", {
            "username": f"weak_{uuid.uuid4().hex[:6]}",
            "password": "abcdef",
        })
        self.assert_status(status, 400, "无数字密码返回 400")

        # 弱密码（无字母）
        status, body = self._request("POST", "/api/v1/auth/register", {
            "username": f"weak2_{uuid.uuid4().hex[:6]}",
            "password": "123456",
        })
        self.assert_status(status, 400, "无字母密码返回 400")

        # 过短密码
        status, body = self._request("POST", "/api/v1/auth/register", {
            "username": f"short_{uuid.uuid4().hex[:6]}",
            "password": "Ab1",
        })
        self.assert_status(status, 422, "过短密码返回 422")

        # 过短用户名
        status, body = self._request("POST", "/api/v1/auth/register", {
            "username": "a",
            "password": "Pass123",
        })
        self.assert_status(status, 422, "过短用户名返回 422")

        # 空请求体
        status, body = self._request("POST", "/api/v1/auth/register", {})
        self.assert_status(status, 422, "空请求体返回 422")

        return uname

    def test_login(self, username: str):
        """登录接口"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}── 登录测试 ──{Colors.END}")

        # 正常登录
        status, body = self._request("POST", "/api/v1/auth/login", {
            "username": username,
            "password": "Pass123",
        })
        self.assert_status(status, 200, "正常登录返回 200")
        self.assert_contains(body, "access_token", "响应包含 access_token")
        self.assert_contains(body, "refresh_token", "响应包含 refresh_token")
        self.assert_value(body.get("token_type"), "bearer", "token_type 为 bearer")

        # 错误密码
        status, body = self._request("POST", "/api/v1/auth/login", {
            "username": username,
            "password": "WrongPass123",
        })
        self.assert_status(status, 401, "错误密码返回 401")

        # 不存在的用户
        status, body = self._request("POST", "/api/v1/auth/login", {
            "username": "nonexistent_user_xyz",
            "password": "Pass123",
        })
        self.assert_status(status, 401, "不存在用户返回 401")

        # 空用户名
        status, body = self._request("POST", "/api/v1/auth/login", {
            "username": "",
            "password": "Pass123",
        })
        self.assert_status(status, 422, "空用户名返回 422")

        # 获取有效 token 供后续测试使用
        _, login_body = self._request("POST", "/api/v1/auth/login", {
            "username": username,
            "password": "Pass123",
        })
        return login_body.get("access_token"), login_body.get("refresh_token")

    def test_refresh_token(self, refresh_token: str, access_token: str):
        """刷新 Token"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}── 刷新 Token 测试 ──{Colors.END}")

        # 正常刷新
        status, body = self._request("POST", "/api/v1/auth/refresh", {
            "refresh_token": refresh_token,
        })
        self.assert_status(status, 200, "正常刷新返回 200")
        self.assert_contains(body, "access_token", "响应包含新 access_token")
        self.assert_value(body.get("token_type"), "bearer", "token_type 为 bearer")

        # 无效 token
        status, body = self._request("POST", "/api/v1/auth/refresh", {
            "refresh_token": "invalid.token.here",
        })
        self.assert_status(status, 401, "无效 refresh_token 返回 401")

        # 用 access_token 冒充 refresh_token
        status, body = self._request("POST", "/api/v1/auth/refresh", {
            "refresh_token": access_token,
        })
        self.assert_status(status, 401, "用 access_token 刷新返回 401")

    def test_auth_guard(self):
        """认证守卫 — 未登录访问受保护接口"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}── 认证守卫测试 ──{Colors.END}")

        for endpoint in ["/api/v1/schedules", "/api/v1/recipes"]:
            status, _ = self._request("GET", endpoint)
            self.assert_status(status, 401, f"未登录访问 {endpoint} 返回 401")

        # 无效 token
        status, _ = self._request("GET", "/api/v1/schedules", headers={
            "Authorization": "Bearer invalid.token.here",
        })
        self.assert_status(status, 401, "无效 token 访问返回 401")

    def test_schedules(self, token: str):
        """日程 CRUD"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}── 日程 CRUD 测试 ──{Colors.END}")
        headers = self._auth_headers(token)

        # 创建
        status, body = self._request("POST", "/api/v1/schedules", {
            "title": "测试日程",
            "description": "测试描述",
            "start_time": "2025-06-01T10:00:00Z",
            "end_time": "2025-06-01T11:00:00Z",
            "priority": 0,
            "status": "pending",
            "tags": ["测试"],
        }, headers)
        self.assert_status(status, 200, "创建日程返回 200")
        self.assert_contains(body, "id", "响应包含 id")
        self.assert_value(body.get("title"), "测试日程", "标题匹配")
        schedule_id = body.get("id")

        # 创建第二个
        status, body2 = self._request("POST", "/api/v1/schedules", {
            "title": "测试日程2",
            "start_time": "2025-06-02T10:00:00Z",
            "tags": ["工作"],
        }, headers)
        self.assert_status(status, 200, "创建第二个日程返回 200")
        schedule_id2 = body2.get("id")

        # 列表
        status, body = self._request("GET", "/api/v1/schedules", headers=headers)
        self.assert_status(status, 200, "列出日程返回 200")
        self.assert_true(len(body) >= 2, f"至少有 2 个日程，实际 {len(body)}")

        # 查询单个
        status, body = self._request("GET", f"/api/v1/schedules/{schedule_id}", headers=headers)
        self.assert_status(status, 200, "查询单个日程返回 200")
        self.assert_value(body.get("title"), "测试日程", "查询标题匹配")

        # 更新
        status, body = self._request("PATCH", f"/api/v1/schedules/{schedule_id}", {
            "title": "更新后的日程",
            "status": "completed",
        }, headers)
        self.assert_status(status, 200, "更新日程返回 200")
        self.assert_value(body.get("title"), "更新后的日程", "更新后标题匹配")
        self.assert_value(body.get("status"), "completed", "更新后状态匹配")

        # 查询不存在的
        fake_id = "00000000-0000-0000-0000-000000000000"
        status, _ = self._request("GET", f"/api/v1/schedules/{fake_id}", headers=headers)
        self.assert_status(status, 404, "查询不存在日程返回 404")

        # 删除
        status, _ = self._request("DELETE", f"/api/v1/schedules/{schedule_id}", headers=headers)
        self.assert_status(status, 200, "删除日程返回 200")

        # 确认已删除
        status, _ = self._request("GET", f"/api/v1/schedules/{schedule_id}", headers=headers)
        self.assert_status(status, 404, "已删除日程返回 404")

        # 清理第二个
        self._request("DELETE", f"/api/v1/schedules/{schedule_id2}", headers=headers)

    def test_recipes(self, token: str):
        """菜谱 CRUD"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}── 菜谱 CRUD 测试 ──{Colors.END}")
        headers = self._auth_headers(token)

        # 创建
        status, body = self._request("POST", "/api/v1/recipes", {
            "title": "番茄炒蛋",
            "description": "经典家常菜",
            "ingredients": [
                {"name": "鸡蛋", "amount": "2", "unit": "个"},
                {"name": "番茄", "amount": "1", "unit": "个"},
            ],
            "instructions": ["打蛋", "切番茄", "翻炒"],
            "prep_time_min": 10,
            "cook_time_min": 15,
            "servings": 2,
            "tags": ["家常菜"],
        }, headers)
        self.assert_status(status, 200, "创建菜谱返回 200")
        self.assert_contains(body, "id", "响应包含 id")
        self.assert_value(body.get("title"), "番茄炒蛋", "标题匹配")
        self.assert_true(len(body.get("ingredients", [])) == 2, "食材数量为 2")
        self.assert_true(len(body.get("instructions", [])) == 3, "步骤数量为 3")
        recipe_id = body.get("id")

        # 列表
        status, body = self._request("GET", "/api/v1/recipes", headers=headers)
        self.assert_status(status, 200, "列出菜谱返回 200")
        self.assert_true(len(body) >= 1, f"至少有 1 个菜谱，实际 {len(body)}")

        # 查询单个
        status, body = self._request("GET", f"/api/v1/recipes/{recipe_id}", headers=headers)
        self.assert_status(status, 200, "查询单个菜谱返回 200")
        self.assert_value(body.get("title"), "番茄炒蛋", "查询标题匹配")

        # 更新
        status, body = self._request("PATCH", f"/api/v1/recipes/{recipe_id}", {
            "title": "升级版番茄炒蛋",
            "servings": 4,
        }, headers)
        self.assert_status(status, 200, "更新菜谱返回 200")
        self.assert_value(body.get("title"), "升级版番茄炒蛋", "更新后标题匹配")
        self.assert_value(body.get("servings"), 4, "更新后份数匹配")

        # 更新食材
        status, body = self._request("PATCH", f"/api/v1/recipes/{recipe_id}", {
            "ingredients": [
                {"name": "牛肉", "amount": "500", "unit": "克"},
            ],
        }, headers)
        self.assert_status(status, 200, "更新食材返回 200")
        self.assert_true(len(body.get("ingredients", [])) == 1, "更新后食材数量为 1")

        # 查询不存在的
        fake_id = "00000000-0000-0000-0000-000000000000"
        status, _ = self._request("GET", f"/api/v1/recipes/{fake_id}", headers=headers)
        self.assert_status(status, 404, "查询不存在菜谱返回 404")

        # 删除
        status, _ = self._request("DELETE", f"/api/v1/recipes/{recipe_id}", headers=headers)
        self.assert_status(status, 200, "删除菜谱返回 200")

        # 确认已删除
        status, _ = self._request("GET", f"/api/v1/recipes/{recipe_id}", headers=headers)
        self.assert_status(status, 404, "已删除菜谱返回 404")

    def test_user_isolation(self):
        """用户数据隔离"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}── 用户隔离测试 ──{Colors.END}")

        # 创建两个用户
        uname_a = f"isolate_a_{uuid.uuid4().hex[:6]}"
        uname_b = f"isolate_b_{uuid.uuid4().hex[:6]}"

        self._request("POST", "/api/v1/auth/register", {"username": uname_a, "password": "Pass123"})
        self._request("POST", "/api/v1/auth/register", {"username": uname_b, "password": "Pass123"})

        _, login_a = self._request("POST", "/api/v1/auth/login", {"username": uname_a, "password": "Pass123"})
        _, login_b = self._request("POST", "/api/v1/auth/login", {"username": uname_b, "password": "Pass123"})

        token_a = login_a["access_token"]
        token_b = login_b["access_token"]

        # 用户 A 创建日程
        self._request("POST", "/api/v1/schedules", {
            "title": "A的日程",
            "start_time": "2025-06-01T10:00:00Z",
        }, self._auth_headers(token_a))

        # 用户 A 创建菜谱
        self._request("POST", "/api/v1/recipes", {
            "title": "A的菜谱",
            "ingredients": [],
            "instructions": [],
        }, self._auth_headers(token_a))

        # 用户 B 看不到 A 的数据
        status, schedules_b = self._request("GET", "/api/v1/schedules", headers=self._auth_headers(token_b))
        if self.assert_status(status, 200, "用户B列出日程返回 200"):
            a_schedules = [s for s in schedules_b if s.get("title") == "A的日程"]
            self.assert_true(len(a_schedules) == 0, "用户B看不到A的日程")

        status, recipes_b = self._request("GET", "/api/v1/recipes", headers=self._auth_headers(token_b))
        if self.assert_status(status, 200, "用户B列出菜谱返回 200"):
            a_recipes = [r for r in recipes_b if r.get("title") == "A的菜谱"]
            self.assert_true(len(a_recipes) == 0, "用户B看不到A的菜谱")

    def test_priority_validation(self):
        """日程优先级校验"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}── 参数校验测试 ──{Colors.END}")

        uname = f"valid_{uuid.uuid4().hex[:6]}"
        self._request("POST", "/api/v1/auth/register", {"username": uname, "password": "Pass123"})
        _, login = self._request("POST", "/api/v1/auth/login", {"username": uname, "password": "Pass123"})
        headers = self._auth_headers(login["access_token"])

        # 优先级超出范围
        status, _ = self._request("POST", "/api/v1/schedules", {
            "title": "测试",
            "start_time": "2025-06-01T10:00:00Z",
            "priority": 5,
        }, headers)
        self.assert_status(status, 422, "优先级超范围返回 422")

        # 菜谱缺少必填字段
        status, _ = self._request("POST", "/api/v1/recipes", {
            "ingredients": [],
            "instructions": [],
        }, headers)
        self.assert_status(status, 422, "菜谱缺少标题返回 422")

    def test_pagination(self):
        """分页测试"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}── 分页测试 ──{Colors.END}")

        uname = f"page_{uuid.uuid4().hex[:6]}"
        self._request("POST", "/api/v1/auth/register", {"username": uname, "password": "Pass123"})
        _, login = self._request("POST", "/api/v1/auth/login", {"username": uname, "password": "Pass123"})
        headers = self._auth_headers(login["access_token"])

        # 创建 5 个日程
        for i in range(5):
            self._request("POST", "/api/v1/schedules", {
                "title": f"分页日程{i}",
                "start_time": f"2025-06-{i+1:02d}T10:00:00Z",
            }, headers)

        # 查询前 3 个
        status, body = self._request("GET", "/api/v1/schedules?limit=3", headers=headers)
        self.assert_status(status, 200, "分页查询返回 200")
        self.assert_true(len(body) == 3, f"limit=3 返回 3 条，实际 {len(body)}")

        # 跳过前 3 个
        status, body = self._request("GET", "/api/v1/schedules?skip=3&limit=3", headers=headers)
        self.assert_status(status, 200, "skip+limit 查询返回 200")
        self.assert_true(len(body) == 2, f"skip=3,limit=3 返回 2 条，实际 {len(body)}")

    def test_case_insensitive_username(self):
        """用户名大小写不敏感"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}── 用户名校验测试 ──{Colors.END}")

        uname = f"Case_{uuid.uuid4().hex[:6]}"
        self._request("POST", "/api/v1/auth/register", {"username": uname, "password": "Pass123"})

        # 用小写登录
        _, login = self._request("POST", "/api/v1/auth/login", {
            "username": uname.lower(),
            "password": "Pass123",
        })
        self.assert_true("access_token" in login, "小写用户名登录成功")

        # 用大写注册应冲突
        status, _ = self._request("POST", "/api/v1/auth/register", {
            "username": uname.upper(),
            "password": "Pass456",
        })
        self.assert_status(status, 409, "大写用户名注册冲突返回 409")

    def test_maintenance_api(self):
        """运维 API"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}── 运维 API 测试 ──{Colors.END}")

        # 无签名访问应失败
        status, _ = self._request("GET", "/api/v1/maintenance/stats")
        self.assert_true(status in (401, 403), f"无签名访问返回 {status}")

    # ── 运行入口 ──────────────────────────────────────────────

    def run_all(self):
        print(f"\n{Colors.BOLD}{'='*50}")
        print(f"  web-test 全面测试")
        print(f"  目标: {self.base_url}")
        print(f"{'='*50}{Colors.END}")

        self.test_health()
        username = self.test_register()
        token, refresh = self.test_login(username)
        self.test_refresh_token(refresh, token)
        self.test_auth_guard()
        self.test_schedules(token)
        self.test_recipes(token)
        self.test_user_isolation()
        self.test_priority_validation()
        self.test_pagination()
        self.test_case_insensitive_username()
        self.test_maintenance_api()

        # 结果汇总
        total = self.passed + self.failed
        print(f"\n{Colors.BOLD}{'='*50}")
        print(f"  测试结果: {total} 项")
        print(f"  {Colors.GREEN}通过: {self.passed}{Colors.END}")
        if self.failed:
            print(f"  {Colors.RED}失败: {self.failed}{Colors.END}")
            print(f"\n  {Colors.RED}失败详情:{Colors.END}")
            for name, reason in self.errors:
                print(f"    {Colors.RED}✗{Colors.END} {name}")
                print(f"      {reason}")
        else:
            print(f"  {Colors.GREEN}全部通过!{Colors.END}")
        print(f"{'='*50}{Colors.END}\n")

        return 0 if self.failed == 0 else 1


def main():
    parser = argparse.ArgumentParser(description="web-test: 全面 E2E 集成测试")
    parser.add_argument("--base-url", default="http://localhost:8000", help="后端 API 基础 URL")
    args = parser.parse_args()

    tester = WebTest(args.base_url)
    sys.exit(tester.run_all())


if __name__ == "__main__":
    main()
