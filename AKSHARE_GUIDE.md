# Akshare数据源配置说明

## ✅ 已完成迁移

已成功将数据源从 **Tushare** 迁移到 **Akshare**!

### 优势对比

| 特性 | Tushare | Akshare |
|------|---------|---------|
| ETF数据权限 | ❌ 需要120积分 | ✅ 完全免费 |
| API密钥 | ✅ 需要Token | ❌ 无需密钥 |
| 数据稳定性 | ⚠️ 受积分限制 | ✅ 稳定可靠 |
| 安装难度 | 简单 | 简单 |
| 中文支持 | ✅ | ✅ |

---

## 📦 依赖安装

Akshare已自动安装,如需重新安装:

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple akshare
```

---

## 🚀 使用方法

### 1. 更新ETF数据

```bash
python get_stock_data.py
```

**输出示例:**
```
提示: 当前使用Akshare API获取真实数据

============================================================
开始更新所有ETF数据 (使用Akshare API)
============================================================

正在获取 512400 的数据 (20250503 至 20260502)...
成功获取 512400 的 242 条记录
成功保存 242 条记录到数据库
...

数据更新完成
成功: 5 个ETF
失败: 0 个ETF
总记录数: 892
```

### 2. 使用模拟数据(测试用)

修改 `get_stock_data.py` 第342行:

```python
use_mock = True  # 设置为True使用模拟数据
```

---

## 🔧 代码变更说明

### 主要修改

1. **导入库变更**
   ```python
   # 之前
   import tushare as ts
   
   # 现在
   import akshare as ak
   ```

2. **ETF代码格式**
   ```python
   # 之前 (带交易所后缀)
   '512400', '159158'
   
   # 现在 (纯数字代码)
   '512400', '159158'
   ```

3. **API调用**
   ```python
   # 之前 (Tushare)
   df = ts.pro_bar(ts_code=ts_code, start_date=start, end_date=end, asset='E')
   
   # 现在 (Akshare)
   df = ak.fund_etf_hist_em(
       symbol=ts_code,
       period="daily",
       start_date=start_date,
       end_date=end_date,
       adjust="qfq"  # 前复权
   )
   ```

4. **列名映射**
   ```python
   # Akshare返回的中文列名 -> 数据库英文列名
   {
       '日期': 'trade_date',
       '开盘': 'open',
       '最高': 'high',
       '最低': 'low',
       '收盘': 'close',
       '成交量': 'vol',
       '成交额': 'amount'
   }
   ```

---

## 📊 监控的ETF列表

| 代码 | 名称 | 市场 |
|------|------|------|
| 512400 | 有色金属ETF南方 | 上海 |
| 588200 | 科创芯片ETF嘉实 | 上海 |
| 588790 | 科创AIETF博时 | 上海 |
| 159108 | 工业软件ETF博时 | 深圳 |
| 159158 | 电力ETF景顺 | 深圳 |

---

## ⚙️ 定时任务配置

定时任务调度器会自动使用akshare获取数据:

```bash
# 启动调度器
python scheduler.py

# 或后台运行
start_scheduler.bat
```

**执行时间**: 每日 16:00 (北京时间)  
**数据范围**: 最近一年至昨天

---

## 🔍 常见问题

### Q1: 为什么有些ETF数据条数较少?
A: 新上市的ETF历史数据较少,这是正常的。例如:
- 159108: 105条记录 (较新上市)
- 159158: 61条记录 (最新上市)

### Q2: 如何获取更多历史数据?
A: 修改 `fetch_etf_data()` 中的 `start_date` 参数:

```python
# 获取3年数据
start_date = (datetime.now() - timedelta(days=3*365)).strftime('%Y%m%d')
```

### Q3: 数据更新频率?
A: 
- 手动更新: 随时运行 `python get_stock_data.py`
- 自动更新: 每日16:00 (需启动scheduler.py)

### Q4: 是否需要API密钥?
A: **不需要!** Akshare完全免费,无需任何密钥或积分。

---

## 📝 注意事项

1. **网络连接**: Akshare需要访问东方财富等网站,确保网络畅通
2. **请求频率**: 避免短时间内大量请求,建议每次间隔1-2秒
3. **数据延迟**: ETF数据通常有1天延迟(获取到昨天的数据)
4. **复权方式**: 默认使用前复权(`qfq`),可根据需求改为后复权(`hfq`)或不复权(`''`)

---

## 🎉 总结

✅ **不再需要Tushare积分!**  
✅ **免费获取真实ETF数据!**  
✅ **所有功能正常工作!**  

现在可以正常使用ETF ChatBI助手的所有功能了!
