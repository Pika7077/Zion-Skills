"""Regression tests for observable acceptance/rejection and exported content."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from export_output import audit_assets, audit_variety, audit_fidelity, generate_markdown, validate_shot, validate_payload


def fixture():
    shots = []
    for i in range(3):
        shots.append({
            'shot_number': i+1, 'time_range': {'start': i*10, 'end': (i+1)*10},
            'duration_seconds': 10, 'framing': '特写', 'focal_length': '35mm',
            'aperture': 'f/4', 'pov_family': '过肩', 'camera_height': '平视',
            'camera_angle': '平拍',
            'composition': '匹配视线', 'camera_movement': '固定',
            'lighting': '左侧窗光照亮手和合同，人物背光侧保留面部细节',
            'description': ['手指压住合同', '反打林岚，手离开合同', '合同停止，两人等待回答'][i],
            'seedance_prompt': ['手指压住合同', '反打林岚，手离开合同', '合同停止，两人等待回答'][i],
            'new_feedback': ['合同移动受阻', '手退出交接位置', '对峙没有得到回答'][i],
            'physical_feedback': '纸张摩擦后停止',
            'cut_motivation': '观察新的回应',
            'addition_note': '动作细节为导演补充',
        })
    return {'meta': {'target_model': 'Seedance 2.5', 'total_duration_seconds': 30,
                     'generation_limit_seconds': 30, 'aspect_ratio': '9:16'},
            'shots': shots, 'constraints': '显示原文指定字幕并保留配乐'}


class Regression(unittest.TestCase):
    def asset_fixture(self, status='uploaded'):
        d = fixture()
        d['meta'].update({
            'handoff_schema_version': '1.0',
            'project_id': 'PRJ_demo',
            'source_script_version': 'script_v3',
            'source_scene_ids': ['SC001'],
            'asset_mode': {
                'enabled': True,
                'character_assets': [{
                    'asset_id': 'CHR_linlan', 'ref': '@林岚', 'version': '1.2',
                    'status': status,
                    'files': [{'path': 'assets/linlan_v1.2.png'}],
                    'target_reference': 'ref_01' if status == 'uploaded' else None,
                }],
            },
        })
        for shot in d['shots']:
            shot['source_scene_id'] = 'SC001'
            shot['character_refs'] = ['@林岚']
        return d

    def test_30_seconds_static_reverse_closeup_accepted(self):
        d=fixture()
        self.assertTrue(audit_variety(d)['passed'])
        self.assertTrue(audit_fidelity(d)['passed'])

    def test_short_clip_not_forced_to_30(self):
        d=fixture(); d['shots']=d['shots'][:1]; d['meta']['total_duration_seconds']=10
        self.assertTrue(audit_fidelity(d)['passed'])

    def test_high_energy_is_not_quota(self):
        d=fixture(); d['meta']['pacing_profile']='high_energy'
        self.assertTrue(audit_variety(d)['passed'])
        self.assertTrue(audit_fidelity(d)['passed'])

    def test_legacy_is_explicit_only(self):
        d=fixture(); d['meta']['pacing_profile']='legacy_quota'
        self.assertFalse(audit_variety(d)['passed'])
        self.assertFalse(audit_fidelity(d)['passed'])

    def test_over_budget_and_missing_budget_rejected(self):
        for change in ({'total_duration_seconds':31}, {'generation_limit_seconds':40}):
            with self.subTest(change=change):
                d=fixture(); d['meta'].update(change)
                self.assertFalse(audit_fidelity(d)['passed'])
        d=fixture(); del d['meta']['generation_limit_seconds']
        self.assertFalse(audit_fidelity(d)['passed'])

    def test_other_model_uses_confirmed_budget_without_seedance_cap(self):
        d=fixture(); d['meta'].update(target_model='Other Verified Model', generation_limit_seconds=40)
        self.assertTrue(audit_fidelity(d)['passed'])

    def test_director_only_needs_no_model_or_generation_budget(self):
        d=fixture(); d['meta'].pop('target_model'); d['meta'].pop('generation_limit_seconds')
        for shot in d['shots']:
            shot.pop('seedance_prompt')
        self.assertTrue(audit_fidelity(d)['passed'])
        out=generate_markdown(d)
        self.assertIn('未指定（纯导演稿）', out)
        self.assertNotIn('完整提示词', out)

    def test_formal_shots_require_framing_movement_and_lighting(self):
        for field in ('framing', 'camera_movement', 'lighting'):
            with self.subTest(field=field):
                d = fixture()
                d['shots'][0][field] = ''
                self.assertTrue(any(field in issue for issue in validate_shot(d['shots'][0])))
                self.assertTrue(any(field in issue for issue in audit_variety(d)['issues']))

        d = fixture()
        d['shots'][0]['lighting'] = '同上'
        self.assertTrue(any('lighting' in issue for issue in validate_shot(d['shots'][0])))
        self.assertTrue(any('lighting' in issue for issue in audit_variety(d)['issues']))

    def test_markdown_shows_camera_and_lighting_choices(self):
        out = generate_markdown(fixture())
        self.assertIn('镜头1（0-10秒）：特写', out)
        self.assertIn('**运镜**：固定', out)
        self.assertIn('**光线**：左侧窗光照亮手和合同', out)

    def test_fractional_times_allowed(self):
        d=fixture(); d['shots'][0]['time_range']['end']=9.5; d['shots'][0]['duration_seconds']=9.5
        d['shots'][1]['time_range']['start']=9.5; d['shots'][1]['duration_seconds']=10.5
        self.assertTrue(audit_fidelity(d)['passed'])

    def test_broken_timeline_rejected(self):
        for change in ({'start':11}, {'start':-1}, {'end':0}, {'end':float('nan')}):
            with self.subTest(change=change):
                d=fixture(); d['shots'][0]['time_range'].update(change)
                self.assertFalse(audit_fidelity(d)['passed'])

    def test_empty_or_missing_content_rejected(self):
        d=fixture(); d['shots']=[]
        self.assertFalse(audit_variety(d)['passed']); self.assertFalse(audit_fidelity(d)['passed'])
        d=fixture(); del d['shots'][0]['new_feedback']
        self.assertFalse(audit_variety(d)['passed']); self.assertFalse(audit_fidelity(d)['passed'])

    def test_capacity_compared_with_actual_group(self):
        d=fixture(); d['shots']=d['shots'][:1]; d['meta']['total_duration_seconds']=10
        d['fidelity_gate']={'dialogue_capacity': {'total_min_seconds':12}}
        self.assertFalse(audit_fidelity(d)['passed'])

    def test_motion_path_required_when_moving(self):
        d=fixture(); d['shots'][0]['camera_movement']='下移跟随纸张'
        self.assertFalse(audit_fidelity(d)['passed'])
        d['shots'][0]['camera_move_triplet']={'origin':'脸部','direction':'下移至桌面','stop_result':'纸张停住处'}
        self.assertTrue(audit_fidelity(d)['passed'])

    def test_internal_cut_rejected_not_reverse_shot_label(self):
        d=fixture(); d['shots'][0]['description']='先看纸张，然后切至林岚面部'
        self.assertFalse(audit_fidelity(d)['passed'])

    def test_markdown_preserves_details_without_conflicting_constraints(self):
        d=fixture(); out=generate_markdown(d)
        self.assertIn('纸张摩擦后停止',out)
        self.assertIn('观察新的回应',out)
        self.assertIn('导演补充',out)
        self.assertIn('显示原文指定字幕并保留配乐',out)
        self.assertNotIn('无音乐，无字幕',out)
        self.assertNotIn('下限 4',out)

    def test_optics_are_optional_and_legacy_values_remain_readable(self):
        d = fixture()
        for shot in d['shots']:
            shot.pop('focal_length')
            shot.pop('aperture')
            self.assertEqual(validate_shot(shot, require_prompt=True), [])
        self.assertNotIn('焦段/光圈', generate_markdown(d))
        d['shots'][0].update(focal_length='未指定', aperture='未指定')
        self.assertEqual(validate_shot(d['shots'][0], require_prompt=True), [])
        self.assertNotIn('焦段/光圈', generate_markdown(d))
        d['shots'][0].update(focal_length='50mm', aperture='f/4')
        self.assertIn('50mm f/4', generate_markdown(d))

    def test_missing_analysis_does_not_invent_project_decisions(self):
        out = generate_markdown(fixture())
        for invented in ('## 场景分析', '## 节奏地图', '建立层', '短漫剧',
                         '真人写实', '标准全量', '## 全局风格锁定', '特殊风格化：不启用'):
            with self.subTest(invented=invented):
                self.assertNotIn(invented, out)
        self.assertIn('手指压住合同', out)

    def test_provided_legacy_analysis_and_parameters_are_preserved(self):
        d = fixture()
        d['scene_analysis'] = {'emotion_arc': {'start': '期待'}, 'narrative_engine': '试探'}
        d['rhythm_map'] = {'accumulation': {'shots': '2', 'pace': '停顿'}}
        d['meta']['params'] = {'video_type': '实验短片', 'visual_style': '纸片动画', 'run_mode': '局部重排'}
        d['meta']['global_style'] = {'media_source': '纸张拼贴'}
        d['meta']['special_stylization'] = {'enabled': False}
        out = generate_markdown(d)
        for supplied in ('期待', '试探', '镜头：2', '停顿', '实验短片', '纸片动画', '局部重排', '纸张拼贴', '特殊风格化：不启用'):
            self.assertIn(supplied, out)
        for invented in ('建立层', '爆发层', '余震层', 'trigger=?'):
            self.assertNotIn(invented, out)

    def test_missing_constraints_do_not_override_requested_music_or_subtitles(self):
        for absent in ('missing', None, ''):
            with self.subTest(constraints=absent):
                d = fixture()
                if absent == 'missing':
                    d.pop('constraints')
                else:
                    d['constraints'] = absent
                d['shots'][0]['generation_prompt'] = '响起已选配乐，出现字幕“请进”。'
                out = generate_markdown(d)
                self.assertIn('响起已选配乐，出现字幕“请进”。', out)
                self.assertNotIn('不额外加入配乐或字幕', out)
                self.assertNotIn('约束：', out)

    def test_camera_relation_height_and_angle_remain_separate(self):
        d=fixture(); d['shots'][0].update(pov_family='过肩', camera_height='略低', camera_angle='仰拍')
        out=generate_markdown(d)
        self.assertIn('**观察方式**：过肩', out)
        self.assertIn('**机位高度**：略低', out)
        self.assertIn('**角度**：仰拍', out)

    def test_supplied_pass_flag_does_not_skip_audit(self):
        d=fixture(); d['variety_check']={'passed':True}; del d['shots'][0]['new_feedback']
        self.assertIn('缺少 new_feedback',generate_markdown(d))

    def test_asset_handoff_requires_identity_version_status_and_source(self):
        d = self.asset_fixture()
        self.assertTrue(audit_assets(d)['passed'])
        out = generate_markdown(d)
        self.assertIn('PRJ_demo / script_v3', out)
        self.assertIn('CHR_linlan@1.2；uploaded；target=ref_01', out)
        self.assertIn('源场次 ID**：SC001', out)
        del d['meta']['project_id']
        del d['meta']['asset_mode']['character_assets'][0]['version']
        report = audit_assets(d)
        self.assertFalse(report['passed'])
        self.assertTrue(any('project_id' in issue for issue in report['issues']))
        self.assertTrue(any('version' in issue for issue in report['issues']))

    def test_unregistered_asset_reference_is_rejected(self):
        d = self.asset_fixture()
        d['shots'][0]['character_refs'] = ['@不存在']
        self.assertFalse(audit_assets(d)['passed'])
        self.assertFalse(audit_variety(d)['passed'])

    def test_prompt_binding_requires_uploaded_target_reference(self):
        d = self.asset_fixture(status='approved')
        report = audit_assets(d)
        self.assertFalse(report['passed'])
        self.assertTrue(any('尚未 uploaded' in issue for issue in report['issues']))
        for shot in d['shots']:
            shot.pop('seedance_prompt')
        self.assertTrue(audit_assets(d)['passed'])

    def test_uploaded_asset_requires_target_reference(self):
        d = self.asset_fixture()
        d['meta']['asset_mode']['character_assets'][0]['target_reference'] = None
        self.assertFalse(audit_assets(d)['passed'])

    def test_cli_exit_code_and_batch_wrappers(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'scene.json'; d=fixture()
            p.write_text(json.dumps([{'file':'scene','status':'success','data':d}]),encoding='utf-8')
            cmd=[sys.executable,'-B','-X','utf8',str(SCRIPTS/'export_output.py'),str(p),'--audit']
            self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,0)
            d['shots'][0]['time_range']['start']=2
            p.write_text(json.dumps(d),encoding='utf-8')
            self.assertNotEqual(subprocess.run(cmd,capture_output=True).returncode,0)

    def test_cli_validate_rejects_fake_asset_binding(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'asset_scene.json'
            d = self.asset_fixture()
            p.write_text(json.dumps(d), encoding='utf-8')
            cmd = [sys.executable, '-B', '-X', 'utf8', str(SCRIPTS/'export_output.py'), str(p), '--validate']
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
            d['shots'][0]['character_refs'] = ['@MISSING']
            p.write_text(json.dumps(d), encoding='utf-8')
            self.assertNotEqual(subprocess.run(cmd, capture_output=True).returncode, 0)

    def test_no_shot_time_hides_timecodes(self):
        d = fixture()
        with_time = generate_markdown(d)
        without = generate_markdown(d, show_shot_time=False)
        self.assertIn('### 镜头1（0-10秒）：特写', with_time)
        self.assertIn('### 镜头1：特写', without)
        self.assertNotIn('（0-10秒）', without)

    def test_validate_rejects_invalid_top_level_and_nested_types(self):
        payloads = [None, 42, 'text', [], [42], {}, {'results': None},
                    {'shots': [42]}, {'meta': [], 'shots': [{}]},
                    {'meta': {'asset_mode': []}, 'shots': [{}]},
                    {'shots': 'not a list'}]
        for payload in payloads:
            with self.subTest(payload=payload):
                self.assertTrue(validate_payload(payload)[0])

    def test_validate_accepts_single_list_wrapper_and_exported_batch(self):
        d = fixture()
        wrapper = {'file': 'scene', 'status': 'success', 'data': d}
        for payload in (d, [d], [wrapper], {'batch_meta': {}, 'results': [wrapper]}):
            with self.subTest(payload_type=type(payload).__name__):
                self.assertEqual(validate_payload(payload), ([], 1))

    def test_validate_checks_every_batch_item_and_reports_file(self):
        valid = fixture()
        bad = self.asset_fixture()
        bad['shots'][0]['character_refs'] = ['@MISSING']
        payload = [{'file': 'good.json', 'status': 'success', 'data': valid},
                   {'file': 'bad.json', 'status': 'success', 'data': bad}]
        errors, count = validate_payload(payload)
        self.assertEqual(count, 2)
        self.assertTrue(any('bad.json' in error and '@MISSING' in error for error in errors))
        self.assertTrue(validate_payload([{'file': 'failed', 'status': 'error', 'error': 'cannot parse', 'data': valid}])[0])

    def test_cli_validate_invalid_list_exits_nonzero(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'invalid.json'
            p.write_text('[42]', encoding='utf-8')
            result = subprocess.run([sys.executable, '-B', '-X', 'utf8', str(SCRIPTS/'export_output.py'), str(p), '--validate'], capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(result.returncode, 1)
            self.assertIn('第 1 项', result.stdout)
            self.assertNotIn('Traceback', result.stderr)

    def test_cli_batch_validation_rejects_empty_and_invalid_directory(self):
        with tempfile.TemporaryDirectory() as td:
            directory = Path(td)
            cmd = [sys.executable, '-B', '-X', 'utf8', str(SCRIPTS/'export_output.py'), td, '--batch', '--validate']
            self.assertNotEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
            (directory/'good.json').write_text(json.dumps(fixture()), encoding='utf-8')
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
            (directory/'bad.json').write_text('[42]', encoding='utf-8')
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(result.returncode, 1)
            self.assertIn('bad.json', result.stdout)

    def test_validate_rejects_wrong_required_text_field_types(self):
        for field in ('framing', 'camera_movement', 'lighting', 'description'):
            for value in ([], {}, True, 42, None, '  '):
                with self.subTest(field=field, value=value):
                    data = fixture()
                    data['shots'][0][field] = value
                    self.assertTrue(validate_payload(data)[0])

    def test_validate_requires_positive_integer_shot_number(self):
        for value in (True, '1', 0, -1, 1.5):
            data = fixture()
            data['shots'][0]['shot_number'] = value
            self.assertTrue(validate_payload(data)[0])

    def test_validate_requires_finite_increasing_nonnegative_timing(self):
        for timing in ({}, {'start': 0}, {'start': False, 'end': 1},
                       {'start': '0', 'end': 1}, {'start': -1, 'end': 1},
                       {'start': 1, 'end': 1}, {'start': 2, 'end': 1},
                       {'start': 0, 'end': float('inf')}, {'start': float('nan'), 'end': 1}):
            with self.subTest(timing=timing):
                data = fixture()
                data['shots'][0]['time_range'] = timing
                self.assertTrue(validate_payload(data)[0])
        data = fixture()
        data['shots'][0]['time_range'] = {'start': 0, 'end': .5}
        self.assertEqual(validate_payload(data)[0], [])

    def test_validate_rejects_non_string_generation_prompt_without_crashing(self):
        for field in ('generation_prompt', 'seedance_prompt'):
            data = fixture()
            data['shots'][0][field] = ['not text']
            self.assertTrue(validate_payload(data)[0])

    def test_cli_rejects_empty_timing_and_list_description(self):
        data = fixture()
        data['shots'][0]['time_range'] = {}
        data['shots'][0]['description'] = []
        with tempfile.TemporaryDirectory() as td:
            file = Path(td)/'invalid-fields.json'
            file.write_text(json.dumps(data), encoding='utf-8')
            result = subprocess.run([sys.executable, '-B', '-X', 'utf8', str(SCRIPTS/'export_output.py'), str(file), '--validate'], capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(result.returncode, 1)
            self.assertIn('time_range', result.stdout)
            self.assertIn('description', result.stdout)
            self.assertNotIn('Traceback', result.stderr)


if __name__=='__main__':
    unittest.main()
