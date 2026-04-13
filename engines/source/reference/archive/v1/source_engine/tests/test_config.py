"""Tests for source engine config loader — SPEC §8.

Tests 66–70 from session5-test-plan.md.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from engines.source.src.config import SourceEngineConfig, load_config


class TestConfigLoader:
    """Tests for load_config()."""

    def test_all_four_config_files_loaded(self, tmp_path: Path) -> None:
        """Test 66: All 4 config files loaded correctly."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        muhaqiqs = ["شعيب الأرناؤوط", "أحمد شاكر"]
        publishers = {
            "دار التراث": {"score": 0.75, "variants": ["دار التراث - القاهرة"]}
        }
        transliteration = {"scholars": {"النووي": "nawawi"}, "titles": {"ألفية": "alfiyyah"}}
        synonyms = {"منظومة": "nazm", "حاشية": "hashiyah"}

        (config_dir / "recognized_muhaqiqs.json").write_text(
            json.dumps(muhaqiqs, ensure_ascii=False), encoding="utf-8"
        )
        (config_dir / "known_publishers.json").write_text(
            json.dumps(publishers, ensure_ascii=False), encoding="utf-8"
        )
        (config_dir / "transliteration.json").write_text(
            json.dumps(transliteration, ensure_ascii=False), encoding="utf-8"
        )
        (config_dir / "genre_synonyms.json").write_text(
            json.dumps(synonyms, ensure_ascii=False), encoding="utf-8"
        )

        config = load_config(tmp_path)

        assert config.recognized_muhaqiqs == muhaqiqs
        assert config.known_publishers == publishers
        assert config.transliteration == transliteration
        assert config.genre_synonyms == synonyms
        assert config.library_root == tmp_path
        assert config.staging_path == tmp_path / "staging"

    def test_missing_files_produce_empty_defaults(self, tmp_path: Path) -> None:
        """Test 67: Missing config files produce empty defaults, not errors."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        # No files created

        config = load_config(tmp_path)

        assert config.recognized_muhaqiqs == []
        assert config.known_publishers == {}
        assert config.transliteration == {}
        assert config.genre_synonyms == {}

    def test_malformed_json_raises_with_filename(self, tmp_path: Path) -> None:
        """Test 68: Malformed JSON raises with the filename in the error."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "recognized_muhaqiqs.json").write_text(
            "{bad json", encoding="utf-8"
        )

        with pytest.raises(ValueError, match="recognized_muhaqiqs.json"):
            load_config(tmp_path)

    def test_arabic_text_with_diacritics_preserved(self, tmp_path: Path) -> None:
        """Test 69: Arabic text with diacritics is preserved in config."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        name_with_diacritics = "مُحَمَّدُ بْنُ إِسْمَاعِيلَ البُخَارِيُّ"
        muhaqiqs = [name_with_diacritics]
        (config_dir / "recognized_muhaqiqs.json").write_text(
            json.dumps(muhaqiqs, ensure_ascii=False), encoding="utf-8"
        )

        config = load_config(tmp_path)

        assert config.recognized_muhaqiqs[0] == name_with_diacritics

    def test_publisher_variants_loaded(self, tmp_path: Path) -> None:
        """Test 70: Publisher variants are accessible from loaded config."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        publishers = {
            "مؤسسة الرسالة": {
                "score": 0.80,
                "variants": ["دار الرسالة", "مؤسسة الرسالة - بيروت"],
            }
        }
        (config_dir / "known_publishers.json").write_text(
            json.dumps(publishers, ensure_ascii=False), encoding="utf-8"
        )

        config = load_config(tmp_path)

        entry = config.known_publishers["مؤسسة الرسالة"]
        assert entry["score"] == 0.80
        assert "دار الرسالة" in entry["variants"]
        assert len(entry["variants"]) == 2


class TestSourceEngineConfigDefaults:
    """Verify default values match SPEC §8."""

    def test_default_thresholds(self) -> None:
        """SPEC §8 threshold defaults."""
        config = SourceEngineConfig()
        assert config.confidence_threshold_auto_accept == 0.70
        assert config.confidence_threshold_block == 0.50
        assert config.trust_score_verified_threshold == 0.65
        assert config.human_gate_batch_size == 20
