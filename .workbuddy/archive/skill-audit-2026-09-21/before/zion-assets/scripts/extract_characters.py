#!/usr/bin/env python3
"""
人物信息提取和 JSON 输出生成脚本。
接收文本内容（剧本/对白/视频ASR文本），识别人物并生成结构化 JSON。
"""

import sys
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path


# ============================================================
# 人物识别引擎
# ============================================================

class CharacterExtractor:
    """从文本中识别人物并提取信息"""

    def __init__(self, text: str, source_type: str = "剧本",
                 source_file: str = "inline-input", file_type: str = "txt"):
        self.text = text
        self.source_type = source_type
        self.source_file = source_file
        self.file_type = file_type
        self.lines = text.splitlines()
        self.characters = {}  # name -> info dict
        self.aliases_map = {}  # 别名 -> 正式名

    def extract(self) -> dict:
        """主提取流程"""
        # Step 1: 识别剧本结构
        scene_blocks = self._split_scenes()

        # Step 2: 识别所有出场人物
        self._identify_characters(scene_blocks)

        # Step 3: 合并同一个人物的不同称呼
        self._merge_aliases()

        # Step 4: 提取每个角色的详细信息
        self._extract_character_info()

        # Step 5: 提取人物关系
        self._extract_relationships()

        # Step 6: 质量检查
        self._quality_check()

        # Step 7: 生成输出
        return self._generate_output()

    def _split_scenes(self) -> list:
        """将文本按场景/场次分割"""
        scene_patterns = [
            r'^【场景\d+[：:].*】',
            r'^第[一二三四五六七八九十\d]+场',
            r'^Scene\s+\d+',
            r'^场次[：:]\s*\d+',
        ]

        blocks = []
        current_block = []
        for line in self.lines:
            is_scene_start = any(re.match(p, line.strip()) for p in scene_patterns)
            if is_scene_start and current_block:
                blocks.append("\n".join(current_block))
                current_block = [line]
            else:
                current_block.append(line)
        if current_block:
            blocks.append("\n".join(current_block))

        return blocks if blocks else ["\n".join(self.lines)]

    def _identify_characters(self, scene_blocks: list):
        """从场景块中识别所有人物"""
        # 对白模式：角色名后跟对白
        dialogue_pattern = re.compile(r'^([^\s：（(]{1,8})[：:](.*)')

        # 叙述提及模式
        mention_patterns = [
            re.compile(r'([^\s，。,\.]{2,4})(?:说|道|问|答|喊|叫|吼|叫喊)'),
        ]

        for block in scene_blocks:
            lines = block.splitlines()
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # 匹配对白格式
                d_match = dialogue_pattern.match(line)
                if d_match:
                    name = d_match.group(1).strip()
                    dialogue = d_match.group(2).strip()
                    # 过滤非人物行（如"旁白""OS""画外音"等）
                    if not self._is_meta_label(name) and len(name) <= 8:
                        char_id = self._normalize_name(name)
                        if char_id not in self.characters:
                            self.characters[char_id] = {
                                "name": name,
                                "aliases": [],
                                "appearance_count": 0,
                                "dialogues": [],
                                "mentions": [],
                                "context_lines": [],
                            }
                        self.characters[char_id]["dialogues"].append(dialogue)
                        self.characters[char_id]["appearance_count"] += 1

    def _is_meta_label(self, name: str) -> bool:
        """判断是否是元标签而非人物名"""
        meta_patterns = [
            r'^(旁白|OS|画外音|字幕|标题|章节|第.*场|Scene|场次)',
            r'^[（(]',  # 以括号开头
            r'^[【\[]',  # 以方括号开头
        ]
        return any(re.match(p, name) for p in meta_patterns)

    def _normalize_name(self, name: str) -> str:
        """标准化人物名，去除空格和标点"""
        return re.sub(r'[\s（）()\[\]【】""'']', '', name).strip()

    def _merge_aliases(self):
        """合并同一人物的不同称呼"""
        # 处理常见的别名情况
        # 1. 单名是双名的简写：如"婉儿"是"林婉儿"的子串
        names = list(self.characters.keys())

        for i, name_a in enumerate(names):
            for j, name_b in enumerate(names):
                if i >= j:
                    continue
                if name_a not in self.characters or name_b not in self.characters:
                    continue

                # B是A的子串 → B可能是A的昵称
                if len(name_b) < len(name_a) and name_b in name_a:
                    self._merge_characters(name_b, name_a)
                elif len(name_a) < len(name_b) and name_a in name_b:
                    self._merge_characters(name_a, name_b)

    def _merge_characters(self, from_name: str, to_name: str):
        """将 from_name 的信息合并到 to_name"""
        if from_name not in self.characters or to_name not in self.characters:
            return

        from_char = self.characters[from_name]
        to_char = self.characters[to_name]

        to_char["aliases"].append(from_char["name"])
        to_char["dialogues"].extend(from_char["dialogues"])
        to_char["appearance_count"] += from_char["appearance_count"]

        self.aliases_map[from_name] = to_name
        del self.characters[from_name]

    def _extract_character_info(self):
        """从文本中提取每个角色的详细信息"""
        for char_id, char in self.characters.items():
            # 提取对白中的台词风格
            char["dialogue_style"] = self._analyze_dialogue_style(char["dialogues"])

            # 从上下文提取外貌/身份等（简化版，实际使用时配合AI分析）
            char["extracted_info"] = self._extract_from_context(char_id, char)

    def _analyze_dialogue_style(self, dialogues: list) -> dict:
        """分析台词风格"""
        if not dialogues:
            return {"tone": "未知", "habits": [], "pace": "未知", "keywords": []}

        total_chars = sum(len(d) for d in dialogues)
        avg_length = total_chars / len(dialogues)

        # 判断句长节奏
        if avg_length < 10:
            pace = "快（短句为主）"
        elif avg_length < 30:
            pace = "适中"
        else:
            pace = "慢（长句为主）"

        # 检测反问句比例
        rhetorical = sum(1 for d in dialogues if '？' in d or '?' in d)
        rhetorical_ratio = rhetorical / len(dialogues)

        if rhetorical_ratio > 0.3:
            tone = "反问/质疑型"
        elif any(d.endswith('！') or d.endswith('!') for d in dialogues):
            tone = "直接/情绪型"
        else:
            tone = "陈述/理性型"

        return {
            "tone": tone,
            "pace": pace,
            "habits": [],
            "keywords": [],
            "sample_lines": dialogues[:3],
            "avg_sentence_length": round(avg_length, 1),
        }

    def _extract_from_context(self, char_id: str, char: dict) -> dict:
        """从文本上下文中提取人物额外信息（基于全文搜索）"""
        info = {}
        # 在全文搜索角色名出现的上下文
        name_patterns = [char["name"]] + char.get("aliases", [])
        for pattern in name_patterns:
            for i, line in enumerate(self.lines):
                if pattern in line:
                    # 记录角色名出现的上下文行
                    start = max(0, i - 1)
                    end = min(len(self.lines), i + 2)
                    char["context_lines"].extend(self.lines[start:end])

        # 后续由AI分析context_lines提取外貌、性格、身份等
        return info

    def _extract_relationships(self):
        """提取人物关系"""
        # 通过共现场景和互相对白推断关系
        # 简化版：记录任意两个角色间有对白交互
        # 完整版需要NLP关系抽取
        pass

    def _quality_check(self):
        """质量检查"""
        issues = []
        # 检查是否有重名
        # 检查所有人物是否都有必要信息
        for char_id, char in self.characters.items():
            if not char.get("dialogues"):
                issues.append(f"角色 '{char['name']}' 没有对白")
        return issues

    def _generate_output(self) -> dict:
        """生成符合 Schema 的 JSON 输出"""
        tz = timezone(timedelta(hours=8))
        processed_at = datetime.now(tz).strftime("%Y-%m-%dT%H:%M:%S+08:00")

        # 按出场次数排序
        sorted_chars = sorted(
            self.characters.items(),
            key=lambda x: x[1]["appearance_count"],
            reverse=True
        )

        # 确定角色层级
        total_chars = len(sorted_chars)
        characters_output = []

        for idx, (char_id, char) in enumerate(sorted_chars):
            # 确定角色层级
            if total_chars <= 3:
                if idx == 0:
                    role_level = "主角"
                else:
                    role_level = "重要配角"
            elif idx < 3:
                role_level = "主角"
            elif idx < total_chars * 0.3 + 2:
                role_level = "重要配角"
            else:
                role_level = "功能角色"

            char_output = {
                "id": f"char_{idx + 1:03d}",
                "name": char["name"],
                "aliases": char.get("aliases", []),
                "gender": "未知",
                "age_range": "未知",
                "role_level": role_level,
                "appearance_count": char["appearance_count"],
                "appearance": {
                    "hair": "未知",
                    "face": "未知",
                    "body_type": "未知",
                    "height": "未知",
                    "skin_tone": "未知",
                    "distinguishing_features": [],
                    "clothing_style": "未知",
                },
                "personality": {
                    "core_traits": [],
                    "behavior_patterns": [],
                    "emotional_style": "未知",
                },
                "background": {
                    "occupation": "未知",
                    "social_class": "未知",
                    "education": "未知",
                    "family": "未知",
                    "backstory": "未知",
                },
                "relationships": [],
                "dialogue_style": char.get("dialogue_style", {}),
                "visual_dna": {
                    "visual_symbol": "未知",
                    "color_scheme": "未知",
                    "posture": "未知",
                    "aura_keywords": [],
                },
                "evidence_levels": {
                    "name": "原文明确",
                    "gender": "未知",
                    "age": "未知",
                    "appearance": "未知",
                    "personality": "未知",
                    "background": "未知",
                    "relationships": "未知",
                },
            }
            characters_output.append(char_output)

        return {
            "meta": {
                "source": self.source_type,
                "source_file": self.source_file,
                "file_type": self.file_type,
                "processed_at": processed_at,
                "total_characters": len(characters_output),
                "extraction_notes": [
                    "自动提取仅识别对白人物与基础语言特征；其他字段保持未知，等待证据复核或授权补全。",
                ],
            },
            "characters": characters_output,
        }


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_characters.py <text_file_or_content> [--source-type 剧本|视频]")
        sys.exit(1)

    input_arg = sys.argv[1]
    source_type = "剧本"
    for i, arg in enumerate(sys.argv):
        if arg == "--source-type" and i + 1 < len(sys.argv):
            source_type = sys.argv[i + 1]

    input_path = Path(input_arg)
    if input_path.is_file():
        with input_path.open("r", encoding="utf-8") as f:
            text = f.read()
        source_file = input_path.name
        file_type = input_path.suffix.lower().lstrip(".") or "txt"
    else:
        text = input_arg
        source_file = "inline-input"
        file_type = "txt"

    extractor = CharacterExtractor(text, source_type, source_file, file_type)
    result = extractor.extract()

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
