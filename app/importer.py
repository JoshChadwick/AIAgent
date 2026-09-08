"""Repeatably import the supplied source JSON without modifying it."""

import json
import re
from html import unescape
from pathlib import Path

from sqlalchemy import delete

from app.database import SessionLocal
from app.models import Monster, MonsterDefense, MonsterFeature

SOURCE_FILE = Path(__file__).resolve().parents[1] / "Data" / "srd_5e_monsters.json"


def first_int(value: str | None) -> int | None:
    match = re.search(r"\d+", value or "")
    return int(match.group()) if match else None


def parse_cr(value: str) -> float | None:
    match = re.match(r"\s*(\d+)(?:/(\d+))?", value)
    if not match:
        return None
    return int(match.group(1)) / int(match.group(2) or 1)


def parse_xp(value: str) -> int | None:
    match = re.search(r"\(([\d,]+) XP\)", value)
    return int(match.group(1).replace(",", "")) if match else None


def parse_meta(value: str) -> tuple[str | None, str | None, str | None]:
    left, _, alignment = value.partition(",")
    parts = left.strip().split(maxsplit=1)
    return (parts[0] if parts else None, parts[1] if len(parts) > 1 else None, alignment.strip() or None)


def parse_speeds(value: str) -> dict[str, int | None]:
    output = {key: None for key in ("walk", "fly", "swim", "climb", "burrow")}
    for mode, distance in re.findall(r"(?:(walk|fly|swim|climb|burrow)\s*)?(\d+)\s*ft", value, re.IGNORECASE):
        output[(mode or "walk").lower()] = int(distance)
    return output


def text_from_html(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def feature_name(value: str) -> str | None:
    match = re.search(r"<strong>([^<]+)</strong>", value)
    return unescape(match.group(1)).strip(". ") if match else None


def feature_blocks(value: str) -> list[str]:
    blocks = re.findall(r"<p[^>]*>.*?</p>", value, flags=re.IGNORECASE | re.DOTALL)
    return blocks or [value]


def split_values(value: str | None) -> list[str]:
    return [item.strip().lower() for item in (value or "").split(",") if item.strip()]


def import_records(source: Path = SOURCE_FILE) -> int:
    records = json.loads(source.read_text(encoding="utf-8"))
    with SessionLocal.begin() as session:
        session.execute(delete(MonsterDefense))
        session.execute(delete(MonsterFeature))
        session.execute(delete(Monster))
        for raw in records:
            size, creature_type, alignment = parse_meta(raw["meta"])
            speeds = parse_speeds(raw["Speed"])
            monster = Monster(
                slug=re.sub(r"[^a-z0-9]+", "-", raw["name"].lower()).strip("-"),
                name=raw["name"], size=size, creature_type=creature_type, alignment=alignment,
                armor_class=first_int(raw["Armor Class"]), armor_class_detail=raw["Armor Class"],
                hit_points=first_int(raw["Hit Points"]), hit_dice=raw["Hit Points"],
                challenge_rating=parse_cr(raw["Challenge"]), xp=parse_xp(raw["Challenge"]),
                speed_walk_ft=speeds["walk"], speed_fly_ft=speeds["fly"], speed_swim_ft=speeds["swim"],
                speed_climb_ft=speeds["climb"], speed_burrow_ft=speeds["burrow"],
                strength=int(raw["STR"]), dexterity=int(raw["DEX"]), constitution=int(raw["CON"]),
                intelligence=int(raw["INT"]), wisdom=int(raw["WIS"]), charisma=int(raw["CHA"]),
                senses_text=raw["Senses"], languages_text=raw["Languages"], image_url=raw.get("img_url"),
                raw_source_json=raw,
            )
            session.add(monster)
            session.flush()
            for label, category in {
                "Damage Immunities": "damage_immunity", "Damage Resistances": "damage_resistance",
                "Damage Vulnerabilities": "damage_vulnerability", "Condition Immunities": "condition_immunity",
            }.items():
                session.add_all(MonsterDefense(monster_id=monster.id, category=category, value=item)
                                for item in split_values(raw.get(label)))
            for label, kind in {"Traits": "trait", "Actions": "action", "Reactions": "reaction",
                                "Legendary Actions": "legendary_action"}.items():
                if value := raw.get(label):
                    session.add_all(
                        MonsterFeature(monster_id=monster.id, kind=kind, name=feature_name(block),
                                       description_html=block, description_text=text_from_html(block), ordinal=ordinal)
                        for ordinal, block in enumerate(feature_blocks(value))
                    )
    return len(records)


if __name__ == "__main__":
    print(f"Imported {import_records()} monsters.")
