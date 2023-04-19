import datetime
from sqlalchemy import Integer, String, ForeignKey, Boolean, DATE
from sqlalchemy.orm import (
    declarative_base,
    relationship,
    Mapped,
    mapped_column,
)

from sqlalchemy.dialects.postgresql import JSON

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    is_bot: Mapped[bool] = mapped_column(Boolean)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    username: Mapped[str] = mapped_column(String, nullable=True)
    is_premium: Mapped[bool] = mapped_column(Boolean, nullable=True)
    added_to_attachment_menu: Mapped[bool] = mapped_column(Boolean, nullable=True)
    language_code: Mapped[str] = mapped_column(String, nullable=True)

    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    github: Mapped[str] = mapped_column(String, nullable=True)
    fio: Mapped[str] = mapped_column(String, nullable=True)

    defense_records: Mapped[list["DefenseRecord"]] = relationship(
        "DefenseRecord", back_populates="student"
    )

    def __repr__(self):
        return f"User(id='{self.id}', is_bot='{self.is_bot}', first_name='{self.first_name}', last_name='{self.last_name}', username='{self.username}', is_premium='{self.is_premium}', added_to_attachment_menu='{self.added_to_attachment_menu}', is_admin='{self.is_admin}', github='{self.github}', fio='{self.fio}')"


class DefenseRecord(Base):
    __tablename__ = "defense_records"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    student: Mapped[User] = relationship("User", back_populates="defense_records")
    teacher: Mapped[str] = mapped_column(String)
    task: Mapped[str] = mapped_column(String)
    status: Mapped[bool] = mapped_column(Boolean)
    date: Mapped[datetime.datetime] = mapped_column(DATE, nullable=True)
    additional_data: Mapped[str] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"DefenseRecord(id='{self.id}', student_id='{self.student_id}', teacher='{self.teacher}', task='{self.task}', status='{self.status}', additional_data='{self.additional_data}')"
