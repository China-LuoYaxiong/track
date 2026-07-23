#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""可选参数解析与 CSV 列校验单元测试。"""

import csv
import os
import tempfile
import unittest

from validate import (
    REQUIRED_CSV_COLUMNS,
    assert_csv_columns,
    classify_results,
    get_latest_record,
    is_not_future_event,
    is_optional_param_line,
    parse_params_from_detail,
)


class TestOptionalParamParsing(unittest.TestCase):
    def _parsed(self, *lines):
        detail = '\n'.join(lines)
        return parse_params_from_detail(detail)

    def test_comment_phrase_optional(self):
        line = 'model_id={模型id} # 有就报，没有就算了'
        self.assertTrue(is_optional_param_line(line))
        parsed = self._parsed('current_page_name=home_page', line)
        self.assertIn('model_id', parsed['optional'])
        self.assertNotIn('model_id', parsed['required'])

    def test_comment_standalone_optional(self):
        for line in (
            'work_id={作品id} # 可选',
            'tag={标签} # 选填',
            'foo=bar # 非必填字段',
        ):
            with self.subTest(line=line):
                self.assertTrue(is_optional_param_line(line))

    def test_comment_descriptive_not_optional(self):
        for line in (
            'element_content={补充内容} # 可选场景下传',
            'foo=bar # 可选择 A 或 B',
            'duration={停留时长} # 单位秒',
        ):
            with self.subTest(line=line):
                self.assertFalse(is_optional_param_line(line))

    def test_brace_placeholder_optional(self):
        for line in (
            'element_content={可选补充}',
            'model_id = {可选参数}',
            'foo={可选}',
            'tag={选填参数}',
        ):
            with self.subTest(line=line):
                self.assertTrue(is_optional_param_line(line))

    def test_brace_dynamic_required(self):
        for line in (
            'ref_page_url={前页的url}',
            'element_name={点击什么报什么}',
            'element_content={补充内容}',
        ):
            with self.subTest(line=line):
                self.assertFalse(is_optional_param_line(line))

    def test_optional_supplement_with_descriptive_comment(self):
        line = 'element_content={可选补充} # 比如 switch_language 时传 CN、en 等'
        parsed = self._parsed('current_page_name=home_page', line)
        self.assertIn('element_content', parsed['optional'])


class TestCsvColumns(unittest.TestCase):
    def _write_csv(self, headers):
        f = tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.csv', delete=False)
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        row = {h: '' for h in headers}
        if 'st_event_name' in row:
            row['st_event_name'] = 'log_click_client'
        writer.writerow(row)
        f.close()
        return f.name

    def test_required_columns_present(self):
        path = self._write_csv(REQUIRED_CSV_COLUMNS)
        try:
            assert_csv_columns(path)
        finally:
            os.unlink(path)

    def test_missing_column_exits(self):
        headers = [c for c in REQUIRED_CSV_COLUMNS if c != 'st_available_message']
        path = self._write_csv(headers)
        try:
            with self.assertRaises(SystemExit):
                assert_csv_columns(path)
        finally:
            os.unlink(path)


class TestFutureEventTimeFilter(unittest.TestCase):
    """取最新时排除 st_event_time 晚于检验时刻的记录。"""

    def _rec(self, event_time_ms, status='1'):
        return {
            'st_event_time': event_time_ms,
            'st_status': status,
            'st_event_datetime': '',
            'properties': {},
            'extra_params': [],
            'missing_params': [],
            'nested_issues': [],
            'raw_message': {'st_event_time': event_time_ms, 'properties': {}},
            'st_error_info': '',
        }

    def test_future_excluded_from_latest(self):
        now_ms = 1_700_000_000_000  # fixed
        past = self._rec(now_ms - 3600_000, '1')
        future = self._rec(now_ms + 7 * 86400_000, '2')
        self.assertTrue(is_not_future_event(past, now_ms))
        self.assertFalse(is_not_future_event(future, now_ms))
        latest = get_latest_record([past, future], now_ms)
        self.assertIs(latest, past)

    def test_classify_prefers_past_success_over_future_fail(self):
        now_ms = 1_700_000_000_000
        past_ok = self._rec(now_ms - 1000, '1')
        future_fail = self._rec(now_ms + 86400_000, '2')
        point = {
            '定义参数': ['element_name'],
            '上报参数详情': 'element_name=foo',
            '可选参数': [],
        }
        past_ok['properties'] = {'element_name': 'foo'}
        future_fail['properties'] = {'element_name': 'foo'}
        latest, case, reported, stored, compliant = classify_results(
            [past_ok, future_fail], point, now_ms=now_ms
        )
        self.assertTrue(reported)
        self.assertTrue(stored)
        self.assertIs(latest, past_ok)
        self.assertIs(case, past_ok)

    def test_only_future_reported_not_stored(self):
        now_ms = 1_700_000_000_000
        future = self._rec(now_ms + 1000, '2')
        point = {
            '定义参数': [],
            '上报参数详情': '',
            '可选参数': [],
        }
        latest, case, reported, stored, compliant = classify_results(
            [future], point, now_ms=now_ms
        )
        self.assertTrue(reported)
        self.assertFalse(stored)
        self.assertIs(latest, future)


if __name__ == '__main__':
    unittest.main()
