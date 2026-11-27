"""catalogs

Revision ID: 0001
Revises:
Create Date: 2026-11-25
"""
import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "drones",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(80), nullable=False, unique=True),
        sa.Column("battery_wh", sa.Float(), nullable=False),
        sa.Column("v_min", sa.Float(), nullable=False),
        sa.Column("v_max", sa.Float(), nullable=False),
        sa.Column("h_min", sa.Float(), nullable=False),
        sa.Column("h_max", sa.Float(), nullable=False),
        sa.Column("v_vertical", sa.Float(), nullable=False),
        sa.Column("p_base_w", sa.Float(), nullable=False),
        sa.Column("c_drag", sa.Float(), nullable=False),
        sa.Column("c_altitude_j_m", sa.Float(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.CheckConstraint("battery_wh > 0", name="ck_drones_battery"),
        sa.CheckConstraint("v_min > 0 AND v_max > v_min", name="ck_drones_speed"),
        sa.CheckConstraint("h_min > 0 AND h_max > h_min", name="ck_drones_height"),
        sa.CheckConstraint("v_vertical > 0 AND p_base_w > 0", name="ck_drones_power"),
        sa.CheckConstraint("c_drag >= 0 AND c_altitude_j_m >= 0", name="ck_drones_coefficients"),
    )
    op.create_table(
        "cameras",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(80), nullable=False, unique=True),
        sa.Column("modality", sa.String(16), nullable=False),
        sa.Column("fov_deg", sa.Float(), nullable=False),
        sa.Column("n_px_width", sa.Integer(), nullable=False),
        sa.Column("power_w", sa.Float(), nullable=False),
        sa.Column("battery_wh", sa.Float(), nullable=False),
        sa.Column("max_range_m", sa.Float(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.CheckConstraint("modality IN ('optical', 'thermal')", name="ck_cameras_modality"),
        sa.CheckConstraint("fov_deg > 0 AND fov_deg < 180", name="ck_cameras_fov"),
        sa.CheckConstraint("n_px_width >= 1", name="ck_cameras_pixels"),
        sa.CheckConstraint("power_w >= 0 AND battery_wh > 0 AND max_range_m > 0", name="ck_cameras_limits"),
    )
    op.create_table(
        "persons",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(80), nullable=False, unique=True),
        sa.Column("posture", sa.String(16), nullable=False),
        sa.Column("critical_dim_m", sa.Float(), nullable=False),
        sa.Column("px_min_optical", sa.Integer(), nullable=False),
        sa.Column("px_min_thermal", sa.Integer(), nullable=False),
        sa.CheckConstraint("posture IN ('standing', 'sitting', 'lying')", name="ck_persons_posture"),
        sa.CheckConstraint("critical_dim_m > 0", name="ck_persons_dimension"),
        sa.CheckConstraint("px_min_optical >= 1 AND px_min_thermal >= 1", name="ck_persons_pixels"),
    )


def downgrade() -> None:
    op.drop_table("persons")
    op.drop_table("cameras")
    op.drop_table("drones")
