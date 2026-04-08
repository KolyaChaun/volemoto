import os
import sys
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool
from alembic import context

# Добавляем корень проекта в sys.path чтобы импортировать src.*
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv()

# Импортируем Base и все модели — иначе autogenerate их не увидит
from src.db.database import Base  # noqa: E402
import src.models.bike        # noqa: F401, E402
import src.models.brand       # noqa: F401, E402
import src.models.review      # noqa: F401, E402
import src.models.hero_slide  # noqa: F401, E402
import src.models.admin       # noqa: F401, E402

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# URL берём из .env, не из alembic.ini
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()