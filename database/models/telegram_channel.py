import math
import random
import string
from typing import List, Dict, Any

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from tortoise import Model, fields


class TelegramChannel(Model):
    channel_callback_value = fields.TextField(pk=True)
    channel_id = fields.BigIntField()
    group_id = fields.BigIntField(null=True)
    post_id = fields.BigIntField(null=True)
    owner_id = fields.BigIntField()
    give_callback_value = fields.TextField()
    name = fields.TextField()

    async def add_channel(
        self,
        owner_id: int,
        channel_id: int,
        give_callback_value: str,
        name: str,
        group_id: int = False
    ):
        give_cb = give_callback_value if give_callback_value else ''
        existing = await self.filter(
            owner_id=owner_id,
            channel_id=channel_id,
            give_callback_value=give_cb
        ).first()

        if existing:
            await self.filter(channel_callback_value=existing.channel_callback_value).update(
                name=name,
                group_id=group_id if group_id else existing.group_id
            )
            return existing.channel_callback_value

        random_callback_value = ''.join(
            random.choices(
                string.ascii_letters + string.digits, k=60
            )
        )

        await self.create(
            owner_id=owner_id,
            group_id=group_id if group_id else 0,
            channel_id=channel_id,
            give_callback_value=give_cb,
            channel_callback_value=random_callback_value,
            name=name
        )
        return random_callback_value

    async def add_post_id(self, callback_value: str, post_id: int):
        await self.filter(give_callback_value=callback_value).update(post_id=post_id)

    async def delete_channel(self, channel_callback_value: str = False, give_callback_value: str = False):
        if channel_callback_value:
            record = await self.filter(channel_callback_value=channel_callback_value).first()
            if record:
                if not record.give_callback_value:
                    # Asosiy menyudan o'chirilganda, ushbu egasining barcha dublikatlarini o'chiramiz
                    await self.filter(owner_id=record.owner_id, channel_id=record.channel_id).delete()
                else:
                    await self.filter(channel_callback_value=channel_callback_value).delete()
        elif give_callback_value:
            await self.filter(give_callback_value=give_callback_value).all().delete()

    async def exists_channel(
        self,
        channel_id: int,
        give_callback_value: str = False,
        owner_id: int = False
    ) -> bool:
        if give_callback_value and owner_id:
            return await self.filter(
                channel_id=channel_id,
                give_callback_value=give_callback_value,
                owner_id=owner_id
            ).exists()
        elif give_callback_value:
            return await self.filter(
                channel_id=channel_id,
                give_callback_value=give_callback_value
            ).exists()
        elif owner_id:
            return await self.filter(
                channel_id=channel_id,
                owner_id=owner_id
            ).exists()
        return await self.filter(channel_id=channel_id).exists()

    async def get_channel_id(self, channel_callback_value: str) -> list[dict[str, Any]] | dict[str, Any]:
        return await self.filter(channel_callback_value=channel_callback_value).all().values('channel_id')

    async def get_owner_distinct_channels(self, owner_id: int) -> list[dict[str, Any]]:
        """Ushbu adminning barcha unikal kanallarini qaytarish"""
        channels = await self.filter(owner_id=owner_id).all().values(
            'channel_id',
            'name',
            'post_id',
            'group_id',
            'owner_id',
            'give_callback_value',
            'channel_callback_value'
        )
        seen = set()
        distinct = []
        for ch in channels:
            if ch['channel_id'] not in seen:
                seen.add(ch['channel_id'])
                distinct.append(ch)
        return distinct

    async def get_channel_data(
        self,
        channel_callback_value: str = False,
        owner_id: int = False,
        give_callback_value: str = False,
    ):
        if channel_callback_value:
            return await self.filter(channel_callback_value=channel_callback_value).all().values(
                'channel_id',
                'name',
                'post_id',
                'group_id',
                'owner_id',
                'give_callback_value',
                'channel_callback_value'
            )
        elif give_callback_value:
            query = self.filter(give_callback_value=give_callback_value)
            if owner_id:
                query = query.filter(owner_id=owner_id)
            channels = await query.all().values(
                'channel_id',
                'name',
                'post_id',
                'group_id',
                'owner_id',
                'give_callback_value',
                'channel_callback_value'
            )
            # Bir konkurs ichida ham bir xil kanal dublikat bo'lib chiqmasligi uchun dedup qilamiz
            seen = set()
            distinct = []
            for ch in channels:
                if ch['channel_id'] not in seen:
                    seen.add(ch['channel_id'])
                    distinct.append(ch)
            return distinct
        elif owner_id:
            return await self.get_owner_distinct_channels(owner_id=owner_id)
        return []

    async def get_keyboard(self, owner_id: int, give_callback_value: str = False) -> InlineKeyboardMarkup | bool:
        if give_callback_value:
            channels_data = await self.filter(
                owner_id=owner_id,
                give_callback_value=give_callback_value
            ).all().values('name', 'channel_callback_value', 'channel_id')
        else:
            channels_data = await self.filter(
                owner_id=owner_id
            ).all().values('name', 'channel_callback_value', 'channel_id')

        if channels_data:
            # Har bir kanal faqat 1 marta chiqishi uchun channel_id bo'yicha saralaymiz
            seen_channel_ids = set()
            distinct_channels = []
            for ch in channels_data:
                if ch['channel_id'] not in seen_channel_ids:
                    seen_channel_ids.add(ch['channel_id'])
                    distinct_channels.append(ch)

            markup = InlineKeyboardMarkup()
            for channel in distinct_channels:
                markup.add(InlineKeyboardButton(
                    f"📢 {channel['name']}",
                    callback_data=channel['channel_callback_value'],
                    style="primary"
                ))
            return markup
        else:
            return False
