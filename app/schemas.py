from typing import Literal

from pydantic import BaseModel, Field

Comparison = Literal["eq", "lte", "gte", "contains", "text"]


class Filter(BaseModel):
    field: Literal[
        "name", "size", "creature_type", "alignment", "challenge_rating", "armor_class",
        "hit_points", "strength", "dexterity", "constitution", "intelligence", "wisdom",
        "charisma", "damage_immunity", "damage_resistance", "damage_vulnerability",
        "condition_immunity", "feature_text",
    ]
    operator: Comparison
    value: str | int | float


class QueryPlan(BaseModel):
    filters: list[Filter] = Field(default_factory=list, max_length=12)
    limit: int = Field(default=20, ge=1, le=100)


class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    limit: int = Field(default=20, ge=1, le=100)


class MonsterSummary(BaseModel):
    slug: str
    name: str
    size: str | None
    creature_type: str | None
    alignment: str | None
    challenge_rating: float | None
    armor_class: int | None
    hit_points: int | None


class QueryResponse(BaseModel):
    interpretation: QueryPlan
    parser: Literal["rules", "ollama", "fallback"]
    results: list[MonsterSummary]
