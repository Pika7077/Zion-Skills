"""Schema-level regression tests for the deterministic character extractor."""
from pathlib import Path
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from extract_characters import CharacterExtractor


class CharacterSchemaRegression(unittest.TestCase):
    def test_unknown_values_and_meta_follow_schema(self):
        result = CharacterExtractor(
            "林岚：签了。\n周衡：我不签。",
            source_type="剧本",
            source_file="scene.txt",
            file_type="txt",
        ).extract()
        self.assertEqual(result["meta"]["source_file"], "scene.txt")
        self.assertEqual(result["meta"]["file_type"], "txt")
        allowed = {"原文明确", "合理推断", "设计补全", "未知"}
        for character in result["characters"]:
            self.assertIn(character["gender"], {"男", "女", "未知"})
            self.assertNotEqual(character["age_range"], "待分析")
            self.assertTrue(set(character["evidence_levels"].values()) <= allowed)


if __name__ == "__main__":
    unittest.main()
