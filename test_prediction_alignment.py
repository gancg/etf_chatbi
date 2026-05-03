"""
测试ARIMA预测图表横坐标对齐问题
"""

import pandas as pd
import numpy as np
from chart_generator import ChartGenerator


def test_prediction_chart_alignment():
    """测试预测图表横坐标对齐"""
    
    generator = ChartGenerator()
    
    # 模拟历史数据(30天)
    historical_dates = [f'2026040{i}' for i in range(1, 31)]
    historical_prices = np.random.randn(30).cumsum() + 100
    
    # 模拟预测数据(7天)
    prediction_dates = [f'202605{str(i).zfill(2)}' for i in range(1, 8)]
    prediction_prices = np.random.randn(7).cumsum() + 100
    upper_bound = prediction_prices + 2
    lower_bound = prediction_prices - 2
    
    print("="*60)
    print("测试ARIMA预测图表横坐标对齐")
    print("="*60)
    print(f"历史数据: {len(historical_dates)}天")
    print(f"预测数据: {len(prediction_dates)}天")
    print(f"总数据点: {len(historical_dates) + len(prediction_dates)}天")
    print()
    
    # 生成预测图表
    print("生成预测图表...")
    filepath = generator.generate_prediction_chart(
        historical_dates,
        historical_prices.tolist(),
        prediction_dates,
        prediction_prices.tolist(),
        upper_bound=upper_bound.tolist(),
        lower_bound=lower_bound.tolist(),
        title='ARIMA价格预测 (横坐标对齐测试)'
    )
    
    if filepath:
        print(f"✅ 预测图表已保存: {filepath}")
        print()
        print("请检查图表:")
        print("1. 历史价格和预测价格应该连续显示")
        print("2. 横坐标日期标签应该与数据点对齐")
        print("3. 最后一个历史日期和第一个预测日期应该相邻")
    else:
        print("❌ 预测图表生成失败")
    
    print()
    print("="*60)
    print("测试完成!")
    print("="*60)


if __name__ == '__main__':
    test_prediction_chart_alignment()
