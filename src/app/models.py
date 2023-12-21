import enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import TIMESTAMP, Table, Column, String, Date, ForeignKey, Time
from typing import Annotated, List, Optional
from datetime import date, time
from database import Base

intpk = Annotated[int, mapped_column(primary_key=True)]

class DecisionEnum(enum.Enum):
    VPO1 = "VPO1"
    VSU = "VSU"
    VPO = "VPO"
    VFO = "VFO"
    VIN = "VIN"
    VFA = "VFA"

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
    birth_date: Mapped[date] = mapped_column(Date)
    level: Mapped[LevelEnum]
    ##foreignkeys##
    # nationality_id = mapped_column(ForeignKey("nationalities.id"))
    natinality_name: Mapped[str] = mapped_column(String(5))
    ## relations##
    # nationality: Mapped["Nationality"] = relationship(
    #     back_populates="figthers"
    # )
    fight_statistic: Mapped["FightStatistic"] = relationship(
        back_populates="fighter"
    )
    fighter_info: Mapped["FightInfo"] = relationship(
        back_populates="fighter"
    )
    oponent_info: Mapped["FightInfo"] = relationship(
        back_populates="oponent"
    )
    winner_info: Mapped["FightInfo"] = relationship(
        back_populates="winner"
    )


class Nationality(Base):
    __tablename__ = "nationalities"
    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(50))

    ## relations##
    # figthers: Mapped[List["Fighter"]] = relationship(
    #     back_populates="nationality"
    # )


class Tournament(Base):
    __tablename__ = "tournaments"
    id: Mapped[intpk]
    name: Mapped[str]

    ## relations##
    fightinfos: Mapped[List["FightInfo"]] = relationship(
        back_populates="tournament"
    )


class FightInfo(Base):
    __tablename__ = "fightinfos"
    id: Mapped[intpk]
    wrestling_type: Mapped[WrestlingTypeEnum]
    fight_date: Mapped[date] = mapped_column(Date)
    location: Mapped[str] = mapped_column(String(200))
    weight_category: Mapped[str] = mapped_column(String(50))
    stage: Mapped[StageEnum]
    author: Mapped[str] = mapped_column(String(60))
    decision: Mapped[DecisionEnum]
    oponent1_point: Mapped[int]
    oponent2_point: Mapped[int]

    ##foreignkeys##
    fighter_id: Mapped[int] = mapped_column(ForeignKey("fighters.id"))
    oponent_id: Mapped[int] = mapped_column(ForeignKey("fighters.id"))
    winner_id: Mapped[int] = mapped_column(ForeignKey("fighters.id"))
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournaments.id"))

    ## relations##
    tournament: Mapped["Tournament"] = relationship(
        back_populates="fightinfos"
    )
    fight_statistic: Mapped["FightStatistic"] = relationship(back_populates="fightinfos", uselist=False)
    fighter: Mapped["Fighter"] = relationship(
        back_populates= "fighter_info", uselist=False
    )
    oponent: Mapped["Fighter"] = relationship(
        back_populates= "oponent_info", uselist=False
    )
    winner: Mapped["Fighter"] = relationship(
        back_populates= "winner", uselist=False
    )


class ActionName(Base):
    __tablename__ = "actions"
    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(100))
    
    ## relations##
    action_fightstatistics: Mapped[List["FightStatistic"]] = relationship(
        back_populates="action_name"
    )

class FightStatistic(Base):
    __tablename__ = "fightstatistics"
    id: Mapped[intpk]
    action_time: Mapped[str] = mapped_column(String(15))
    action_time_second: Mapped[int]
    action_number: Mapped[int]
    score: Mapped[int]
    successful: Mapped[bool]
    fighter_number: Mapped[int]
    video_second_begin = Column(TIMESTAMP)
    video_second_end = Column(TIMESTAMP)
    video_link: Mapped[str] = mapped_column(String(100))
    

    ##foreignkeys##
    fight_id: Mapped[int] = mapped_column(ForeignKey("fightinfos.id"))
    action_name_id: Mapped[int] = mapped_column(ForeignKey("actions.id"))
    technique_id: Mapped[int] = mapped_column(ForeignKey("techniques.id"))
    fighter_id: Mapped[int] = mapped_column(ForeignKey("fighters.id"))

    ## relations##
    technique: Mapped["Technique"] = relationship(
        back_populates="fightstatistics",
        
    )
    fighter: Mapped["Fighter"] = relationship(
        back_populates="fight_statistic"
    )
    action_name: Mapped["ActionName"] = relationship(
        back_populates="action_fightstatistics"
    )
    fightinfos: Mapped["FightInfo"] = relationship(
        back_populates="fight_statistic"
    )


class Technique(Base):
    __tablename__ = "techniques"
    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(100))

    ## relations##
    fightstatistics: Mapped[List["FightStatistic"]] = relationship(
        back_populates="technique"
    )





