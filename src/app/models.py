import enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import TIMESTAMP, Table, Column, String, Date, ForeignKey, Time
from typing import Annotated, List, Optional
from datetime import date, time
from database import Base

intpk = Annotated[int, mapped_column(primary_key=True)]


class LevelEnum(enum.Enum):
    Seniors = "Seniors"
    U17 = "U17"
    U20 = "U20"
    U23 = "U23"
    Veterans = "Veterans"


class StageEnum(enum.Enum):
    Qualification = "Qualification"
    onesixteen = "1/16"
    oneeighth = "1/8"
    onequarter = "1/4"
    onehalf = "1/2"
    Final = "Final"


class WrestlingTypeEnum(enum.Enum):
    Freestyle = "Freestyle"


class Fighter(Base):
    __tablename__ = "fighters"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(50))
    nationality_id = mapped_column(ForeignKey("nationalities.id"))
    birth_date: Mapped[date] = mapped_column(Date)
    level: Mapped[LevelEnum]
    nationality: Mapped["Nationality"] = relationship(
        back_populates="fighters"
    )
    fight_statistic: Mapped["FightStatistic"] = relationship(
        back_populates="fighter"
    )


class Nationality(Base):
    __tablename__ = "nationalities"
    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(50))
    figthers: Mapped[List["Fighter"]] = relationship(
        back_populates="nationality"
    )


class Tournament(Base):
    __tablename__ = "tournaments"
    id: Mapped[intpk]
    name: Mapped[str]
    fightinfos: Mapped[List["FightInfo"]] = relationship(
        back_populates="tournament"
    )


class FightInfo(Base):
    __tablename__ = "fightinfos"
    id: Mapped[intpk]
    fighter_id: Mapped[int] = mapped_column(ForeignKey("fighters.id"))
    oponent_id: Mapped[int] = mapped_column(ForeignKey("fighters.id"))
    wrestling_type: Mapped[WrestlingTypeEnum]
    fight_date: Mapped[date] = mapped_column(Date)
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournaments.id"))
    location: Mapped[str] = mapped_column(String(200))
    weight_category: Mapped[str] = mapped_column(String(50))
    stage: Mapped[StageEnum]
    author: Mapped[str] = mapped_column(String(60))
    tournament: Mapped["Tournament"] = relationship(
        back_populates="fightinfos"
    )
    fight_statistic = relationship("FightStatistic", back_populates="fightinfos", uselist=False)


class FightStatistic(Base):
    __tablename__ = "fightstatistics"
    id: Mapped[intpk]
    fight_id: Mapped[int] = mapped_column(ForeignKey("fightinfos.id"))
    action_time: Mapped[str] = mapped_column(String(15))
    action_time_second: Mapped[int]
    fighter_number: Mapped[int]
    score: Mapped[int]
    action: Mapped[int]
    successful: Mapped[bool]
    technique_id: Mapped[int] = mapped_column(ForeignKey("techniques.id"))
    video_second_begin = Column(TIMESTAMP)
    video_second_end = Column(TIMESTAMP)
    video_link: Mapped[str] = mapped_column(String(100))
    fighter_id: Mapped[int] = mapped_column(ForeignKey("fighters.id"))
    technique: Mapped["Technique"] = relationship(
        back_populates="fightstatistics"
    )
    fighter: Mapped["Fighter"] = relationship(
        back_populates="fight_statistic"
    )


class Technique(Base):
    __tablename__ = "techniques"
    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(100))
    fightstatistics: Mapped[List["FightStatistic"]] = relationship(
        back_populates="technique"
    )





