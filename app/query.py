import json
import re

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Monster, MonsterDefense, MonsterFeature
from app.schemas import Filter, QueryPlan

SIZES = {"tiny", "small", "medium", "large", "huge", "gargantuan"}
TYPES = {"aberration", "beast", "celestial", "construct", "dragon", "elemental", "fey", "fiend", "giant", "humanoid", "monstrosity", "ooze", "plant", "undead"}


def number(value: str) -> float:
    numerator, _, denominator = value.partition("/")
    return int(numerator) / int(denominator or 1)


def parse_rules(query: str, limit: int = 20) -> QueryPlan:
    text = query.lower()
    filters: list[Filter] = []
    for size in SIZES:
        if re.search(rf"\b{size}\b", text):
            filters.append(Filter(field="size", operator="eq", value=size.title()))
    for creature_type in TYPES:
        if re.search(rf"\b{creature_type}s?\b", text):
            filters.append(Filter(field="creature_type", operator="eq", value=creature_type))
    cr = re.search(r"\b(?:cr|challenge rating)\s*(?:of\s*)?(\d+(?:/\d+)?)\s*(or lower|or less|or higher|or more|and below|and above)?", text)
    if cr:
        suffix = cr.group(2) or ""
        filters.append(Filter(field="challenge_rating", operator="gte" if "higher" in suffix or "more" in suffix or "above" in suffix else "lte" if suffix else "eq", value=number(cr.group(1))))
    for stat, field in {"strength": "strength", "dexterity": "dexterity", "constitution": "constitution", "intelligence": "intelligence", "wisdom": "wisdom", "charisma": "charisma", "ac": "armor_class", "armor class": "armor_class", "hp": "hit_points", "hit points": "hit_points"}.items():
        found = re.search(rf"\b{re.escape(stat)}\s*(?:of\s*)?(\d+)\s*(or lower|or less|or higher|or more)?", text)
        if found:
            suffix = found.group(2) or ""
            filters.append(Filter(field=field, operator="gte" if "higher" in suffix or "more" in suffix else "lte" if suffix else "eq", value=int(found.group(1))))
    defense = re.search(r"\b(?:immune to|immunity to)\s+([a-z ]+?)(?=\s+(?:and|with|that)\b|$)", text)
    if defense:
        filters.append(Filter(field="damage_immunity", operator="contains", value=defense.group(1).strip()))
    feature = re.search(r"\b(?:with|has|have)\s+(.+)$", text)
    if feature and not filters:
        filters.append(Filter(field="feature_text", operator="text", value=feature.group(1).strip()))
    return QueryPlan(filters=filters, limit=limit)


async def parse_with_ollama(query: str, limit: int) -> QueryPlan | None:
    settings = get_settings()
    if not settings.ollama_enabled:
        return None
    schema = '{"filters":[{"field":"allowed field","operator":"eq|lte|gte|contains|text","value":"value"}]}'
    allowed_fields = "name, size, creature_type, alignment, challenge_rating, armor_class, hit_points, strength, dexterity, constitution, intelligence, wisdom, charisma, damage_immunity, damage_resistance, damage_vulnerability, condition_immunity, feature_text"
    prompt = f"Convert this D&D monster search to JSON only. Allowed fields: {allowed_fields}. Use {schema}. Query: {query}"
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(f"{settings.ollama_url}/api/generate", json={"model": settings.ollama_model, "prompt": prompt, "stream": False, "format": "json"})
            response.raise_for_status()
        payload = json.loads(response.json()["response"])
        payload["limit"] = limit
        return QueryPlan.model_validate(payload)
    except (httpx.HTTPError, KeyError, ValueError):
        return None


def execute_plan(session: Session, plan: QueryPlan) -> list[Monster]:
    statement = select(Monster)
    direct_fields = {name: getattr(Monster, name) for name in ("name", "size", "creature_type", "alignment", "challenge_rating", "armor_class", "hit_points", "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma")}
    defenses = {"damage_immunity", "damage_resistance", "damage_vulnerability", "condition_immunity"}
    for item in plan.filters:
        if item.field in direct_fields:
            column = direct_fields[item.field]
            statement = statement.where({"eq": column == item.value, "lte": column <= item.value, "gte": column >= item.value, "contains": column.ilike(f"%{item.value}%"), "text": column.ilike(f"%{item.value}%")}[item.operator])
        elif item.field in defenses:
            statement = statement.where(Monster.defenses.any((MonsterDefense.category == item.field) & (MonsterDefense.value.ilike(f"%{item.value}%"))))
        elif item.field == "feature_text":
            statement = statement.where(Monster.features.any(MonsterFeature.description_text.ilike(f"%{item.value}%")))
    return list(session.scalars(statement.order_by(Monster.challenge_rating, Monster.name).limit(plan.limit)))
