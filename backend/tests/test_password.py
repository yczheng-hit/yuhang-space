"""密码工具测试。"""

import pytest

from app.security.password import hash_password, verify_password, validate_password_strength


class TestPasswordValidation:
    """密码强度校验测试。"""

    def test_valid_password(self):
        """包含字母和数字的密码通过校验。"""
        validate_password_strength("Pass123")  # 不应抛异常

    def test_no_digit(self):
        """缺少数字的密码应抛 ValueError。"""
        with pytest.raises(ValueError, match="数字"):
            validate_password_strength("abcdef")

    def test_no_letter(self):
        """缺少字母的密码应抛 ValueError。"""
        with pytest.raises(ValueError, match="字母"):
            validate_password_strength("123456")

    def test_too_short(self):
        """过短密码应抛 ValueError。"""
        with pytest.raises(ValueError, match="不能少于"):
            validate_password_strength("Ab1")


class TestPasswordHashing:
    """密码哈希测试。"""

    def test_hash_and_verify(self):
        """哈希后应能正确验证。"""
        password = "MyPass123"
        hashed = hash_password(password)
        assert verify_password(password, hashed)

    def test_wrong_password_fails(self):
        """错误密码不应通过验证。"""
        hashed = hash_password("MyPass123")
        assert not verify_password("WrongPass123", hashed)

    def test_different_hashes(self):
        """同一密码多次哈希应产生不同结果（salt 不同）。"""
        h1 = hash_password("MyPass123")
        h2 = hash_password("MyPass123")
        assert h1 != h2
