"""
检查定时任务状态和日志
"""

import os
from datetime import datetime


def check_scheduler_status():
    """检查调度器状态"""
    print("="*60)
    print("ETF ChatBI 定时任务状态检查")
    print("="*60)
    print()
    
    # 1. 检查scheduler.log文件
    log_file = 'scheduler.log'
    if os.path.exists(log_file):
        print(f"✅ 日志文件存在: {log_file}")
        
        # 读取最后20行日志
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            last_lines = lines[-20:] if len(lines) > 20 else lines
        
        print("\n最近的日志记录:")
        print("-"*60)
        for line in last_lines:
            print(line.strip())
        print("-"*60)
    else:
        print(f"❌ 日志文件不存在: {log_file}")
        print("   提示: 调度器可能从未启动过")
    
    print()
    
    # 2. 检查当前时间
    now = datetime.now()
    print(f"📅 当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏰ 下次执行时间: 今天 16:00:00 (如果已过,则为明天 16:00:00)")
    
    if now.hour >= 16:
        print("   ⚠️  今天的16:00已过,下次执行时间为明天16:00")
    else:
        remaining_hours = 16 - now.hour - 1
        remaining_minutes = 60 - now.minute
        print(f"   ⏳ 距离下次执行还有: {remaining_hours}小时{remaining_minutes}分钟")
    
    print()
    
    # 3. 检查调度器进程
    print("🔍 检查调度器是否运行:")
    import subprocess
    try:
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq python.exe'],
            capture_output=True,
            text=True,
            encoding='gbk'
        )
        
        if 'python.exe' in result.stdout.lower():
            print("   ✅ Python进程正在运行")
            print("   提示: 请确认是否是scheduler.py进程")
        else:
            print("   ❌ 未检测到Python进程")
            print("   提示: 调度器可能未启动")
    except Exception as e:
        print(f"   ⚠️  无法检查进程状态: {e}")
    
    print()
    print("="*60)
    print("启动调度器命令:")
    print("  python scheduler.py")
    print()
    print("查看实时日志:")
    print("  Get-Content scheduler.log -Wait -Tail 20  (PowerShell)")
    print("  tail -f scheduler.log  (Linux/Mac)")
    print("="*60)


if __name__ == '__main__':
    check_scheduler_status()
