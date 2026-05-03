# 定时任务使用说明

## 问题诊断

### 当前状态
- ❌ 调度器未启动
- ❌ 没有scheduler.log日志文件
- ⚠️ 今天的16:00已过

### 为什么定时任务没有执行?

**原因**: `scheduler.py`需要**单独启动并持续运行**,它不会自动启动。

定时任务调度器是一个**独立的后台服务**,必须手动启动并保持运行状态,才能在每天16:00自动执行任务。

---

## 解决方案

### 方法1: 手动启动调度器(推荐用于测试)

```bash
python scheduler.py
```

**注意**: 
- 此命令会**阻塞终端**,需要保持窗口打开
- 按 `Ctrl+C` 可以停止调度器
- 日志会同时输出到控制台和`scheduler.log`文件

### 方法2: Windows后台运行(推荐用于生产)

创建 `start_scheduler.bat`:

```batch
@echo off
start /B python scheduler.py
echo 调度器已在后台启动
echo 查看日志: type scheduler.log
```

### 方法3: 使用Windows任务计划程序(最可靠)

1. 打开"任务计划程序"
2. 创建基本任务
3. 设置触发器: 每天16:00
4. 操作: 启动程序 `python.exe`
5. 参数: `scheduler.py`
6. 起始于: 项目目录路径

---

## 验证调度器是否运行

### 检查日志文件

```bash
# PowerShell
Get-Content scheduler.log -Tail 20

# 实时查看日志
Get-Content scheduler.log -Wait -Tail 20
```

### 使用检查脚本

```bash
python check_scheduler.py
```

### 查看进程

```bash
# PowerShell
Get-Process python | Where-Object {$_.Path -like "*ETF_ChatBI*"}

# 或
tasklist | findstr python
```

---

## 日志示例

### 正常启动日志
```
2026-04-30 15:00:00,000 - ETFScheduler - INFO - 调度器已启动,将在每日16:00(北京时间)执行更新任务
2026-04-30 15:00:00,001 - ETFScheduler - INFO - 当前时间: 2026-04-30 15:00:00
2026-04-30 15:00:00,002 - ETFScheduler - INFO - 按 Ctrl+C 退出
```

### 任务执行日志
```
2026-04-30 16:00:00,000 - ETFScheduler - INFO - ============================================================
2026-04-30 16:00:00,001 - ETFScheduler - INFO - 执行每日更新任务
2026-04-30 16:00:00,002 - ETFScheduler - INFO - ============================================================
2026-04-30 16:00:00,003 - ETFScheduler - INFO - [2026-04-30 16:00:00.003000] 开始更新ETF数据...
2026-04-30 16:00:01,500 - ETFScheduler - INFO - [2026-04-30 16:00:01.500000] ETF数据更新完成
2026-04-30 16:00:01,501 - ETFScheduler - INFO - [2026-04-30 16:00:01.501000] 开始检查价格波动...
2026-04-30 16:00:02,000 - ETFScheduler - INFO - 没有ETF达到5%的涨跌幅阈值
2026-04-30 16:00:02,001 - ETFScheduler - INFO - [2026-04-30 16:00:02.001000] 价格波动检查完成
2026-04-30 16:00:02,002 - ETFScheduler - INFO - ============================================================
2026-04-30 16:00:02,003 - ETFScheduler - INFO - 每日更新任务完成
```

---

## 重要配置说明

### 时区设置
调度器已配置为**北京时间 (Asia/Shanghai)**,确保在正确的本地时间执行。

### 错过执行容忍
设置了`misfire_grace_time=3600`,如果系统关机或调度器停止,在1小时内重新启动时会补执行错过的任务。

### 任务监听
添加了任务执行监听器,会自动记录:
- ✅ 任务成功执行
- ❌ 任务执行失败及错误信息

---

## 常见问题

### Q1: 为什么16:00没有执行?
**A**: 调度器没有启动。需要运行 `python scheduler.py` 并保持运行。

### Q2: 如何确认调度器正在运行?
**A**: 
1. 检查是否有`scheduler.log`文件
2. 运行 `python check_scheduler.py`
3. 查看Python进程

### Q3: 调度器启动后能关闭终端吗?
**A**: 
- 直接运行: 不能关闭终端
- 后台运行: 可以关闭终端(使用方法2)
- 任务计划: 不需要保持终端打开(使用方法3)

### Q4: 如何修改执行时间?
**A**: 编辑 `scheduler.py` 第132-133行:
```python
hour=16,    # 改为其他小时
minute=0,   # 改为其他分钟
```

### Q5: 如何临时禁用定时任务?
**A**: 
1. 停止调度器 (Ctrl+C)
2. 或者注释掉 `scheduler.add_job()` 那一行

---

## 快速启动指南

### 第一次使用

```bash
# 1. 启动调度器
python scheduler.py

# 2. 保持终端窗口打开
# 3. 等待16:00自动执行
# 4. 查看scheduler.log确认执行结果
```

### 日常使用

**选项A**: 每次开机手动启动
```bash
python scheduler.py
```

**选项B**: 设置为Windows服务(推荐)
使用NSSM或其他工具将scheduler.py注册为Windows服务,开机自动启动。

**选项C**: 使用任务计划程序
设置每天15:55启动调度器,确保16:00时已经在运行。

---

## 监控和维护

### 定期检查
建议每天检查一次`scheduler.log`,确认任务正常执行。

### 日志清理
`scheduler.log`会持续增长,建议定期清理或轮转:

```powershell
# 保留最近1000行
Get-Content scheduler.log -Tail 1000 | Set-Content scheduler_clean.log
Move-Item scheduler_clean.log scheduler.log -Force
```

### 错误处理
如果任务执行失败,会在日志中记录错误信息。根据错误提示进行修复。

---

## 总结

✅ **已修复的问题**:
1. 添加了北京时间时区配置
2. 添加了完整的日志记录
3. 添加了任务执行监听
4. 添加了错过执行容忍机制
5. 创建了状态检查脚本

⚠️ **需要注意**:
- 调度器需要**手动启动并保持运行**
- 建议使用后台运行或任务计划程序
- 定期检查日志确认任务执行

📝 **下一步**:
1. 启动调度器: `python scheduler.py`
2. 等待16:00观察执行情况
3. 检查`scheduler.log`确认结果
