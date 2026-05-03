"""
测试图表横坐标优化功能
"""

import pandas as pd
import numpy as np
from chart_generator import ChartGenerator


def test_xtick_optimization():
    """测试横坐标优化"""
    
    generator = ChartGenerator()
    
    # 生成242个交易日的数据(约一年的数据)
    dates = pd.date_range('2025-01-01', periods=242, freq='B')
    dates_str = [d.strftime('%Y%m%d') for d in dates]
    prices = np.random.randn(242).cumsum() + 100
    
    print("="*60)
    print("测试图表横坐标优化")
    print("="*60)
    print(f"数据点数量: {len(dates_str)}")
    print(f"优化前: 所有{len(dates_str)}个日期都会显示(过于密集)")
    print(f"优化后: 最多显示20个均匀分布的日期")
    print()
    
    # 生成折线图
    print("生成折线图...")
    filepath = generator.generate_line_chart(
        dates_str, 
        prices,
        title='价格走势图 (横坐标优化测试)',
        x_label='日期',
        y_label='价格'
    )
    
    if filepath:
        print(f"✅ 折线图已保存: {filepath}")
    else:
        print("❌ 折线图生成失败")
    
    print()
    print("="*60)
    print("测试完成!")
    print("="*60)
    print()
    print("请查看生成的图表文件,横坐标应该只显示约20个均匀分布的日期标签")


if __name__ == '__main__':
    test_xtick_optimization()
