"""Regression tests for observable acceptance/rejection and exported content."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from export_output import audit_assets, audit_variety, audit_fidelity, generate_markdown


def fixture():
    shots = []
    for i in range(3):
        shots.append({
            'shot_number': i+1, 'time_range': {'start': i*10, 'end': (i+1)*10},
            'duration_seconds': 10, 'framing': '特写', 'focal_length': '35mm',
            'aperture': 'f/4', 'pov_family': '过肩', 'camera_height': '平视',
            'camera_angle': '平拍',
            'composition': '匹配视线', 'camera_movement': '固定',
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


if __name__=='__main__':
    unittest.main()
