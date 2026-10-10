from datetime import datetime, timedelta
from typing import NamedTuple

from tortoise import Model, fields

from config import timezone_info


class GiveAwayStatisticInfo(NamedTuple):
    count_members_in_24_hours: int
    count_members_summary: int



class GiveAwayStatistic(Model):
    giveaway_callback_value = fields.TextField(pk=True)
    members = fields.JSONField(null=True)
    post_link = fields.TextField()
    winners = fields.JSONField(null=True)



    async def add_statistic(
        self,
        giveaway_callback_value: str,
        members: list,
        winners: list,
        post_link: str,
    ):
        if not await self.exists(giveaway_callback_value=giveaway_callback_value):

            await self.create(
                giveaway_callback_value=giveaway_callback_value,
                members=members,
                winners=winners,
                post_link=post_link
            )


    async def delete_statistic(self, giveaway_callback_value: str):
        await self.filter(giveaway_callback_value=giveaway_callback_value).delete()



    async def exists_member(
        self,
        giveaway_callback_value: str,
        member_username: str = None,
        member_id: int = None
    ) -> bool:
        old_data = await self.filter(
            giveaway_callback_value=giveaway_callback_value
        ).all().values('members')

        try:
            members = old_data[0]['members'] if old_data and old_data[0].get('members') else []

            for member in members:
                if member_id and member.get('user_id') == member_id:
                    return True
                if member_username and member.get('username') == member_username:
                    return True

            return False

        except (KeyError, IndexError):
            return False

    async def get_data(self, giveaway_callback_value: str) -> dict:
        data = await self.filter(
            giveaway_callback_value=giveaway_callback_value
        ).all().values('members')

        return data

    async def get_members_count(self, giveaway_callback_value: str) -> int:
        old_data = await self.filter(
            giveaway_callback_value=giveaway_callback_value
        ).all().values('members')
        try:
            members = old_data[0]['members'] if old_data and old_data[0].get('members') else []
            return len(members)
        except Exception:
            return 0

    async def get_member_ticket(
        self,
        giveaway_callback_value: str,
        member_id: int,
        member_username: str = None
    ) -> str:
        old_data = await self.filter(
            giveaway_callback_value=giveaway_callback_value
        ).all().values('members')
        try:
            members = old_data[0]['members'] if old_data and old_data[0].get('members') else []
            for idx, member in enumerate(members, 1):
                if member.get('user_id') == member_id or (member_username and member.get('username') == member_username):
                    return member.get('ticket_number', f"#TK-{idx:04d}")
        except Exception:
            pass
        return f"#TK-{member_id % 90000 + 10000:04d}"

    async def get_statistic(self, giveaway_callback_value: str) -> GiveAwayStatisticInfo | bool:
        data = await self.filter(
            giveaway_callback_value=giveaway_callback_value
        ).all().values('members')

        if data:
            count_members_in_24_hours = []
            count_members_summary = []

            members = data[0]['members'] or []
            for member in members:
                try:
                    join_date = datetime.strptime(member["join_date"], "%Y-%m-%d %H:%M:%S.%f%z")
                    if join_date > datetime.now(timezone_info) - timedelta(days=1):
                        count_members_in_24_hours.append(member)
                except Exception:
                    pass

                count_members_summary.append(member.get('username', 'user'))

            return GiveAwayStatisticInfo(
                count_members_in_24_hours=len(count_members_in_24_hours),
                count_members_summary=len(count_members_summary)
            )
        else:
            return False

    async def update_statistic_members(
        self,
        giveaway_callback_value: str,
        new_member_username: str,
        new_member_id: int,
    ) -> bool:
        old_data = await self.filter(
            giveaway_callback_value=giveaway_callback_value
        ).all().values('members')

        members = old_data[0]['members'] if old_data and old_data[0].get('members') else []

        for member in members:
            if new_member_id == member.get('user_id'):
                return False
            if new_member_username and new_member_username == member.get('username'):
                return False

        ticket_number = f"#TK-{len(members) + 1:04d}"
        members.append({
            'username': new_member_username,
            'user_id': new_member_id,
            'ticket_number': ticket_number,
            'join_date': str(datetime.now(timezone_info))
        })

        await self.filter(
            giveaway_callback_value=giveaway_callback_value
        ).update(members=members)

        return True




