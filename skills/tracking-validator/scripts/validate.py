#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
埋点验证脚本 - 核心验证逻辑
输入：埋点方案Excel + 测试数据CSV + 序号范围
输出：HTML验证报告
"""

import csv
import json
import re
import sys
import os
import html as html_module
import pandas as pd
from datetime import datetime

# 预置属性（st_ 开头，可硬编码，不参与多余参数校验）
PRESET_ST_PARAMS = [
    'st_role_id',
    'st_account_id',
    'st_distinct_id',
    'st_event_name',
    'st_event_time',
]

# 完整白名单 = PRESET_ST_PARAMS + Excel「预置属性和公共属性」中的非 st_ 公共属性
# 运行时由 apply_system_params_from_excel 写入
SYSTEM_PARAMS = list(PRESET_ST_PARAMS)

# 「上报参数详情」注释中表示可选参数的短语（可出现在描述性注释任意位置）
OPTIONAL_PARAM_COMMENT_PHRASES = [
    r'有就报[，,]?没有就算了',
    r'没有就算了',
    r'非必填',
]

# 注释整体或句首的独立「可选 / 选填」标注（避免误匹配「可选场景」「可选择」等描述）
OPTIONAL_PARAM_COMMENT_STANDALONE = [
    r'^可选$',
    r'^选填$',
    r'^可选[，,；;]',
    r'^选填[，,；;]',
]

# 报告展示用：事件信封字段（非 Excel 业务白名单；与「多余参数」校验无关）
REPORT_ENVELOPE_FIELDS = [
    'st_pk_id', 'st_status', 'st_user_id', 'st_role_id', 'st_account_id',
    'st_distinct_id', 'st_event_name', 'st_event_time', 'st_event_datetime',
]

# 测试数据 CSV 必需列（用户提供时仅需这 5 列）
REQUIRED_CSV_COLUMNS = [
    'st_event_name',
    'st_raw_message',
    'st_status',
    'st_error_info',
    'st_available_message',
]

def get_skill_source_dir():
    """skill 内置示例文件目录（禁止用于正式验证）。"""
    return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'source'))

def is_skill_builtin_file(file_path):
    """判断路径是否落在 skill/source/ 内置示例目录内。"""
    abs_path = os.path.normpath(os.path.abspath(file_path))
    source_dir = get_skill_source_dir()
    try:
        return os.path.commonpath([abs_path, source_dir]) == source_dir
    except ValueError:
        return False

def assert_user_input_files(excel_file, csv_file):
    """校验必须使用用户提供的输入文件，禁止 fallback 到 skill 内置示例。"""
    for label, path in [('埋点方案 Excel', excel_file), ('测试数据 CSV', csv_file)]:
        if not path or not str(path).strip():
            print(f'错误：{label} 未指定。请使用用户 @ 提供的文件路径。')
            sys.exit(1)
        if not os.path.isfile(path):
            print(f'错误：{label} 不存在: {path}')
            sys.exit(1)
        if is_skill_builtin_file(path):
            print(f'错误：{label} 使用了 skill 内置示例文件，禁止用于验证: {os.path.abspath(path)}')
            print('请改用用户 @ 提供的 xlsx 和 csv 文件。')
            sys.exit(1)


def assert_csv_columns(csv_file):
    """校验 CSV 包含验证所需的 5 列。"""
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            print('错误：CSV 文件为空或缺少表头。')
            sys.exit(1)
        headers = [h.strip() for h in reader.fieldnames if h and h.strip()]
        missing = [col for col in REQUIRED_CSV_COLUMNS if col not in headers]
        if missing:
            print('错误：测试数据 CSV 缺少必需列：')
            for col in missing:
                print(f'  - {col}')
            print('')
            print('请提供以下 5 列（表头名称须完全一致）：')
            for col in REQUIRED_CSV_COLUMNS:
                print(f'  - {col}')
            sys.exit(1)
        extra = [col for col in headers if col not in REQUIRED_CSV_COLUMNS]
        if extra:
            print(f'提示：CSV 含额外列 {extra}，验证时仅使用必需 5 列，其余列可忽略。')

def event_time_value(record):
    """用于排序，数值越大越新。"""
    try:
        return int(record.get('st_event_time') or 0)
    except (TypeError, ValueError):
        return 0

def normalize_event_time_ms(st_event_time):
    """将 st_event_time 统一为毫秒时间戳；无法解析时返回 0。"""
    try:
        ts = int(st_event_time or 0)
    except (TypeError, ValueError):
        return 0
    if ts <= 0:
        return 0
    # 秒级（约 10 位）转毫秒
    if ts < 10 ** 12:
        ts *= 1000
    return ts

def get_validation_now_ms():
    """检验时刻（脚本执行时的当前时间），毫秒。"""
    return int(datetime.now().timestamp() * 1000)

def is_not_future_event(record, now_ms=None):
    """
    事件时间不超过检验时刻则可用于「取最新」判定。
    无法解析时间时不因「未来」排除（避免误伤脏数据）。
    """
    if now_ms is None:
        now_ms = get_validation_now_ms()
    ts = normalize_event_time_ms(record.get('st_event_time'))
    if ts <= 0:
        return True
    return ts <= now_ms

def filter_not_future_records(results, now_ms=None):
    """排除 st_event_time 晚于检验时刻的记录。"""
    if now_ms is None:
        now_ms = get_validation_now_ms()
    return [r for r in results if is_not_future_event(r, now_ms)]

def count_future_records(results, now_ms=None):
    """统计事件时间为未来的候选条数。"""
    if now_ms is None:
        now_ms = get_validation_now_ms()
    return sum(1 for r in results if not is_not_future_event(r, now_ms))

def extract_event_datetime(raw_message, csv_row=None):
    """从 st_available_message 或 st_event_time 提取可读时间。"""
    if csv_row:
        avail = csv_row.get('st_available_message', '')
        if avail:
            try:
                dt = json.loads(avail).get('st_event_datetime')
                if dt:
                    return str(dt)
            except Exception:
                pass

    st_event_time = raw_message.get('st_event_time')
    if st_event_time:
        try:
            ts = int(st_event_time)
            if ts > 10 ** 12:
                ts /= 1000
            return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            pass

    return ''

def get_latest_record(results, now_ms=None):
    """
    每个点位取最新一条匹配记录作为判定依据。
    仅在 st_event_time <= 检验时刻 的候选中取最新，排除未来时间脏数据。
    """
    eligible = filter_not_future_records(results, now_ms)
    if not eligible:
        return None
    return max(eligible, key=event_time_value)

def get_latest_stored_record(results, now_ms=None):
    """
    取最新一条已入库（st_status=1）的匹配记录，用于入库案例与入库错误原因或警告。
    同样排除事件时间晚于检验时刻的记录。
    """
    eligible = filter_not_future_records(results, now_ms)
    stored = [r for r in eligible if str(r.get('st_status', '')) == '1']
    if not stored:
        return None
    return max(stored, key=event_time_value)

def parse_number_sequence(seq_str):
    """
    解析序号字符串，支持格式：
    - 20-35（范围）
    - 20,21,22（列表）
    - 20-25,30,35（混合）
    """
    numbers = []
    parts = seq_str.split(',')
    for part in parts:
        part = part.strip()
        if '-' in part:
            start, end = part.split('-', 1)
            start = int(start.strip())
            end = int(end.strip())
            numbers.extend(range(start, end + 1))
        else:
            numbers.append(int(part))
    return sorted(set(numbers))

def normalize_page_identifier(value):
    """后端埋点等无页面标识时，Excel 单元格可能为空或 nan。"""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ''
    page = str(value).strip()
    if page.lower() in ('nan', 'none', ''):
        return ''
    return page

def parse_common_attrs_from_excel(excel_file):
    """
    从 Excel「预置属性和公共属性」Sheet 读取「公共属性」名称。
    规则：
    - st_role_id / st_account_id / st_distinct_id / st_event_name / st_event_time 为预置属性，脚本硬编码，不依赖本函数
    - Sheet 中其余属性（如 platform_type、adid、utm_source、channel）必须从 Excel 获取
    - Sheet 里若也写了上述 5 个 st_ 预置属性，读取时跳过（避免重复）
    """
    try:
        df = pd.read_excel(excel_file, sheet_name='预置属性和公共属性')
    except (ValueError, KeyError) as e:
        print(f'错误：无法读取 Excel「预置属性和公共属性」Sheet: {e}')
        sys.exit(1)

    name_col = None
    for col in df.columns:
        if str(col).strip() in ('属性名称', '属性名', '参数名称', '参数名'):
            name_col = col
            break
    if name_col is None and len(df.columns) > 0:
        name_col = df.columns[0]

    if name_col is None:
        print('错误：Excel「预置属性和公共属性」Sheet 无可用列')
        sys.exit(1)

    preset_st_set = set(PRESET_ST_PARAMS)
    names = []
    for val in df[name_col].dropna():
        name = str(val).strip()
        if not name or name.lower() == 'nan':
            continue
        if name in preset_st_set:
            continue  # 预置 st_ 属性由硬编码承担
        names.append(name)
    # 去重且保序
    seen = set()
    unique = []
    for n in names:
        if n not in seen:
            seen.add(n)
            unique.append(n)
    return unique


def apply_system_params_from_excel(excel_file):
    """
    SYSTEM_PARAMS = 硬编码预置 st_ 属性 + Excel 公共属性（非 st_ 部分）。
    """
    global SYSTEM_PARAMS
    common = parse_common_attrs_from_excel(excel_file)
    SYSTEM_PARAMS = list(PRESET_ST_PARAMS) + common
    return SYSTEM_PARAMS, common


def parse_excel_tracking_plan(excel_file, target_numbers):
    """
    从Excel解析埋点方案，返回指定序号的埋点定义
    """
    # 读取开发计划Sheet
    df = pd.read_excel(excel_file, sheet_name='开发计划')
    
    points = []
    for _, row in df.iterrows():
        seq_num = int(row.iloc[0])  # 序号（第一列）
        
        if seq_num not in target_numbers:
            continue
        
        # 提取字段（注意：页面截图列在索引2，需要跳过）
        point = {
            '序号': seq_num,
            '埋点信息': str(row.iloc[1]),  # 埋点信息
            '页面标识': normalize_page_identifier(row.iloc[3]),  # 页面标识（索引3，跳过页面截图）
            '埋点事件': str(row.iloc[4]),  # 埋点事件
            '上报时机': str(row.iloc[5]),  # 上报时机
            '上报参数详情': str(row.iloc[6]),  # 上报参数详情
            '前后端埋点': str(row.iloc[7]),  # 前后端埋点
            '定义参数': [],  # 待解析（必填 + 可选）
            '必填参数': [],
            '可选参数': [],
            '匹配条件': {}  # 待解析
        }
        
        # 解析上报参数详情，提取参数名（区分必填 / 可选）
        parsed_params = parse_params_from_detail(point['上报参数详情'])
        point['定义参数'] = parsed_params['all']
        point['必填参数'] = parsed_params['required']
        point['可选参数'] = parsed_params['optional']
        
        # 从上报参数详情解析匹配条件（非动态参数）
        point['匹配条件'] = parse_match_conditions_from_detail(point['上报参数详情'])
        
        points.append(point)
    
    return points

def comment_indicates_optional(comment):
    """判断 # 后注释是否将参数标为可选。"""
    comment = comment.strip()
    if not comment:
        return False
    if any(re.search(pattern, comment) for pattern in OPTIONAL_PARAM_COMMENT_PHRASES):
        return True
    return any(re.search(pattern, comment) for pattern in OPTIONAL_PARAM_COMMENT_STANDALONE)

def is_optional_param_line(line):
    """
    判断参数是否可选，满足任一即视为可选：
    1. # 注释含「有就报，没有就算了」等短语，或独立标注「可选 / 选填」
    2. 值侧为 {可选参数}、{可选}、{选填...}、{可选补充} 等占位写法（有没有上报都无所谓）
    """
    if '#' in line:
        comment = line.split('#', 1)[1]
        if comment_indicates_optional(comment):
            return True

    if '=' not in line:
        return False

    value_part = line.split('=', 1)[1]
    if '#' in value_part:
        value_part = value_part.split('#', 1)[0]
    value_part = value_part.strip()
    if not value_part:
        return False

    # {可选参数}、{可选}、{选填参数} 等：花括号内语义为可选/选填
    brace_match = re.match(r'^\{([^}]*)\}$', value_part)
    if brace_match and re.search(r'可选|选填', brace_match.group(1)):
        return True

    return False

def parse_params_from_detail(detail_str):
    """
    从上报参数详情解析参数名，区分必填与可选。
    返回 {'all': [...], 'required': [...], 'optional': [...]}
    """
    required = []
    optional = []
    lines = detail_str.split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # 提取参数名（=前面的部分）
        if '=' in line:
            param_name = line.split('=')[0].strip()
            if not param_name:
                continue
            if is_optional_param_line(line):
                optional.append(param_name)
            else:
                required.append(param_name)
    
    return {
        'all': required + optional,
        'required': required,
        'optional': optional,
    }

def extract_nested_keys_for_param(detail_str, param_name):
    """
    从上报参数详情中的示例块提取嵌套 JSON 对象应包含的键名。
    例如 element_content 示例 [{model_id: "xxx"}, {model_id: "yyy", pos: 0}]
    返回 {'model_id', 'pos'}。
    """
    keys = set()
    lines = detail_str.split('\n')
    in_context = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if param_name in stripped:
            in_context = True
        if in_context or param_name in stripped:
            for match in re.finditer(r'\{\s*"?([a-zA-Z_][a-zA-Z0-9_]*)"?\s*:', stripped):
                keys.add(match.group(1))
    return keys

def parse_nested_key_expectations(detail_str, defined_params):
    """解析各参数在嵌套 JSON 中期望出现的键名。"""
    expectations = {}
    for param_name in defined_params:
        nested_keys = extract_nested_keys_for_param(detail_str, param_name)
        if nested_keys:
            expectations[param_name] = nested_keys
    return expectations

def try_parse_json_value(value):
    """尝试将属性值解析为 JSON（支持字符串形式的 JSON）。"""
    if value is None:
        return None
    if isinstance(value, (list, dict)):
        return value
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None

def check_nested_structure_compliance(properties, detail_str, defined_params):
    """
    校验嵌套结构：如 element_content 内应为 model_id，实际上报 model_name 则不合规。
    """
    issues = []
    expectations = parse_nested_key_expectations(detail_str, defined_params)
    for param_name, expected_keys in expectations.items():
        if param_name not in properties:
            continue
        parsed = try_parse_json_value(properties[param_name])
        if parsed is None:
            continue
        items = parsed if isinstance(parsed, list) else [parsed]
        param_issue = None
        for item in items:
            if not isinstance(item, dict) or not item:
                continue
            actual_keys = set(item.keys())
            for expected_key in expected_keys:
                if expected_key not in actual_keys:
                    wrong_keys = sorted(actual_keys - expected_keys)
                    wrong_desc = '、'.join(wrong_keys) if wrong_keys else '（无）'
                    param_issue = (
                        f"【{param_name}】内应使用【{expected_key}】，实际上报【{wrong_desc}】"
                    )
                    break
            if param_issue:
                break
        if param_issue:
            issues.append(param_issue)
    return issues

def check_param_compliance(properties, defined_params, detail_str=None, optional_params=None):
    """
    对比实际上报参数与「上报参数详情」定义，判断是否合规。
    - 缺失必填参数、嵌套键名错误 → 不合规
    - 多余参数 → 仅警告，不影响合规判定
    - 可选参数（注释如「有就报，没有就算了」）缺失不算不合规
    """
    optional_params = optional_params or []
    required_params = [p for p in defined_params if p not in optional_params]
    actual_params = list(properties.keys())
    extra_params = [p for p in actual_params if p not in defined_params and p not in SYSTEM_PARAMS]
    missing_params = [p for p in required_params if p not in properties]
    nested_issues = []
    if detail_str:
        nested_issues = check_nested_structure_compliance(properties, detail_str, defined_params)
    is_compliant = not missing_params and not nested_issues
    return {
        'extra_params': extra_params,
        'missing_params': missing_params,
        'nested_issues': nested_issues,
        'is_compliant': is_compliant,
    }

def parse_match_conditions_from_detail(param_detail):
    """
    从上报参数详情解析匹配条件（非动态参数）
    """
    conditions = {}
    lines = param_detail.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        if '=' in line:
            parts = line.split('=', 1)
            param_name = parts[0].strip()
            param_value = parts[1].strip()
            
            # 跳过动态参数（包含 {} 的值）
            if '{' in param_value or '}' in param_value:
                continue
            
            # 跳过注释部分
            if '#' in param_value:
                param_value = param_value.split('#')[0].strip()
            
            # 跳过current_page_name（已在主匹配中处理）
            if param_name == 'current_page_name':
                continue
            
            # 只添加有确定值的参数作为匹配条件
            if param_value and param_name:
                conditions[param_name] = param_value
    
    return conditions


def parse_dynamic_params_from_detail(detail_str):
    """
    从上报参数详情中提取动态参数（值包含{...}占位，排除可选语义）。
    返回 {param_name: placeholder_text}。
    """
    dynamic = {}
    lines = detail_str.split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            parts = line.split('=', 1)
            param_name = parts[0].strip()
            param_value = parts[1].strip()
            if '#' in param_value:
                param_value = param_value.split('#')[0].strip()
            # 值以 {...} 开头即为动态参数（可能有后续描述文字）
            brace_match = re.match(r'^\{([^}]*)\}', param_value)
            if brace_match:
                inner = brace_match.group(1)
                if re.search(r'可选|选填', inner):
                    continue
                dynamic[param_name] = inner
    return dynamic


def collect_param_samples(all_results, dynamic_params, max_samples=20):
    """
    从所有匹配记录中收集动态参数的实际取值（最多 max_samples 个）。
    返回 {param_name: [value1, value2, ...]}。
    """
    samples = {p: set() for p in dynamic_params}
    if not samples:
        return {}
    for record in all_results:
        props = record.get('properties', {})
        for param in dynamic_params:
            if param in props and props[param] is not None:
                samples[param].add(str(props[param]))
    result = {}
    for param, values in samples.items():
        sorted_vals = sorted(values)[:max_samples]
        if sorted_vals:
            result[param] = sorted_vals
    return result


def analyze_tracking_data(
    csv_file,
    target_event_name,
    target_page_name,
    defined_params,
    match_conditions,
    detail_str='',
    optional_params=None,
):
    """
    分析CSV数据，查找匹配的记录
    """
    results = []
    
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['st_event_name'] != target_event_name:
                continue
            
            try:
                raw_message = json.loads(row['st_raw_message'])
            except:
                continue
            
            properties = raw_message.get('properties', {})
            current_page_name = properties.get('current_page_name', '')
            
            # 无页面标识的后端埋点，仅按事件名和匹配条件筛选
            if target_page_name and current_page_name != target_page_name:
                continue
            
            # 检查额外匹配条件
            match = True
            for key, value in match_conditions.items():
                if properties.get(key, '') != value:
                    match = False
                    break
            
            if not match:
                continue
            
            compliance = check_param_compliance(
                properties, defined_params, detail_str, optional_params=optional_params
            )
            
            result = {
                'st_pk_id': raw_message.get('st_pk_id', ''),
                'st_user_id': raw_message.get('st_user_id', ''),
                'st_role_id': raw_message.get('st_role_id', ''),
                'st_account_id': raw_message.get('st_account_id', ''),
                'st_distinct_id': raw_message.get('st_distinct_id', ''),
                'st_event_name': raw_message.get('st_event_name', ''),
                'st_event_time': raw_message.get('st_event_time', ''),
                'st_event_datetime': extract_event_datetime(raw_message, row),
                'platform_type': properties.get('platform_type', ''),
                'adid': properties.get('adid', ''),
                'properties': properties,
                'extra_params': compliance['extra_params'],
                'missing_params': compliance['missing_params'],
                'nested_issues': compliance['nested_issues'],
                'is_compliant': compliance['is_compliant'],
                'st_status': row.get('st_status', ''),
                'st_error_info': row.get('st_error_info', ''),
                'raw_message': raw_message
            }
            results.append(result)

    results.sort(key=event_time_value, reverse=True)
    return results

def format_json_case(record, defined_params=None):
    """
    格式化JSON案例，包含预置属性和业务属性。
    defined_params 不为空时，业务属性展示方案定义的参数；
    方案外多余参数单独放入「多余参数（方案未定义）」区块，与警告对应。
    预置/公共属性白名单 = 硬编码 5 个 st_ 预置属性 + Excel「预置属性和公共属性」中的公共属性。
    """
    raw_message = record['raw_message']
    properties = record['properties']

    # 报告信封字段（便于对照）+ Excel 公共属性（出现在 properties 中的才展示）
    preset = {
        'st_pk_id': raw_message.get('st_pk_id', ''),
        'st_status': record.get('st_status', ''),
        'st_user_id': raw_message.get('st_user_id', ''),
        'st_role_id': raw_message.get('st_role_id', ''),
        'st_account_id': raw_message.get('st_account_id', ''),
        'st_distinct_id': raw_message.get('st_distinct_id', ''),
        'st_event_name': raw_message.get('st_event_name', ''),
        'st_event_time': raw_message.get('st_event_time', ''),
        'st_event_datetime': record.get('st_event_datetime', ''),
    }
    for key in SYSTEM_PARAMS:
        if key in REPORT_ENVELOPE_FIELDS or key in preset:
            # 已在信封区展示；若 properties 也有同名字段则覆盖为实际上报值
            if key in properties:
                preset[key] = properties[key]
            continue
        if key in properties:
            preset[key] = properties[key]

    case_data = {
        '预置属性和公共属性': preset,
        '业务属性': {}
    }
    extra_props = {}

    for key in properties:
        if key in SYSTEM_PARAMS:
            continue
        if defined_params is not None and key not in defined_params:
            extra_props[key] = properties[key]
            continue
        case_data['业务属性'][key] = properties[key]

    if extra_props:
        case_data['多余参数（方案未定义）'] = extra_props

    return case_data

def format_case_json_text(case_data):
    """单行展示每个参数，便于横向滚动对照。"""
    if not case_data:
        return '无'
    lines = ['{']
    sections = list(case_data.items())
    for si, (section, props) in enumerate(sections):
        lines.append(f'  "{section}": {{')
        items = list(props.items())
        for i, (key, value) in enumerate(items):
            comma = ',' if i < len(items) - 1 else ''
            val_str = json.dumps(value, ensure_ascii=False, separators=(',', ':'))
            lines.append(f'    "{key}": {val_str}{comma}')
        section_comma = ',' if si < len(sections) - 1 else ''
        lines.append(f'  }}{section_comma}')
    lines.append('}')
    return '\n'.join(lines)

def escape_html(text):
    return html_module.escape(str(text) if text is not None else '')

def render_case_box(text):
    """案例 JSON 独立滚动区域（横纵双向滚动）。"""
    if not text or text == '无':
        return '<div class="scroll-box case-box"><div class="empty-text">无</div></div>'
    return f'<div class="scroll-box case-box"><pre class="case-json">{escape_html(text)}</pre></div>'

def render_error_box(text):
    """错误/警告独立滚动区域。"""
    if not text or text == '无':
        return '<div class="scroll-box error-box"><div class="empty-text">无</div></div>'
    return f'<div class="scroll-box error-box"><div class="error-text">{escape_html(text)}</div></div>'

def get_compliance_from_record(record, point):
    """基于指定记录的 properties 实时计算合规结果（与入库案例同源）。"""
    if not record or not point:
        return {
            'extra_params': record.get('extra_params', []) if record else [],
            'missing_params': record.get('missing_params', []) if record else [],
            'nested_issues': record.get('nested_issues', []) if record else [],
            'is_compliant': record.get('is_compliant', False) if record else False,
        }
    return check_param_compliance(
        record.get('properties', {}),
        point['定义参数'],
        point['上报参数详情'],
        optional_params=point.get('可选参数', []),
    )

def get_system_errors(record, compliance=None):
    """系统校验错误 + 缺失必填参数（真正导致入库失败的原因）。"""
    reasons = []

    st_error_info = record.get('st_error_info', '')
    if st_error_info:
        try:
            error_obj = json.loads(st_error_info)
            for value in error_obj.values():
                reasons.extend(value)
        except Exception:
            reasons.append(st_error_info)

    missing_params = (compliance or {}).get('missing_params') or record.get('missing_params', [])
    if missing_params:
        reasons.append(f"必填参数【{'、'.join(missing_params)}】缺失")

    return reasons

def get_extra_param_warning(compliance):
    """方案未定义的多余参数，仅作警告，不影响 st_status=1 的入库判定。"""
    extra_params = compliance.get('extra_params', [])
    if extra_params:
        return f"参数【{'、'.join(extra_params)}】上报参数详情中不要求上报"
    return None

def get_nested_compliance_warning(compliance):
    """嵌套结构不合规（如 element_content 内键名与方案不一致）。"""
    nested_issues = compliance.get('nested_issues', [])
    if nested_issues:
        return '；'.join(nested_issues)
    return None

def format_error_or_warning(record, point=None, stored_only=False):
    """
    格式：错误原因 / 不合规 / 警告 分行展示。
    与入库案例使用同一条 record + 同一套 properties 实时校验。
    """
    compliance = get_compliance_from_record(record, point) if point else {
        'extra_params': record.get('extra_params', []),
        'missing_params': record.get('missing_params', []),
        'nested_issues': record.get('nested_issues', []),
    }
    parts = []
    if not stored_only:
        # 未来事件时间：不参与「取最新」判定；若仍被展示则补充说明
        if not is_not_future_event(record):
            parts.append(
                '错误原因：事件时间（st_event_time）晚于检验时刻，已排除出「取最新」判定范围'
            )
        errors = get_system_errors(record, compliance)
        if errors:
            parts.append('错误原因：' + '；'.join(errors))
    nested_warning = get_nested_compliance_warning(compliance)
    if nested_warning:
        parts.append('不合规：' + nested_warning)
    warning = get_extra_param_warning(compliance)
    if warning:
        parts.append('警告：' + warning)
    return '\n'.join(parts) if parts else '无'

def get_error_reason(record):
    """兼容旧调用，等同于 format_error_or_warning。"""
    return format_error_or_warning(record)

def classify_results(results, point, now_ms=None):
    """
    每个点位仅取最新一条匹配记录判定上报/入库。
    「最新」限定为 st_event_time <= 检验时刻；未来时间记录不参与判定。
    入库案例与合规判定使用同一条 case_record（已入库时取最新入库记录）。

    若候选全是未来时间：仍算已上报，但不可用于入库判定（入库=否），
    用其中时间最晚的一条作展示与错误说明。
    """
    if not results:
        return None, None, False, False, False

    has_reported = True
    if now_ms is None:
        now_ms = get_validation_now_ms()

    latest = get_latest_record(results, now_ms)
    if not latest:
        # 仅有未来时间记录：上报有据，但不纳入入库判定
        latest_any = max(results, key=event_time_value)
        compliance = get_compliance_from_record(latest_any, point)
        return latest_any, latest_any, True, False, compliance['is_compliant']

    has_stored = str(latest.get('st_status', '')) == '1'
    case_record = get_latest_stored_record(results, now_ms) if has_stored else latest
    compliance = get_compliance_from_record(case_record, point)
    is_compliant = compliance['is_compliant']
    return latest, case_record, has_reported, has_stored, is_compliant

def is_reported_and_stored(item):
    """是否已上报且已入库。"""
    return item['has_reported'] and item['has_stored']

def is_reported_stored_compliant(item):
    """是否已上报、已入库且合规。"""
    return item['has_reported'] and item['has_stored'] and item.get('is_compliant', False)

def is_reported_stored_non_compliant(item):
    """是否已上报、已入库但不合规。"""
    return item['has_reported'] and item['has_stored'] and not item.get('is_compliant', False)

def is_reported_not_stored(item):
    """是否已上报但未入库。"""
    return item['has_reported'] and not item['has_stored']

def is_not_reported(item):
    """是否未上报。"""
    return not item['has_reported']

TAB_FILTERS = {
    'all': lambda item: True,
    'ok_compliant': is_reported_stored_compliant,
    'ok_non_compliant': is_reported_stored_non_compliant,
    'reported_not_stored': is_reported_not_stored,
    'not_reported': is_not_reported,
}

def render_report_table_rows(all_results, tab_filter='all'):
    """生成报告表格行 HTML。tab_filter: all | ok | reported_not_stored | not_reported"""
    match_fn = TAB_FILTERS.get(tab_filter, lambda item: True)
    rows_html = ''
    for item in all_results:
        if not match_fn(item):
            continue

        has_reported = item['has_reported']
        point = item['point']
        latest = item['latest']
        case_record = item.get('case_record')
        has_stored = item['has_stored']
        is_compliant = item.get('is_compliant', False)

        success_case = None
        error_or_warning = '无'
        error_case = None

        if has_stored and case_record:
            success_case = format_json_case(case_record, point['定义参数'])
            error_or_warning = format_error_or_warning(case_record, point, stored_only=True)
        elif latest:
            error_or_warning = format_error_or_warning(latest, point, stored_only=False)
            error_case = format_json_case(latest)

        success_text = format_case_json_text(success_case)

        param_samples = item.get('param_samples', {})
        if param_samples and success_text != '无':
            sample_lines = ['', '═══ 动态参数取值（最多20条） ═══']
            for param, values in param_samples.items():
                v_str = '、'.join(values)
                sample_lines.append(f'  {param}: {v_str}')
            success_text += '\n' + '\n'.join(sample_lines)

        error_text = format_case_json_text(error_case) if error_case else '无'
        page_id = point['页面标识'] if point['页面标识'] else '—'
        spec_detail = point['上报参数详情']
        if spec_detail.lower() == 'nan':
            spec_detail = '—'

        rows_html += f"""
            <tr>
                <td class="col-no">{point['序号']}</td>
                <td class="col-name">{escape_html(point['埋点信息'])}</td>
                <td class="col-spec">{escape_html(page_id)}</td>
                <td class="col-event">{escape_html(point['埋点事件'])}</td>
                <td class="col-param"><pre class="spec-detail">{escape_html(spec_detail)}</pre></td>
                <td class="col-status"><span class="{'yes' if has_reported else 'no'}">{'✅ 是' if has_reported else '❌ 否'}</span></td>
                <td class="col-status"><span class="{'yes' if has_stored else 'no'}">{'✅ 是' if has_stored else '❌ 否'}</span></td>
                <td class="col-status"><span class="{'yes' if is_compliant else 'no'}">{'✅ 是' if is_compliant else '❌ 否'}</span></td>
                <td class="col-case">{render_case_box(success_text)}</td>
                <td class="col-error">{render_error_box(error_or_warning)}</td>
                <td class="col-case">{render_case_box(error_text)}</td>
            </tr>"""
    return rows_html

def render_tab_panel(tab_id, rows_html, empty_message, active=False):
    """生成单个 Tab 面板 HTML。"""
    panel_cls = 'tab-panel active' if active else 'tab-panel'
    if rows_html.strip():
        return f"""
        <div id="{tab_id}" class="{panel_cls}">
        <div class="table-wrap">
        <table>
            {REPORT_TABLE_HEADER}
            {rows_html}
        </table>
        </div>
        </div>"""
    return f"""
        <div id="{tab_id}" class="{panel_cls}">
        <div class="table-wrap">
        <table>
            {REPORT_TABLE_HEADER}
        </table>
        </div>
        <div class="tab-empty">{empty_message}</div>
        </div>"""

REPORT_TABLE_HEADER = """
            <colgroup>
                <col style="width: 48px">
                <col style="width: 130px">
                <col style="width: 110px">
                <col style="width: 128px">
                <col style="width: 320px">
                <col style="width: 72px">
                <col style="width: 72px">
                <col style="width: 72px">
                <col style="width: 510px">
                <col style="width: 510px">
                <col style="width: 510px">
            </colgroup>
            <tr>
                <th class="col-no">序号</th>
                <th class="col-name">埋点信息</th>
                <th class="col-spec">页面标识</th>
                <th class="col-event">埋点事件</th>
                <th class="col-param">上报参数详情</th>
                <th class="col-status">是否上报</th>
                <th class="col-status">是否入库</th>
                <th class="col-status">是否合规</th>
                <th class="col-case">入库案例</th>
                <th class="col-error">入库错误原因或警告</th>
                <th class="col-case">错误案例</th>
            </tr>"""

def generate_html_report(all_results, input_meta=None):
    """
    生成HTML验证报告
    input_meta: {'excel_file': ..., 'csv_file': ...} 写入报告页脚
    """
    # 统计
    total_points = len(all_results)
    ok_compliant_points = sum(1 for r in all_results if is_reported_stored_compliant(r))
    ok_non_compliant_points = sum(1 for r in all_results if is_reported_stored_non_compliant(r))
    reported_not_stored_points = sum(1 for r in all_results if is_reported_not_stored(r))
    not_reported_points = sum(1 for r in all_results if is_not_reported(r))

    all_rows_html = render_report_table_rows(all_results, tab_filter='all')
    ok_compliant_rows_html = render_report_table_rows(all_results, tab_filter='ok_compliant')
    ok_non_compliant_rows_html = render_report_table_rows(all_results, tab_filter='ok_non_compliant')
    reported_not_stored_rows_html = render_report_table_rows(all_results, tab_filter='reported_not_stored')
    not_reported_rows_html = render_report_table_rows(all_results, tab_filter='not_reported')
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>埋点验证报告</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Microsoft YaHei', sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden; }}
        h1 {{ padding: 15px 20px; background: #007bff; color: white; font-size: 16px; }}
        .table-wrap {{ overflow-x: auto; max-width: 100%; }}
        table {{
            border-collapse: collapse;
            font-size: 12px;
            table-layout: fixed;
            width: max-content;
            min-width: 100%;
            --col-no-width: 48px;
            --col-name-width: 130px;
            --col-spec-width: 110px;
            --col-event-width: 128px;
            --col-param-width: calc(var(--col-event-width) * 2.5);
            --col-status-width: 72px;
            --col-case-width: 510px;
        }}
        th, td {{ padding: 8px 6px; border: 1px solid #e9ecef; vertical-align: top; text-align: left; overflow: hidden; }}
        th {{ background: #f8f9fa; font-weight: bold; white-space: nowrap; position: sticky; top: 0; z-index: 1; }}
        th.col-no, td.col-no {{ width: var(--col-no-width); min-width: var(--col-no-width); max-width: var(--col-no-width); white-space: nowrap; }}
        th.col-name, td.col-name {{ width: var(--col-name-width); min-width: var(--col-name-width); max-width: var(--col-name-width); white-space: normal; word-break: break-word; line-height: 1.45; }}
        th.col-spec, td.col-spec {{ width: var(--col-spec-width); min-width: var(--col-spec-width); max-width: var(--col-spec-width); word-break: break-all; }}
        th.col-event {{ width: var(--col-event-width); min-width: var(--col-event-width); max-width: var(--col-event-width); white-space: nowrap; font-weight: bold; }}
        td.col-event {{ width: var(--col-event-width); min-width: var(--col-event-width); max-width: var(--col-event-width); white-space: normal; word-break: break-all; line-height: 1.45; font-family: Consolas, monospace; font-size: 11px; }}
        th.col-param, td.col-param {{ width: var(--col-param-width); min-width: var(--col-param-width); max-width: var(--col-param-width); white-space: normal; word-break: break-word; line-height: 1.45; }}
        th.col-status, td.col-status {{ width: var(--col-status-width); min-width: var(--col-status-width); max-width: var(--col-status-width); white-space: nowrap; text-align: center; }}
        th.col-case, td.col-case, th.col-error, td.col-error {{ width: var(--col-case-width); min-width: var(--col-case-width); max-width: var(--col-case-width); padding: 6px; }}
        .scroll-box {{ overflow: auto; border-radius: 4px; border: 1px solid #dee2e6; max-width: 100%; }}
        .scroll-box.case-box {{ width: 100%; height: 180px; background: #2d3748; }}
        .scroll-box.error-box {{ width: 100%; height: 120px; background: #fff3cd; }}
        pre.case-json {{ color: #e2e8f0; padding: 8px; font-size: 10px; white-space: pre; margin: 0; font-family: Consolas, monospace; display: block; width: max-content; min-width: 100%; }}
        pre.spec-detail {{ background: #f8f9fa; color: #333; padding: 6px 8px; border-radius: 4px; font-size: 10px; white-space: pre-wrap; word-break: break-word; margin: 0; font-family: Consolas, monospace; max-width: 100%; }}
        .error-text {{ color: #856404; padding: 6px 8px; font-size: 11px; white-space: pre-wrap; word-break: break-word; line-height: 1.45; margin: 0; }}
        .empty-text {{ color: #adb5bd; padding: 8px; font-size: 11px; text-align: center; }}
        .yes {{ color: #28a745; font-weight: bold; }}
        .no {{ color: #dc3545; font-weight: bold; }}
        .footer {{ padding: 10px 20px; background: #f8f9fa; font-size: 11px; color: #6c757d; }}
        .summary {{ padding: 15px 20px; background: #e9ecef; }}
        .summary span {{ margin-right: 20px; }}
        .tabs {{ display: flex; gap: 0; padding: 0 20px; background: #e9ecef; border-bottom: 1px solid #dee2e6; }}
        .tab-btn {{
            padding: 10px 18px;
            border: none;
            background: transparent;
            cursor: pointer;
            font-size: 13px;
            color: #495057;
            border-bottom: 3px solid transparent;
            margin-bottom: -1px;
        }}
        .tab-btn:hover {{ color: #007bff; }}
        .tab-btn.active {{
            color: #007bff;
            font-weight: bold;
            border-bottom-color: #007bff;
            background: white;
        }}
        .tab-panel {{ display: none; }}
        .tab-panel.active {{ display: block; }}
        .tab-empty {{ padding: 40px 20px; text-align: center; color: #6c757d; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>埋点点位验证报告</h1>
        <div class="summary">
            <span>总点位数：{total_points}</span>
            <span>已上报已入库合规：{ok_compliant_points}</span>
            <span>已上报已入库不合规：{ok_non_compliant_points}</span>
            <span>已上报未入库：{reported_not_stored_points}</span>
            <span>未上报：{not_reported_points}</span>
        </div>
        <div class="tabs">
            <button type="button" class="tab-btn active" data-tab="tab-all">全部 ({total_points})</button>
            <button type="button" class="tab-btn" data-tab="tab-ok-compliant">已上报已入库合规 ({ok_compliant_points})</button>
            <button type="button" class="tab-btn" data-tab="tab-ok-non-compliant">已上报已入库不合规 ({ok_non_compliant_points})</button>
            <button type="button" class="tab-btn" data-tab="tab-reported-not-stored">已上报未入库 ({reported_not_stored_points})</button>
            <button type="button" class="tab-btn" data-tab="tab-not-reported">未上报 ({not_reported_points})</button>
        </div>"""

    html += render_tab_panel('tab-all', all_rows_html, '暂无验证点位', active=True)
    html += render_tab_panel('tab-ok-compliant', ok_compliant_rows_html, '暂无已上报已入库合规的点位')
    html += render_tab_panel('tab-ok-non-compliant', ok_non_compliant_rows_html, '暂无已上报已入库不合规的点位')
    html += render_tab_panel('tab-reported-not-stored', reported_not_stored_rows_html, '暂无已上报未入库的点位')
    html += render_tab_panel('tab-not-reported', not_reported_rows_html, '暂无未上报的点位')
    
    footer_lines = [f"验证时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"]
    if input_meta:
        footer_lines.append(f"埋点方案：{escape_html(input_meta.get('excel_file', ''))}")
        footer_lines.append(f"测试数据：{escape_html(input_meta.get('csv_file', ''))}")
    footer_html = '<br>'.join(footer_lines)

    html += f"""
        <div class="footer">{footer_html}</div>
    </div>
    <script>
    (function () {{
        var buttons = document.querySelectorAll('.tab-btn');
        var panels = document.querySelectorAll('.tab-panel');
        buttons.forEach(function (btn) {{
            btn.addEventListener('click', function () {{
                var target = btn.getAttribute('data-tab');
                buttons.forEach(function (b) {{ b.classList.remove('active'); }});
                panels.forEach(function (p) {{ p.classList.remove('active'); }});
                btn.classList.add('active');
                var panel = document.getElementById(target);
                if (panel) panel.classList.add('active');
            }});
        }});
    }})();
    </script>
</body>
</html>"""
    
    return html

def generate_output_filename(numbers):
    """
    生成输出文件名
    """
    if len(numbers) <= 3:
        seq_str = '_'.join(str(n) for n in numbers)
    else:
        seq_str = f"{numbers[0]}_{numbers[-1]}"
    return f"tracking_report_{seq_str}.html"

def main():
    # 解析命令行参数
    if len(sys.argv) < 4:
        print("用法: python validate.py <excel_file> <csv_file> <序号范围> [output_file]")
        print("说明: excel_file / csv_file 必须为用户 @ 提供的文件，禁止使用 skill/source/ 内置示例")
        print("示例: python validate.py /path/to/【odirouter】埋点方案与开发计划.xlsx /path/to/odirouter_data.csv 1-175")
        sys.exit(1)
    
    excel_file = os.path.abspath(sys.argv[1])
    csv_file = os.path.abspath(sys.argv[2])
    seq_range = sys.argv[3]
    output_file = sys.argv[4] if len(sys.argv) > 4 else None

    assert_user_input_files(excel_file, csv_file)
    assert_csv_columns(csv_file)
    print('=== 本次验证使用的文件（用户提供）===')
    print(f'埋点方案: {excel_file}')
    print(f'测试数据: {csv_file}')
    print('')

    # 预置 st_ 硬编码 + Excel 公共属性（其余必须从 Sheet 获取）
    system_params, excel_common = apply_system_params_from_excel(excel_file)
    print(f'预置属性（硬编码）: {", ".join(PRESET_ST_PARAMS)}')
    print(f'公共属性（来自Excel）: {", ".join(excel_common) if excel_common else "（无）"}')
    print(f'合计不校验多余: {", ".join(system_params)}')
    
    # 解析序号范围
    target_numbers = parse_number_sequence(seq_range)
    print(f"验证序号: {target_numbers}")
    
    # 解析Excel埋点方案
    global all_points
    all_points = parse_excel_tracking_plan(excel_file, target_numbers)
    print(f"从Excel解析到 {len(all_points)} 个埋点定义")
    
    # 验证每个点位
    all_results = []
    for point in all_points:
        results = analyze_tracking_data(
            csv_file,
            point['埋点事件'],
            point['页面标识'],
            point['定义参数'],
            point['匹配条件'],
            point['上报参数详情'],
            optional_params=point.get('可选参数', []),
        )
        latest, case_record, has_reported, has_stored, is_compliant = classify_results(results, point)
        
        dynamic_params = parse_dynamic_params_from_detail(point['上报参数详情'])
        param_samples = collect_param_samples(results, dynamic_params)

        all_results.append({
            'point': point,
            'results': results,
            'latest': latest,
            'case_record': case_record,
            'has_reported': has_reported,
            'has_stored': has_stored,
            'is_compliant': is_compliant,
            'param_samples': param_samples,
        })
        
        latest_dt = latest.get('st_event_datetime', '') if latest else ''
        future_n = count_future_records(results)
        future_hint = f', 排除未来时间{future_n}条' if future_n else ''
        print(
            f"序号{point['序号']}: {point['埋点信息']} - 候选{len(results)}条{future_hint}, "
            f"取最新({latest_dt}), 上报={'是' if has_reported else '否'}, "
            f"入库={'是' if has_stored else '否'}, 合规={'是' if is_compliant else '否'}"
        )
    
    # 生成HTML报告
    html_content = generate_html_report(all_results, input_meta={
        'excel_file': excel_file,
        'csv_file': csv_file,
    })
    
    # 输出文件
    if not output_file:
        output_file = generate_output_filename(target_numbers)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n已生成报告: {output_file}")

if __name__ == "__main__":
    main()
