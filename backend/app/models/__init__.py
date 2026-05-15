"""SQLAlchemy ORM 模型注册。"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.models.media import MediaFile  # noqa: E402
from app.models.order import Order  # noqa: E402
from app.models.recipe import Recipe  # noqa: E402
from app.models.schedule import Schedule  # noqa: E402
from app.models.user import User  # noqa: E402
from app.models.weight import WeightProfile, WeightRecord  # noqa: E402

__all__ = ["Base", "User", "Schedule", "Recipe", "MediaFile", "Order", "WeightProfile", "WeightRecord"]
