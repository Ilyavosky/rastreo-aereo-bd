"""maneuvers log and extended generation statistics

Revision ID: 0005
Revises: 0004
Create Date: 2026-11-27
"""
import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None

MANEUVER_KINDS = "'outbound', 'search', 'return'"


def upgrade() -> None:
    op.create_table(
        "maneuvers",
        sa.Column(
            "solution_id",
            sa.Integer(),
            sa.ForeignKey("solutions.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("drone_index", sa.Integer(), primary_key=True),
        sa.Column("seq", sa.Integer(), primary_key=True),
        sa.Column("drone_id", sa.Integer(), nullable=False),
        sa.Column("kind", sa.String(16), nullable=False),
        sa.Column("x0", sa.Float(), nullable=False),
        sa.Column("y0", sa.Float(), nullable=False),
        sa.Column("h0", sa.Float(), nullable=False),
        sa.Column("x1", sa.Float(), nullable=False),
        sa.Column("y1", sa.Float(), nullable=False),
        sa.Column("h1", sa.Float(), nullable=False),
        sa.Column("distance_m", sa.Float(), nullable=False),
        sa.Column("altitude_change_m", sa.Float(), nullable=False),
        sa.Column("speed_start_ms", sa.Float(), nullable=False),
        sa.Column("speed_cruise_ms", sa.Float(), nullable=False),
        sa.Column("speed_end_ms", sa.Float(), nullable=False),
        sa.Column("accel_ms2", sa.Float(), nullable=False),
        sa.Column("t_start_s", sa.Float(), nullable=False),
        sa.Column("t_end_s", sa.Float(), nullable=False),
        sa.Column("t_accel_s", sa.Float(), nullable=False),
        sa.Column("t_cruise_s", sa.Float(), nullable=False),
        sa.Column("t_brake_s", sa.Float(), nullable=False),
        sa.Column("t_vertical_s", sa.Float(), nullable=False),
        sa.Column("energy_base_wh", sa.Float(), nullable=False),
        sa.Column("energy_drag_wh", sa.Float(), nullable=False),
        sa.Column("energy_climb_wh", sa.Float(), nullable=False),
        sa.Column("energy_accel_wh", sa.Float(), nullable=False),
        sa.Column("battery_remaining_pct", sa.Float(), nullable=False),
        sa.Column("camera_energy_wh", sa.Float(), nullable=False),
        sa.CheckConstraint(f"kind IN ({MANEUVER_KINDS})", name="ck_maneuvers_kind"),
        sa.CheckConstraint("t_end_s >= t_start_s", name="ck_maneuvers_time"),
    )
    op.add_column("generations", sa.Column("evaluations", sa.Integer(), nullable=True))
    op.add_column("generations", sa.Column("elapsed_s", sa.Float(), nullable=True))
    op.add_column("generations", sa.Column("n_front", sa.Integer(), nullable=True))
    op.add_column("generations", sa.Column("mean_r_de", sa.Float(), nullable=True))
    op.add_column("generations", sa.Column("mean_t_mission_min", sa.Float(), nullable=True))
    op.add_column("generations", sa.Column("mean_e_total_wh", sa.Float(), nullable=True))


def downgrade() -> None:
    for column in (
        "mean_e_total_wh", "mean_t_mission_min", "mean_r_de", "n_front", "elapsed_s", "evaluations",
    ):
        op.drop_column("generations", column)
    op.drop_table("maneuvers")
