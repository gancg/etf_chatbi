# ETF数据获取说明

## 问题说明

由于Tushare的ETF数据接口(`fund_daily`)需要**120积分以上**的权限,当前Token无法直接获取真实ETF数据。

## 解决方案

### 方案1: 使用模拟数据(当前默认)

**优点**:
- ✅ 立即可用,无需等待
- ✅ 可以开发和测试所有功能
- ✅ 数据格式与真实数据一致

**缺点**:
- ❌ 数据是随机生成的,不是真实市场价格

**使用方法**:
```bash
python get_stock_data.py
```

已默认启用模拟数据,会自动为5个监控ETF生成262条/每个的历史数据。

### 方案2: 提升Tushare积分获取真实数据

**步骤**:
1. 访问 https://tushare.pro/
2. 注册/登录账号
3. 通过以下方式提升积分至120分以上:
   - 完善个人信息 (+5分)
   - 邀请好友注册 (+20分/人)
   - 社区贡献
   - 付费购买积分
4. 获取新的Token
5. 修改 `get_stock_data.py`:
   ```python
   use_mock = False  # 改为False使用真实API
   ```

## 模拟数据说明

### 数据特点
- **时间范围**: 过去365个工作日
- **数据量**: 每个ETF约262条记录
- **价格基准**:
  - 512400 (有色金属): 1.0元
  - 588200 (科创芯片): 0.8元
  - 588790 (科创AI): 0.9元
  - 159108 (工业软件): 1.1元
  - 159158 (电力): 0.85元

### 数据字段
```python
{
    'ts_code': '股票代码',
    'ts_name': '股票名称',
    'trade_date': '交易日期(YYYYMMDD)',
    'open': '开盘价',
    'high': '最高价',
    'low': '最低价',
    'close': '收盘价',
    'vol': '成交量',
    'amount': '成交额'
}
```

### 生成算法
- 使用正态分布模拟日收益率(均值0,标准差2%)
- 基于基准价格生成随机游走价格
- 确保OHLC数据的合理性
- 使用ETF代码作为随机种子,保证每次生成一致

## 验证数据

```bash
# 检查数据库
python -c "from database import DatabaseManager; db = DatabaseManager(); print(db.verify_database())"

# 查询数据示例
python -c "import pandas as pd; from database import DatabaseManager; db = DatabaseManager(); conn = db.connect(); df = pd.read_sql('SELECT * FROM stock_history LIMIT 5', conn); print(df); db.close()"
```

## 切换到真实数据

当您获得Tushare权限后:

1. **更新Token**:
   ```bash
   # 编辑 .env 文件
   TRUSHARE_API_KEY=your_new_token
   ```

2. **修改代码**:
   编辑 `get_stock_data.py` 第348行:
   ```python
   use_mock = False  # 改为False
   ```

3. **重新获取数据**:
   ```bash
   python get_stock_data.py
   ```

## 注意事项

⚠️ **重要提示**:
- 模拟数据仅用于开发和测试
- 生产环境建议使用真实数据
- 模拟数据的价格走势不代表真实市场表现
- 所有分析结果(技术指标、预测等)基于模拟数据,仅供参考

## 常见问题

### Q: 为什么不用其他免费数据源?
A: Tushare是最稳定的中文金融数据源,虽然ETF需要权限,但其他数据(股票、指数等)基础权限即可获取。

### Q: 模拟数据会影响分析结果吗?
A: 会影响数值的准确性,但不会影响功能的正确性。所有算法(MACD、布林带、ARIMA等)都能正常工作。

### Q: 如何知道当前使用的是模拟数据还是真实数据?
A: 运行 `get_stock_data.py` 时会明确提示:
   - "开始更新所有ETF数据 (使用模拟数据)"
   - "开始更新所有ETF数据 (使用Tushare API)"

---

**最后更新**: 2026-04-30  
**状态**: ✅ 模拟数据已启用,系统可正常使用
