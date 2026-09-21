#!/usr/bin/env python3
"""
分镜结果导出脚本
支持导出为结构化 JSON 和格式化 Markdown

用法：
  python export_output.py <input_json> --format json [--output <output_path>]
  python export_output.py <input_json> --format markdown [--output <output_path>]
  python export_output.py <input_dir> --format markdown --batch [--output <output_path>]
"""

import argparse
import json
import os
import re
from datetime import datetime
from storyboard_audit import audit_assets, audit_content, audit_timing

# 观察方式：字段名 pov_family 沿用旧名以兼容历史数据；取值现直接写名称（不用 V 代号）。
# 下表仅在读到旧代号时用于翻出可读名称。
LEGACY_VIEW_CODES = {
    'V1': '客观正面', 'V2': '过肩 OTS', 'V3': '正侧面 90°', 'V4': '3/4 侧背',
    'V5': '正背', 'V6': '低角度仰拍', 'V7': '高角度俯拍', 'V8': '主观 POV',
    'V9': '反射中介', 'V10': '遮挡偷拍', 'V11': '插入细节', 'V12': '弧线环绕',
}
POV_FAMILIES = LEGACY_VIEW_CODES

# 五维镜头语言：用于重复机位判定
CAMERA_DIMS = ['framing', 'camera_height', 'camera_angle', 'pov_family', 'composition', 'camera_movement']

# 资产模式下判定为"服装外貌描写"的高风险词（启发式，仅作提示）
APPEARANCE_HINTS = ['穿着', '一身', '西装', '衬衫', '外套', '长衫', '旗袍', '裙子',
                    '发型', '短发', '长发', '五官', '英俊', '美丽', '身材', '身高']

# ===== 剧本保真硬门词表（与 references/script-fidelity-gates.md 保持一致）=====

# 禁止的模糊方位词
VAGUE_SPATIAL = ['一侧', '一边', '另一侧', '另一边', '某侧', '某边', '斜侧',
                 '侧前方', '门边', '桌旁', '不远处', '适当距离']

# 禁止的单位、罗盘方位与字样（正则）
FORBIDDEN_MEASURE_PATTERNS = [
    (r'\d+\s*厘米', '厘米距离'),
    (r'\d+\s*毫米', '毫米距离'),
    (r'\d+(\.\d+)?\s*米(?![/米])', '米制距离'),
    (r'(东南|东北|西南|西北)', '罗盘方位'),
    (r'全画幅', '「全画幅」字样'),
    (r'虚拟镜头', '「虚拟镜头」字样'),
]

# 规范景别名（仅对这些名字做焦段-景别严格校验，其余景别写法跳过以免误报）
CANONICAL_FRAMINGS = ['大全景', '全景', '中景', '中近景', '近景', '特写', '大特写']

# 含「缓慢」类副词的运镜最小时长
SLOW_MOVE_PATTERN = r'缓慢|慢速|徐徐|慢推|慢摇|慢移|渐近|渐远'
SLOW_MOVE_MIN_SECONDS = 3

# 隐藏切镜：单个编号镜头内不得出现
HIDDEN_CUT_TERMS = ['交替近景', '反打', '跳切', '切至', '插入镜头', '蒙太奇']

# 引号外禁止出现的人物代词（与 references/script-fidelity-gates.md 第七节禁词表一致，含「其」）
PERSON_PRONOUNS = ['我', '你', '您', '他', '她', '他们', '她们', '本人', '其', '对方', '自己']

# 含「其/你/他」等字但非人物指代的常见复合词，检查前先剔除，避免误报
SAFE_COMPOUNDS = ['其他', '其它', '其中', '其实', '尤其', '及其', '其余', '其次', '其间', '极其', '自我', '自己人', '己方']

# 焦段 -> 允许的景别（仅对规范景别名做严格校验，避免误报）
FOCAL_SHOT_BANDS = [
    (0, 24, ['大全景']),
    (25, 35, ['全景']),
    (36, 55, ['中景']),
    (56, 79, ['中近景']),
    (80, 120, ['近景']),
    (121, 200, ['特写']),
    (201, 10 ** 6, ['大特写']),
]

# 密度档：15 秒镜头硬下限与反馈空档上限
DENSITY_BASE15 = {'ordinary': 6, 'action_reversal': 8, 'fight': 10}
DENSITY_GMAX = {'ordinary': 3.0, 'action_reversal': 2.5, 'fight': 2.0}

# ===== 画幅导演档（与 references/aspect-ratio-directing.md 第二节保持一致）=====
# axis: horizontal=横向主导 / vertical=纵向主导 / square=中心主导
# main_focal: 该画幅的主力焦段窗口（超出即告警，须给出理由）
ASPECT_PROFILES = {
    '16:9': {
        'axis': 'horizontal', 'label': '16:9 横版', 'main_focal': (24, 200),
        'summary': '横向为主 / 按需要建立环境 / 同框 3-5 人 / 焦段全段可用 / 底部10% 安全区 / 场景红利：人景并置 + 环境一次铺开',
        'advise': '广角环境展示充分，长焦可压缩空间；环境与人同框并置，左右空间承载关系',
    },
    '9:16': {
        'axis': 'vertical', 'label': '9:16 竖版', 'main_focal': (35, 85),
        'summary': '纵向为主 / 局部切片建立 / 同框人数按可读性安排 / 焦段主力 35-85mm / 上12% 下18% 安全区 / 场景重组：人物前置 + 环境走上下纵深',
        'advise': '保持关键动作可读，按需用纵深、同框或细节补充空间关系',
    },
    '21:9': {
        'axis': 'horizontal', 'label': '21:9 超宽', 'main_focal': (24, 50),
        'summary': '横向极致 / 全景建立 / 中心对称与左右对峙 / 广角 24-50mm 主力',
        'advise': '广角端优势最大；长焦纵向裁切后压缩过头',
    },
    '3:4': {
        'axis': 'vertical', 'label': '3:4 竖偏方', 'main_focal': (28, 100),
        'summary': '纵向为主保留横向余量 / 局部切片建立 / 同框 2-3 人 / 焦段主力 28-100mm',
        'advise': '≤24mm 横向展不开',
    },
    '1:1': {
        'axis': 'square', 'label': '1:1 方画幅', 'main_focal': (35, 85),
        'summary': '中心主导 / 局部切片建立 / 同框人数按可读性安排 / 焦段主力 35-85mm',
        'advise': '≤24mm 展不开；≥135mm 压迫过强',
    },
}

# 竖版/方版主力构图（见 aspect-ratio-directing.md 第三节）
VERTICAL_COMPOSITIONS = ['上下分层', '顶框压头', '底部压框', '垂直纵深', '贴边半框', '纵向框中框']
# 横版主力构图
HORIZONTAL_COMPOSITIONS = ['左右对峙分置', '对角线', '偏框留白', '三分法']
# 建立级景别
ESTABLISH_FRAMINGS = ['大全景', '全景']

# 引号（中文弯引号与直引号），用于剥离原台词后再查代词
QUOTE_PAIRS = [('“', '”'), ('"', '"'), ('「', '」')]


def generation_prompt(shot: dict) -> str:
    """Return the generic prompt field, with the legacy Seedance field as fallback."""
    return shot.get('generation_prompt') or shot.get('seedance_prompt') or ''


def asset_binding(asset: dict) -> str:
    """Return the concrete file or target binding retained in the handoff."""
    if asset.get('target_reference'):
        return f"target={asset['target_reference']}"
    values = []
    for item in asset.get('files') or []:
        if isinstance(item, str) and item:
            values.append(item)
        elif isinstance(item, dict):
            value = item.get('path') or item.get('file') or item.get('uri')
            if value:
                values.append(value)
    return f"file={','.join(values)}" if values else '无可用映射'


def validate_shot(shot: dict, require_prompt: bool = False) -> list:
    """验证单个镜头的必要字段，返回错误列表"""
    errors = []
    required = ['shot_number', 'time_range', 'framing', 'camera_movement', 'description']
    for field in required:
        if field not in shot or shot[field] is None or shot[field] == '':
            errors.append(f"镜头 {shot.get('shot_number', '?')} 缺少字段: {field}")
    if require_prompt and not generation_prompt(shot).strip():
        errors.append(f"镜头 {shot.get('shot_number', '?')} 缺少 generation_prompt/seedance_prompt")
    return errors


def audit_legacy_variety(data: dict) -> dict:
    """镜头多样性审计：防单调与防主角视角单一。返回 {passed, issues[], stats{}}"""
    shots = data.get('shots', [])
    duration = data.get('meta', {}).get('total_duration_seconds', 15)
    issues = []
    stats = {}

    if not shots:
        return {'passed': True, 'issues': [], 'stats': {}}

    # 观察方式数量（字段名 pov_family 保留，兼容旧数据；取值直接写名称，不用 V 代号）
    families = [s.get('pov_family') for s in shots if s.get('pov_family')]
    fam_count = len(set(families))
    min_required = 6 if duration > 30 else 4
    stats['pov_family_count'] = fam_count
    stats['pov_family_min_required'] = min_required
    stats['pov_families_used'] = sorted(set(families))
    if fam_count and fam_count < min_required:
        issues.append(f"观察方式仅 {fam_count} 种，低于下限 {min_required} 种（观察单一风险）")

    # 连续三镜同一观察方式
    for i in range(len(families) - 2):
        if families[i] and families[i] == families[i + 1] == families[i + 2]:
            issues.append(f"镜头 {i+1}-{i+3} 连续三镜同一观察方式 {families[i]}，必须打散")
            break

    # 正面平视占比（兼容旧代号 V1 与新写法）
    front_count = sum(1 for v in families if v in ('V1', '客观正面', '正面'))
    v1_ratio = front_count / len(families) if families else 0
    stats['v1_front_ratio'] = round(v1_ratio, 2)
    if v1_ratio > 1 / 3:
        issues.append(f"正面平视占比 {v1_ratio:.0%}，超过 1/3 上限（观察单调）")

    # 机位高度档位
    heights = [s.get('camera_height') for s in shots if s.get('camera_height')]
    height_count = len(set(heights))
    stats['camera_height_count'] = height_count
    stats['camera_height_levels'] = sorted(set(heights))
    if heights and height_count < 3:
        issues.append(f"机位高度仅 {height_count} 档，低于 3 档下限（高度扁平）")

    # 构图种类
    comps = [s.get('composition') for s in shots if s.get('composition')]
    comp_count = len(set(comps))
    stats['composition_count'] = comp_count
    if comps and comp_count < 3:
        issues.append(f"构图仅 {comp_count} 种，低于 3 种下限（画面雷同）")

    # 运镜种类与固定镜头占比
    moves = [s.get('camera_movement') for s in shots if s.get('camera_movement')]
    move_count = len(set(moves))
    stats['movement_count'] = move_count
    stats['movement_varieties'] = sorted(set(moves))
    if moves and move_count < 4:
        issues.append(f"运镜方式仅 {move_count} 种，低于 4 种下限（运镜呆板）")
    static_ratio = sum(1 for m in moves if m and '固定' in str(m)) / len(moves) if moves else 0
    stats['static_ratio'] = round(static_ratio, 2)
    if static_ratio > 1 / 3:
        issues.append(f"固定镜头占比 {static_ratio:.0%}，超过 1/3 上限（非信息炸弹场景）")

    # 重复机位：连续两镜五维中 >=3 维相同
    for i in range(len(shots) - 1):
        a, b = shots[i], shots[i + 1]
        same = [d for d in CAMERA_DIMS
                if a.get(d) and b.get(d) and a.get(d) == b.get(d)]
        if len(same) >= 3:
            issues.append(
                f"镜头 {i+1} 与 {i+2} 在 {len(same)} 个维度相同（{'/'.join(same)}），"
                f"判定重复机位，后一镜须重做")

    # 场景参考角度连续性
    angles = [s.get('scene_ref_angle') for s in shots if s.get('scene_ref_angle')]
    stats['scene_ref_angles'] = angles
    for i in range(len(angles) - 1):
        if angles[i] == angles[i + 1]:
            issues.append(f"镜头 {i+1} 与 {i+2} 场景参考角度同为「{angles[i]}」，须轮换")

    # 资产模式：主要人物服装外貌描写检测
    asset_mode = data.get('meta', {}).get('asset_mode', {})
    if asset_mode.get('enabled'):
        declared = asset_mode.get('character_assets', [])
        declared_refs = [c.get('ref', '') for c in declared]
        for s in shots:
            prompt = f"{generation_prompt(s)} {s.get('description', '')}"
            if any(ref in prompt for ref in declared_refs if ref):
                for hint in APPEARANCE_HINTS:
                    if hint in prompt:
                        issues.append(
                            f"镜头 {s.get('shot_number', '?')} 在资产模式下出现外貌词「{hint}」，"
                            f"与参考图冲突，须删除")
                        break
            elif not s.get('character_refs'):
                issues.append(f"镜头 {s.get('shot_number', '?')} 未标注 character_refs（资产模式必填）")

    return {'passed': len(issues) == 0, 'issues': issues, 'stats': stats}


def strip_quoted(text: str) -> str:
    """剥离引号内的原台词内容（原台词对人物代词完整豁免），返回引号外文本"""
    out, stack = [], []
    for ch in text or '':
        if stack:
            if ch == stack[-1]:
                stack.pop()
            continue
        closing = next((r for l, r in QUOTE_PAIRS if ch == l), None)
        if closing:
            stack.append(closing)
            continue
        out.append(ch)
    return ''.join(out)


def audit_variety(data: dict) -> dict:
    result = audit_content(data)
    if data.get('meta', {}).get('pacing_profile') == 'legacy_quota' and data.get('shots'):
        legacy = audit_legacy_variety(data)
        result['issues'].extend(legacy['issues'])
        result['stats'].update(legacy['stats'])
        result['passed'] = not result['issues']
    return result


def audit_fidelity(data: dict) -> dict:
    return audit_timing(data)


def format_time_range(shot: dict) -> str:
    """格式化时间范围"""
    tr = shot.get('time_range', {})
    start = tr.get('start', 0)
    end = tr.get('end', 0)
    return f"{start}-{end}秒"


def generate_markdown(data: dict) -> str:
    """将分镜数据生成为格式化 Markdown"""
    meta = data.get('meta', {})
    scene = data.get('scene_analysis', {})
    rhythm = data.get('rhythm_map', {})
    shots = data.get('shots', [])
    global_style = meta.get('global_style', {})

    source_name = meta.get('source_file', '未命名')
    md = []

    # 标题
    md.append(f"# {source_name} 分镜脚本\n")

    # 基本信息
    md.append("## 基本信息\n")
    if meta.get('source'):
        source_label = {'script': '剧本', 'video': '视频'}.get(meta['source'], meta['source'])
        md.append(f"- **来源类型**：{source_label}")
    md.append(f"- **来源文件**：{source_name}")
    md.append(f"- **场景类型**：{meta.get('scene_type', '未指定')}")
    md.append(f"- **总时长**：{meta.get('total_duration_seconds', 0)}秒")
    md.append(f"- **目标模型**：{meta.get('target_model') or '未指定（纯导演稿）'}")
    if meta.get('image_engine'):
        md.append(f"- **图像引擎**：{meta['image_engine']}")
    md.append(f"- **画幅**：{meta.get('aspect_ratio') or '未确认'}")
    md.append(f"- **生成时间**：{meta.get('generated_at', datetime.now().strftime('%Y-%m-%d %H:%M'))}\n")

    # 兼容已有分析与节奏字段，只导出实际提供的内容。
    analysis_lines = []
    for key, label, fields in [
            ('emotion_arc', '情绪弧线', ('start', 'trigger', 'peak', 'resolution')),
            ('power_structure', '权力结构', ('controller', 'passive')),
            ('color_progression', '色调走向', ('start', 'transition', 'end'))]:
        values = scene.get(key) or {}
        details = [f"{field}={values[field]}" for field in fields if values.get(field)]
        if details:
            analysis_lines.append(f"- **{label}**：{'；'.join(details)}")
    if scene.get('narrative_engine'):
        analysis_lines.append(f"- **叙事引擎**：{scene['narrative_engine']}")
    if analysis_lines:
        md.extend(["## 场景分析\n", *analysis_lines, ""])

    rhythm_lines = []
    for key, label in [('establishment', '建立层'), ('accumulation', '积累层'),
                       ('explosion', '爆发层'), ('aftershock', '余震层')]:
        stage = rhythm.get(key) or {}
        details = []
        if stage.get('shots') is not None:
            details.append(f"镜头：{stage['shots']}")
        if stage.get('pace'):
            details.append(f"节奏：{stage['pace']}")
        if details:
            rhythm_lines.append(f"- **{label}**：{'；'.join(details)}")
    if rhythm_lines:
        md.extend(["## 节奏地图\n", *rhythm_lines, ""])

    # 参数确认
    asset_mode = meta.get('asset_mode', {}) or {}
    params = meta.get('params', {})
    md.append("## 项目参数\n")
    md.append(f"- **项目/剧本版本**：{meta.get('project_id', '未登记')} / {meta.get('source_script_version', '未登记')}")
    md.append(f"- **交接契约**：{meta.get('handoff_schema_version', '未登记')}")
    md.append(f"- **源场次**：{'、'.join(meta.get('source_scene_ids') or []) or '未登记'}")
    md.append(f"- **画幅比例**：{params.get('aspect_ratio') or meta.get('aspect_ratio') or '未确认'}")
    for key, label in [('video_type', '视频类型'), ('visual_style', '媒介/视觉风格'),
                       ('run_mode', '运行模式'), ('audio_ref', '音频参考')]:
        if params.get(key):
            md.append(f"- **{label}**：{params[key]}")
    if asset_mode.get('enabled') or meta.get('temp_asset_mode'):
        md.append(f"- **资产模式**：{'全能参考' if asset_mode.get('enabled') else '临时资产引用'}")
    md.append("")

    # 使用的 @资产清单（与 output-schema.md 区块顺序一致：参数确认 → 资产清单 → 资产引用表 → 状态资产引用）
    if asset_mode.get('enabled') or meta.get('temp_asset_mode'):
        md.append("## 使用的 @资产清单\n")
        md.append("```text")
        md.append(f"人物：{' '.join(c.get('ref', '') for c in asset_mode.get('character_assets', []))}")
        md.append(f"场景：{' '.join(s.get('ref', '') for s in asset_mode.get('scene_assets', []))}")
        md.append(f"道具：{' '.join(p.get('ref', '') for p in asset_mode.get('prop_assets', []))}")
        md.append(f"其他：{' '.join(p.get('ref', '') for p in asset_mode.get('other_assets', []))}")
        md.append("```\n")

    # 资产引用表（全能参考模式）
    if asset_mode.get('enabled'):
        md.append("## 资产引用表\n")
        syntax = asset_mode.get('reference_syntax', '@')
        md.append("```text")
        chars = asset_mode.get('character_assets', [])
        for c in chars:
            identity = c.get('identity') or c.get('role')
            suffix = f"；{identity}" if identity else ''
            md.append(f"人物资产：{c.get('ref', '')} [{c.get('asset_id', '')}@{c.get('version', '')}；{c.get('status', '')}；{asset_binding(c)}{suffix}]")
        scenes = asset_mode.get('scene_assets', [])
        for sc in scenes:
            angles = sc.get('angles', [])
            suffix = '（单角度）' if sc.get('single_angle_only') else ''
            md.append(f"场景资产：{sc.get('ref', '')} [{sc.get('asset_id', '')}@{sc.get('version', '')}；{sc.get('status', '')}；{asset_binding(sc)}]（{' / '.join(angles)}）{suffix}")
            if sc.get('fixed_props'):
                md.append(f"  固定陈设：{sc['fixed_props']}")
        props = asset_mode.get('prop_assets', [])
        for p in props:
            md.append(f"道具资产：{p.get('ref', '')} [{p.get('asset_id', '')}@{p.get('version', '')}；{p.get('status', '')}；{asset_binding(p)}]")
        for p in asset_mode.get('other_assets', []):
            md.append(f"其他资产：{p.get('ref', '')} [{p.get('asset_id', '')}@{p.get('version', '')}；{p.get('status', '')}；{asset_binding(p)}]")
        if asset_mode.get('unregistered_characters'):
            md.append(f"未登记角色：{asset_mode['unregistered_characters']}")
        md.append(f"引用符号：{syntax}")
        md.append("```\n")

    # 状态资产引用（按 output-schema.md 顺序：资产引用表之后、全局风格锁定之前）
    state_ref = meta.get('state_assets', {}) or {}
    if state_ref.get('official') or state_ref.get('temporary') or state_ref.get('suggested'):
        md.append("## 状态资产引用\n")
        md.append("```text")
        md.append(f"使用正式状态资产：{'、'.join(state_ref.get('official', [])) or '无'}")
        md.append(f"使用临时状态引用：{'、'.join(state_ref.get('temporary', [])) or '无'}")
        md.append(f"建议补做状态资产：{'、'.join(state_ref.get('suggested', [])) or '无'}")
        if state_ref.get('temporary'):
            md.append("临时资产引用说明：当前为临时资产引用版，建议后续补做正式多状态资产库。")
        else:
            md.append("临时资产引用说明：不适用。")
        md.append("```\n")

    # 全局风格锁定
    style_parts = []
    for key in ['media_source', 'render_method', 'character_texture',
                'motion_quality', 'material_language', 'lighting_color']:
        # 资产模式下剔除已被资产锁定的槽位
        if asset_mode.get('enabled') and key in ('character_texture', 'material_language'):
            continue
        if global_style.get(key):
            style_parts.append(global_style[key])
    special = meta.get('special_stylization') or {}
    if style_parts or asset_mode.get('enabled') or 'enabled' in special:
        md.extend(["## 全局风格锁定\n", "```text"])
        if style_parts:
            md.append(f"风格锁定：{'，'.join(style_parts)}。")
        if asset_mode.get('enabled'):
            md.append("资产模式：全能参考。人物与场景外观以资产引用表为准，提示词不重复外貌与服装。")
        if special.get('enabled'):
            md.append(f"特殊风格化：启用。{special.get('description', '')}")
        elif special.get('enabled') is False:
            md.append("特殊风格化：不启用。")
        md.append("```\n")

    # 角色音色设定
    voice_profiles = data.get('voice_profiles', [])
    if voice_profiles:
        md.append("## 角色音色设定\n")
        md.append("```text")
        for vp in voice_profiles:
            md.append(f"{vp.get('ref', '@未命名')}：{vp.get('voice', '')}")
        md.append("```\n")

    # 分镜脚本
    md.append("## 分镜脚本\n")
    for shot in shots:
        n = shot.get('shot_number', '?')
        framing = shot.get('framing', '')
        tr = format_time_range(shot)
        pov = shot.get('pov_family', '')
        pov_name = shot.get('pov_family_name') or POV_FAMILIES.get(pov, '')
        if pov_name and pov_name != pov:
            pov_label = f"{pov} {pov_name}".strip()
        else:
            pov_label = pov
        heading = f"### 镜头{n}（{tr}）：{framing}"
        if pov_label:
            heading += f" ｜ {pov_label}"
        md.append(heading + "\n")
        if shot.get('source_scene_id'):
            md.append(f"- **源场次 ID**：{shot.get('source_scene_id')}")
        optics = [str(shot[key]) for key in ('focal_length', 'aperture')
                  if shot.get(key) and shot[key] != '未指定']
        if optics:
            md.append(f"- **焦段/光圈**：{' '.join(optics)}")
        if shot.get('camera_height'):
            md.append(f"- **机位高度**：{shot.get('camera_height')}")
        if pov_label:
            md.append(f"- **观察方式**：{pov_label}")
        if shot.get('composition'):
            md.append(f"- **构图**：{shot.get('composition')}")
        md.append(f"- **运镜**：{shot.get('camera_movement', '?')}")
        if shot.get('camera_angle'):
            md.append(f"- **角度**：{shot.get('camera_angle', '')}")
        if shot.get('scene_ref_angle'):
            md.append(f"- **场景参考**：{shot.get('scene_ref_angle')}参考")
        if shot.get('character_refs'):
            md.append(f"- **人物引用**：{'、'.join(shot.get('character_refs'))}")
        if shot.get('scene_refs'):
            md.append(f"- **场景引用**：{'、'.join(shot.get('scene_refs'))}")
        if shot.get('prop_refs'):
            md.append(f"- **道具引用**：{'、'.join(shot.get('prop_refs'))}")
        if shot.get('asset_refs'):
            md.append(f"- **其他资产引用**：{'、'.join(shot.get('asset_refs'))}")
        md.append(f"- **画面描述**：{shot.get('description', '')}")
        for key, label in [('shot_function', '镜头目的'), ('new_feedback', '信息与变化'),
                           ('continuity_in', '起始状态'), ('continuity_out', '结束状态'),
                           ('cut_motivation', '切点理由'), ('addition_note', '来源与补充')]:
            if shot.get(key):
                md.append(f"- **{label}**：{shot[key]}")

        if shot.get('character_emotion'):
            md.append(f"- **情绪**：{shot.get('character_emotion', '')}")
        if shot.get('physiological_detail'):
            md.append(f"- **生理性细节**：{shot.get('physiological_detail', '')}")
        if shot.get('physical_feedback'):
            md.append(f"- **物理反馈**：{shot.get('physical_feedback', '')}")
        if shot.get('dialogue'):
            md.append(f"- **对白**：\"{shot.get('dialogue', '')}\"（{shot.get('dialogue_tone', '')}）")
        prompt = generation_prompt(shot)
        if prompt:
            md.append(f"- **生成提示词**：`{prompt}`")
        md.append("")

    # 视角分布自检
    audit = audit_variety(data)
    md.append("## 视角分布自检\n")
    stats = audit.get('stats', {})
    issues = audit.get('issues', [])
    passed = audit.get('passed', True)

    def _line(label, value, ok=None):
        mark = '' if ok is None else (' ✅' if ok else ' ❌')
        return f"- **{label}**：{value}{mark}"

    profile = data.get('meta', {}).get('pacing_profile', 'narrative')
    md.append(_line('节奏档', profile))
    md.append(_line('镜头统计', f"观察方式 {stats.get('pov_family_count', 0)}；"
                    f"高度 {stats.get('camera_height_count', 0)}；"
                    f"角度 {stats.get('camera_angle_count', 0)}；运镜 {stats.get('movement_count', 0)}"))
    md.append(_line('固定镜头占比', f"{stats.get('static_ratio', 0):.0%}"))
    if profile != 'legacy_quota':
        md.append('以上为描述性统计，无默认配额。')
    for issue in issues:
        md.append(f'- 未通过：{issue}')
    for warning in audit.get('warnings', []):
        md.append(f'- 人工复核：{warning}')
    md.append(_line('结构检查', '通过' if passed else '未通过', passed))

    fidelity = audit_fidelity(data)
    fstats = fidelity.get('stats', {})
    fissues = fidelity.get('issues', [])
    md.append("\n## 时间与容量核对\n")
    md.append(_line('容量占用', f"{fstats.get('dialogue_capacity_seconds', '未知')}秒"
                    + ('（保守估算）' if fstats.get('dialogue_capacity_estimated') else '（输入规划值）')))
    md.append(_line('组时长 / 本次预算', f"{meta.get('total_duration_seconds', '?')} / "
                    f"{fstats.get('generation_limit_seconds') if fstats.get('generation_limit_seconds') is not None else '未确认'}秒"))
    if profile == 'legacy_quota':
        md.append(_line('旧配额镜头数', f"{fstats.get('actual_shots', 0)} / Smin {fstats.get('smin', 0)}"))
    for issue in fissues:
        md.append(f'- 未通过：{issue}')
    md.append(_line('时间结构检查', '通过' if not fissues else '未通过', not fissues))
    md.append('脚本不验证原文保真、物理合理性、艺术效果或模型生成成功。\n')

    prompts = [(shot, generation_prompt(shot)) for shot in shots if generation_prompt(shot)]
    if prompts:
        model_label = meta.get('target_model') or '未指定模型'
        md.append(f"## {model_label} 完整提示词\n")
        md.append("```text")

        if data.get('group_summary'):
            md.append(f"本组剧情：{data['group_summary']}")
        if data.get('space_layout'):
            md.append(f"人物空间站位：{data['space_layout']}")
        if data.get('environment'):
            md.append(f"环境：{data['environment']}")
        md.append("")

        for shot, prompt in prompts:
            tr = format_time_range(shot)
            n = shot.get('shot_number', '?')
            md.append(f"镜头{n}（{tr}）：{prompt}")

        if data.get('constraints'):
            md.append(f"约束：{data['constraints']}")
        if data.get('ending_state'):
            md.append(f"\n本组末尾空间状态：{data['ending_state']}")
        md.append(f"视频时长：{meta.get('total_duration_seconds', 0)}秒")
        md.append("```\n")

    # 收束方式
    if data.get('ending_method'):
        md.append("## 收束方式\n")
        md.append(f"{data['ending_method']}\n")

    # 生成前提醒
    reminders = data.get('pre_generation_reminders', [])
    if reminders:
        md.append("## 生成前提醒\n")
        for r in reminders:
            md.append(f"- {r}")
        md.append("")

    return '\n'.join(md)


def generate_batch_markdown(results: list) -> str:
    """将多个分镜结果合并为一个 Markdown"""
    parts = []
    for i, result in enumerate(results):
        file_name = result.get('file', f'文件{i+1}')
        if result.get('status') == 'error':
            parts.append(f"# {file_name}\n\n**处理失败**：{result.get('error', '未知错误')}\n\n---\n")
        else:
            data = result.get('data', result)
            data['meta'] = data.get('meta', {})
            data['meta']['source_file'] = file_name
            parts.append(generate_markdown(data))
            parts.append("\n---\n")
    return '\n'.join(parts)


def generate_batch_json(results: list) -> str:
    """生成批量 JSON"""
    batch = {
        'batch_meta': {
            'total_files': len(results),
            'generated_at': datetime.now().isoformat()
        },
        'results': results
    }
    return json.dumps(batch, ensure_ascii=False, indent=2)


def export_json(data, output_path: str = None) -> str:
    """导出为 JSON"""
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(json_str)
        print(f"JSON 已导出: {output_path}")
    return json_str


def export_markdown(data, output_path: str = None) -> str:
    """导出为 Markdown"""
    if isinstance(data, list):
        md_str = generate_batch_markdown(data)
    else:
        md_str = generate_markdown(data)

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_str)
        print(f"Markdown 已导出: {output_path}")
    return md_str


def main():
    parser = argparse.ArgumentParser(description='分镜结果导出工具')
    parser.add_argument('input', help='输入 JSON 文件或目录路径')
    parser.add_argument('--format', '-f', choices=['json', 'markdown'],
                        default='markdown', help='输出格式')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--batch', '-b', action='store_true',
                        help='批量模式（输入为目录）')
    parser.add_argument('--validate', action='store_true',
                        help='验证输出数据完整性')
    parser.add_argument('--audit', action='store_true',
                        help='结构、时间与容量检查；艺术质量须人工复核')
    parser.add_argument('--fidelity', action='store_true',
                        help='仅检查时间、容量和连续状态；不替代源文比对')

    args = parser.parse_args()

    # 加载数据
    if args.batch and os.path.isdir(args.input):
        results = []
        for f in sorted(os.listdir(args.input)):
            if f.endswith('.json'):
                fpath = os.path.join(args.input, f)
                with open(fpath, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                results.append({'file': f, 'status': 'success', 'data': data})
        data = results
    else:
        with open(args.input, 'r', encoding='utf-8') as f:
            data = json.load(f)

    # 验证
    if args.validate and not args.batch:
        if isinstance(data, dict):
            shots = data.get('shots', [])
            errors = [] if shots else ['没有镜头']
            require_prompt = data.get('meta', {}).get('include_generation_prompts') is True or any(
                generation_prompt(shot) for shot in shots if isinstance(shot, dict)
            )
            for shot in shots:
                errors.extend(validate_shot(shot, require_prompt=require_prompt))
            errors.extend(audit_assets(data)['issues'])
            if errors:
                print("验证错误:")
                for e in errors:
                    print(f"  - {e}")
                raise SystemExit(1)
            else:
                print(f"验证通过：{len(shots)} 个镜头数据完整")
        return

    # 审计
    if args.audit or args.fidelity:
        targets = data if isinstance(data, list) else [data]
        failed = not bool(targets)
        run_variety = args.audit
        for item in targets:
            if not isinstance(item, dict):
                failed = True
                continue
            item = item.get('data', item)
            name = item.get('meta', {}).get('source_file', '未命名')

            if run_variety:
                report = audit_variety(item)
                print(f"\n=== 镜头多样性审计：{name} ===")
                failed = failed or not report['passed']
                st = report['stats']
                print(f"观察方式：{st.get('pov_family_count', 0)} 种"
                      f"（下限 {st.get('pov_family_min_required', 4)}）"
                      f" 机位高度：{st.get('camera_height_count', 0)} 档"
                      f" 角度：{st.get('camera_angle_count', 0)} 种"
                      f" 构图：{st.get('composition_count', 0)} 种"
                      f" 运镜：{st.get('movement_count', 0)} 种")
                print(f"正面占比：{st.get('v1_front_ratio', 0):.0%}"
                      f" 固定镜头占比：{st.get('static_ratio', 0):.0%}")
                if report['issues']:
                    print(f"未通过（{len(report['issues'])} 项）：")
                    for iss in report['issues']:
                        print(f"  - {iss}")
                else:
                    print("自动结构检查通过；仍需人工核对内容。")

            f_report = audit_fidelity(item)
            print(f"\n=== 剧本保真硬门审计：{name} ===")
            failed = failed or not f_report['passed']
            fst = f_report['stats']
            est_tag = '（估算）' if fst.get('dialogue_capacity_estimated') else ''
            budget = fst.get('generation_limit_seconds')
            budget_label = f"{budget}s" if budget is not None else "未确认"
            print(f"台词容量：{fst.get('dialogue_capacity_seconds', 0)}s{est_tag} / 本次预算 {budget_label}"
                  f"  密度档：{fst.get('density_category', 'ordinary')}"
                  f"  镜头数：{fst.get('actual_shots', 0)} / Smin {fst.get('smin', 0)}")
            if f_report['issues']:
                print(f"未通过（{len(f_report['issues'])} 项）：")
                for iss in f_report['issues']:
                    print(f"  - {iss}")
            else:
                print("自动结构检查通过；仍需人工核对内容。")
        if failed:
            raise SystemExit(1)
        return

    # 导出
    if args.format == 'json':
        result_str = export_json(data, args.output)
    else:
        result_str = export_markdown(data, args.output)

    if not args.output:
        print(result_str)


if __name__ == '__main__':
    main()
