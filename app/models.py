from __future__ import annotations

from typing import Any

from sqlalchemy import JSON, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Monster(Base):
    __tablename__ = "monsters"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    size: Mapped[str | None] = mapped_column(String(20), index=True)
    creature_type: Mapped[str | None] = mapped_column(String(80), index=True)
    alignment: Mapped[str | None] = mapped_column(String(80), index=True)
    armor_class: Mapped[int | None] = mapped_column(Integer, index=True)
    armor_class_detail: Mapped[str | None] = mapped_column(String(200))
    hit_points: Mapped[int | None] = mapped_column(Integer, index=True)
    hit_dice: Mapped[str | None] = mapped_column(String(80))
    challenge_rating: Mapped[float | None] = mapped_column(index=True)
    xp: Mapped[int | None] = mapped_column(Integer, index=True)
    speed_walk_ft: Mapped[int | None] = mapped_column(Integer)
    speed_fly_ft: Mapped[int | None] = mapped_column(Integer)
    speed_swim_ft: Mapped[int | None] = mapped_column(Integer)
    speed_climb_ft: Mapped[int | None] = mapped_column(Integer)
    speed_burrow_ft: Mapped[int | None] = mapped_column(Integer)
    strength: Mapped[int] = mapped_column(Integer)
    dexterity: Mapped[int] = mapped_column(Integer)
    constitution: Mapped[int] = mapped_column(Integer)
    intelligence: Mapped[int] = mapped_column(Integer)
    wisdom: Mapped[int] = mapped_column(Integer)
    charisma: Mapped[int] = mapped_column(Integer)
    senses_text: Mapped[str] = mapped_column(Text)
    languages_text: Mapped[str] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(Text)
    raw_source_json: Mapped[dict[str, Any]] = mapped_column(JSON)

    defenses: Mapped[list[MonsterDefense]] = relationship(cascade="all, delete-orphan")
    features: Mapped[list[MonsterFeature]] = relationship(cascade="all, delete-orphan")


class MonsterDefense(Base):
    __tablename__ = "monster_defenses"
    __table_args__ = (UniqueConstraint("monster_id", "category", "value"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    monster_id: Mapped[int] = mapped_column(ForeignKey("monsters.id"), index=True)
    category: Mapped[str] = mapped_column(String(32), index=True)
    value: Mapped[str] = mapped_column(String(80), index=True)


class MonsterFeature(Base):
    __tablename__ = "monster_features"

    id: Mapped[int] = mapped_column(primary_key=True)
    monster_id: Mapped[int] = mapped_column(ForeignKey("monsters.id"), index=True)
    kind: Mapped[str] = mapped_column(String(24), index=True)
    name: Mapped[str | None] = mapped_column(String(200))
    description_html: Mapped[str] = mapped_column(Text)
    description_text: Mapped[str] = mapped_column(Text)
    ordinal: Mapped[int] = mapped_column(Integer)
