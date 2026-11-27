"""catalog physics: drone mass and acceleration, camera optics, person silhouette

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-27
"""
import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("drones", sa.Column("manufacturer", sa.String(60), nullable=True))
    op.add_column("drones", sa.Column("model", sa.String(80), nullable=True))
    op.add_column("drones", sa.Column("size_class", sa.String(8), nullable=True))
    op.add_column("drones", sa.Column("mass_kg", sa.Float(), nullable=True))
    op.add_column("drones", sa.Column("a_max_ms2", sa.Float(), nullable=True))
    op.add_column("drones", sa.Column("accel_efficiency", sa.Float(), nullable=True))
    op.add_column("drones", sa.Column("datasheet_url", sa.Text(), nullable=True))
    op.execute(
        """
        UPDATE drones SET
            manufacturer = 'Genérico',
            model = name,
            size_class = CASE name WHEN 'Ligero' THEN 'small' WHEN 'Estándar' THEN 'medium'
                         WHEN 'Largo alcance' THEN 'large'
                         ELSE CASE WHEN battery_wh < 80 THEN 'small'
                                   WHEN battery_wh < 200 THEN 'medium' ELSE 'large' END END,
            mass_kg = CASE name WHEN 'Ligero' THEN 0.45 WHEN 'Estándar' THEN 1.5
                      WHEN 'Largo alcance' THEN 3.5 ELSE 1.5 END,
            a_max_ms2 = CASE name WHEN 'Largo alcance' THEN 2.83 ELSE 3.43 END,
            accel_efficiency = 0.7
        WHERE manufacturer IS NULL
        """
    )
    for column in ("manufacturer", "model", "size_class", "mass_kg", "a_max_ms2", "accel_efficiency"):
        op.alter_column("drones", column, nullable=False)
    op.create_check_constraint(
        "ck_drones_size_class", "drones", "size_class IN ('small', 'medium', 'large')"
    )
    op.create_check_constraint("ck_drones_mass", "drones", "mass_kg > 0")
    op.create_check_constraint("ck_drones_acceleration", "drones", "a_max_ms2 > 0")
    op.create_check_constraint(
        "ck_drones_accel_efficiency", "drones", "accel_efficiency > 0 AND accel_efficiency <= 1"
    )

    op.add_column("cameras", sa.Column("focal_length_mm", sa.Float(), nullable=True))
    op.add_column("cameras", sa.Column("sensor_width_mm", sa.Float(), nullable=True))
    op.execute(
        """
        UPDATE cameras SET sensor_width_mm = CASE WHEN modality = 'thermal'
            THEN n_px_width * 0.012 ELSE 6.4 END
        """
    )
    op.execute(
        """
        UPDATE cameras SET focal_length_mm =
            sensor_width_mm / (2 * tan(radians(fov_deg / 2)))
        """
    )
    op.alter_column("cameras", "focal_length_mm", nullable=False)
    op.alter_column("cameras", "sensor_width_mm", nullable=False)
    op.drop_constraint("ck_cameras_fov", "cameras", type_="check")
    op.drop_column("cameras", "fov_deg")
    op.create_check_constraint(
        "ck_cameras_optics", "cameras", "focal_length_mm > 0 AND sensor_width_mm > 0"
    )

    op.add_column("persons", sa.Column("height_m", sa.Float(), nullable=True))
    op.add_column("persons", sa.Column("body_width_m", sa.Float(), nullable=True))
    op.add_column("persons", sa.Column("build", sa.String(8), nullable=True))
    op.add_column("persons", sa.Column("age_group", sa.String(8), nullable=True))
    op.execute(
        """
        UPDATE persons SET
            height_m = CASE name WHEN 'Niño' THEN 1.2 ELSE 1.7 END,
            body_width_m = CASE name WHEN 'Adulto tendido' THEN 0.5 ELSE critical_dim_m END,
            build = 'average',
            age_group = CASE name WHEN 'Niño' THEN 'child' ELSE 'adult' END
        WHERE height_m IS NULL
        """
    )
    for column in ("height_m", "body_width_m", "build", "age_group"):
        op.alter_column("persons", column, nullable=False)
    op.create_check_constraint("ck_persons_build", "persons", "build IN ('slim', 'average', 'heavy')")
    op.create_check_constraint(
        "ck_persons_age_group", "persons", "age_group IN ('child', 'teen', 'adult', 'senior')"
    )
    op.create_check_constraint(
        "ck_persons_silhouette", "persons", "height_m > 0 AND body_width_m > 0"
    )


def downgrade() -> None:
    op.drop_constraint("ck_persons_silhouette", "persons", type_="check")
    op.drop_constraint("ck_persons_age_group", "persons", type_="check")
    op.drop_constraint("ck_persons_build", "persons", type_="check")
    for column in ("age_group", "build", "body_width_m", "height_m"):
        op.drop_column("persons", column)

    op.add_column("cameras", sa.Column("fov_deg", sa.Float(), nullable=True))
    op.execute(
        "UPDATE cameras SET fov_deg = degrees(2 * atan(sensor_width_mm / (2 * focal_length_mm)))"
    )
    op.alter_column("cameras", "fov_deg", nullable=False)
    op.drop_constraint("ck_cameras_optics", "cameras", type_="check")
    op.create_check_constraint("ck_cameras_fov", "cameras", "fov_deg > 0 AND fov_deg < 180")
    op.drop_column("cameras", "sensor_width_mm")
    op.drop_column("cameras", "focal_length_mm")

    op.drop_constraint("ck_drones_accel_efficiency", "drones", type_="check")
    op.drop_constraint("ck_drones_acceleration", "drones", type_="check")
    op.drop_constraint("ck_drones_mass", "drones", type_="check")
    op.drop_constraint("ck_drones_size_class", "drones", type_="check")
    for column in (
        "datasheet_url", "accel_efficiency", "a_max_ms2", "mass_kg", "size_class", "model", "manufacturer",
    ):
        op.drop_column("drones", column)
