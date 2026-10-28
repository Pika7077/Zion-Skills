"""多会话并发守卫：技能写租约 + 基线快照。

同一工作区可能被 codex 与 WorkBuddy 同时编辑，本工具提供两道防线：

1. 写租约（lock）：同一技能同一时刻只允许一个会话修改。
   python .workbuddy/tools/skill_guard.py status
   python .workbuddy/tools/skill_guard.py acquire <skill> --owner <工具名> --session <会话唯一ID> --intent <要做什么>
   python .workbuddy/tools/skill_guard.py release <skill> --owner <工具名> --session <同一会话ID>
   python .workbuddy/tools/skill_guard.py acquire <skill> --owner <工具名> --session <会话ID> --force

2. 基线快照（snapshot/check）：动手前拍快照，交付前比对，发现别人在你作业期间改过哪些文件。
   python .workbuddy/tools/skill_guard.py snapshot --by <会话名>
   python .workbuddy/tools/skill_guard.py check

租约文件在 .workbuddy/locks/，基线在 .workbuddy/state/baseline.json。两者都不随技能分发。
每个会话使用独立 session；系统锁串行化租约更新，JSON 使用原子替换。
"""

import argparse
import hashlib
import json
import os
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from functools import wraps

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SKILLS = ["zion-assets", "zion-qa", "zion-script", "zion-storyboard"]
LOCK_DIR = os.path.join(ROOT, ".workbuddy", "locks")
STATE_DIR = os.path.join(ROOT, ".workbuddy", "state")
DEFAULT_TTL = 180


def now():
    return datetime.now(timezone.utc).astimezone()


def lock_path(skill):
    return os.path.join(LOCK_DIR, skill + ".json")


def read_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return default


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".guard-", suffix=".tmp", dir=os.path.dirname(path))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2, sort_keys=True)
            fh.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextmanager
def skill_mutex(skill):
    """Serialize lease read/modify/write; OS releases the lock if a process dies."""
    os.makedirs(LOCK_DIR, exist_ok=True)
    with open(os.path.join(LOCK_DIR, skill + ".mutex"), "a+b") as fh:
        fh.seek(0, os.SEEK_END)
        if fh.tell() == 0:
            fh.write(b"0")
            fh.flush()
        fh.seek(0)
        acquired = False
        try:
            try:
                if os.name == "nt":
                    import msvcrt
                    msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                acquired = True
            except OSError as error:
                raise OSError("租约正在被另一进程更新，请重试：%s" % skill) from error
            yield
        finally:
            if acquired:
                fh.seek(0)
                if os.name == "nt":
                    msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(fh.fileno(), fcntl.LOCK_UN)


def lease_operation(func):
    @wraps(func)
    def run(args):
        if args.skill not in SKILLS or not args.owner.strip() or not args.session.strip():
            print("技能、工具名与会话 ID 必须有效。", file=sys.stderr)
            return 2
        if hasattr(args, "ttl") and args.ttl <= 0:
            print("租约分钟数必须大于 0。", file=sys.stderr)
            return 2
        try:
            with skill_mutex(args.skill):
                return func(args)
        except (OSError, ValueError) as error:
            print("租约操作已停止：%s" % error, file=sys.stderr)
            return 1
    return run


def lock_state(lock):
    since = datetime.fromisoformat(lock["since"])
    if since.tzinfo is None:
        raise ValueError("租约时间必须包含时区")
    expires = since + timedelta(minutes=lock.get("ttl_minutes", DEFAULT_TTL))
    return since, expires, now() > expires


def read_lease(skill):
    """Unreadable/corrupt leases are errors, never an unoccupied skill."""
    path = lock_path(skill)
    try:
        with open(path, encoding="utf-8") as fh:
            lock = json.load(fh)
    except FileNotFoundError:
        return None
    try:
        if not isinstance(lock, dict) or not isinstance(lock.get("owner"), str) or not lock["owner"].strip():
            raise ValueError("缺少 owner")
        ttl = lock.get("ttl_minutes", DEFAULT_TTL)
        if type(ttl) is not int or ttl <= 0:
            raise ValueError("ttl_minutes 无效")
        lock_state(lock)
    except (KeyError, TypeError, ValueError, OverflowError) as error:
        raise ValueError("租约文件损坏，停止操作：%s" % path) from error
    return lock


def cmd_status(_args):
    print("== 写租约 ==")
    rows = []
    for skill in SKILLS:
        lock = read_lease(skill)
        if not lock:
            rows.append((skill, "-", "-", "-", "-", "空闲"))
            continue
        _since, expires, stale = lock_state(lock)
        left = expires - now()
        rows.append((
            skill,
            lock.get("owner", "?"),
            lock.get("session_id", "旧租约：无会话ID"),
            lock["since"][11:16],
            ("已过期 %d 分钟" % int(-left.total_seconds() // 60)) if stale else ("剩 %d 分钟" % int(left.total_seconds() // 60)),
            lock.get("intent", ""),
        ))
    for r in rows:
        print("  %-16s %-10s %-20s %-6s %-14s %s" % r)
    print()
    print("未持租约的技能不要写入；需要时用 acquire 领取。")
    return 0


@lease_operation
def cmd_acquire(args):
    skill = args.skill
    lock = read_lease(skill)
    if lock:
        _since, expires, stale = lock_state(lock)
        same_owner = lock.get("owner") == args.owner and lock.get("session_id") == args.session
        if not same_owner and not stale and not args.force:
            print("被占用：%s 自 %s 起持有 %s（%s）" % (lock.get("owner"), lock["since"], skill, lock.get("intent", "")))
            print("会话 %s 持有租约；等待 release，或用 --force 显式接管。" % lock.get("session_id", "旧版"))
            return 1
        if not same_owner:
            lock.setdefault("history", []).append({
                "event": "takeover" if not stale else "stale-takeover",
                "from": lock.get("owner"),
                "from_session": lock.get("session_id"),
                "by": args.owner,
                "by_session": args.session,
                "at": now().isoformat(timespec="seconds"),
            })
            print("⚠️ 已从 %s 手中%s %s。" % (lock.get("owner"), "抢回" if stale else "强制夺取", skill))
    data = lock or {}
    data.update({
        "skill": skill,
        "owner": args.owner,
        "session_id": args.session,
        "since": now().isoformat(timespec="seconds"),
        "ttl_minutes": args.ttl,
        "intent": args.intent or "",
    })
    write_json(lock_path(skill), data)
    print("持有租约：%s ← %s / %s（%d 分钟内有效）" % (skill, args.owner, args.session, args.ttl))
    return 0


@lease_operation
def cmd_release(args):
    lock = read_lease(args.skill)
    if not lock:
        print("%s 本就没有租约。" % args.skill)
        return 0
    if (lock.get("owner") != args.owner or lock.get("session_id") != args.session) and not args.force:
        print("租约属于 %s / %s；工具名相同不代表同一会话。" % (lock.get("owner"), lock.get("session_id", "旧版")))
        return 1
    os.remove(lock_path(args.skill))
    print("已释放：%s（原持有者 %s）" % (args.skill, lock.get("owner")))
    return 0


def walk_skills():
    out = {}
    for skill in SKILLS:
        for dp, dn, fn in os.walk(os.path.join(ROOT, skill)):
            dn[:] = [d for d in dn if d != "__pycache__"]
            for f in fn:
                if f.endswith((".pyc", ".pyo")):
                    continue
                p = os.path.join(dp, f)
                with open(p, "rb") as fh:
                    digest = hashlib.sha1(fh.read()).hexdigest()
                out[os.path.relpath(p, ROOT).replace(os.sep, "/")] = digest
    return out


def cmd_snapshot(args):
    data = {"saved_at": now().isoformat(timespec="seconds"), "saved_by": args.by, "files": walk_skills()}
    write_json(os.path.join(STATE_DIR, "baseline.json"), data)
    print("基线已记录：%d 个文件（%s，by %s）" % (len(data["files"]), data["saved_at"], args.by))
    return 0


def cmd_check(args):
    base = read_json(os.path.join(STATE_DIR, "baseline.json"))
    if not base:
        print("还没有基线；先跑 snapshot。")
        return 1
    cur = walk_skills()
    old = base["files"]
    changed = sorted(p for p in set(old) & set(cur) if old[p] != cur[p])
    added = sorted(set(cur) - set(old))
    removed = sorted(set(old) - set(cur))
    print("== 与基线（%s，by %s）比对 ==" % (base["saved_at"], base.get("saved_by", "?")))
    for label, items in (("新增", added), ("改动", changed), ("删除", removed)):
        print("  %s %d" % (label, len(items)))
        for p in items:
            print("     %s %s" % ("+" if label == "新增" else ("~" if label == "改动" else "-"), p))
    if not (added or changed or removed):
        print("  无变化。")
    print()
    print("上面若出现不是你改的文件，说明有其它会话在同一时段写入；先对齐再继续。")
    return 0


def main():
    ap = argparse.ArgumentParser(description="技能写租约与基线快照")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status").set_defaults(func=cmd_status)

    p = sub.add_parser("acquire")
    p.add_argument("skill", choices=SKILLS)
    p.add_argument("--owner", required=True, help="工具名，如 codex / workbuddy")
    p.add_argument("--session", required=True, help="本会话唯一 ID；续租和释放时复用")
    p.add_argument("--intent", default="")
    p.add_argument("--ttl", type=int, default=DEFAULT_TTL, help="租约分钟数，默认 %d" % DEFAULT_TTL)
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_acquire)

    p = sub.add_parser("release")
    p.add_argument("skill", choices=SKILLS)
    p.add_argument("--owner", required=True)
    p.add_argument("--session", required=True)
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_release)

    p = sub.add_parser("snapshot")
    p.add_argument("--by", default="unknown")
    p.set_defaults(func=cmd_snapshot)

    sub.add_parser("check").set_defaults(func=cmd_check)

    args = ap.parse_args()
    try:
        return args.func(args)
    except (OSError, ValueError) as error:
        print("操作已停止：%s" % error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
