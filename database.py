"""
ETF ChatBI 助手 - 数据库管理模块
负责创建和管理SQLite数据库
"""

import sqlite3
import os
from datetime import datetime


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path='stock_data.db'):
        """
        初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        """连接到数据库"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            try:
                self.conn.close()
            except:
                pass
            finally:
                self.conn = None
    
    def create_tables(self):
        """创建数据表结构"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # 创建stock_history表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts_code TEXT NOT NULL,
                ts_name TEXT NOT NULL,
                trade_date TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                vol REAL,
                amount REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建索引优化查询性能
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_trade_date 
            ON stock_history(trade_date)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_ts_code 
            ON stock_history(ts_code)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_ts_name 
            ON stock_history(ts_name)
        ''')
        
        # 创建联合索引用于常见查询
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_code_date 
            ON stock_history(ts_code, trade_date)
        ''')
        
        conn.commit()
        print("数据库表创建成功")
        return True
    
    def check_table_exists(self, table_name='stock_history'):
        """
        检查表是否存在
        
        Args:
            table_name: 表名
            
        Returns:
            bool: 表是否存在
        """
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        ''', (table_name,))
        result = cursor.fetchone()
        return result is not None
    
    def get_table_schema(self, table_name='stock_history'):
        """
        获取表结构信息
        
        Args:
            table_name: 表名
            
        Returns:
            list: 表字段信息列表
        """
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(f'PRAGMA table_info({table_name})')
        columns = cursor.fetchall()
        return [col[1] for col in columns]
    
    def verify_database(self):
        """
        验证数据库完整性
        
        Returns:
            dict: 验证结果
        """
        result = {
            'db_exists': os.path.exists(self.db_path),
            'db_size': os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0,
            'table_exists': False,
            'schema_valid': False,
            'indexes': []
        }
        
        if result['db_exists']:
            result['table_exists'] = self.check_table_exists()
            
            if result['table_exists']:
                expected_columns = [
                    'id', 'ts_code', 'ts_name', 'trade_date',
                    'open', 'high', 'low', 'close', 'vol', 'amount',
                    'created_at', 'updated_at'
                ]
                actual_columns = self.get_table_schema()
                result['schema_valid'] = all(col in actual_columns for col in expected_columns)
                
                # 检查索引
                conn = self.connect()
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT name FROM sqlite_master 
                    WHERE type='index' AND tbl_name='stock_history'
                ''')
                result['indexes'] = [row[0] for row in cursor.fetchall()]
        
        return result
    
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()


if __name__ == '__main__':
    # 测试数据库创建
    db_manager = DatabaseManager()
    
    try:
        # 创建表
        db_manager.create_tables()
        
        # 验证数据库
        verification = db_manager.verify_database()
        print("\n数据库验证结果:")
        for key, value in verification.items():
            print(f"  {key}: {value}")
        
    finally:
        db_manager.close()
