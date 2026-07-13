# source/ 目录说明

本目录下的文件**仅供 Skill 开发时了解 Excel / CSV 格式**，不得用于正式埋点验证。

| 文件 | 用途 |
|------|------|
| `副本-【odirouter】埋点方案与开发计划.xlsx` | 方案 Excel 列结构参考 |
| `odirouter_test_data.csv` | 完整导出格式参考（正式验证仅需 5 列） |
| `odirouter_test_data_minimal.csv` | **5 列精简格式参考** |

## 测试数据 CSV 精简格式（5 列）

正式验证时用户 CSV **只需**以下列：

```
st_event_name,st_raw_message,st_status,st_error_info,st_available_message
```

详见 `odirouter_test_data_minimal.csv`。

## 正式验证时

必须使用用户 @ 提供的 xlsx 和 csv，例如：

```
/path/to/【odirouter】埋点方案与开发计划.xlsx
/path/to/odirouter_data.csv
```

`validate.py` 会拦截对本目录文件的调用并退出。
