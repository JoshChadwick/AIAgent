from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Monster
from app.query import execute_plan, parse_rules, parse_with_ollama
from app.schemas import Filter, MonsterSummary, QueryPlan, QueryRequest, QueryResponse

app = FastAPI(title="SRD Monster Query API", version="0.1.0")


def summary(monster: Monster) -> MonsterSummary:
    return MonsterSummary(slug=monster.slug, name=monster.name, size=monster.size,
                          creature_type=monster.creature_type, alignment=monster.alignment,
                          challenge_rating=monster.challenge_rating, armor_class=monster.armor_class,
                          hit_points=monster.hit_points)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/monsters/{slug}")
def get_monster(slug: str, session: Session = Depends(get_session)) -> dict:
    monster = session.scalar(select(Monster).where(Monster.slug == slug))
    if not monster:
        raise HTTPException(status_code=404, detail="Monster not found")
    return monster.raw_source_json


@app.get("/v1/monsters", response_model=list[MonsterSummary])
def list_monsters(
    creature_type: str | None = None,
    size: str | None = None,
    cr_lte: float | None = Query(default=None, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_session),
) -> list[MonsterSummary]:
    """Structured alternative to natural-language search."""
    filters = []
    if creature_type:
        filters.append(Filter(field="creature_type", operator="eq", value=creature_type.lower()))
    if size:
        filters.append(Filter(field="size", operator="eq", value=size.title()))
    if cr_lte is not None:
        filters.append(Filter(field="challenge_rating", operator="lte", value=cr_lte))
    return [summary(monster) for monster in execute_plan(session, QueryPlan(filters=filters, limit=limit))]


@app.post("/v1/query", response_model=QueryResponse)
async def natural_query(request: QueryRequest, session: Session = Depends(get_session)) -> QueryResponse:
    plan = parse_rules(request.query, request.limit)
    parser = "rules"
    if not plan.filters:
        llm_plan = await parse_with_ollama(request.query, request.limit)
        if llm_plan:
            plan, parser = llm_plan, "ollama"
        else:
            parser = "fallback"
    return QueryResponse(interpretation=plan, parser=parser, results=[summary(monster) for monster in execute_plan(session, plan)])
