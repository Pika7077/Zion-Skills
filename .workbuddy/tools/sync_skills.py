"""把工作区技能镜像到安装目录。

用法：
    python .workbuddy/tools/sync_skills.py                      # 同步两处安装目录
    python .workbuddy/tools/sync_skills.py --target codex       # 只同步 ~/.codex/skills
    python .workbuddy/tools/sync_skills.py --target workbuddy   # 只同步 ~/.workbuddy/skills
    python .workbuddy/tools/sync_skills.py --dry                # 只报告差异

镜像规则：安装目录内的技能文件与工作区保持一致——缺失文件补齐，
内容不同的覆盖，工作区已删除的文件一并移除。__pycache__ 与 .pyc 不参与同步。

多会话协作时用 --target 只写自己那份：codex 写 ~/.codex/skills，
WorkBuddy 写 ~/.workbuddy/skills，避免两边同时写同一目录。
先在工作区修改并跑完 skill_lint.py，再执行本脚本。
"""

import filecmp
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SKILLS = ["zion-assets", "zion-qa", "zion-script", "zion-storyboard"]
TARGETS = {
    "codex": os.path.join(os.path.expanduser("~"), ".codex", "skills"),
    "workbuddy": os.path.join(os.path.expanduser("~"), ".workbuddy", "skills"),
}


def walk(base):
    out = {}
    for dp, dn, fn in os.walk(base):
        dn[:] = [d for d in dn if d != "__pycache__"]
        for f in fn:
            if f.endswith((".pyc", ".pyo")):
                continue
            p = os.path.join(dp, f)
            out[os.path.relpath(p, base)] = p
    return out


def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        return 0
    dry = "--dry" in sys.argv
    which = ["codex", "workbuddy"]
    for i, a in enumerate(sys.argv):
        if a == "--target" and i + 1 < len(sys.argv):
            which = [sys.argv[i + 1]]
    bad = [w for w in which if w not in TARGETS]
    if bad:
        print("未知目标：%s（可选 %s）" % (", ".join(bad), " / ".join(TARGETS)))
        return 2

    added = updated = removed = 0
    for name in which:
        target = TARGETS[name]
        print("== %s (%s) ==" % (name, target))
        for skill in SKILLS:
            src = os.path.join(ROOT, skill)
            dst = os.path.join(target, skill)
            if not os.path.isdir(dst):
                print("  跳过（目标不存在）：%s" % dst)
                continue
            s, d = walk(src), walk(dst)

            for rel, sp in sorted(s.items()):
                dp = os.path.join(dst, rel)
                if rel not in d:
                    print("  + %s/%s" % (skill, rel))
                    added += 1
                elif not filecmp.cmp(sp, dp, shallow=False):
                    print("  ~ %s/%s" % (skill, rel))
                    updated += 1
                else:
                    continue
                if not dry:
                    os.makedirs(os.path.dirname(dp), exist_ok=True)
                    shutil.copy2(sp, dp)

            for rel in sorted(set(d) - set(s)):
                print("  - %s/%s" % (skill, rel))
                removed += 1
                if not dry:
                    os.remove(os.path.join(dst, rel))

    print()
    print("added=%d updated=%d removed=%d%s" % (added, updated, removed, " (dry)" if dry else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
