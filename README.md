# ETF ChatBI 助手

智能ETF数据分析系统,支持自然语言查询、技术分析、趋势预测和价格波动邮件提醒。

## 项目简介

ETF ChatBI是一个基于大语言模型的智能ETF分析工具,通过自然语言交互方式,为用户提供:
- 📊 ETF数据查询和分析
- 📈 技术指标计算(MACD、布林带)
- 🔮 趋势预测(ARIMA、Prophet)
- 📧 价格波动邮件提醒
- 💬 自然语言SQL查询

## 当前状态

✅ **基础架构已完成**
- 数据库管理模块
- 邮件通知模块  
- 定时任务调度器
- 完整的测试框架(61个测试用例全部通过)

⏸️ **待实现功能**
- 数据获取(tushare API集成)
- SQL查询工具
- 技术指标分析
- 趋势预测模型
- Web UI界面

## 快速开始

### 环境要求

- Python 3.8+
- SQLite3

### 安装依赖

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple apscheduler
```

### 配置环境变量

创建`.env`文件:

```bash
# Tushare API Token (可选,用于数据获取)
TUSHARE_TOKEN=your_tushare_token

# DashScope API Key (可选,用于LLM功能)
DASHSCOPE_API_KEY=your_dashscope_api_key

# 邮件配置 (用于价格提醒)
EMAIL_SMTP_SERVER=smtp.qq.com
EMAIL_SMTP_PORT=465
EMAIL_SENDER=your_email@qq.com
EMAIL_PASSWORD=your_email_password_or_auth_code
EMAIL_RECEIVER=receiver1@email.com,receiver2@email.com
```

### 运行测试

```bash
# 运行所有测试
python test/run_tests.py

# 运行特定测试
python -m unittest test.test_data_integrity.TestDatabaseCreation -v
python -m unittest test.test_functional.TestEmailNotification -v
```

### 启动调度器

```bash
python scheduler.py
```

调度器将在每日16:00自动:
1. 更新ETF数据
2. 检查价格波动
3. 发送涨幅超过5%的邮件提醒

## 项目结构

```
ETF_ChatBI/
├── .lingma/
│   └── rules/
│       └── rules_for_all.md          # 开发规范
├── spec/
│   └── etf-chat-bi-spec.md           # 功能架构文档
├── test/
│   ├── __init__.py
│   ├── README.md                     # 测试说明
│   ├── run_tests.py                  # 测试运行器
│   ├── test_functional.py            # 功能测试
│   ├── test_data_integrity.py        # 数据完整性测试
│   └── test_performance.py           # 性能测试
├── database.py                       # 数据库管理模块 ✅
├── email_notifier.py                 # 邮件通知模块 ✅
├── scheduler.py                      # 定时任务调度器 ✅
├── TDD_SUMMARY.md                    # TDD开发总结
└── README.md                         # 项目说明(本文件)
```

## 核心模块说明

### 1. DatabaseManager (database.py)

SQLite数据库管理器,负责:
- 创建和管理stock_history表
- 建立索引优化查询性能
- 提供数据库连接和验证功能

```python
from database import DatabaseManager

db = DatabaseManager()
db.create_tables()

# 验证数据库
result = db.verify_database()
print(result)
```

### 2. EmailNotifier (email_notifier.py)

邮件通知服务,负责:
- 检测ETF价格波动(阈值5%)
- 发送HTML格式提醒邮件
- 支持多收件人

```python
from email_notifier import EmailNotifier

notifier = EmailNotifier()

# 检查并发送通知
etf_data = [
    {
        'ts_code': '512400',
        'ts_name': '有色金属ETF南方',
        'current_close': 1.05,
        'previous_close': 1.00
    }
]

notified = notifier.check_and_notify(etf_data, threshold=5.0)
```

### 3. ETFScheduler (scheduler.py)

定时任务调度器,负责:
- 每日16:00自动执行更新任务
- 检查价格波动并发送邮件
- 错误处理和日志记录

```python
from scheduler import ETFScheduler

scheduler = ETFScheduler()
scheduler.start()  # 启动调度器
```

## 监控的ETF列表

| 代码 | 名称 | 简称 |
|------|------|------|
| 512400 | 南方中证申万有色金属ETF | 有色金属ETF南方 |
| 588200 | 嘉实上证科创板芯片ETF | 科创芯片ETF嘉实 |
| 588790 | 博时上证科创板人工智能ETF | 科创AIETF博时 |
| 159108 | 博时中证工业软件主题ETF | 工业软件ETF博时 |
| 159158 | 景顺长城中证绿色电力ETF | 电力ETF景顺 |

## 测试覆盖

### 已实现测试 (12个)
- ✅ 数据库创建和验证 (3个测试)
- ✅ 邮件通知功能 (4个测试)
- ✅ 定时任务调度 (5个测试)

### 待实现测试 (49个)
- ⏸️ SQL查询功能 (4个测试)
- ⏸️ MACD分析 (4个测试)
- ⏸️ 布林带分析 (3个测试)
- ⏸️ ARIMA预测 (4个测试)
- ⏸️ Prophet分析 (4个测试)
- ⏸️ 其他功能和性能测试

**总计: 61个测试用例,当前12个已实现并通过**

## 开发方法

本项目采用**TDD(测试驱动开发)**方法:

1. **红(Red)**: 先编写失败的测试
2. **绿(Green)**: 实现最小代码让测试通过
3. **重构(Refactor)**: 优化代码质量

详见 [TDD_SUMMARY.md](TDD_SUMMARY.md)

## 技术栈

- **数据库**: SQLite3
- **调度器**: APScheduler
- **邮件**: smtplib (Python标准库)
- **测试**: unittest
- **数据处理**: pandas (待集成)
- **可视化**: matplotlib/plotly (待集成)
- **AI框架**: qwen-agent (待集成)
- **数据源**: tushare (待集成)

## 下一步计划

1. **数据获取模块**: 集成tushare API获取ETF数据
2. **SQL查询工具**: 实现自然语言转SQL查询
3. **技术指标**: 实现MACD和布林带分析
4. **趋势预测**: 实现ARIMA和Prophet模型
5. **Web UI**: 基于qwen-agent构建对话界面

## 贡献指南

欢迎贡献代码!请遵循以下步骤:

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 许可证

本项目仅供学习使用。

## 联系方式

如有问题或建议,请提Issue。

---

**最后更新**: 2026-04-30
**版本**: 0.1.0 (基础架构版)
