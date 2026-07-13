#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""可选参数解析与 CSV 列校验单元测试。"""

import csv
import os
import tempfile
import unittest

from validate import REQUIRED_CSV_COLUMNS, assert_csv_columns, is_optional_param_line, parse_params_from_detail


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


if __name__ == '__main__':
    unittest.main()
