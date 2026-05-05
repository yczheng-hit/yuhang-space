"""密码哈希与强度校验。"""

import re

import bcrypt

from app.core.constants import PASSWORD_MIN_LENGTH, PASSWORD_PATTERN

_pattern = re.compile(PASSWORD_PATTERN)


def validate_password_strength(password: str) -> None:
    """校验密码强度，不满足则抛出 ValueError。"""
    if len(password) < PASSWORD_MIN_LENGTH:
        raise ValueError(f"密码长度不能少于 {PASSWORD_MIN_LENGTH} 位")
    if not _pattern.match(password):
        raise ValueError("密码必须包含英文字母和数字")


def hash_password(password: str) -> str:
    """返回密码的 bcrypt 哈希值。"""
    validate_password_strength(password)
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """校验明文密码与哈希是否匹配。"""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
