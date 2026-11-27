"""runs, generations and solutions

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-25
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None

RUN_STATUSES = "'queued', 'running', 'completed', 'failed', 'cancelled'"
SOLUTION_PROFILES = (
    "'pareto', 'best_detection', 'lowest_consumption', 'balanced', 'grid', "
    "'random_best_detection', 'random_lowest_consumption', 'random_balanced'"
)


def upgrade() -> None:
    op.create_table(
        "runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("scenario_id", sa.Integer(), sa.ForeignKey("scenarios.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("cancel_requested", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("progress", sa.Float(), nullable=False, server_default="0"),
        sa.Column("params", postgresql.JSONB(), nullable=False),
        sa.Column("scenario_snapshot", postgresql.JSONB(), nullable=False),
        sa.Column("catalog_snapshot", postgresql.JSONB(), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(f"status IN ({RUN_STATUSES})", name="ck_runs_status"),
        sa.CheckConstraint("progress >= 0 AND progress <= 1", name="ck_runs_progress"),
    )
    op.create_index("ix_runs_status", "runs", ["status"])
    op.create_table(
        "generations",
        sa.Column("run_id", sa.Integer(), sa.ForeignKey("runs.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("gen", sa.Integer(), primary_key=True),
        sa.Column("n_feasible", sa.Integer(), nullable=False),
        sa.Column("best_r_de", sa.Float(), nullable=True),
        sa.Column("best_t_mission_min", sa.Float(), nullable=True),
        sa.Column("best_e_total_wh", sa.Float(), nullable=True),
        sa.Column("hypervolume", sa.Float(), nullable=True),
    )
    op.create_table(
        "solutions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_id", sa.Integer(), sa.ForeignKey("runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("profile", sa.String(32), nullable=False),
        sa.Column("feasible", sa.Boolean(), nullable=False),
        sa.Column("constraint_violation", sa.Float(), nullable=False),
        sa.Column("r_de", sa.Float(), nullable=False),
        sa.Column("t_mission_min", sa.Float(), nullable=False),
        sa.Column("e_total_wh", sa.Float(), nullable=False),
        sa.Column("area_explored_pct", sa.Float(), nullable=False),
        sa.Column("area_detected_pct", sa.Float(), nullable=False),
        sa.Column("chromosome", postgresql.JSONB(), nullable=False),
        sa.Column("route", postgresql.JSONB(), nullable=False),
        sa.CheckConstraint(f"profile IN ({SOLUTION_PROFILES})", name="ck_solutions_profile"),
    )
    op.create_index("ix_solutions_run_profile", "solutions", ["run_id", "profile"])


def downgrade() -> None:
    op.drop_index("ix_solutions_run_profile", table_name="solutions")
    op.drop_table("solutions")
    op.drop_table("generations")
    op.drop_index("ix_runs_status", table_name="runs")
    op.drop_table("runs")
