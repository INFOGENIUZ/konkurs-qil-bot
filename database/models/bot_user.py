from datetime import datetime, timedelta
from tortoise import Model, fields
from config import timezone_info


class BotUser(Model):
    user_id = fields.BigIntField(pk=True)
    username = fields.TextField(null=True)
    first_name = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    is_blocked = fields.BooleanField(default=False)

    @classmethod
    async def add_or_update(cls, user_id: int, username: str = None, first_name: str = None):
        try:
            user = await cls.filter(user_id=user_id).first()
            if user:
                if user.username != username or user.first_name != first_name or user.is_blocked:
                    await cls.filter(user_id=user_id).update(
                        username=username,
                        first_name=first_name,
                        is_blocked=False
                    )
            else:
                await cls.create(
                    user_id=user_id,
                    username=username,
                    first_name=first_name,
                    is_blocked=False
                )
        except Exception:
            pass

    @classmethod
    async def mark_blocked(cls, user_id: int):
        try:
            await cls.filter(user_id=user_id).update(is_blocked=True)
        except Exception:
            pass

    @classmethod
    async def get_total_count(cls) -> int:
        return await cls.filter(is_blocked=False).count()

    @classmethod
    async def get_today_count(cls) -> int:
        try:
            now = datetime.now(timezone_info)
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            return await cls.filter(created_at__gte=start_of_day).count()
        except Exception:
            return 0

    @classmethod
    async def get_all_ids(cls) -> list[int]:
        users = await cls.filter(is_blocked=False).all().values('user_id')
        return [u['user_id'] for u in users]
