import enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import TIMESTAMP, Table, Column, String, Date, ForeignKey, text
from typing import Annotated, List, Optional
from datetime import date, time
from database import Base

intpk = Annotated[int, mapped_column(primary_key=True)]


class FightInfo(Base):
    __tablename__ = "fightinfos"
    id: Mapped[intpk]
    wrestling_type: Mapped[str]
    fight_date: Mapped[date] = mapped_column(Date)
    location: Mapped[str] = mapped_column(String(200))
    weight_category: Mapped[int]
    stage: Mapped[str]
    author: Mapped[str] = mapped_column(String(60), nullable=True)
    decision: Mapped[str]
    oponent1_point: Mapped[int]
    oponent2_point: Mapped[int]
    level: Mapped[str] = mapped_column(nullable=True, server_default="Senior")
    is_submitted: Mapped[bool] = mapped_column(nullable=True, server_default=text('false'))
    ##foreignkeys##
    fighter_id: Mapped[int] = mapped_column(ForeignKey("fighters.id"))
    oponent_id: Mapped[int] = mapped_column(ForeignKey("fighters.id"))
    winner_id: Mapped[int] = mapped_column(ForeignKey("fighters.id"))
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournaments.id"))

    ## relations##
    tournament: Mapped["Tournament"] = relationship(
        back_populates="fightinfos"
    )
    fight_statistic: Mapped[List["FightStatistic"]] = relationship(back_populates="fightinfos",
                                                             primaryjoin="FightInfo.id==FightStatistic.fight_id")
    fighter: Mapped["Fighter"] = relationship(
        back_populates="fighter_info", uselist=False, foreign_keys=[fighter_id]
    )
    oponent: Mapped["Fighter"] = relationship(
        back_populates="oponent_info", uselist=False, foreign_keys=[oponent_id]
    )
    winner: Mapped["Fighter"] = relationship(
        back_populates="winner", uselist=False, foreign_keys=[winner_id]
    )

class Fighter(Base):
    __tablename__ = "fighters"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(255))
    birth_date: Mapped[date] = mapped_column(Date)
    level: Mapped[str] = mapped_column(String(255))
    natinality_name: Mapped[str] = mapped_column(String(255))

    fight_statistic: Mapped["FightStatistic"] = relationship(
        back_populates="fighter", foreign_keys="FightStatistic.fighter_id"
    )
    oponent_statistic: Mapped["FightStatistic"] = relationship(
        back_populates="opponent", uselist=False, foreign_keys="FightStatistic.opponent_id"
    )
    fighter_info: Mapped["FightInfo"] = relationship(
        back_populates="fighter", uselist=False, foreign_keys="FightInfo.fighter_id"
    )
    oponent_info: Mapped["FightInfo"] = relationship(
        back_populates="oponent", uselist=False, foreign_keys="FightInfo.oponent_id"
    )
    winner: Mapped["FightInfo"] = relationship(
        back_populates="winner", uselist=False, foreign_keys="FightInfo.winner_id"
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
    # action_time: Mapped[str] = mapped_column(String(15), nullable=True)
    action_time_second: Mapped[int]
    action_number: Mapped[str]
    score: Mapped[int]
    successful: Mapped[bool]
    author: Mapped[str] = mapped_column(String(100))
    # fighter_number: Mapped[int] #delete this column
    video_second_begin = Column(TIMESTAMP, nullable=True)
    video_second_end = Column(TIMESTAMP, nullable=True)
    video_link: Mapped[str] = mapped_column(String(100), nullable=True)
    defense_reason: Mapped[bool]

    ##foreignkeys##
    fight_id: Mapped[int] = mapped_column(ForeignKey("fightinfos.id"))
    action_name_id: Mapped[int] = mapped_column(ForeignKey("actions.id"))
    technique_id: Mapped[int] = mapped_column(ForeignKey("techniques.id"))
    fighter_id: Mapped[int] = mapped_column(ForeignKey("fighters.id"))
    opponent_id: Mapped[int] = mapped_column(ForeignKey("fighters.id"), nullable=True)


    ## relations##
    technique: Mapped["Technique"] = relationship(
        back_populates="fightstatistics",
        
    )
    fighter: Mapped["Fighter"] = relationship(
        back_populates="fight_statistic", foreign_keys=[fighter_id]
    )
    opponent: Mapped["Fighter"] = relationship(
        back_populates="oponent_statistic", foreign_keys=[opponent_id]
    )
    action_name: Mapped["ActionName"] = relationship(
        back_populates="action_fightstatistics"
    )
    fightinfos: Mapped["FightInfo"] = relationship(
        back_populates="fight_statistic", uselist=True
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
    date = Column(Date)

    ## relations##
    fightinfos: Mapped[List["FightInfo"]] = relationship(
        back_populates="tournament"
    )

class Technique(Base):
    __tablename__ = "techniques"
    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(100))

    ## relations##
    fightstatistics: Mapped[List["FightStatistic"]] = relationship(
        back_populates="technique"
    )



# class DecisionEnum(enum.Enum):
#     VPO1 = "VPO1"
#     VSU = "VSU"
#     VPO = "VPO"
#     VFO = "VFO"
#     VIN = "VIN"
#     VFA = "VFA"

# class LevelEnum(enum.Enum):
#     Seniors = "Seniors"
#     U17 = "U17"
#     U20 = "U20"
#     U23 = "U23"
#     Veterans = "Veterans"


# class StageEnum(enum.Enum):
#     Qualification = "Qualification"
#     GOLD = "GOLD"
#     BRONZE = "BRONZE"
#     Repechage = "Repechage"
#     onesixteen = "1/16"
#     oneeighth = "1/8"
#     onequarter = "1/4"
#     onehalf = "1/2"
#     Final = "Final"


# class WrestlingTypeEnum(enum.Enum):
#     Freestyle = "Freestyle"

# id e gore fight ifno goturmek

# fight infonun icine statisticani elave etmek
    
# technequenin apisini yazmaq
    
# statistic post - fighter_id, opponent_id, second, score, action_id, successfull, technique_id, defense_reason, author