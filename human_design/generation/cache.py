"""sqlite3 单文件生成缓存（标准库，零新增依赖）。

- 键 = sha256(facts_hash + layer + focus + question_norm + model + prompt_version)
- 只存 facts_hash → 文本；绝不存出生资料、昵称、性别等个人输入。
- WAL + busy_timeout，每次操作开/关连接（FastAPI 线程池下不跨线程共享连接）。
- INSERT OR IGNORE 幂等；库损坏/schema 不兼容 → 删库重建（缓存可重建，不阻塞启动）。
"""
from __future__ import annotations

import hashlib
import logging
import os
import sqlite3
import time
from pathlib import Path

logger = logging.getLogger("human_design.generation.cache")

SCHEMA_VERSION = "1"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS gen_cache (
  cache_key   TEXT PRIMARY KEY,
  facts_hash  TEXT NOT NULL,
  layer       TEXT NOT NULL,
  prompt_ver  TEXT NOT NULL,
  model       TEXT NOT NULL,
  content     TEXT NOT NULL,
  created_at  INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_facts ON gen_cache(facts_hash);
"""


def default_cache_path() -> Path:
    env_path = os.environ.get("HD_CACHE_PATH")
    if env_path:
        return Path(env_path)
    return Path(__file__).resolve().parents[2] / "cache.db"


def cache_key(
    facts_hash: str,
    layer: str,
    focus: str,
    question_norm: str,
    model: str,
    prompt_version: str,
) -> str:
    raw = "|".join((facts_hash, layer, focus or "", question_norm or "", model or "", prompt_version))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def normalize_question(question: str | None) -> str:
    return " ".join((question or "").split())


class GenerationCache:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else default_cache_path()
        self._ensure_schema()

    # ---------------------------------------------------------------- 连接管理

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=5.0)
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA busy_timeout=5000")
        return connection

    def _ensure_schema(self) -> None:
        try:
            with self._connect() as connection:
                connection.executescript(_SCHEMA)
                connection.execute(
                    "INSERT OR IGNORE INTO meta(key, value) VALUES('schema_version', ?)",
                    (SCHEMA_VERSION,),
                )
                row = connection.execute(
                    "SELECT value FROM meta WHERE key='schema_version'"
                ).fetchone()
                if row and row[0] != SCHEMA_VERSION:
                    raise sqlite3.DatabaseError(f"schema version mismatch: {row[0]}")
        except sqlite3.DatabaseError:
            # 缓存可重建：删库重建优于阻塞启动。
            logger.warning("cache.db 损坏或版本不兼容，删除重建：%s", self.path)
            self._reset()

    def _reset(self) -> None:
        for suffix in ("", "-wal", "-shm"):
            candidate = Path(f"{self.path}{suffix}")
            if candidate.exists():
                candidate.unlink()
        with self._connect() as connection:
            connection.executescript(_SCHEMA)
            connection.execute(
                "INSERT OR IGNORE INTO meta(key, value) VALUES('schema_version', ?)",
                (SCHEMA_VERSION,),
            )

    # ---------------------------------------------------------------- 读写

    def get(self, key: str) -> str | None:
        try:
            with self._connect() as connection:
                row = connection.execute(
                    "SELECT content FROM gen_cache WHERE cache_key = ?", (key,)
                ).fetchone()
            return row[0] if row else None
        except sqlite3.DatabaseError:
            logger.warning("缓存读取失败，按未命中处理。")
            return None

    def set(
        self,
        key: str,
        facts_hash: str,
        layer: str,
        content: str,
        *,
        model: str = "",
        prompt_version: str = "",
    ) -> None:
        try:
            with self._connect() as connection:
                connection.execute(
                    "INSERT OR IGNORE INTO gen_cache"
                    "(cache_key, facts_hash, layer, prompt_ver, model, content, created_at)"
                    " VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (key, facts_hash, layer, prompt_version, model, content, int(time.time())),
                )
        except sqlite3.DatabaseError:
            logger.warning("缓存写入失败，忽略（不影响主流程）。")
