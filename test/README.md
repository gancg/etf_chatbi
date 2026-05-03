# ETF ChatBI 助手测试目录

本目录包含ETF ChatBI助手的完整测试用例,按照spec文档要求编写。

## 测试文件说明

### 1. test_functional.py - 功能测试
对应spec文档第268-275行的功能测试要求,包含:

- **TestStartup**: Web UI启动测试
  - 验证应用正常启动
  - 验证端口可用性
  - 验证环境变量加载

- **TestSQLQuery**: SQL查询功能测试
  - 查询最近一个月收盘价
  - 相对日期处理
  - 大数据集汇总模式
  - 图表自动生成

- **TestMACDAnalysis**: MACD分析测试
  - 有色金属ETF的MACD分析
  - MACD参数验证(12,26,9)
  - 金叉/死叉信号检测
  - 交易策略模拟

- **TestBollingerBands**: 布林带分析测试
  - 科创AIETF的布林带分析
  - 布林带参数验证(窗口20,标准差2)
  - 超买/超卖信号检测

- **TestARIMAPrediction**: ARIMA预测测试
  - 工业软件ETF未来7天价格预测
  - ARIMA模型配置(5,1,5)
  - 置信区间计算
  - 预测图表生成

- **TestProphetAnalysis**: Prophet周期性分析测试
  - 电力ETF趋势和周期性分析
  - 长期趋势识别
  - 季节性模式分析(周、月、年)
  - 组件分解图生成

- **TestEmailNotification**: 邮件提醒测试
  - 涨跌幅>=5%时触发邮件
  - 邮件内容格式验证
  - SMTP配置读取
  - 多收件人支持

### 2. test_data_integrity.py - 数据完整性测试
对应spec文档第277-283行的数据完整性验证要求,包含:

- **TestDatabaseCreation**: 数据库创建测试
  - stock_data.db文件存在性
  - 数据库连接测试
  - 表结构验证

- **TestMonitoredETFData**: 监控ETF数据测试
  - 5个监控ETF数据存在性
  - 数据完整性检查
  - ETF代码与名称映射

- **TestScheduledTask**: 定时任务测试
  - 每日16:00定时执行配置
  - 更新任务注册验证
  - 更新函数逻辑测试
  - 错误处理测试

- **TestChartGeneration**: 图表生成测试
  - image_show目录存在性
  - 图表文件命名规范
  - 图片文件有效性验证
  - 图表内容准确性

- **TestDataIntegrity**: 数据完整性综合测试
  - 数据一致性
  - 索引优化验证
  - 数据更新幂等性

### 3. test_performance.py - 性能测试
对应spec文档第285-290行的性能验证要求,包含:

- **TestSQLQueryPerformance**: SQL查询性能测试
  - 响应时间 < 5秒
  - 并发查询性能
  - 索引优化效果

- **TestTechnicalAnalysisPerformance**: 技术分析性能测试
  - MACD计算不阻塞UI
  - 布林带计算性能
  - ARIMA预测性能
  - Prophet分析性能

- **TestChartGenerationPerformance**: 图表生成性能测试
  - 图表生成速度 < 3秒
  - 多图表生成性能
  - 文件I/O性能

- **TestLargeDataSetPerformance**: 大数据集性能测试
  - 汇总模式切换
  - 汇总数据准确性
  - 分页处理(如支持)

- **TestSystemResourceUsage**: 系统资源使用测试
  - 内存使用情况
  - 数据库连接管理
  - 多用户会话隔离

### 4. run_tests.py - 测试运行器
统一运行所有测试用例的脚本。

## 运行测试

### 运行所有测试
```bash
python test/run_tests.py
```

### 运行单个测试文件
```bash
# 功能测试
python -m unittest test.test_functional

# 数据完整性测试
python -m unittest test.test_data_integrity

# 性能测试
python -m unittest test.test_performance
```

### 运行特定测试类
```bash
python -m unittest test.test_functional.TestSQLQuery
```

### 运行特定测试方法
```bash
python -m unittest test.test_functional.TestSQLQuery.test_query_recent_close_price
```

###  verbose模式(显示详细输出)
```bash
python -m unittest test.test_functional -v
```

## 测试状态说明

当前所有测试用例均为**TODO状态**,需要实现具体的测试逻辑。测试框架已搭建完成,包含:

- ✅ 测试类和方法定义
- ✅ 测试场景描述
- ✅ 预期结果说明
- ✅ 测试步骤注释
- ⏳ 具体实现代码(待完成)

## 下一步工作

1. 实现各个测试方法的具体逻辑
2. 准备测试数据和mock对象
3. 配置测试环境
4. 运行测试并修复问题
5. 添加持续集成(CI)支持

## 注意事项

- 测试用例遵循spec文档要求
- 使用unittest框架
- 所有测试方法都包含详细的TODO注释
- 暂时不实现具体代码,仅搭建测试框架
- 后续根据实际实现逐步完善测试逻辑
