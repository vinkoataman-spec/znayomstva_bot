import os
import time
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    BigInteger,
    Column,
    Integer,
    MetaData,
    String,
    Table,
    and_,
    create_engine,
    inspect,
    select,
    text,
)

WEEK_SECONDS = 7 * 24 * 60 * 60
MAX_FREE_LIKES_PER_WEEK = 20

# Runtime-only state (ці стани не критично тримати в БД)
states: Dict[int, str] = {}
search_state: Dict[int, Dict[str, Any]] = {}
admin_state: Dict[int, Dict[str, Any]] = {}

def _default_database_url() -> str:
    """
    Priority:
    1) Explicit DATABASE_URL
    2) Railway Volume path (/data/bot.db) if mounted
    3) Local sqlite file (bot.db)
    """
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url
    if os.path.isdir("/data"):
        return "sqlite:////data/bot.db"
    return "sqlite:///bot.db"


DATABASE_URL = _default_database_url()
engine = create_engine(DATABASE_URL, future=True)
metadata = MetaData()

users_table = Table(
    "users",
    metadata,
    Column("chat_id", BigInteger, primary_key=True),
    Column("gender", String(32), nullable=True),
    Column("name", String(255), nullable=True),
    Column("age", Integer, nullable=True),
    Column("photo_file_id", String(255), nullable=True),
    Column("city", String(255), nullable=True),
    Column("premium_until", BigInteger, nullable=False, default=0),
    Column("search_wanted_gender", String(32), nullable=True),
    Column("search_age_range", String(16), nullable=True),
    Column("search_region_mode", String(8), nullable=True),
)

likes_table = Table(
    "likes",
    metadata,
    Column("from_chat_id", BigInteger, nullable=False),
    Column("to_chat_id", BigInteger, nullable=False),
)

quota_table = Table(
    "weekly_quota",
    metadata,
    Column("chat_id", BigInteger, primary_key=True),
    Column("count", Integer, nullable=False, default=0),
    Column("reset_at", BigInteger, nullable=False, default=0),
)

metadata.create_all(engine)


def _migrate_users_search_columns() -> None:
    insp = inspect(engine)
    if not insp.has_table("users"):
        return
    cols = {c["name"] for c in insp.get_columns("users")}
    alters: List[str] = []
    if "search_wanted_gender" not in cols:
        alters.append("ALTER TABLE users ADD COLUMN search_wanted_gender VARCHAR(32)")
    if "search_age_range" not in cols:
        alters.append("ALTER TABLE users ADD COLUMN search_age_range VARCHAR(16)")
    if "search_region_mode" not in cols:
        alters.append("ALTER TABLE users ADD COLUMN search_region_mode VARCHAR(8)")
    for sql in alters:
        with engine.begin() as conn:
            conn.execute(text(sql))


_migrate_users_search_columns()


def now_ts() -> int:
    return int(time.time())


def _row_to_profile(row: Any) -> Dict[str, Any]:
    return {
        "gender": row.gender,
        "name": row.name,
        "age": row.age,
        "photo_file_id": row.photo_file_id,
        "city": row.city,
    }


def ensure_user(chat_id: int) -> Dict[str, Any]:
    with engine.begin() as conn:
        row = conn.execute(
            select(users_table).where(users_table.c.chat_id == chat_id)
        ).first()
        if not row:
            conn.execute(
                users_table.insert().values(
                    chat_id=chat_id,
                    gender=None,
                    name=None,
                    age=None,
                    photo_file_id=None,
                    city=None,
                    premium_until=0,
                )
            )
            return {
                "gender": None,
                "name": None,
                "age": None,
                "photo_file_id": None,
                "city": None,
            }
        return _row_to_profile(row)


def get_user(chat_id: int) -> Optional[Dict[str, Any]]:
    with engine.begin() as conn:
        row = conn.execute(
            select(users_table).where(users_table.c.chat_id == chat_id)
        ).first()
        return _row_to_profile(row) if row else None


def update_user_fields(chat_id: int, **fields: Any) -> None:
    ensure_user(chat_id)
    with engine.begin() as conn:
        conn.execute(
            users_table.update()
            .where(users_table.c.chat_id == chat_id)
            .values(**fields)
        )


def get_saved_search_filters(chat_id: int) -> Optional[Dict[str, str]]:
    with engine.begin() as conn:
        row = conn.execute(
            select(
                users_table.c.search_wanted_gender,
                users_table.c.search_age_range,
                users_table.c.search_region_mode,
            ).where(users_table.c.chat_id == chat_id)
        ).first()
    if not row:
        return None
    g, a, r = row.search_wanted_gender, row.search_age_range, row.search_region_mode
    if not g or not a or not r:
        return None
    return {
        "wanted_gender": str(g),
        "age_range": str(a),
        "region_mode": str(r),
    }


def save_search_filters(
    chat_id: int, wanted_gender: str, age_range: str, region_mode: str
) -> None:
    update_user_fields(
        chat_id,
        search_wanted_gender=wanted_gender,
        search_age_range=age_range,
        search_region_mode=region_mode,
    )


def clear_search_filters(chat_id: int) -> None:
    update_user_fields(
        chat_id,
        search_wanted_gender=None,
        search_age_range=None,
        search_region_mode=None,
    )


def is_profile_complete(chat_id: int) -> bool:
    profile = get_user(chat_id)
    if not profile:
        return False
    return all(
        profile.get(key) is not None
        for key in ("gender", "name", "age", "photo_file_id", "city")
    )


def get_all_complete_users() -> Dict[int, Dict[str, Any]]:
    out: Dict[int, Dict[str, Any]] = {}
    with engine.begin() as conn:
        rows = conn.execute(select(users_table)).all()
        for row in rows:
            profile = _row_to_profile(row)
            if all(
                profile.get(key) is not None
                for key in ("gender", "name", "age", "photo_file_id", "city")
            ):
                out[int(row.chat_id)] = profile
    return out


def has_premium(chat_id: int) -> bool:
    with engine.begin() as conn:
        row = conn.execute(
            select(users_table.c.premium_until).where(users_table.c.chat_id == chat_id)
        ).first()
        if not row:
            return False
        return int(row.premium_until or 0) > now_ts()


def set_premium(chat_id: int, days: int) -> int:
    ensure_user(chat_id)
    with engine.begin() as conn:
        row = conn.execute(
            select(users_table.c.premium_until).where(users_table.c.chat_id == chat_id)
        ).first()
        current_expiry = int(row.premium_until or 0) if row else 0
        base = current_expiry if current_expiry > now_ts() else now_ts()
        new_expiry = base + days * 24 * 60 * 60
        conn.execute(
            users_table.update()
            .where(users_table.c.chat_id == chat_id)
            .values(premium_until=new_expiry)
        )
        return new_expiry


def premium_expiry(chat_id: int) -> Optional[int]:
    with engine.begin() as conn:
        row = conn.execute(
            select(users_table.c.premium_until).where(users_table.c.chat_id == chat_id)
        ).first()
        if not row:
            return None
        exp = int(row.premium_until or 0)
        return exp if exp > 0 else None


def add_like(from_chat_id: int, to_chat_id: int) -> None:
    with engine.begin() as conn:
        exists = conn.execute(
            select(likes_table).where(
                and_(
                    likes_table.c.from_chat_id == from_chat_id,
                    likes_table.c.to_chat_id == to_chat_id,
                )
            )
        ).first()
        if not exists:
            conn.execute(
                likes_table.insert().values(
                    from_chat_id=from_chat_id,
                    to_chat_id=to_chat_id,
                )
            )


def get_likes_received(chat_id: int) -> List[int]:
    with engine.begin() as conn:
        rows = conn.execute(
            select(likes_table.c.from_chat_id).where(likes_table.c.to_chat_id == chat_id)
        ).all()
        return [int(r.from_chat_id) for r in rows]


def can_use_free_like(chat_id: int) -> bool:
    with engine.begin() as conn:
        row = conn.execute(
            select(quota_table).where(quota_table.c.chat_id == chat_id)
        ).first()
        now = now_ts()
        if not row or now >= int(row.reset_at):
            if row:
                conn.execute(
                    quota_table.update()
                    .where(quota_table.c.chat_id == chat_id)
                    .values(count=0, reset_at=now + WEEK_SECONDS)
                )
            else:
                conn.execute(
                    quota_table.insert().values(
                        chat_id=chat_id,
                        count=0,
                        reset_at=now + WEEK_SECONDS,
                    )
                )
            return True
        return int(row.count) < MAX_FREE_LIKES_PER_WEEK


def register_free_like(chat_id: int) -> int:
    with engine.begin() as conn:
        row = conn.execute(
            select(quota_table).where(quota_table.c.chat_id == chat_id)
        ).first()
        now = now_ts()
        if not row or now >= int(row.reset_at):
            count = 1
            reset_at = now + WEEK_SECONDS
            if row:
                conn.execute(
                    quota_table.update()
                    .where(quota_table.c.chat_id == chat_id)
                    .values(count=count, reset_at=reset_at)
                )
            else:
                conn.execute(
                    quota_table.insert().values(
                        chat_id=chat_id,
                        count=count,
                        reset_at=reset_at,
                    )
                )
            return count
        new_count = int(row.count) + 1
        conn.execute(
            quota_table.update()
            .where(quota_table.c.chat_id == chat_id)
            .values(count=new_count)
        )
        return new_count

