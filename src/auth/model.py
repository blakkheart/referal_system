from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column

from database.db import async_session_factory, Base


class User(Base):
    __tablename__ = 'user_table'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    phone_number: Mapped[str] = mapped_column(String(15))
    invite_code: Mapped[str | None] = mapped_column(String(6), default=None)
    used_code: Mapped[str | None] = mapped_column(String(6), default=None)

    @property
    async def used_invite_code(self):
        async with async_session_factory() as session:
            query = select(User).filter_by(used_code=self.invite_code)
            result = await session.execute(query)
            list_of_users: list[User] = result.scalars().all()
            return list_of_users
