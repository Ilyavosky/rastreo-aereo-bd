import json
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.dialects.postgresql import insert

load_dotenv()

UNIQUE_KEYS = {
    "drones": "name",
    "cameras": "name",
    "persons": "name",
    "scenario_templates": "slug",
}


def main() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("La variable de entorno DATABASE_URL no está definida")

    seed_file = Path(os.environ.get("SEED_FILE", "data/seed.json"))
    data = json.loads(seed_file.read_text(encoding="utf-8"))

    engine = create_engine(database_url)
    metadata = MetaData()
    with engine.begin() as connection:
        for table_name, key in UNIQUE_KEYS.items():
            rows = data.get(table_name, [])
            if rows:
                table = Table(table_name, metadata, autoload_with=connection)
                statement = insert(table).values(rows).on_conflict_do_nothing(index_elements=[key])
                connection.execute(statement)
            print(f"{table_name}: {len(rows)} filas procesadas")


if __name__ == "__main__":
    main()
