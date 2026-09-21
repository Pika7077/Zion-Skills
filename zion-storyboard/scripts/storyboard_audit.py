"""Structural checks, separate from human assessment of narrative and physics."""
import math
import re

PROFILES = {'narrative', 'high_energy', 'legacy_quota'}
BASE = {'ordinary': 6, 'action_reversal': 8, 'fight': 10}
GAPS = {'ordinary': 3.0, 'action_reversal': 2.5, 'fight': 2.0}


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _prompts_requested(data):
    shots = data.get('shots', [])
    return data.get('meta', {}).get('include_generation_prompts') is True or any(
        isinstance(s, dict) and (s.get('generation_prompt') or s.get('seedance_prompt'))
        for s in shots
    )


def _has_real_file(files):
    if not isinstance(files, list):
        return False
    for item in files:
        if isinstance(item, str) and item.strip():
            return True
        if isinstance(item, dict) and any(item.get(k) for k in ('path', 'file', 'uri')):
            return True
    return False


def audit_assets(data):
    """Validate the lossless asset handoff used by formal storyboards."""
    meta = data.get('meta', {})
    mode = meta.get('asset_mode') or {}
    if not mode.get('enabled'):
        return {'passed': True, 'issues': [], 'warnings': [], 'stats': {'asset_mode': False}}

    issues, warnings = [], []
    for field in ('handoff_schema_version', 'project_id', 'source_script_version'):
        if not str(meta.get(field) or '').strip():
            issues.append(f'资产模式缺少 meta.{field}')
    source_scene_ids = meta.get('source_scene_ids')
    if not isinstance(source_scene_ids, list) or not source_scene_ids or not all(
            isinstance(v, str) and v.strip() for v in source_scene_ids):
        issues.append('资产模式需要非空 meta.source_scene_ids')
        source_scene_ids = []

    entries = []
    for category in ('character_assets', 'scene_assets', 'prop_assets', 'other_assets'):
        values = mode.get(category, [])
        if not isinstance(values, list):
            issues.append(f'meta.asset_mode.{category} 必须是列表')
            continue
        for item in values:
            if not isinstance(item, dict):
                issues.append(f'meta.asset_mode.{category} 的每项必须是对象')
                continue
            entries.append((category, item))
    if not entries:
        issues.append('已启用资产模式，但没有资产交接项')

    by_token, ids, refs = {}, set(), set()
    for category, item in entries:
        asset_id = str(item.get('asset_id') or '').strip()
        ref = str(item.get('ref') or '').strip()
        version = str(item.get('version') or '').strip()
        status = item.get('status')
        label = asset_id or ref or category
        if not asset_id:
            issues.append(f'资产 {label} 缺少 asset_id')
        elif asset_id in ids:
            issues.append(f'重复 asset_id：{asset_id}')
        else:
            ids.add(asset_id)
        if not ref:
            issues.append(f'资产 {label} 缺少 ref')
        elif ref in refs:
            issues.append(f'重复资产 ref：{ref}')
        else:
            refs.add(ref)
        if not version:
            issues.append(f'资产 {label} 缺少 version')
        if status not in ('approved', 'uploaded'):
            issues.append(f'资产 {label} 状态 {status!r} 不可用于正式分镜')
        elif status == 'approved' and not _has_real_file(item.get('files')):
            issues.append(f'approved 资产 {label} 缺少真实文件')
        elif status == 'uploaded' and not item.get('target_reference'):
            issues.append(f'uploaded 资产 {label} 缺少 target_reference')
        if asset_id:
            by_token[asset_id] = item
        if ref:
            by_token[ref] = item

    used_tokens = set()
    for shot in data.get('shots', []):
        if not isinstance(shot, dict):
            continue
        shot_number = shot.get('shot_number', '?')
        scene_id = shot.get('source_scene_id')
        if not isinstance(scene_id, str) or not scene_id.strip():
            issues.append(f'镜头 {shot_number} 缺少 source_scene_id')
        elif source_scene_ids and scene_id not in source_scene_ids:
            issues.append(f'镜头 {shot_number} 的 source_scene_id 未登记：{scene_id}')
        for field in ('asset_refs', 'character_refs', 'scene_refs', 'prop_refs'):
            values = shot.get(field, [])
            if isinstance(values, str):
                values = [values]
            if values is None:
                continue
            if not isinstance(values, list):
                issues.append(f'镜头 {shot_number} 的 {field} 必须是列表')
                continue
            for token in values:
                if not isinstance(token, str) or not token.strip():
                    issues.append(f'镜头 {shot_number} 的 {field} 含无效引用')
                    continue
                used_tokens.add(token)
                if token not in by_token:
                    issues.append(f'镜头 {shot_number} 引用了未登记资产：{token}')

    if _prompts_requested(data):
        for token in sorted(used_tokens):
            item = by_token.get(token)
            if item and (item.get('status') != 'uploaded' or not item.get('target_reference')):
                issues.append(f'生成提示词引用 {token}，但资产尚未 uploaded 或缺少 target_reference')

    return {
        'passed': not issues,
        'issues': issues,
        'warnings': warnings,
        'stats': {'asset_mode': True, 'declared_assets': len(entries), 'used_asset_refs': len(used_tokens)},
    }


def audit_content(data):
    shots = data.get('shots', [])
    profile = data.get('meta', {}).get('pacing_profile', 'narrative')
    issues, warnings = [], []
    if profile not in PROFILES:
        issues.append(f'未知 pacing_profile：{profile}')
    if not isinstance(shots, list) or not shots:
        return {'passed': False, 'issues': issues + ['没有可检查的镜头'], 'warnings': [], 'stats': {}}
    if any(not isinstance(s, dict) for s in shots):
        return {'passed': False, 'issues': issues + ['镜头必须是对象'], 'warnings': [], 'stats': {}}
    families = [s.get('pov_family') for s in shots if s.get('pov_family')]
    heights = [s.get('camera_height') for s in shots if s.get('camera_height')]
    angles = [s.get('camera_angle') for s in shots if s.get('camera_angle')]
    moves = [s.get('camera_movement') for s in shots if s.get('camera_movement')]
    stats = {
        'pacing_profile': profile,
        'pov_family_count': len(set(families)), 'pov_family_min_required': 0,
        'pov_families_used': sorted(set(families)),
        'camera_height_count': len(set(heights)), 'camera_height_levels': sorted(set(heights)),
        'camera_angle_count': len(set(angles)), 'camera_angles_used': sorted(set(angles)),
        'movement_count': len(set(moves)), 'movement_varieties': sorted(set(moves)),
        'composition_count': len({s.get('composition') for s in shots if s.get('composition')}),
        'v1_front_ratio': sum(1 for v in families if v in ('V1', '客观正面', '正面')) / len(families) if families else 0,
        'static_ratio': sum('固定' in m or '静止' in m for m in moves) / len(moves) if moves else 0,
        'scene_ref_angles': [s['scene_ref_angle'] for s in shots if s.get('scene_ref_angle')],
    }
    for s in shots:
        for field in ('description', 'new_feedback'):
            if not isinstance(s.get(field), str) or not s[field].strip():
                issues.append(f"镜头 {s.get('shot_number', '?')} 缺少 {field}")
    for a, b in zip(shots, shots[1:]):
        if a.get('description') and a.get('description') == b.get('description'):
            warnings.append(f"镜头 {a.get('shot_number')} 与 {b.get('shot_number')} 描述相同，人工核对是否重复事件")
    asset_report = audit_assets(data)
    issues.extend(asset_report['issues'])
    warnings.extend(asset_report['warnings'])
    stats.update(asset_report['stats'])
    warnings.append('需人工核对源文、补充权限、物理反馈、视线与动作承接；字段齐全不代表艺术质量合格。')
    return {'passed': not issues, 'issues': issues, 'warnings': warnings, 'stats': stats}


def audit_timing(data):
    shots = data.get('shots', [])
    meta = data.get('meta', {})
    profile = meta.get('pacing_profile', 'narrative')
    duration = meta.get('total_duration_seconds')
    limit = meta.get('generation_limit_seconds')
    prompts_requested = _prompts_requested(data)
    gate = data.get('fidelity_gate') or {}
    issues, stats = [], {'pacing_profile': profile, 'generation_limit_seconds': limit}
    target_model = meta.get('target_model')
    model = str(target_model or '').lower().replace(' ', '')
    if prompts_requested and not target_model:
        issues.append('包含生成提示词时必须记录 target_model')
    if profile not in PROFILES:
        issues.append(f'未知 pacing_profile：{profile}')
    if not number(duration) or duration <= 0:
        issues.append('组时长必须是正数')
    if prompts_requested and (not number(limit) or limit <= 0):
        issues.append('包含生成提示词时，generation_limit_seconds 必须记录采用的正数预算（用户给定或模型默认上限）')
    elif limit is not None and (not number(limit) or limit <= 0):
        issues.append('生成时长预算必须是正数')
    elif model == 'seedance2.5' and limit is not None and limit > 30:
        issues.append('Seedance 2.5 普通单次预算不能超过 30 秒；延长需单独规划')
    if issues:
        return {'passed': False, 'issues': issues, 'stats': stats}
    if number(limit) and duration > limit + 1e-6:
        issues.append(f'组时长 {duration}s 超过本次生成预算 {limit}s')
    if not isinstance(shots, list) or not shots or any(not isinstance(s, dict) for s in shots):
        return {'passed': False, 'issues': issues + ['没有有效镜头列表'], 'stats': stats}

    cap = gate.get('dialogue_capacity') or {}
    if cap:
        total = cap.get('total_min_seconds')
        if total is None:
            parts = [cap.get(k, 0) for k in ('lip_sync_min_seconds', 'visual_reading_min_seconds', 'action_reserve_seconds')]
            total = sum(parts) if all(number(v) and v >= 0 for v in parts) else None
    else:
        spoken = sum(len(re.findall(r'[\u4e00-\u9fff]', s.get('dialogue') or '')) for s in shots)
        sentences = sum(bool(s.get('dialogue')) for s in shots)
        total = spoken / 3.4 + 0.4 * sentences + (3 if spoken else 0)
        stats['dialogue_capacity_estimated'] = True
    if not number(total) or total < 0:
        issues.append('声音/动作容量必须是非负有限数值')
    else:
        stats['dialogue_capacity_seconds'] = round(total, 2)
        if total > duration + 1e-6:
            issues.append(f'声音与动作容量 {total:.2f}s 超过实际组长 {duration}s')

    dg = gate.get('density_gate') or {}
    category = dg.get('category', 'ordinary')
    legacy = profile == 'legacy_quota'
    smin = math.ceil(duration * BASE.get(category, 6) / 15) if legacy else 0
    stats.update(density_category=category if legacy else profile, smin=smin, actual_shots=len(shots))
    if legacy:
        if category not in BASE:
            issues.append(f'未知旧密度档：{category}')
        if len(shots) < smin:
            issues.append(f'旧配额档镜头数 {len(shots)} 低于 Smin={smin}')
        gap = dg.get('max_gap_seconds')
        if number(gap) and gap > GAPS.get(category, 3):
            issues.append('旧配额档反馈空档超限')

    previous = 0.0
    seen = set()
    for s in shots:
        n = s.get('shot_number')
        if not isinstance(n, int) or isinstance(n, bool) or n < 1 or n in seen:
            issues.append(f'镜头编号无效或重复：{n}')
        if isinstance(n, int):
            seen.add(n)
        tr = s.get('time_range') or {}
        start, end = tr.get('start'), tr.get('end')
        if not number(start) or not number(end):
            issues.append(f'镜头 {n} 时间码缺失或非有限数值')
            continue
        if start < 0 or end <= start:
            issues.append(f'镜头 {n} 时间区间必须为正向且非负')
        if abs(start - previous) > 1e-6:
            issues.append(f'镜头 {n} 起始 {start}s 与前段结束 {previous}s 不连续')
        previous = end
        stated = s.get('duration_seconds')
        if stated is not None and (not number(stated) or abs(stated - (end - start)) > 1e-6):
            issues.append(f'镜头 {n} duration_seconds 与时间区间不符')
        if not isinstance(s.get('new_feedback'), str) or not s['new_feedback'].strip():
            issues.append(f'镜头 {n} 缺少 new_feedback，需写明变化或有意义的等待')
        body = f"{s.get('description', '')} {s.get('generation_prompt') or s.get('seedance_prompt', '')}"
        # A separately numbered reverse shot is legal. Only explicit extra cuts need review.
        if re.search(r'然后切至|再切到|随后切至|交替近景|连续跳切', body):
            issues.append(f'镜头 {n} 可能含未编号的内部切换，需拆镜或改为连续观察')
        move = s.get('camera_movement', '')
        active = re.search(r'推进|拉远|横移|升高|下降|下移|上移|环绕|跟随|摇镜|甩镜|推近', move)
        if active:
            triplet = s.get('camera_move_triplet') or {}
            if any(not triplet.get(k) for k in ('origin', 'direction', 'stop_result')):
                issues.append(f'镜头 {n} 主动运镜缺少起点/路径/落点')
    if abs(previous - duration) > 1e-6:
        issues.append(f'末镜结束 {previous}s 不等于组时长 {duration}s')
    if gate.get('handoff_equation_ok') is False:
        issues.append('跨组人物/道具状态承接未通过')
    if gate.get('group_tail_stable_state') is False:
        issues.append('组尾承接状态尚未落实')
    return {'passed': not issues, 'issues': issues, 'stats': stats}
