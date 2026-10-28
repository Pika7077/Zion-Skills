"""Schema-level regression tests for the deterministic character extractor."""
from pathlib import Path
import sys
import json
import subprocess
import tempfile
import unittest
from uuid import UUID

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

    def test_legacy_ids_and_unregistered_assets(self):
        result = CharacterExtractor("林岚：签了。\n周衡：我不签。").extract()
        self.assertEqual([c["id"] for c in result["characters"]],
                         ["char_001", "char_002"])
        run_id = result["meta"]["extraction_run_id"]
        self.assertEqual(str(UUID(run_id)), run_id)
        for character in result["characters"]:
            self.assertEqual(character["extraction_id"],
                             f"{run_id}:{character['id']}")
            self.assertIsNone(character["asset_id"])

    def test_batch_records_do_not_collide_for_same_filename_or_inline_input(self):
        for source_file in ("scene.txt", "inline-input"):
            with self.subTest(source_file=source_file):
                results = [CharacterExtractor(text, source_file=source_file).extract()
                           for text in ("林岚：签了。", "周衡：我不签。")]
                records = [c for result in results for c in result["characters"]]
                self.assertEqual(records[0]["id"], records[1]["id"])
                by_extraction_id = {c["extraction_id"]: c for c in records}
                self.assertEqual(len(by_extraction_id), 2)
                self.assertEqual({c["name"] for c in by_extraction_id.values()},
                                 {"林岚", "周衡"})

    def test_reordered_extraction_does_not_claim_stable_identity(self):
        before = CharacterExtractor("林岚：签了。\n林岚：快。\n周衡：不签。").extract()
        after = CharacterExtractor("林岚：签了。\n周衡：不签。\n周衡：不行。").extract()
        first = {c["name"]: c for c in before["characters"]}
        second = {c["name"]: c for c in after["characters"]}
        self.assertNotEqual(first["林岚"]["id"], second["林岚"]["id"])
        self.assertNotEqual(first["林岚"]["extraction_id"],
                            second["林岚"]["extraction_id"])
        self.assertTrue(all(c["asset_id"] is None
                            for c in before["characters"] + after["characters"]))

    def test_reusing_extractor_starts_a_new_result_without_accumulation(self):
        extractor = CharacterExtractor("林岚：签了。")
        first, second = extractor.extract(), extractor.extract()
        self.assertNotEqual(first["meta"]["extraction_run_id"],
                            second["meta"]["extraction_run_id"])
        self.assertEqual(first["characters"][0]["appearance_count"], 1)
        self.assertEqual(second["characters"][0]["appearance_count"], 1)

    def test_contained_names_are_not_merged_without_evidence(self):
        for text in ('王强：我不是王强生。\n王强生：我们是两个人。',
                     '王强生：我们是两个人。\n王强：我不是王强生。'):
            result = CharacterExtractor(text).extract()
            self.assertEqual({c['name'] for c in result['characters']}, {'王强', '王强生'})
            self.assertTrue(all(c['appearance_count'] == 1 and c['aliases'] == [] for c in result['characters']))
            self.assertTrue(any('暂保留独立人物' in note for note in result['meta']['extraction_notes']))

    def test_speaker_directions_preserve_names_and_dialogue(self):
        result = CharacterExtractor('林岚（低声）：签了。\n周衡 (迟疑)（回头）: 不签。\n旁白（轻声）：夜深了。').extract()
        by_name = {c['name']: c for c in result['characters']}
        self.assertEqual(set(by_name), {'林岚', '周衡'})
        self.assertEqual(by_name['林岚']['dialogue_style']['sample_lines'], ['签了。'])
        self.assertEqual(by_name['周衡']['dialogue_style']['sample_lines'], ['不签。'])

    def test_possible_alias_notes_do_not_accumulate_between_runs(self):
        extractor = CharacterExtractor('林婉儿：我到了。\n婉儿：等一下。')
        first, second = extractor.extract(), extractor.extract()
        self.assertEqual(first['meta']['extraction_notes'], second['meta']['extraction_notes'])
        self.assertEqual(len(first['characters']), 2)

    def run_cli(self, *args, stdin=None):
        return subprocess.run([sys.executable, '-B', '-X', 'utf8', str(SCRIPTS/'extract_characters.py'), *map(str,args)], input=stdin, capture_output=True, text=True, encoding='utf-8', timeout=10)

    def test_cli_parser_json_preserves_body_and_source(self):
        with tempfile.TemporaryDirectory() as td:
            file, parsed = Path(td)/'scene.txt', Path(td)/'parsed.json'
            file.write_text('林岚：签了。\n周衡：不签。', encoding='utf-8')
            converted = subprocess.run([sys.executable, '-B', '-X', 'utf8', str(SCRIPTS/'parse_input.py'), str(file), '--output', str(parsed)], capture_output=True)
            self.assertEqual(converted.returncode, 0)
            result = self.run_cli(parsed)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual({c['name'] for c in data['characters']}, {'林岚','周衡'})
            self.assertEqual((data['meta']['source_file'], data['meta']['file_type']), ('scene.txt','txt'))

    def test_cli_parser_stdout_can_feed_extractor_stdin(self):
        payload = {'type':'text', 'file_type':'docx', 'source_file':'scene.docx', 'text':'林岚：签了。'}
        result = self.run_cli('-', stdin=json.dumps(payload))
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data['characters'][0]['name'], '林岚')
        self.assertEqual(data['meta']['source_file'], 'scene.docx')
        self.assertEqual(data['meta']['file_type'], 'docx')

    def test_cli_rejects_unusable_parser_payloads(self):
        for payload in ([42], {'type':'video', 'metadata':{}},
                        {'type':'text','text':''}, {'type':'text','text':[]},
                        {'type':'text','text':'[WARNING] No usable text'}):
            with self.subTest(payload=payload):
                result = self.run_cli('-', stdin=json.dumps(payload))
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, '')

    def test_cli_raw_text_is_still_supported(self):
        result = self.run_cli('林岚：签了。', '--input-format', 'text', '--source-type', '剧本')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['characters'][0]['name'], '林岚')

    def test_cli_malformed_or_missing_json_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            file = Path(td)/'invalid.json'
            file.write_text('{bad', encoding='utf-8')
            for path in (file, Path(td)/'missing.json'):
                result = self.run_cli(path)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, '')

    def test_auto_detection_keeps_bracketed_stage_directions_as_text(self):
        result = self.run_cli('[场景1]\n林岚：签了。\n周衡：不签。')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual({c['name'] for c in json.loads(result.stdout)['characters']}, {'林岚','周衡'})


if __name__ == "__main__":
    unittest.main()
