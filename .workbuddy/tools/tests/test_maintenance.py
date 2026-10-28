"""Behavioral regression tests; all filesystem writes stay in temporary fixtures."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from datetime import timedelta
from types import SimpleNamespace
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, TOOLS / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Isolated(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name).resolve()
        self.addCleanup(self.temporary.cleanup)
        # Verify the directory used for recursive fixture cleanup.
        self.assertEqual(self.base.parent, Path(tempfile.gettempdir()).resolve())

    def inventory(self, base):
        return {str(p.relative_to(base)): p.read_bytes() for p in base.rglob('*') if p.is_file()}


class SyncTests(Isolated):
    def setUp(self):
        super().setUp()
        self.sync = load('sync_skills')
        self.source = self.base / 'source'
        self.targets = {name: self.base / name for name in ('codex', 'workbuddy')}
        for skill in self.sync.SKILLS:
            src = self.source / skill
            src.mkdir(parents=True)
            (src / 'SKILL.md').write_text('new entry', encoding='utf-8')
            (src / 'reference.md').write_text('new reference', encoding='utf-8')
            for target in self.targets.values():
                dst = target / skill
                dst.mkdir(parents=True)
                (dst / 'SKILL.md').write_text('installed entry', encoding='utf-8')
                (dst / 'obsolete.md').write_text('obsolete reference', encoding='utf-8')
        self.sync.ROOT = str(self.source)
        self.sync.TARGETS = {k: str(v) for k, v in self.targets.items()}

    def run_sync(self, *args):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return self.sync.main(list(args))

    def test_invalid_arguments_never_modify_installations(self):
        before = self.inventory(self.base)
        for args in (['--drry'], ['--dr'], ['--target'], ['--target', 'unknown'], ['--tar', 'codex']):
            with self.subTest(args=args), self.assertRaises(SystemExit) as result:
                self.run_sync(*args)
            self.assertEqual(result.exception.code, 2)
            self.assertEqual(before, self.inventory(self.base))

    def test_missing_source_never_deletes_installed_files(self):
        before = self.inventory(self.base)
        self.sync.ROOT = str(self.base / 'missing')
        self.assertNotEqual(self.run_sync('--target', 'codex'), 0)
        self.assertEqual(before, self.inventory(self.base))

    def test_missing_later_skill_entry_blocks_entire_sync(self):
        (self.source / self.sync.SKILLS[-1] / 'SKILL.md').unlink()
        before = self.inventory(self.base)
        self.assertNotEqual(self.run_sync(), 0)
        self.assertEqual(before, self.inventory(self.base))

    def test_empty_entry_blocks_entire_sync(self):
        (self.source / self.sync.SKILLS[-1] / 'SKILL.md').write_text('  ', encoding='utf-8')
        before = self.inventory(self.base)
        self.assertNotEqual(self.run_sync(), 0)
        self.assertEqual(before, self.inventory(self.base))

    def test_source_read_error_blocks_entire_sync(self):
        before = self.inventory(self.base)
        walk = self.sync.walk
        def fail_on_last(path):
            if str(path).endswith(self.sync.SKILLS[-1]):
                raise PermissionError('fixture unreadable')
            return walk(path)
        with patch.object(self.sync, 'walk', fail_on_last):
            self.assertNotEqual(self.run_sync(), 0)
        self.assertEqual(before, self.inventory(self.base))

    def test_dry_run_never_adds_overwrites_or_deletes(self):
        before = self.inventory(self.base)
        self.assertEqual(self.run_sync('--dry'), 0)
        self.assertEqual(before, self.inventory(self.base))

    def test_selected_target_mirrors_and_other_target_stays_unchanged(self):
        other = self.inventory(self.targets['workbuddy'])
        self.assertEqual(self.run_sync('--target=codex'), 0)
        self.assertEqual(self.inventory(self.source), self.inventory(self.targets['codex']))
        self.assertEqual(other, self.inventory(self.targets['workbuddy']))

    def test_missing_referenced_subtree_does_not_delete_installed_rules(self):
        skill = self.sync.SKILLS[-1]
        (self.source/skill/'SKILL.md').write_text('[规则](references/rules.md)', encoding='utf-8')
        for target in self.targets.values():
            rules = target/skill/'references/rules.md'
            rules.parent.mkdir()
            rules.write_text('keep installed rules', encoding='utf-8')
        before = self.inventory(self.base)
        self.assertNotEqual(self.run_sync(), 0)
        self.assertEqual(before, self.inventory(self.base))

    def test_missing_nested_reference_blocks_sync(self):
        (self.source/self.sync.SKILLS[-1]/'reference.md').write_text('[更多](missing.md)', encoding='utf-8')
        before = self.inventory(self.base)
        self.assertNotEqual(self.run_sync(), 0)
        self.assertEqual(before, self.inventory(self.base))

    def test_missing_entry_script_blocks_sync(self):
        (self.source/self.sync.SKILLS[-1]/'SKILL.md').write_text('python scripts/missing.py input.json', encoding='utf-8')
        before = self.inventory(self.base)
        self.assertNotEqual(self.run_sync(), 0)
        self.assertEqual(before, self.inventory(self.base))

    def test_invalid_markdown_encoding_blocks_sync(self):
        (self.source/self.sync.SKILLS[-1]/'reference.md').write_bytes(b'\xff\xfe')
        before = self.inventory(self.base)
        self.assertNotEqual(self.run_sync(), 0)
        self.assertEqual(before, self.inventory(self.base))

    def test_external_and_same_file_links_are_allowed(self):
        (self.source/self.sync.SKILLS[-1]/'SKILL.md').write_text('# Entry\n[本站](#entry) [外部](https://example.org/rules)', encoding='utf-8')
        self.assertEqual(self.run_sync('--target', 'codex'), 0)

    def test_repository_sources_pass_preflight(self):
        self.sync.ROOT = str(TOOLS.parents[1])
        self.assertEqual(self.run_sync('--dry'), 0)


RUNNER = '''
import importlib.util, pathlib, sys, time
spec = importlib.util.spec_from_file_location('guard_child', sys.argv[1])
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)
guard.LOCK_DIR = sys.argv[2]
ready, go = sys.argv[3:5]
if ready != '-':
    pathlib.Path(ready).write_text('ready')
if go != '-':
    deadline = time.monotonic() + 10
    while not pathlib.Path(go).exists():
        if time.monotonic() > deadline:
            raise RuntimeError('test rendezvous timed out')
        time.sleep(.01)
sys.argv = [sys.argv[1]] + sys.argv[5:]
raise SystemExit(guard.main())
'''


class GuardTests(Isolated):
    def setUp(self):
        super().setUp()
        self.guard = load('skill_guard')
        self.guard.LOCK_DIR = str(self.base / 'locks')
        self.skill = 'zion-storyboard'

    def args(self, session='session-a', **kwargs):
        values = dict(skill=self.skill, owner='codex', session=session, intent='fixture', ttl=180, force=False)
        values.update(kwargs)
        return SimpleNamespace(**values)

    def quiet(self, func, args):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return func(args)

    def acquire(self, session='session-a', **kwargs):
        return self.quiet(self.guard.cmd_acquire, self.args(session, **kwargs))

    def release(self, session='session-a', **kwargs):
        return self.quiet(self.guard.cmd_release, self.args(session, **kwargs))

    def start_child(self, session, ready='-', go='-', force=False):
        cmd = [sys.executable, '-B', '-X', 'utf8', '-c', RUNNER, str(TOOLS / 'skill_guard.py'), self.guard.LOCK_DIR, str(ready), str(go), 'acquire', self.skill, '--owner', 'codex', '--session', session]
        if force:
            cmd.append('--force')
        child = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        def stop():
            if child.poll() is None:
                child.kill()
            child.communicate(timeout=10)
        self.addCleanup(stop)
        return child

    def wait_ready(self, *paths):
        deadline = time.monotonic() + 8
        while not all(p.exists() for p in paths):
            self.assertLess(time.monotonic(), deadline, 'child did not reach rendezvous')
            time.sleep(.01)

    def test_same_tool_different_sessions_cannot_share_lease(self):
        self.assertEqual(self.acquire(), 0)
        self.assertNotEqual(self.acquire('session-b'), 0)
        self.assertEqual(self.guard.read_lease(self.skill)['session_id'], 'session-a')

    def test_same_session_can_renew_and_release(self):
        self.assertEqual(self.acquire(), 0)
        self.assertEqual(self.acquire(ttl=90), 0)
        self.assertEqual(self.guard.read_lease(self.skill)['ttl_minutes'], 90)
        self.assertEqual(self.release(), 0)
        self.assertIsNone(self.guard.read_lease(self.skill))

    def test_wrong_session_or_owner_cannot_release(self):
        self.assertEqual(self.acquire(), 0)
        self.assertNotEqual(self.release('session-b'), 0)
        self.assertNotEqual(self.release(owner='workbuddy'), 0)
        self.assertIsNotNone(self.guard.read_lease(self.skill))

    def test_expired_lease_can_be_taken_over_and_records_sessions(self):
        self.acquire()
        lock = self.guard.read_lease(self.skill)
        lock['since'] = (self.guard.now() - timedelta(minutes=200)).isoformat()
        self.guard.write_json(self.guard.lock_path(self.skill), lock)
        self.assertEqual(self.acquire('session-b'), 0)
        event = self.guard.read_lease(self.skill)['history'][-1]
        self.assertEqual((event['event'], event['from_session'], event['by_session']), ('stale-takeover', 'session-a', 'session-b'))

    def test_force_takeover_invalidates_previous_session(self):
        self.acquire()
        self.assertEqual(self.acquire('session-b', force=True), 0)
        self.assertNotEqual(self.release(), 0)
        self.assertEqual(self.release('session-b'), 0)

    def test_corrupt_lease_is_not_treated_as_available(self):
        path = Path(self.guard.lock_path(self.skill))
        path.parent.mkdir()
        for value in ('{broken', '{}', 'null'):
            with self.subTest(value=value):
                path.write_text(value, encoding='utf-8')
                self.assertNotEqual(self.acquire(), 0)
                self.assertNotEqual(self.release(), 0)
                self.assertEqual(path.read_text(encoding='utf-8'), value)

    def test_legacy_lease_is_not_renewed_by_owner_name_only(self):
        self.acquire()
        lock = self.guard.read_lease(self.skill)
        lock.pop('session_id')
        self.guard.write_json(self.guard.lock_path(self.skill), lock)
        self.assertNotEqual(self.acquire(), 0)
        self.assertNotEqual(self.release(), 0)

    def test_nonpositive_ttl_does_not_create_a_lease(self):
        for ttl in (0, -1):
            self.assertNotEqual(self.acquire(ttl=ttl), 0)
        self.assertFalse(Path(self.guard.lock_path(self.skill)).exists())

    def test_two_processes_have_exactly_one_winner(self):
        ready_a, ready_b, go = (self.base / name for name in ('ready-a', 'ready-b', 'go'))
        children = [self.start_child('session-a', ready_a, go), self.start_child('session-b', ready_b, go)]
        self.wait_ready(ready_a, ready_b)
        go.write_text('go')
        outputs = [child.communicate(timeout=12) for child in children]
        self.assertEqual(sorted(child.returncode for child in children), [0, 1], outputs)
        self.assertIn(self.guard.read_lease(self.skill)['session_id'], ('session-a', 'session-b'))

    def test_os_mutex_cannot_be_bypassed_even_with_force(self):
        with self.guard.skill_mutex(self.skill):
            child = self.start_child('session-b', force=True)
            output = child.communicate(timeout=12)
            self.assertNotEqual(child.returncode, 0, output)
            self.assertFalse(Path(self.guard.lock_path(self.skill)).exists())
        self.assertEqual(self.acquire(), 0)

    def test_failed_atomic_replace_preserves_previous_lease(self):
        self.acquire()
        before = Path(self.guard.lock_path(self.skill)).read_bytes()
        with patch.object(self.guard.os, 'replace', side_effect=PermissionError('fixture')):
            self.assertNotEqual(self.acquire(ttl=90), 0)
        self.assertEqual(Path(self.guard.lock_path(self.skill)).read_bytes(), before)
        self.assertFalse(list(Path(self.guard.LOCK_DIR).glob('.guard-*.tmp')))

    def test_process_exit_releases_os_mutex(self):
        ready = self.base / 'holder-ready'
        holder_code = RUNNER.split('ready, go =')[0] + '''
with guard.skill_mutex('zion-storyboard'):
    pathlib.Path(sys.argv[3]).write_text('ready')
    time.sleep(30)
'''
        child = subprocess.Popen([sys.executable, '-B', '-X', 'utf8', '-c', holder_code,
                                  str(TOOLS/'skill_guard.py'), self.guard.LOCK_DIR, str(ready)],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            self.wait_ready(ready)
            child.kill()
            child.communicate(timeout=10)
            self.assertEqual(self.acquire(), 0)
        finally:
            if child.poll() is None:
                child.kill()
            child.communicate(timeout=10)

    def test_cli_requires_session_before_any_write(self):
        cmd = [sys.executable, '-B', '-X', 'utf8', '-c', RUNNER,
               str(TOOLS/'skill_guard.py'), self.guard.LOCK_DIR, '-', '-',
               'acquire', self.skill, '--owner', 'codex']
        result = subprocess.run(cmd, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertFalse(Path(self.guard.lock_path(self.skill)).exists())


if __name__ == '__main__':
    unittest.main()
