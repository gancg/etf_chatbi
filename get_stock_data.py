"""
ETF ChatBI 助手 - 数据获取模块
通过 akshare API 获取ETF历史交易数据
"""

import akshare as ak
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from database import DatabaseManager


class StockDataFetcher:
    """ETF数据获取器"""
    
    def __init__(self):
        """初始化数据获取器"""
        # 数据库管理器
        self.db_manager = DatabaseManager()
        
        # 监控的ETF列表
        self.monitored_etfs = [
            {'ts_code': '512400', 'ts_name': '有色金属ETF南方'},
            {'ts_code': '588200', 'ts_name': '科创芯片ETF嘉实'},
            {'ts_code': '588790', 'ts_name': '科创AIETF博时'},
            {'ts_code': '159108', 'ts_name': '工业软件ETF博时'},
            {'ts_code': '159158', 'ts_name': '电力ETF景顺'}
        ]
    
    def fetch_etf_data(self, ts_code, start_date=None, end_date=None, use_mock=False):
        """
        获取单个ETF的历史数据
        
        Args:
            ts_code: ETF代码 (如 '512400',不带后缀)
            start_date: 开始日期 (格式: 'YYYYMMDD'),默认为一年前
            end_date: 结束日期 (格式: 'YYYYMMDD'),默认为昨天
            use_mock: 是否使用模拟数据(用于测试)
            
        Returns:
            DataFrame: ETF历史数据
        """
        try:
            # 设置默认日期范围
            if not end_date:
                # 使用前一天作为结束日期(避免获取到未完成的当日数据)
                end_date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
            
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            
            print(f"正在获取 {ts_code} 的数据 ({start_date} 至 {end_date})...")
            
            # 如果使用模拟数据
            if use_mock:
                return self._generate_mock_data(ts_code, start_date, end_date)
            
            # 调用akshare API获取ETF日线数据
            df = ak.fund_etf_hist_em(
                symbol=ts_code,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"  # 前复权
            )
            
            if df is None or df.empty:
                print(f"警告: {ts_code} 未获取到数据")
                return pd.DataFrame()
            
            # 重命名列以匹配数据库字段
            df = df.rename(columns={
                '日期': 'trade_date',
                '开盘': 'open',
                '最高': 'high',
                '最低': 'low',
                '收盘': 'close',
                '成交量': 'vol',
                '成交额': 'amount'
            })
            
            # 转换日期格式为YYYYMMDD
            df['trade_date'] = pd.to_datetime(df['trade_date']).dt.strftime('%Y%m%d')
            
            # 添加股票代码和名称
            etf_info = next((etf for etf in self.monitored_etfs if etf['ts_code'] == ts_code), None)
            if etf_info:
                df['ts_code'] = ts_code
                df['ts_name'] = etf_info['ts_name']
            else:
                df['ts_code'] = ts_code
                df['ts_name'] = ts_code
            
            # 选择需要的列
            df = df[['ts_code', 'ts_name', 'trade_date', 'open', 'high', 'low', 'close', 'vol', 'amount']]
            
            print(f"成功获取 {ts_code} 的 {len(df)} 条记录")
            return df
            
        except Exception as e:
            print(f"获取 {ts_code} 数据失败: {str(e)}")
            return pd.DataFrame()
    
    def _generate_mock_data(self, ts_code, start_date, end_date):
        """
        生成模拟ETF数据(用于测试)
        
        Args:
            ts_code: ETF代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            DataFrame: 模拟的ETF数据
        """
        print(f"[模拟数据] 生成 {ts_code} 的模拟数据...")
        
        # 生成日期范围
        dates = pd.date_range(start=start_date, end=end_date, freq='B')  # B表示工作日
        
        if len(dates) == 0:
            return pd.DataFrame()
        
        # 根据ETF代码设置基准价格
        base_prices = {
            '512400': 1.0,
            '588200': 0.8,
            '588790': 0.9,
            '159108': 1.1,
            '159158': 0.85
        }
        
        base_price = base_prices.get(ts_code, 1.0)
        
        # 生成随机价格数据
        np.random.seed(hash(ts_code) % 2**32)  # 使用ETF代码作为种子,保证一致性
        returns = np.random.normal(0, 0.02, len(dates))  # 日收益率
        prices = base_price * np.cumprod(1 + returns)
        
        # 生成OHLC数据
        opens = prices * (1 + np.random.uniform(-0.01, 0.01, len(dates)))
        highs = prices * (1 + np.abs(np.random.uniform(0, 0.02, len(dates))))
        lows = prices * (1 - np.abs(np.random.uniform(0, 0.02, len(dates))))
        closes = prices
        volumes = np.random.uniform(1000000, 5000000, len(dates))
        amounts = volumes * closes
        
        # 创建DataFrame
        etf_info = next((etf for etf in self.monitored_etfs if etf['ts_code'] == ts_code), None)
        ts_name = etf_info['ts_name'] if etf_info else ts_code
        
        df = pd.DataFrame({
            'ts_code': ts_code,
            'ts_name': ts_name,
            'trade_date': dates.strftime('%Y%m%d'),
            'open': np.round(opens, 3),
            'high': np.round(highs, 3),
            'low': np.round(lows, 3),
            'close': np.round(closes, 3),
            'vol': np.round(volumes, 0),
            'amount': np.round(amounts, 3)
        })
        
        print(f"[模拟数据] 生成 {len(df)} 条记录")
        return df
    
    def save_to_database(self, df):
        """
        将数据保存到SQLite数据库
        
        Args:
            df: DataFrame格式的ETF数据
            
        Returns:
            int: 插入的记录数
        """
        if df is None or df.empty:
            return 0
        
        try:
            conn = self.db_manager.connect()
            cursor = conn.cursor()
            
            inserted_count = 0
            
            for _, row in df.iterrows():
                try:
                    # 检查是否已存在该记录
                    cursor.execute('''
                        SELECT id FROM stock_history 
                        WHERE ts_code = ? AND trade_date = ?
                    ''', (row['ts_code'], row['trade_date']))
                    
                    existing = cursor.fetchone()
                    
                    if existing:
                        # 更新现有记录
                        cursor.execute('''
                            UPDATE stock_history 
                            SET open = ?, high = ?, low = ?, close = ?, 
                                vol = ?, amount = ?, updated_at = CURRENT_TIMESTAMP
                            WHERE ts_code = ? AND trade_date = ?
                        ''', (
                            float(row.get('open', 0)),
                            float(row.get('high', 0)),
                            float(row.get('low', 0)),
                            float(row.get('close', 0)),
                            float(row.get('vol', 0)),
                            float(row.get('amount', 0)),
                            row['ts_code'],
                            row['trade_date']
                        ))
                    else:
                        # 插入新记录
                        cursor.execute('''
                            INSERT INTO stock_history 
                            (ts_code, ts_name, trade_date, open, high, low, close, vol, amount)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            row['ts_code'],
                            row['ts_name'],
                            row['trade_date'],
                            float(row.get('open', 0)),
                            float(row.get('high', 0)),
                            float(row.get('low', 0)),
                            float(row.get('close', 0)),
                            float(row.get('vol', 0)),
                            float(row.get('amount', 0))
                        ))
                    
                    inserted_count += 1
                    
                except Exception as e:
                    print(f"保存记录失败: {str(e)}")
                    continue
            
            conn.commit()
            self.db_manager.close()
            
            print(f"成功保存 {inserted_count} 条记录到数据库")
            return inserted_count
            
        except Exception as e:
            print(f"保存到数据库失败: {str(e)}")
            self.db_manager.close()
            return 0
    
    def update_all_etfs(self, use_mock=False):
        """
        更新所有监控的ETF数据
        
        Args:
            use_mock: 是否使用模拟数据(用于测试)
        
        Returns:
            dict: 更新结果统计
        """
        print("\n" + "="*60)
        if use_mock:
            print("开始更新所有ETF数据 (使用模拟数据)")
        else:
            print("开始更新所有ETF数据 (使用Akshare API)")
        print("="*60 + "\n")
        
        # 确保数据库表已创建
        self.db_manager.create_tables()
        
        results = {
            'success': 0,
            'failed': 0,
            'total_records': 0
        }
        
        for etf in self.monitored_etfs:
            ts_code = etf['ts_code']
            
            # 获取数据
            df = self.fetch_etf_data(ts_code, use_mock=use_mock)
            
            if not df.empty:
                # 保存到数据库
                count = self.save_to_database(df)
                if count > 0:
                    results['success'] += 1
                    results['total_records'] += count
                else:
                    results['failed'] += 1
            else:
                results['failed'] += 1
        
        print("\n" + "="*60)
        print("数据更新完成")
        print(f"成功: {results['success']} 个ETF")
        print(f"失败: {results['failed']} 个ETF")
        print(f"总记录数: {results['total_records']}")
        print("="*60 + "\n")
        
        return results
    
    def get_latest_data(self, ts_code, days=30):
        """
        获取最近N天的数据
        
        Args:
            ts_code: ETF代码
            days: 天数
            
        Returns:
            DataFrame: 最近N天的数据
        """
        try:
            conn = self.db_manager.connect()
            
            query = '''
                SELECT * FROM stock_history 
                WHERE ts_code = ? 
                ORDER BY trade_date DESC 
                LIMIT ?
            '''
            
            df = pd.read_sql_query(query, conn, params=(ts_code, days))
            self.db_manager.close()
            
            return df
            
        except Exception as e:
            print(f"获取最新数据失败: {str(e)}")
            self.db_manager.close()
            return pd.DataFrame()


def main():
    """主函数 - 用于手动执行数据更新"""
    fetcher = StockDataFetcher()
    
    # 使用akshare获取真实数据(免费,无需积分)
    use_mock = False  # 设置为True使用模拟数据
    
    if use_mock:
        print("\n提示: 当前使用模拟数据")
    else:
        print("\n提示: 当前使用Akshare API获取真实数据")
    print()
    
    # 更新所有ETF数据
    results = fetcher.update_all_etfs(use_mock=use_mock)
    
    print("\n数据更新统计:")
    print(f"  成功: {results['success']}")
    print(f"  失败: {results['failed']}")
    print(f"  总记录: {results['total_records']}")


if __name__ == '__main__':
    main()
