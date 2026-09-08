"""initial monster schema"""

import sqlalchemy as sa

from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("monsters", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("slug", sa.String(180), nullable=False, unique=True), sa.Column("name", sa.String(180), nullable=False, unique=True), sa.Column("size", sa.String(20)), sa.Column("creature_type", sa.String(80)), sa.Column("alignment", sa.String(80)), sa.Column("armor_class", sa.Integer()), sa.Column("armor_class_detail", sa.String(200)), sa.Column("hit_points", sa.Integer()), sa.Column("hit_dice", sa.String(80)), sa.Column("challenge_rating", sa.Float()), sa.Column("xp", sa.Integer()), sa.Column("speed_walk_ft", sa.Integer()), sa.Column("speed_fly_ft", sa.Integer()), sa.Column("speed_swim_ft", sa.Integer()), sa.Column("speed_climb_ft", sa.Integer()), sa.Column("speed_burrow_ft", sa.Integer()), sa.Column("strength", sa.Integer(), nullable=False), sa.Column("dexterity", sa.Integer(), nullable=False), sa.Column("constitution", sa.Integer(), nullable=False), sa.Column("intelligence", sa.Integer(), nullable=False), sa.Column("wisdom", sa.Integer(), nullable=False), sa.Column("charisma", sa.Integer(), nullable=False), sa.Column("senses_text", sa.Text(), nullable=False), sa.Column("languages_text", sa.Text(), nullable=False), sa.Column("image_url", sa.Text()), sa.Column("raw_source_json", sa.JSON(), nullable=False))
    for column in ("slug", "name", "size", "creature_type", "alignment", "armor_class", "hit_points", "challenge_rating", "xp"):
        op.create_index(f"ix_monsters_{column}", "monsters", [column])
    op.create_table("monster_defenses", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("monster_id", sa.Integer(), sa.ForeignKey("monsters.id"), nullable=False), sa.Column("category", sa.String(32), nullable=False), sa.Column("value", sa.String(80), nullable=False), sa.UniqueConstraint("monster_id", "category", "value"))
    for column in ("monster_id", "category", "value"):
        op.create_index(f"ix_monster_defenses_{column}", "monster_defenses", [column])
    op.create_table("monster_features", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("monster_id", sa.Integer(), sa.ForeignKey("monsters.id"), nullable=False), sa.Column("kind", sa.String(24), nullable=False), sa.Column("name", sa.String(200)), sa.Column("description_html", sa.Text(), nullable=False), sa.Column("description_text", sa.Text(), nullable=False), sa.Column("ordinal", sa.Integer(), nullable=False))
    op.create_index("ix_monster_features_monster_id", "monster_features", ["monster_id"])
    op.create_index("ix_monster_features_kind", "monster_features", ["kind"])


def downgrade() -> None:
    op.drop_table("monster_features")
    op.drop_table("monster_defenses")
    op.drop_table("monsters")
