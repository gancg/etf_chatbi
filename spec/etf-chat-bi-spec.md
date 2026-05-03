---
trigger: always_on
---
# ETF ChatBI 助手功能架构 Spec 文档

## 上下文

本文档描述 ETF ChatBI 智能数据分析助手的整体功能架构。该系统是一个基于大语言模型的智能ETF分析工具,旨在通过自然语言交互方式,为用户提供ETF数据查询、技术分析、趋势预测等功能,帮助用户更好地理解和分析ETF市场表现。

## 项目定位

**ETF ChatBI 助手**是一个智能ETF数据分析系统,支持用户通过自然语言进行数据查询和技术分析,结合传统金融指标计算和机器学习预测算法,提供全面的ETF分析能力。

## 核心功能模块

### 1. 自动数据管理

- **数据源**: 通过 tushare API 获取ETF历史交易数据
- **存储方式**: SQLite 本地数据库 (`stock_data.db`)
- **定时更新**: 默认每日 16:00 自动更新数据(APScheduler 调度)
- **数据结构**: 
  - 表名: `stock_history`
  - 字段包括: 股票代码(ts_code)、股票名称(ts_name)、交易日期(trade_date)、开盘价(open)、最高价(high)、最低价(low)、收盘价(close)、成交量(vol)、成交额(amount)等
  - 索引优化: 针对交易日期、股票代码、股票名称建立索引

### 2. 自然语言 SQL 查询 (ExcSql)

- **功能描述**: 用户可通过自然语言提问,系统自动转换为SQL查询并执行
- **核心能力**:
  - 智能解析用户意图,生成对应的SQL语句
  - 支持相对日期函数处理(如 `DATE('now', '-1 month')`)
  - 查询结果自动转换为 Markdown 表格展示
  - 超过100条记录时自动切换为汇总显示模式
  - 自动生成可视化图表(Plotly/Matplotlib)
- **使用场景**:
  - "查询科创芯片ETF最近一个月的收盘价"
  - "对比有色金属ETF和电力ETF今年的涨跌幅"
  - "显示工业软件ETF成交量最高的10天"

### 3. 技术指标分析

#### 3.1 MACD 分析 (macd_stock)

- **算法参数**: 快线12、慢线26、信号线9
- **核心功能**:
  - 计算MACD指标(DIF、DEA、MACD柱)
  - 识别金叉(买入信号)和死叉(卖出信号)
  - 模拟基于MACD信号的交易策略
  - 计算过去一年的收益率(默认初始资金10000元)
  - 生成双层图表: 上层价格走势+买卖点,下层MACD指标
- **输出内容**: 信号点列表、收益率、可视化图表

#### 3.2 布林带分析 (boll_stock)

- **算法参数**: 窗口大小20、标准差倍数2(可自定义)
- **核心功能**:
  - 计算布林带(上轨、中轨、下轨)
  - 检测超买信号(突破上轨)和超卖信号(突破下轨)
  - 模拟基于布林带信号的交易策略
  - 计算历史交易收益率
  - 生成包含价格曲线和布林带的可视化图表
- **输出内容**: 超买/超卖点列表、收益率、可视化图表

### 4. 趋势预测分析

#### 4.1 ARIMA 时间序列预测 (arima_stock)

- **模型配置**: ARIMA(5,1,5)
- **核心功能**:
  - 基于过去一年的历史数据进行建模
  - 预测未来N天的股票价格
  - 提供预测值的置信区间(上下界)
  - 生成历史价格与预测价格的对比图表
- **适用场景**: 短期价格趋势预测

#### 4.2 Prophet 周期性分析 (prophet_analysis)

- **核心功能**:
  - 长期趋势(Trend)识别和分析
  - 每周(Weekly)季节性模式分析
  - 每年(Yearly)季节性模式分析
  - 月度(monthly)季节性分量添加
  - 趋势变化点检测
  - 生成Prophet组件分解图和趋势图
- **适用场景**: 中长期趋势分析和周期性规律发现

### 5. 多ETF对比分析

- **功能描述**: 支持同时分析多个ETF的表现
- **监控ETF列表**:
  - 512400: 南方中证申万有色金属ETF (有色金属ETF南方)
  - 588200: 嘉实上证科创板芯片ETF (科创芯片ETF嘉实)
  - 588790: 博时上证科创板人工智能ETF (科创AIETF博时)
  - 159108: 博时中证工业软件主题ETF (工业软件ETF博时)
  - 159158: 景顺长城中证绿色电力ETF (电力ETF景顺)
- **对比维度**: 价格走势、收益率、技术指标、预测结果等

### 6. 可视化图表生成

- **图表类型**:
  - SQL查询结果图表 (`chart_*.png`)
  - MACD分析图表 (`macd_analysis_*.png`)
  - 布林带分析图表 (`bollinger_bands_*.png`)
  - ARIMA预测图表 (`arima_prediction_*.png`)
  - Prophet组件图 (`prophet_components_*.png`)
- **存储位置**: `image_show/` 目录
- **技术栈**: Matplotlib、Plotly

### 7. Web UI 交互界面

- **框架**: qwen-agent.gui.WebUI
- **核心能力**:
  - 基于 Assistant Agent 构建对话机器人
  - 集成所有分析工具作为可调用的 Function
  - 配置聊天建议(prompt.suggestions)引导用户
  - 支持会话上下文理解
  - 返回富文本结果(文字 + 表格 + 图片链接)

### 8. 价格波动邮件提醒 (新增)

- **触发时机**: 每日16:00数据更新完成后自动执行
- **监控对象**: 5个监控ETF列表中的所有ETF
- **检测逻辑**:
  - 计算当日收盘价相对于前一个交易日收盘价的涨跌幅百分比
  - 涨跌幅计算公式: `(今日收盘价 - 昨日收盘价) / 昨日收盘价 * 100%`
  - 当涨跌幅绝对值 >= 5% 时触发邮件提醒(包括上涨和下跌)
- **邮件内容**:
  - ETF代码和名称
  - 当日收盘价和前一日收盘价
  - 涨跌幅百分比及方向(上涨/下跌)
  - 触发时间戳
- **技术实现**:
  - 使用 Python `smtplib` 库发送邮件
  - 支持 SMTP 协议(如 QQ邮箱、163邮箱、Gmail等)
  - 邮件主题格式: `[ETF提醒] {ETF名称} 今日涨跌幅达到 {X}%`
  - 邮件正文包含详细的价格信息和对比数据

## 技术架构

### 技术栈

| 技术 | 用途 |
|------|------|
| **qwen-agent** | AI Agent框架,提供Assistant和工具注册机制 |
| **tushare** | 金融数据API,获取ETF历史数据 |
| **SQLite** | 本地数据库,存储ETF历史数据 |
| **pandas** | 数据处理和分析 |
| **matplotlib/plotly** | 图表生成 |
| **statsmodels** | ARIMA时间序列模型 |
| **prophet** | Facebook开发的周期性分析库 |
| **numpy** | 数值计算 |
| **APScheduler** | 定时任务调度 |
| **smtplib** | 邮件发送服务(标准库) |

### 数据流架构

```
用户输入(自然语言)
    ↓
qwen-agent Assistant (LLM: qwen-max)
    ↓
理解意图 → 选择合适的工具
    ↓
┌─────────────────────────────────────┐
│  工具选择:                           │
│  1. ExcSql → SQL查询                │
│  2. macd_stock → MACD分析           │
│  3. boll_stock → 布林带分析         │
│  4. arima_stock → ARIMA预测         │
│  5. prophet_analysis → Prophet分析  │
└─────────────────────────────────────┘
    ↓
执行工具调用
    ↓
┌─────────────────────────────────────┐
│  数据处理流程:                       │
│  1. 解析参数(JSON)                   │
│  2. 连接SQLite数据库                 │
│  3. 执行查询/计算                    │
│  4. 生成可视化图表                   │
│  5. 保存图表到 image_show/ 目录      │
│  6. 返回结果(Markdown + 图片链接)    │
└─────────────────────────────────────┘
    ↓
LLM整合结果 → 生成自然语言回复
    ↓
返回给用户(文字 + 表格 + 图表)
```

### 工具注册机制

使用 `@register_tool()` 装饰器注册自定义工具:
- `@register_tool('ExcSql')` - SQL查询工具
- `@register_tool('macd_stock')` - MACD分析工具
- `@register_tool('boll_stock')` - 布林带分析工具
- `@register_tool('arima_stock')` - ARIMA预测工具
- `@register_tool('prophet_analysis')` - Prophet分析工具

## 关键文件结构

```
ETF_ChatBI/
├── .lingma/
│   └── rules/
│       └── rules_for_all.md          # 项目开发规范
├── stock_analysis_assistant.py        # 主程序入口(Web UI)
├── get_stock_data.py                  # 数据获取脚本(tushare API)
├── create_stock_sqlite_db.py          # 从Excel创建SQLite数据库
├── check_db_info.py                   # 数据库信息检查工具
├── scheduler.py                       # 定时任务调度器(含邮件提醒逻辑)
├── email_notifier.py                  # 邮件通知服务模块(新增)
├── stock_data.db                      # SQLite数据库文件
├── image_show/                        # 生成的图表目录
│   ├── chart_*.png                    # SQL查询图表
│   ├── macd_analysis_*.png            # MACD分析图表
│   ├── bollinger_bands_*.png          # 布林带分析图表
│   ├── arima_prediction_*.png         # ARIMA预测图表
│   └── prophet_components_*.png       # Prophet组件图
├── temp/                              # 临时文件目录
└── workspace/                         # 工作区目录
```

## 环境配置要求

### Python 依赖

需要在 `requirements.txt` 中声明的包:
- qwen-agent
- tushare
- pandas
- matplotlib / plotly
- statsmodels
- prophet
- numpy
- APScheduler
- sqlite3

### 环境变量

- `TUSHARE_TOKEN`: 从系统环境变量 `TRUSHARE_API_KEY` 获取
- `DASHSCOPE_API_KEY`: 从系统环境变量 `DASHSCOPE_API_KEY` 获取
- `EMAIL_SMTP_SERVER`: SMTP服务器地址(如 smtp.qq.com)
- `EMAIL_SMTP_PORT`: SMTP服务器端口(如 465 或 587)
- `EMAIL_SENDER`: 发件人邮箱地址
- `EMAIL_PASSWORD`: 邮箱授权码或密码(建议使用授权码)
- `EMAIL_RECEIVER`: 收件人邮箱地址(多个邮箱用逗号分隔)
- 配置需在 `.env` 和 `.env.example` 文件中声明
- 允许在模拟数据模式下不强制检查密钥

### 启动命令

```bash
python stock_analysis_assistant.py
```

## 功能特色

1. **智能日期处理**: 自动转换相对日期函数为标准格式
2. **自动图表生成**: 所有查询和分析结果自动生成可视化图表
3. **大数据优化**: 超过100条记录时自动切换为汇总显示
4. **多工具协同**: LLM可根据用户需求自动选择合适的分析工具
5. **定时数据更新**: 每日自动更新最新ETF数据
6. **会话隔离**: 支持多用户会话数据隔离
7. **价格波动提醒**: 当日涨跌幅超过5%时自动发送邮件通知

## 验证方法

### 功能测试

1. **启动应用**: 运行 `python stock_analysis_assistant.py`,确认Web UI正常启动
2. **SQL查询测试**: 输入"查询科创芯片ETF最近一个月的收盘价",验证返回表格和图表
3. **MACD分析测试**: 输入"对有色金属ETF进行MACD分析",验证信号点和收益率计算
4. **布林带测试**: 输入"分析科创AIETF的布林带",验证超买超卖信号检测
5. **ARIMA预测测试**: 输入"预测工业软件ETF未来7天价格",验证预测结果和置信区间
6. **Prophet分析测试**: 输入"分析电力ETF的趋势和周期性",验证组件分解图

### 数据完整性验证

1. 检查 `stock_data.db` 数据库是否正常创建
2. 验证 `stock_history` 表是否包含5个监控ETF的数据
3. 确认定时任务是否在每日16:00正常执行
4. 检查 `image_show/` 目录是否正确生成图表文件
5. 验证邮件提醒功能是否在涨跌幅>=5%时正确触发

### 性能验证

1. SQL查询响应时间应在合理范围内(< 5秒)
2. 技术分析计算不应阻塞UI交互
3. 图表生成速度应流畅(< 3秒)
4. 大数据量查询时应正确切换到汇总模式
