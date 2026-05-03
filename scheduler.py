"""
ETF ChatBI 助手 - 定时任务调度器
负责每日自动更新数据和发送价格提醒
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from datetime import datetime
import os
import sys
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ETFScheduler')

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager
from email_notifier import EmailNotifier


class ETFScheduler:
    """ETF数据调度和通知管理器"""
    
    def __init__(self):
        """初始化调度器"""
        self.scheduler = BlockingScheduler()
        self.db_manager = DatabaseManager()
        self.email_notifier = EmailNotifier()
        
        # 监控的ETF列表
        self.monitored_etfs = [
            {'ts_code': '512400', 'ts_name': '有色金属ETF南方'},
            {'ts_code': '588200', 'ts_name': '科创芯片ETF嘉实'},
            {'ts_code': '588790', 'ts_name': '科创AIETF博时'},
            {'ts_code': '159108', 'ts_name': '工业软件ETF博时'},
            {'ts_code': '159158', 'ts_name': '电力ETF景顺'}
        ]
    
    def update_data(self):
        """
        更新ETF数据
        TODO: 实现从tushare获取数据并更新数据库的逻辑
        """
        logger.info(f"[{datetime.now()}] 开始更新ETF数据...")
        
        # TODO: 调用tushare API获取最新数据
        # TODO: 将数据插入数据库
        
        logger.info(f"[{datetime.now()}] ETF数据更新完成")
        return True
    
    def check_price_alerts(self):
        """
        检查价格波动并发送邮件提醒
        """
        logger.info(f"[{datetime.now()}] 开始检查价格波动...")
        
        try:
            conn = self.db_manager.connect()
            cursor = conn.cursor()
            
            etf_data_list = []
            
            for etf in self.monitored_etfs:
                ts_code = etf['ts_code']
                ts_name = etf['ts_name']
                
                # 查询最近两天的收盘价
                cursor.execute('''
                    SELECT trade_date, close 
                    FROM stock_history 
                    WHERE ts_code = ? 
                    ORDER BY trade_date DESC 
                    LIMIT 2
                ''', (ts_code,))
                
                rows = cursor.fetchall()
                
                if len(rows) >= 2:
                    current_close = rows[0]['close']
                    previous_close = rows[1]['close']
                    
                    etf_data_list.append({
                        'ts_code': ts_code,
                        'ts_name': ts_name,
                        'current_close': current_close,
                        'previous_close': previous_close
                    })
            
            self.db_manager.close()
            
            # 检查并发送通知
            if etf_data_list:
                notified = self.email_notifier.check_and_notify(etf_data_list, threshold=5.0)
                
                if notified:
                    logger.info(f"已发送 {len(notified)} 封价格提醒邮件:")
                    for item in notified:
                        change = ((item['current_close'] - item['previous_close']) / item['previous_close']) * 100
                        logger.info(f"  - {item['ts_name']}: {change:.2f}%")
                else:
                    logger.info("没有ETF达到5%的涨跌幅阈值")
            else:
                logger.warning("没有足够的数据进行价格检查")
                
        except Exception as e:
            logger.error(f"检查价格波动时出错: {str(e)}")
            self.db_manager.close()
        
        logger.info(f"[{datetime.now()}] 价格波动检查完成")
    
    def daily_update_task(self):
        """
        每日更新任务(包含数据更新和价格检查)
        """
        logger.info("\n" + "="*60)
        logger.info("执行每日更新任务")
        logger.info("="*60)
        
        # 1. 更新数据
        self.update_data()
        
        # 2. 检查价格波动
        self.check_price_alerts()
        
        logger.info("="*60)
        logger.info("每日更新任务完成\n")
    
    def start(self):
        """启动调度器"""
        # 添加每日16:00执行的定时任务(北京时间)
        self.scheduler.add_job(
            func=self.daily_update_task,
            trigger='cron',
            hour=16,
            minute=0,
            second=0,
            timezone='Asia/Shanghai',  # 设置时区为北京时间
            id='daily_update',
            name='每日ETF数据更新和价格检查',
            misfire_grace_time=3600  # 允许1小时内的错过执行
        )
        
        # 添加监听器,记录任务执行情况
        self.scheduler.add_listener(self._job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        
        logger.info("调度器已启动,将在每日16:00(北京时间)执行更新任务")
        logger.info(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("按 Ctrl+C 退出\n")
        
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("\n调度器已停止")
            self.db_manager.close()
    
    def _job_listener(self, event):
        """任务执行监听器"""
        if event.exception:
            logger.error(f"任务执行失败: {event.job_id}, 错误: {event.traceback}")
        else:
            logger.info(f"任务执行成功: {event.job_id}, 执行时间: {event.scheduled_run_time}")


def main():
    """主函数"""
    scheduler = ETFScheduler()
    
    # 首次运行时先创建数据库表
    scheduler.db_manager.create_tables()
    
    # 启动调度器
    scheduler.start()


if __name__ == '__main__':
    main()
