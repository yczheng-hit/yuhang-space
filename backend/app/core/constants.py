"""应用常量。"""

# 密码强度
PASSWORD_MIN_LENGTH = 6
PASSWORD_PATTERN = r"^(?=.*[A-Za-z])(?=.*\d).{6,}$"

# 媒体文件类型
FILE_TYPE_IMAGE = "image"
FILE_TYPE_VIDEO = "video"


# 维护 API
MAINTENANCE_TIMESTAMP_MAX_AGE_SECONDS = 300
