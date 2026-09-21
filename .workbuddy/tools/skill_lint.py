"""Zion 技能家族交付前校验。

用法：
    python .workbuddy/tools/skill_lint.py            # 全量校验
    python .workbuddy/tools/skill_lint.py --meta     # 追加元话语候选清单

检查项：
    1. JUNK      非白名单文件类型、缓存目录与系统垃圾（含未知后缀的临时文件）
    2. ORPHAN    无任何入站引用的文件（含 Python 模块 import）
    3. DUPLICATE 内容完全相同的文件（已登记的有意双份除外）
    4. DANGLING  Markdown 链接指向不存在的文件或标题锚点
    5. SECTION_REF 正文 `§x` 章节引用在本档内找不到对应标题
    6. CROSS     跨技能相对路径链接（会使单独安装时断链）
    7. META      疑似无行为作用的说明性文本（--meta，仅报告）

发现 JUNK / ORPHAN / DUPLICATE / DANGLING / SECTION_REF / CROSS 时退出码为 1。
"""

import hashlib
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SKILLS = ["zion-assets", "zion-qa", "zion-script", "zion-storyboard"]
EXEMPT = {"SKILL.md", "_user_meta.json"}

# 允许出现在技能目录内的文件类型白名单。
# 采用白名单而非“已知垃圾后缀黑名单”：后缀黑名单永远漏新临时文件
# （.smokebak / .orig2 / 编辑器交换文件等），且漏网文件会混进 files 计数。
ALLOW_SUFFIX = (
    ".md", ".py", ".json", ".txt", ".yaml", ".yml", ".toml",
    ".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg",
)
ALLOW_NAMES = {"LICENSE", "NOTICE", ".gitkeep"}
JUNK_NAMES = {"Thumbs.db", ".DS_Store", "desktop.ini"}
# 目录级排除：绝不进入的目录名
JUNK_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "node_modules"}

# 有意保留的双份文件：各技能自带一份以支持单独安装，内容必须完全一致。
DECLARED_DUPES = [
    ("zion-assets/scripts/parse_input.py", "zion-storyboard/scripts/parse_input.py"),
]

META_PAT = re.compile(
    # 自述定位型：以“本档/本文件/本契约…”开头的自我描述句，通常不驱动行为
    r"^(本档是|本文件是|本契约是|本检查是|本手册是)"
    # 空泛结尾型
    r"|(仅供参考|总之|综上|简言之|值得一提的是|原则如此)$"
)


def collect():
    files = []
    for s in SKILLS:
        base = os.path.join(ROOT, s)
        for dp, dn, fn in os.walk(base):
            for f in fn:
                files.append(os.path.relpath(os.path.join(dp, f), ROOT))
    return sorted(files)


def read(rel):
    try:
        with open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def slug(title):
    t = title.strip().lower()
    t = re.sub(r"[`*_]", "", t)
    t = re.sub(r"[^\w\u4e00-\u9fff\- ]", "", t)
    return t.replace(" ", "-")


def headings(text):
    out = set()
    for m in re.finditer(r"^(#{1,6})\s+(.+?)\s*$", text, re.M):
        out.add(slug(m.group(2)))
    return out


def heading_keys(text):
    """标题的可引用键：编号（一/2.0）+ 标题正文 + 全文。"""
    keys = set()
    for m in re.finditer(r"^#{2,6}\s+(.+?)\s*$", text, re.M):
        h = m.group(1).strip()
        keys.add(h)
        m2 = re.match(r"^([一二三四五六七八九十]+|\d+(?:\.\d+)*)[、\.]?\s*(.*)$", h)
        if m2:
            keys.add(m2.group(1))
            if m2.group(2).strip():
                keys.add(m2.group(2).strip())
    return keys


# `§` 后允许的引用体：编号或中文数字，后接可选文字（如“五硬软”）
SEC_REF = re.compile(r"§\s*([一二三四五六七八九十]+|\d+(?:\.\d+)*)([^\s，。；：、）)\]|]{0,12})")


def section_ref_owner(text, pos):
    """判断 pos 处的 `§x` 引用归属哪个档。

    规则（按优先级）：
      1. 引用前若出现「本档」「本文件」「本表」，归属本档 → 返回 None。
      2. 引用前最近出现的「档名.md」视为被引档 → 返回该档名。
      3. 都无 → 归属本档 → 返回 None。

    注意「见 [某档](某档.md) §三」与「见本档 §三」写法并存，必须先判本档。
    """
    window = text[max(0, pos - 60):pos]
    own = None
    for m in re.finditer(r"本档|本文件|本表|本文", window):
        own = m.end()
    last_md = None
    for m in re.finditer(r"([\w\-]+\.md)", window):
        last_md = m
    if last_md and (own is None or last_md.end() > own):
        return last_md.group(1)
    return None


def main():
    show_meta = "--meta" in sys.argv
    files = collect()
    docs = [f for f in files if f.endswith((".md", ".py", ".json"))]
    texts = {f: read(f) for f in docs}
    stem_index = {}
    for f in files:
        stem_index.setdefault(os.path.splitext(os.path.basename(f))[0], []).append(f)

    problems = 0

    junk = []
    for f in files:
        base = os.path.basename(f)
        parts = f.replace("\\", "/").split("/")
        if any(p in JUNK_DIRS for p in parts):
            junk.append(f)
        elif base in JUNK_NAMES:
            junk.append(f)
        elif base in EXEMPT or base in ALLOW_NAMES:
            continue
        elif os.path.splitext(base)[1].lower() not in ALLOW_SUFFIX:
            junk.append(f)
    print("== JUNK ==")
    for f in junk:
        print("  " + f)
    problems += len(junk)

    print("== ORPHAN ==")
    for f in files:
        base = os.path.basename(f)
        if base in EXEMPT or f in junk:
            continue
        stem = os.path.splitext(base)[0]
        hit = False
        for g, t in texts.items():
            if g == f:
                continue
            if base in t:
                hit = True
                break
            if f.endswith(".py") and re.search(r"\b%s\b" % re.escape(stem), t):
                hit = True
                break
        if not hit:
            print("  " + f)
            problems += 1

    print("== DUPLICATE ==")
    declared = [frozenset(p.replace("/", os.sep) for p in pair) for pair in DECLARED_DUPES]
    seen = {}
    for f, t in texts.items():
        if not t.strip():
            continue
        seen.setdefault(hashlib.md5(t.encode()).hexdigest(), []).append(f)
    for group in seen.values():
        if len(group) > 1 and frozenset(group) not in declared:
            print("  " + " == ".join(group))
            problems += 1

    print("== DECLARED DUPLICATE（有意双份，内容须一致）==")
    for pair in DECLARED_DUPES:
        a, b = (os.path.normpath(p.replace("/", os.sep)) for p in pair)
        if not (os.path.exists(os.path.join(ROOT, a)) and os.path.exists(os.path.join(ROOT, b))):
            print("  缺失：%s / %s" % (a, b))
            problems += 1
            continue
        same = hashlib.md5(read(a).encode()).hexdigest() == hashlib.md5(read(b).encode()).hexdigest()
        print("  %s %s == %s" % ("OK" if same else "内容不一致", a, b))
        if not same:
            problems += 1

    print("== DANGLING ==")
    for f, t in texts.items():
        if not f.endswith(".md"):
            continue
        d = os.path.dirname(os.path.join(ROOT, f))
        for m in re.finditer(r"\]\(([^)]+)\)", t):
            raw = m.group(1).strip()
            if raw.startswith(("http://", "https://", "mailto:")):
                continue
            path, _, anchor = raw.partition("#")
            if not path:
                continue
            target = os.path.normpath(os.path.join(d, path))
            if not os.path.exists(target):
                print("  %s -> %s (文件缺失)" % (f, raw))
                problems += 1
                continue
            if anchor:
                rel_t = os.path.relpath(target, ROOT)
                if rel_t in texts or os.path.isfile(target):
                    if anchor not in headings(read(rel_t)):
                        print("  %s -> %s (锚点缺失)" % (f, raw))
                        problems += 1

    print("== SECTION_REF（正文 §x 引用在本档找不到对应标题）==")
    by_stem = {os.path.splitext(os.path.basename(f))[0]: f for f in docs}
    sec_ref = 0
    for f, t in sorted(texts.items()):
        if not f.endswith(".md"):
            continue
        own = heading_keys(t)
        for m in SEC_REF.finditer(t):
            num, tail = m.group(1), m.group(2)
            owner = section_ref_owner(t, m.start())
            if owner:
                # 跨档引用：交给被引档校验，不属于本档标题空间
                other = by_stem.get(os.path.splitext(owner)[0])
                if other and other != f:
                    if num not in heading_keys(read(other)):
                        line = t[:m.start()].count("\n") + 1
                        print("  %s:%d  §%s%s -> %s 无此标题" % (f, line, num, tail, owner))
                        sec_ref += 1
                    continue
                # 档名存在但不在本次文档集内，无法校验，跳过
                if other is None:
                    continue
            if num not in own:
                line = t[:m.start()].count("\n") + 1
                print("  %s:%d  §%s%s（本档无此标题）" % (f, line, num, tail))
                sec_ref += 1
    if not sec_ref:
        print("  无")
    problems += sec_ref

    if show_meta:
        print("== META（人工判定）==")
        for f, t in sorted(texts.items()):
            for i, ln in enumerate(t.split("\n"), 1):
                s = ln.strip()
                if s and META_PAT.search(s) and len(s) < 120:
                    print("  %s:%d  %s" % (f, i, s))

    print("== CROSS（单独安装时会失效的跨技能链接）==")
    cross = 0
    for skill in SKILLS:
        hits = set()
        for f, t in texts.items():
            if not f.startswith(skill + os.sep) or not f.endswith(".md"):
                continue
            for m in re.finditer(r"\]\(([^)]+)\)", t):
                raw = m.group(1)
                if "zion-" not in raw:
                    continue
                for other in SKILLS:
                    if other != skill and ("/" + other + "/" in raw or "\\" + other + "\\" in raw):
                        hits.add((f, raw))
        if hits:
            print("  [%s]" % skill)
            for f, raw in sorted(hits):
                print("    %s -> %s" % (f, raw))
            cross += len(hits)
    if not cross:
        print("  无")
    problems += cross

    print()
    print("files=%d  problems=%d" % (len(files), problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
