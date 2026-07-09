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

# 系统预置参数（不检查）
SYSTEM_PARAMS = ['extend', 'adid', 'current_page_url', 'platform_type']

# 预置属性和公共属性字段
PRESET_FIELDS = ['st_pk_id', 'st_user_id', 'st_role_id', 'st_account_id', 
                 'st_distinct_id', 'st_event_name', 'st_event_time', 'st_event_datetime',
                 'platform_type', 'adid']

def event_time_value(record):
    """用于排序，数值越大越新。"""
    try:
        return int(record.get('st_event_time') or 0)
    except (TypeError, ValueError):
        return 0

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

    if csv_row:
        for key in ('st_update_at', 'st_report_time', 'st_event_date'):
            val = csv_row.get(key, '')
            if val:
                return str(val).strip()
    return ''

def get_latest_record(results):
    """每个点位仅取最新一条匹配记录作为判定依据。"""
    if not results:
        return None
    return max(results, key=event_time_value)

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
            '定义参数': [],  # 待解析
            '匹配条件': {}  # 待解析
        }
        
        # 解析上报参数详情，提取参数名
        params = parse_params_from_detail(point['上报参数详情'])
        point['定义参数'] = params
        
        # 从上报参数详情解析匹配条件（非动态参数）
        point['匹配条件'] = parse_match_conditions_from_detail(point['上报参数详情'])
        
        points.append(point)
    
    return points

def parse_params_from_detail(detail_str):
    """
    从上报参数详情解析参数名
    """
    params = []
    lines = detail_str.split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # 提取参数名（=前面的部分）
        if '=' in line:
            param_name = line.split('=')[0].strip()
            if param_name:
                params.append(param_name)
    
    return params

def check_param_compliance(properties, defined_params):
    """
    对比实际上报参数与「上报参数详情」定义，判断是否合规。
    每个点位只允许上报方案中定义的参数（系统预置参数除外）。
    """
    actual_params = list(properties.keys())
    extra_params = [p for p in actual_params if p not in defined_params and p not in SYSTEM_PARAMS]
    missing_params = [p for p in defined_params if p not in properties]
    is_compliant = not extra_params and not missing_params
    return {
        'extra_params': extra_params,
        'missing_params': missing_params,
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

def analyze_tracking_data(csv_file, target_event_name, target_page_name, defined_params, match_conditions):
    """
    分析CSV数据，查找匹配的记录
    """
    results = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
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
            
            compliance = check_param_compliance(properties, defined_params)
            
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
    defined_params 不为空时，业务属性仅展示方案定义的参数。
    """
    raw_message = record['raw_message']
    properties = record['properties']
    
    case_data = {
        '预置属性和公共属性': {
            'st_pk_id': raw_message.get('st_pk_id', ''),
            'st_user_id': raw_message.get('st_user_id', ''),
            'st_role_id': raw_message.get('st_role_id', ''),
            'st_account_id': raw_message.get('st_account_id', ''),
            'st_distinct_id': raw_message.get('st_distinct_id', ''),
            'st_event_name': raw_message.get('st_event_name', ''),
            'st_event_time': raw_message.get('st_event_time', ''),
            'st_event_datetime': record.get('st_event_datetime', ''),
            'platform_type': properties.get('platform_type', ''),
            'adid': properties.get('adid', '')
        },
        '业务属性': {}
    }
    
    for key in properties:
        if key in SYSTEM_PARAMS:
            continue
        if defined_params is not None and key not in defined_params:
            continue
        case_data['业务属性'][key] = properties[key]
    
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

def get_system_errors(record):
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

    missing_params = record.get('missing_params', [])
    if missing_params:
        reasons.append(f"必填参数【{'、'.join(missing_params)}】缺失")

    return reasons

def get_extra_param_warning(record):
    """方案未定义的多余参数，仅作警告，不影响 st_status=1 的入库判定。"""
    extra_params = record.get('extra_params', [])
    if extra_params:
        return f"参数【{'、'.join(extra_params)}】上报参数详情中不要求上报"
    return None

def format_error_or_warning(record):
    """格式：错误原因 / 警告 分行展示。"""
    parts = []
    errors = get_system_errors(record)
    if errors:
        parts.append('错误原因：' + '；'.join(errors))
    warning = get_extra_param_warning(record)
    if warning:
        parts.append('警告：' + warning)
    return '\n'.join(parts) if parts else '无'

def get_error_reason(record):
    """兼容旧调用，等同于 format_error_or_warning。"""
    return format_error_or_warning(record)

def classify_results(results):
    """
    每个点位仅取最新一条匹配记录判定上报/入库。
    是否上报：存在匹配记录；是否入库：最新一条 st_status=1。
    """
    latest = get_latest_record(results)
    if not latest:
        return None, False, False
    has_reported = True
    has_stored = latest['st_status'] == '1'
    return latest, has_reported, has_stored

def generate_html_report(all_results):
    """
    生成HTML验证报告
    """
    # 统计
    total_points = len(all_points)
    reported_points = sum(1 for r in all_results if r['has_reported'])
    stored_points = sum(1 for r in all_results if r['has_stored'])
    not_reported_points = total_points - reported_points
    
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
    </style>
</head>
<body>
    <div class="container">
        <h1>埋点点位验证报告</h1>
        <div class="summary">
            <span>总点位数：{total_points}</span>
            <span>已上报：{reported_points}</span>
            <span>已入库：{stored_points}</span>
            <span>未上报：{not_reported_points}</span>
        </div>
        <div class="table-wrap">
        <table>
            <colgroup>
                <col style="width: 48px">
                <col style="width: 130px">
                <col style="width: 110px">
                <col style="width: 128px">
                <col style="width: 320px">
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
                <th class="col-case">入库案例</th>
                <th class="col-error">入库错误原因或警告</th>
                <th class="col-case">错误案例</th>
            </tr>"""
    
    for item in all_results:
        point = item['point']
        latest = item['latest']
        has_reported = item['has_reported']
        has_stored = item['has_stored']

        success_case = None
        error_or_warning = '无'
        error_case = None

        if latest:
            error_or_warning = format_error_or_warning(latest)
            if has_stored:
                success_case = format_json_case(latest, point['定义参数'])
            else:
                error_case = format_json_case(latest)

        success_text = format_case_json_text(success_case)
        error_text = format_case_json_text(error_case) if error_case else '无'
        page_id = point['页面标识'] if point['页面标识'] else '—'
        spec_detail = point['上报参数详情']
        if spec_detail.lower() == 'nan':
            spec_detail = '—'

        html += f"""
            <tr>
                <td class="col-no">{point['序号']}</td>
                <td class="col-name">{escape_html(point['埋点信息'])}</td>
                <td class="col-spec">{escape_html(page_id)}</td>
                <td class="col-event">{escape_html(point['埋点事件'])}</td>
                <td class="col-param"><pre class="spec-detail">{escape_html(spec_detail)}</pre></td>
                <td class="col-status"><span class="{'yes' if has_reported else 'no'}">{'✅ 是' if has_reported else '❌ 否'}</span></td>
                <td class="col-status"><span class="{'yes' if has_stored else 'no'}">{'✅ 是' if has_stored else '❌ 否'}</span></td>
                <td class="col-case">{render_case_box(success_text)}</td>
                <td class="col-error">{render_error_box(error_or_warning)}</td>
                <td class="col-case">{render_case_box(error_text)}</td>
            </tr>"""
    
    html += f"""
        </table>
        </div>
        <div class="footer">验证时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
    </div>
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
        print("示例: python validate.py 副本-【odirouter】埋点方案与开发计划.xlsx odirouter_test_data.csv 20-35")
        sys.exit(1)
    
    excel_file = sys.argv[1]
    csv_file = sys.argv[2]
    seq_range = sys.argv[3]
    output_file = sys.argv[4] if len(sys.argv) > 4 else None
    
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
            point['匹配条件']
        )
        latest, has_reported, has_stored = classify_results(results)
        
        all_results.append({
            'point': point,
            'results': results,
            'latest': latest,
            'has_reported': has_reported,
            'has_stored': has_stored,
        })
        
        latest_dt = latest.get('st_event_datetime', '') if latest else ''
        print(f"序号{point['序号']}: {point['埋点信息']} - 候选{len(results)}条, 取最新({latest_dt}), 上报={'是' if has_reported else '否'}, 入库={'是' if has_stored else '否'}")
    
    # 生成HTML报告
    html_content = generate_html_report(all_results)
    
    # 输出文件
    if not output_file:
        output_file = generate_output_filename(target_numbers)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n已生成报告: {output_file}")

if __name__ == "__main__":
    main()
