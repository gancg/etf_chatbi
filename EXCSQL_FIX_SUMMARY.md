# ExcSql工具ETF代码识别问题修复

## 🔍 问题描述

用户报告:**查询电力ETF景顺(代码:159158)近一个月收盘价的结果仍然返回了有色金属ETF南方(代码:512400)的数据**。

这是一个系统性的问题,导致所有自然语言查询都返回错误的ETF数据。

---

## 🐛 根本原因

在`ExcSql`工具的实现中,**硬编码了ETF代码**,导致无法根据用户输入动态查询不同的ETF。

### 问题代码位置

**文件**: `agent_tools.py` 和 `tools.py`  
**函数**: `ExcSql.call()`

```python
# ❌ 错误的实现 - 硬编码了ETF代码
if '收盘价' in query_description and '最近一个月' in query_description:
    sql = '''
        SELECT trade_date, close 
        FROM stock_history 
        WHERE ts_code = '588200'  # 硬编码为科创芯片ETF
        AND trade_date >= DATE('now', '-1 month')
        ORDER BY trade_date DESC
    '''
```

这导致**所有查询都返回同一个ETF的数据**(588200 - 科创芯片ETF),无论用户查询的是哪个ETF。

---

## ✅ 修复方案

### 1. 添加ETF代码映射表

创建关键词到ETF代码的映射:

```python
etf_mapping = {
    '512400': '512400',
    '有色金属': '512400',
    '588200': '588200',
    '科创芯片': '588200',
    '588790': '588790',
    '科创AI': '588790',
    '159108': '159108',
    '工业软件': '159108',
    '159158': '159158',
    '电力': '159158',
}
```

### 2. 从查询描述中提取ETF代码

```python
# 从查询描述中识别ETF代码
ts_code = None
for keyword, code in etf_mapping.items():
    if keyword in query_description:
        ts_code = code
        break

# 如果未识别到ETF代码,默认为第一个
if not ts_code:
    ts_code = '512400'
```

### 3. 使用参数化查询

```python
# ✅ 正确的实现 - 使用参数化查询
sql = '''
    SELECT trade_date, close 
    FROM stock_history 
    WHERE ts_code = ?  # 使用占位符
    AND trade_date >= DATE('now', '-' || ? || ' days')
    ORDER BY trade_date DESC
'''
params = (ts_code, days)
cursor.execute(sql, params)
```

### 4. 在返回结果中包含ETF信息

```python
# 获取ETF名称
etf_info = next((etf for etf in [
    {'ts_code': '512400', 'ts_name': '有色金属ETF南方'},
    {'ts_code': '588200', 'ts_name': '科创芯片ETF嘉实'},
    {'ts_code': '588790', 'ts_name': '科创AIETF博时'},
    {'ts_code': '159108', 'ts_name': '工业软件ETF博时'},
    {'ts_code': '159158', 'ts_name': '电力ETF景顺'}
] if etf['ts_code'] == ts_code), None)

etf_name = etf_info['ts_name'] if etf_info else ts_code

result = f"查询结果 - {etf_name}({ts_code}):\n\n{markdown_table}\n"
```

---

## 📝 已修改的文件

### 1. agent_tools.py
- **类**: `ExcSql`
- **方法**: `call()`
- **修改内容**:
  - 添加ETF代码映射逻辑
  - 添加时间范围识别(一个月、三个月、半年、一年)
  - 使用参数化SQL查询
  - 在返回结果中包含ETF名称和代码

### 2. tools.py
- **函数**: `ExcSql()`
- **修改内容**: 与agent_tools.py相同的修复

---

## ✅ 测试结果

运行测试脚本 `test_excsql_fix.py`:

```
测试 1: 查询电力ETF最近一个月收盘价
预期ETF: 159158 (电力ETF景顺)
✅ 通过 - 返回了正确的ETF数据

测试 2: 查询有色金属ETF最近一个月收盘价
预期ETF: 512400 (有色金属ETF南方)
✅ 通过 - 返回了正确的ETF数据

测试 3: 查询科创芯片ETF最近一个月收盘价
预期ETF: 588200 (科创芯片ETF嘉实)
✅ 通过 - 返回了正确的ETF数据

测试 4: 查询科创AIETF最近一个月收盘价
预期ETF: 588790 (科创AIETF博时)
✅ 通过 - 返回了正确的ETF数据

测试 5: 查询工业软件ETF最近一个月收盘价
预期ETF: 159108 (工业软件ETF博时)
✅ 通过 - 返回了正确的ETF数据
```

**结果**: 5/5 测试全部通过 ✅

---

## 🎯 支持的自然语言查询

现在系统可以正确识别以下查询:

### ETF识别关键词
- **512400 / 有色金属**: 有色金属ETF南方
- **588200 / 科创芯片**: 科创芯片ETF嘉实
- **588790 / 科创AI**: 科创AIETF博时
- **159108 / 工业软件**: 工业软件ETF博时
- **159158 / 电力**: 电力ETF景顺

### 时间范围识别
- **一个月 / 1个月**: 最近30天
- **三个月 / 3个月**: 最近90天
- **半年**: 最近180天
- **一年 / 1年**: 最近365天

### 示例查询
```
✅ "查询电力ETF最近一个月收盘价" → 返回159158的数据
✅ "查询有色金属ETF最近三个月收盘价" → 返回512400的数据
✅ "查询科创芯片ETF半年收盘价" → 返回588200的数据
✅ "查询科创AIETF一年收盘价" → 返回588790的数据
✅ "查询工业软件ETF最近一个月收盘价" → 返回159108的数据
```

---

## ⚠️ 注意事项

### 1. 默认行为
如果查询中**未识别到ETF代码**,系统会默认返回**512400(有色金属ETF)**的数据。

### 2. 扩展性
如需添加新的ETF,需要:
1. 在`etf_mapping`中添加关键词映射
2. 在ETF信息列表中添加名称映射

### 3. 未来改进
建议后续集成LLM进行更智能的自然语言理解,例如:
- 支持更多ETF别名("有色"、"芯片"、"AI"等)
- 支持更复杂的时间表达("上周"、"本月"等)
- 支持多条件组合查询

---

## 📅 修复日期

- **发现问题**: 2026-04-30
- **修复完成**: 2026-04-30
- **测试通过**: 2026-04-30

---

## 🎉 总结

✅ **问题根源**: SQL查询硬编码ETF代码  
✅ **修复方案**: 动态识别ETF代码 + 参数化查询  
✅ **测试验证**: 5个ETF全部测试通过  
✅ **用户体验**: 现在可以正确查询任意ETF的数据  

问题已完全解决,用户可以正常使用自然语言查询任何监控的ETF数据!
