from tortoise import Model, fields


class MandatoryChannel(Model):
    id = fields.IntField(pk=True)
    channel_id = fields.BigIntField()
    name = fields.TextField()
    invite_link = fields.TextField(null=True)
    is_active = fields.BooleanField(default=True)

    @classmethod
    async def add_channel(cls, channel_id: int, name: str, invite_link: str = None):
        existing = await cls.filter(channel_id=channel_id).first()
        if existing:
            await cls.filter(id=existing.id).update(
                name=name,
                invite_link=invite_link or existing.invite_link,
                is_active=True
            )
            return existing.id
        created = await cls.create(
            channel_id=channel_id,
            name=name,
            invite_link=invite_link,
            is_active=True
        )
        return created.id

    @classmethod
    async def get_active_channels(cls) -> list[dict]:
        return await cls.filter(is_active=True).all().values('id', 'channel_id', 'name', 'invite_link')

    @classmethod
    async def delete_channel_by_id(cls, channel_pk: int):
        await cls.filter(id=channel_pk).delete()
