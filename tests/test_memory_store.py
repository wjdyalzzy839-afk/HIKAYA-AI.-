import pytest
from hikaya_ai.memory_store import HikayaMemory


def test_memory_saves_record(tmp_path):
    memory = HikayaMemory(tmp_path / "memory.db")

    result = memory.add_memory(
        "معلومة تاريخية",
        category="تاريخ"
    )

    assert result["inserted"] is True
    assert memory.count() == 1


def test_memory_prevents_duplicates(tmp_path):
    memory = HikayaMemory(tmp_path / "memory.db")

    memory.add_memory("معلومة", category="تاريخ")
    result = memory.add_memory("معلومة", category="تاريخ")

    assert result["inserted"] is False
    assert memory.count() == 1


def test_memory_search(tmp_path):
    memory = HikayaMemory(tmp_path / "memory.db")

    memory.add_memory("تاريخ مملكة سبأ", category="تاريخ")

    results = memory.search("سبأ")

    assert len(results) == 1
    assert results[0]["status"] == "unverified"


def test_memory_rejects_empty_content(tmp_path):
    memory = HikayaMemory(tmp_path / "memory.db")

    with pytest.raises(ValueError):
        memory.add_memory("   ")


def test_memory_rejects_unknown_status(tmp_path):
    memory = HikayaMemory(tmp_path / "memory.db")

    with pytest.raises(ValueError):
        memory.add_memory("معلومة", status="unknown")
