"""
测试不同的ETF数据获取方式
"""

import tushare as ts
import os
from datetime import datetime

# 设置token
token = os.getenv('TUSHARE_API_KEY')
print(f"Token: {token[:10]}..." if token else "Token未设置")
ts.set_token(token)
pro = ts.pro_api()

# 测试的ETF代码
etf_codes = ['512400', '588200', '159158']

print("\n" + "="*60)
print("测试ETF数据获取")
print("="*60)

for code in etf_codes:
    print(f"\n测试 ETF: {code}")
    print("-"*60)
    
    # 方法1: fund_daily
    try:
        df1 = pro.fund_daily(ts_code=code, start_date='20240101', end_date='20241231')
        if df1 is not None and not df1.empty:
            print(f"✅ fund_daily: {len(df1)} 条数据")
            print(df1.head(2))
        else:
            print(f"❌ fund_daily: 无数据")
    except Exception as e:
        print(f"❌ fund_daily: {str(e)}")
    
    # 方法2: daily
    try:
        df2 = pro.daily(ts_code=code, start_date='20240101', end_date='20241231')
        if df2 is not None and not df2.empty:
            print(f"✅ daily: {len(df2)} 条数据")
        else:
            print(f"❌ daily: 无数据")
    except Exception as e:
        print(f"❌ daily: {str(e)}")
    
    # 方法3: pro_bar
    try:
        df3 = ts.pro_bar(ts_code=code, start_date='20240101', end_date='20241231', asset='E')
        if df3 is not None and not df3.empty:
            print(f"✅ pro_bar (ETF): {len(df3)} 条数据")
        else:
            print(f"❌ pro_bar (ETF): 无数据")
    except Exception as e:
        print(f"❌ pro_bar (ETF): {str(e)}")
    
    # 方法4: pro_bar (股票模式)
    try:
        df4 = ts.pro_bar(ts_code=code, start_date='20240101', end_date='20241231', asset='E')
        if df4 is not None and not df4.empty:
            print(f"✅ pro_bar: {len(df4)} 条数据")
        else:
            print(f"❌ pro_bar: 无数据")
    except Exception as e:
        print(f"❌ pro_bar: {str(e)}")

print("\n" + "="*60)
print("建议:")
print("1. 如果所有方法都失败,可能是Token权限不足")
print("2. 访问 https://tushare.pro/ 查看积分和权限")
print("3. ETF数据通常需要至少120积分")
print("="*60)
