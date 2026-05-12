"""JWT 工具测试。"""

import pytest

from app.security.jwt import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
)


class TestJWT:
    """JWT 创建与解析测试。"""

    def test_access_token_roundtrip(self):
        """创建 access_token 后应能正确解析。"""
        token = create_access_token("test-user-id")
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "test-user-id"
        assert payload["type"] == "access"

    def test_refresh_token_roundtrip(self):
        """创建 refresh_token 后应能正确解析。"""
        token = create_refresh_token("test-user-id")
        payload = decode_refresh_token(token)
        assert payload is not None
        assert payload["sub"] == "test-user-id"
        assert payload["type"] == "refresh"

    def test_access_token_not_valid_as_refresh(self):
        """access_token 不应被当作 refresh_token 解析。"""
        token = create_access_token("test-user-id")
        payload = decode_refresh_token(token)
        assert payload is None

    def test_refresh_token_not_valid_as_access(self):
        """refresh_token 不应被当作 access_token 解析。"""
        token = create_refresh_token("test-user-id")
        payload = decode_access_token(token)
        assert payload is None

    def test_invalid_token(self):
        """无效 token 应返回 None。"""
        assert decode_access_token("invalid.token.here") is None
        assert decode_refresh_token("invalid.token.here") is None

    def test_empty_token(self):
        """空 token 应返回 None。"""
        assert decode_access_token("") is None
