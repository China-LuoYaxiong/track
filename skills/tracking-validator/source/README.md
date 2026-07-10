# source/ 目录说明

本目录下的文件**仅供 Skill 开发时了解 Excel / CSV 格式**，不得用于正式埋点验证。

| 文件 | 用途 |
|------|------|
| `副本-【odirouter】埋点方案与开发计划.xlsx` | 方案 Excel 列结构参考 |
| `odirouter_test_data.csv` | 测试 CSV 字段格式参考 |

## 正式验证时

必须使用用户 @ 提供的 xlsx 和 csv，例如：

```
/path/to/【odirouter】埋点方案与开发计划.xlsx
/path/to/odirouter_data.csv
```

`validate.py` 会拦截对本目录文件的调用并退出。
