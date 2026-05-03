# ETF ChatBI 助手 - 使用指南

## 📖 目录

- [快速开始](#快速开始)
- [功能说明](#功能说明)
- [配置说明](#配置说明)
- [常见问题](#常见问题)

## 🚀 快速开始

### 1. 环境准备

确保已安装 Python 3.8+ 

```bash
python --version
```

### 2. 安装依赖

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env`:

```bash
copy .env.example .env
```

编辑 `.env` 文件,填入你的API密钥:

```ini
TRUSHARE_API_KEY=你的tushare_token
DASHSCOPE_API_KEY=你的dashscope_api_key
EMAIL_SMTP_SERVER=smtp.qq.com
EMAIL_SMTP_PORT=465
EMAIL_SENDER=your_email@qq.com
EMAIL_PASSWORD=your_auth_code
EMAIL_RECEIVER=receiver@email.com
```

**获取API密钥:**
- Tushare Token: 注册 https://tushare.pro/
- DashScope API Key: 注册 https://dashscope.aliyun.com/

### 4. 启动应用

**方式一: 使用启动脚本 (Windows)**
```bash
start.bat
```

**方式二: 手动启动**
```bash
python stock_analysis_assistant.py
```

访问 http://localhost:7860 开始使用!

## 📊 功能说明

### 1. SQL查询 (ExcSql)

**功能**: 通过自然语言查询ETF历史数据

**示例**:
- "查询科创芯片ETF最近一个月的收盘价"
- "对比有色金属ETF和电力ETF今年的涨跌幅"
- "显示工业软件ETF成交量最高的10天"

**使用**: 在聊天框输入自然语言问题即可

### 2. MACD分析 (macd_stock)

**功能**: 技术指标分析,识别买卖信号

**参数**:
- `ts_code`: ETF代码 (默认: 512400)
- `period`: 分析周期 (默认: 365天)

**示例**:
- "对有色金属ETF进行MACD分析"
- "分析科创芯片ETF的MACD指标"

**输出**:
- 金叉/死叉信号点
- 交易收益率
- MACD双层图表

### 3. 布林带分析 (boll_stock)

**功能**: 检测超买超卖信号

**参数**:
- `ts_code`: ETF代码 (默认: 588790)
- `window`: 窗口大小 (默认: 20)
- `num_std`: 标准差倍数 (默认: 2.0)

**示例**:
- "分析科创AIETF的布林带"
- "检查电力ETF是否超买"

**输出**:
- 超买/超卖信号点
- 布林带图表

### 4. ARIMA预测 (arima_stock)

**功能**: 短期价格趋势预测

**参数**:
- `ts_code`: ETF代码 (默认: 159108)
- `days`: 预测天数 (默认: 7)

**示例**:
- "预测工业软件ETF未来7天价格"
- "预测有色金属ETF未来10天走势"

**输出**:
- 预测价格及置信区间
- 历史与预测对比图表

### 5. Prophet分析 (prophet_analysis)

**功能**: 中长期周期性分析

**参数**:
- `ts_code`: ETF代码 (默认: 159158)

**示例**:
- "分析电力ETF的趋势和周期性"
- "分析科创芯片ETF的季节性规律"

**输出**:
- 趋势、周季节性、年季节性分解
- Prophet组件图

### 6. 价格波动邮件提醒

**功能**: 每日16:00自动检查ETF价格波动,涨幅超过5%时发送邮件

**配置**: 在 `.env` 中设置邮件参数

**启动调度器**:
```bash
python scheduler.py
```

## ⚙️ 配置说明

### 环境变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| TRUSHARE_API_KEY | Tushare API Token | abc123def456 |
| DASHSCOPE_API_KEY | DashScope API Key | sk-xxx |
| EMAIL_SMTP_SERVER | SMTP服务器地址 | smtp.qq.com |
| EMAIL_SMTP_PORT | SMTP端口 | 465 |
| EMAIL_SENDER | 发件人邮箱 | user@qq.com |
| EMAIL_PASSWORD | 邮箱授权码 | auth_code |
| EMAIL_RECEIVER | 收件人邮箱 | receiver@email.com |

### 监控的ETF列表

| 代码 | 名称 | 简称 |
|------|------|------|
| 512400 | 南方中证申万有色金属ETF | 有色金属ETF南方 |
| 588200 | 嘉实上证科创板芯片ETF | 科创芯片ETF嘉实 |
| 588790 | 博时上证科创板人工智能ETF | 科创AIETF博时 |
| 159108 | 博时中证工业软件主题ETF | 工业软件ETF博时 |
| 159158 | 景顺长城中证绿色电力ETF | 电力ETF景顺 |

## ❓ 常见问题

### Q1: 提示"未设置DASHSCOPE_API_KEY"

**A**: 需要在 `.env` 文件中配置DashScope API Key,或设置系统环境变量。

### Q2: 无法获取ETF数据

**A**: 
1. 检查Tushare Token是否正确
2. 确认网络连接正常
3. 查看控制台错误信息

### Q3: 邮件发送失败

**A**:
1. 检查SMTP配置是否正确
2. QQ邮箱需要使用授权码,不是登录密码
3. 确认防火墙未阻止SMTP连接

### Q4: 图表中文显示乱码

**A**: 确保系统安装了中文字体,如SimHei或Microsoft YaHei。

### Q5: 如何更新ETF数据?

**A**: 
```bash
python get_stock_data.py
```

或者等待每日16:00自动更新(需启动scheduler.py)。

### Q6: 如何修改监控的ETF?

**A**: 编辑以下文件中的 `monitored_etfs` 列表:
- `get_stock_data.py`
- `scheduler.py`
- `stock_analysis_assistant.py`

## 📁 项目结构

```
ETF_ChatBI/
├── .env.example              # 环境变量示例
├── .gitignore                # Git忽略文件
├── requirements.txt          # Python依赖
├── start.bat                 # Windows启动脚本
├── README.md                 # 项目说明
├── USAGE.md                  # 使用指南(本文件)
│
├── database.py               # 数据库管理模块
├── email_notifier.py         # 邮件通知模块
├── scheduler.py              # 定时任务调度器
├── get_stock_data.py         # 数据获取模块
├── chart_generator.py        # 图表生成模块
├── tools.py                  # 分析工具集
├── stock_analysis_assistant.py  # Web UI主程序
│
├── spec/
│   └── etf-chat-bi-spec.md   # 功能架构文档
│
├── test/
│   ├── run_tests.py          # 测试运行器
│   ├── test_functional.py    # 功能测试
│   ├── test_data_integrity.py # 数据完整性测试
│   └── test_performance.py   # 性能测试
│
├── image_show/               # 生成的图表目录
├── temp/                     # 临时文件
└── workspace/                # 工作区
```

## 🔧 开发相关

### 运行测试

```bash
# 运行所有测试
python test/run_tests.py

# 运行特定测试
python -m unittest test.test_data_integrity -v
```

### 添加新工具

1. 在 `tools.py` 中实现工具函数
2. 添加函数文档字符串
3. 在 `init_agent()` 的 `function_list` 中注册

### 自定义图表

编辑 `chart_generator.py`,添加新的图表生成方法。

## 📞 技术支持

如有问题,请提Issue或查看spec文档: `spec/etf-chat-bi-spec.md`

---

**版本**: 1.0.0  
**最后更新**: 2026-04-30
