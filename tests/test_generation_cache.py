from __future__ import annotations

import sqlite3
import threading

from human_design.generation.cache import GenerationCache, cache_key, normalize_question


def test_cache_roundtrip_and_idempotent_set(tmp_path) -> None:
    cache = GenerationCache(tmp_path / "cache.db")
    key = cache_key("hash", "L2", "", "", "deepseek-chat", "v0.5.3")
    assert cache.get(key) is None
    cache.set(key, "hash", "L2", "第一版", model="deepseek-chat", prompt_version="v0.5.3")
    cache.set(key, "hash", "L2", "第二版不应覆盖", model="deepseek-chat", prompt_version="v0.5.3")
    assert cache.get(key) == "第一版"  # INSERT OR IGNORE 幂等


def test_cache_key_varies_by_layer_question_model_and_prompt_version() -> None:
    base = cache_key("h", "L2", "", "", "m", "v1")
    assert base != cache_key("h", "L1", "", "", "m", "v1")
    assert base != cache_key("h", "L2", "", normalize_question("  问 题 "), "m", "v1")
    assert base != cache_key("h", "L2", "", "", "m2", "v1")
    assert base != cache_key("h", "L2", "", "", "m", "v2")


def test_cache_stores_only_facts_hash_no_personal_columns(tmp_path) -> None:
    path = tmp_path / "cache.db"
    cache = GenerationCache(path)
    cache.set("k", "facts-hash", "L1", "文本")
    with sqlite3.connect(path) as connection:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(gen_cache)")}
    assert columns == {"cache_key", "facts_hash", "layer", "prompt_ver", "model", "content", "created_at"}


def test_concurrent_writes_same_key_are_safe(tmp_path) -> None:
    path = tmp_path / "cache.db"
    cache = GenerationCache(path)
    key = cache_key("h", "L2", "", "", "m", "v1")
    errors: list[Exception] = []

    def writer(index: int) -> None:
        try:
            GenerationCache(path).set(key, "h", "L2", f"内容{index}")
        except Exception as exc:  # pragma: no cover - 失败时收集
            errors.append(exc)

    threads = [threading.Thread(target=writer, args=(i,)) for i in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert not errors
    content = cache.get(key)
    assert content is not None and content.startswith("内容")
    with sqlite3.connect(path) as connection:
        count = connection.execute("SELECT COUNT(*) FROM gen_cache").fetchone()[0]
    assert count == 1  # 无脏数据


def test_corrupt_cache_file_is_rebuilt_not_blocking(tmp_path) -> None:
    path = tmp_path / "cache.db"
    path.write_bytes(b"this is not a sqlite file at all........")
    cache = GenerationCache(path)  # 不应抛异常
    key = cache_key("h", "L1", "", "", "m", "v1")
    cache.set(key, "h", "L1", "重建后可写")
    assert cache.get(key) == "重建后可写"
