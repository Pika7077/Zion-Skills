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
未知参数或缺失参数立即退出；全部源技能及非空入口通过检查后才开始镜像。
"""

import argparse
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
    def fail(error):
        raise error

    for dp, dn, fn in os.walk(base, onerror=fail):
        dn[:] = [d for d in dn if d != "__pycache__"]
        for f in fn:
            if f.endswith((".pyc", ".pyo")):
                continue
            p = os.path.join(dp, f)
            out[os.path.relpath(p, base)] = p
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--target", choices=sorted(TARGETS))
    parser.add_argument("--dry", action="store_true", help="只报告差异，不写入")
    args = parser.parse_args(argv)
    dry = args.dry
    which = [args.target] if args.target else list(TARGETS)

    # Validate every source before touching any installation, including later skills.
    sources = {}
    try:
        for skill in SKILLS:
            src = os.path.join(ROOT, skill)
            entry = os.path.join(src, "SKILL.md")
            if not os.path.isdir(src) or not os.path.isfile(entry):
                raise OSError("技能源缺失或不完整：%s（需要 SKILL.md）" % src)
            with open(entry, "rb") as fh:
                if not fh.read().strip():
                    raise OSError("技能入口为空：%s" % entry)
            sources[skill] = walk(src)
    except OSError as error:
        print("同步已停止：%s" % error, file=sys.stderr)
        return 1

    added = updated = removed = 0
    for name in which:
        target = TARGETS[name]
        print("== %s (%s) ==" % (name, target))
        for skill in SKILLS:
            dst = os.path.join(target, skill)
            if not os.path.isdir(dst):
                print("  跳过（目标不存在）：%s" % dst)
                continue
            s, d = sources[skill], walk(dst)

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
