"""
ETF ChatBI 助手 - 图表生成模块
支持多种类型的金融图表生成
"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import os
from datetime import datetime


class ChartGenerator:
    """图表生成器"""
    
    def __init__(self, output_dir='image_show'):
        """
        初始化图表生成器
        
        Args:
            output_dir: 图表输出目录
        """
        self.output_dir = output_dir
        
        # 确保输出目录存在
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
    
    def _optimize_xticks(self, ax, dates, max_ticks=20):
        """
        优化X轴刻度显示,避免过于密集
        
        Args:
            ax: matplotlib轴对象
            dates: 日期列表
            max_ticks: 最大刻度数(默认20)
        """
        if len(dates) <= max_ticks:
            # 数据点较少,全部显示
            ax.set_xticks(range(len(dates)))
            ax.set_xticklabels(dates, rotation=45, ha='right')
        else:
            # 数据点较多,均匀采样
            step = len(dates) // max_ticks
            tick_indices = range(0, len(dates), step)
            tick_labels = [dates[i] for i in tick_indices]
            
            ax.set_xticks(tick_indices)
            ax.set_xticklabels(tick_labels, rotation=45, ha='right')
    
    def generate_chart_filename(self, prefix='chart'):
        """
        生成图表文件名
        
        Args:
            prefix: 文件名前缀
            
        Returns:
            str: 完整的文件路径
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{prefix}_{timestamp}.png"
        return os.path.join(self.output_dir, filename)
    
    def generate_line_chart(self, x_data, y_data, title='价格走势图', 
                           x_label='日期', y_label='价格', 
                           color='blue', linewidth=1.5):
        """
        生成折线图
        
        Args:
            x_data: X轴数据
            y_data: Y轴数据
            title: 图表标题
            x_label: X轴标签
            y_label: Y轴标签
            color: 线条颜色
            linewidth: 线条宽度
            
        Returns:
            str: 图表文件路径
        """
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            ax.plot(x_data, y_data, color=color, linewidth=linewidth, label=y_label)
            
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_xlabel(x_label, fontsize=12)
            ax.set_ylabel(y_label, fontsize=12)
            ax.legend(loc='best')
            ax.grid(True, alpha=0.3)
            
            # 优化X轴刻度显示
            self._optimize_xticks(ax, x_data)
            plt.tight_layout()
            
            # 保存图表
            filepath = self.generate_chart_filename('chart')
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close(fig)
            
            print(f"图表已保存: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"生成折线图失败: {str(e)}")
            return None
    
    def generate_macd_chart(self, dates, prices, dif, dea, macd_bar, 
                           signals=None, title='MACD分析图'):
        """
        生成MACD双层图表
        
        Args:
            dates: 日期列表
            prices: 价格列表
            dif: DIF线数据
            dea: DEA线数据
            macd_bar: MACD柱状图数据
            signals: 买卖信号点列表 [{'date': xxx, 'type': 'buy/sell', 'price': xxx}]
            title: 图表标题
            
        Returns:
            str: 图表文件路径
        """
        try:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), 
                                           gridspec_kw={'height_ratios': [2, 1]})
            
            # 上层: 价格走势 + 买卖点
            ax1.plot(dates, prices, 'b-', linewidth=1.5, label='收盘价')
            
            if signals:
                buy_signals = [s for s in signals if s['type'] == 'buy']
                sell_signals = [s for s in signals if s['type'] == 'sell']
                
                if buy_signals:
                    buy_dates = [s['date'] for s in buy_signals]
                    buy_prices = [s['price'] for s in buy_signals]
                    ax1.scatter(buy_dates, buy_prices, marker='^', color='red', 
                              s=100, label='买入信号', zorder=5)
                
                if sell_signals:
                    sell_dates = [s['date'] for s in sell_signals]
                    sell_prices = [s['price'] for s in sell_signals]
                    ax1.scatter(sell_dates, sell_prices, marker='v', color='green', 
                              s=100, label='卖出信号', zorder=5)
            
            ax1.set_title(title, fontsize=14, fontweight='bold')
            ax1.set_ylabel('价格', fontsize=12)
            ax1.legend(loc='best')
            ax1.grid(True, alpha=0.3)
            
            # 下层: MACD指标
            ax2.plot(dates, dif, 'r-', linewidth=1.5, label='DIF')
            ax2.plot(dates, dea, 'g-', linewidth=1.5, label='DEA')
            
            # MACD柱状图
            colors = ['red' if v >= 0 else 'green' for v in macd_bar]
            ax2.bar(dates, macd_bar, color=colors, alpha=0.5, label='MACD')
            
            ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
            ax2.set_ylabel('MACD', fontsize=12)
            ax2.set_xlabel('日期', fontsize=12)
            ax2.legend(loc='best')
            ax2.grid(True, alpha=0.3)
            
            # 优化X轴刻度显示(两个子图使用相同的刻度)
            self._optimize_xticks(ax2, dates)
            ax1.set_xticks(ax2.get_xticks())
            ax1.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha='right')
            plt.tight_layout()
            
            # 保存图表
            filepath = self.generate_chart_filename('macd_analysis')
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close(fig)
            
            print(f"MACD图表已保存: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"生成MACD图表失败: {str(e)}")
            return None
    
    def generate_bollinger_chart(self, dates, prices, upper_band, middle_band, 
                                lower_band, signals=None, title='布林带分析图'):
        """
        生成布林带图表
        
        Args:
            dates: 日期列表
            prices: 价格列表
            upper_band: 上轨数据
            middle_band: 中轨数据
            lower_band: 下轨数据
            signals: 超买超卖信号点
            title: 图表标题
            
        Returns:
            str: 图表文件路径
        """
        try:
            fig, ax = plt.subplots(figsize=(14, 7))
            
            # 价格曲线
            ax.plot(dates, prices, 'b-', linewidth=1.5, label='收盘价')
            
            # 布林带
            ax.plot(dates, upper_band, 'r--', linewidth=1.5, label='上轨')
            ax.plot(dates, middle_band, 'g-', linewidth=1.5, label='中轨')
            ax.plot(dates, lower_band, 'r--', linewidth=1.5, label='下轨')
            
            # 填充布林带区域
            ax.fill_between(dates, upper_band, lower_band, alpha=0.1, color='gray')
            
            if signals:
                overbought = [s for s in signals if s['type'] == 'overbought']
                oversold = [s for s in signals if s['type'] == 'oversold']
                
                if overbought:
                    ob_dates = [s['date'] for s in overbought]
                    ob_prices = [s['price'] for s in overbought]
                    ax.scatter(ob_dates, ob_prices, marker='v', color='red', 
                             s=100, label='超卖信号', zorder=5)
                
                if oversold:
                    os_dates = [s['date'] for s in oversold]
                    os_prices = [s['price'] for s in oversold]
                    ax.scatter(os_dates, os_prices, marker='^', color='green', 
                             s=100, label='超买信号', zorder=5)
            
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_xlabel('日期', fontsize=12)
            ax.set_ylabel('价格', fontsize=12)
            ax.legend(loc='best')
            ax.grid(True, alpha=0.3)
            
            # 优化X轴刻度显示
            self._optimize_xticks(ax, dates)
            plt.tight_layout()
            
            # 保存图表
            filepath = self.generate_chart_filename('bollinger_bands')
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close(fig)
            
            print(f"布林带图表已保存: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"生成布林带图表失败: {str(e)}")
            return None
    
    def generate_prediction_chart(self, historical_dates, historical_prices,
                                 prediction_dates, prediction_prices,
                                 upper_bound=None, lower_bound=None,
                                 title='价格预测图'):
        """
        生成预测对比图表
        
        Args:
            historical_dates: 历史日期
            historical_prices: 历史价格
            prediction_dates: 预测日期
            prediction_prices: 预测价格
            upper_bound: 置信区间上界
            lower_bound: 置信区间下界
            title: 图表标题
            
        Returns:
            str: 图表文件路径
        """
        try:
            fig, ax = plt.subplots(figsize=(14, 7))
            
            # 合并历史日期和预测日期为连续序列
            all_dates = historical_dates + prediction_dates
            
            # 创建数值索引用于绘图
            x_indices = range(len(all_dates))
            hist_indices = x_indices[:len(historical_dates)]
            pred_indices = x_indices[len(historical_dates):]
            
            # 历史数据
            ax.plot(hist_indices, historical_prices, 'b-', 
                   linewidth=2, label='历史价格')
            
            # 预测数据
            ax.plot(pred_indices, prediction_prices, 'r--', 
                   linewidth=2, label='预测价格')
            
            # 置信区间
            if upper_bound is not None and lower_bound is not None:
                ax.fill_between(pred_indices, lower_bound, upper_bound, 
                              alpha=0.2, color='red', label='置信区间')
            
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_xlabel('日期', fontsize=12)
            ax.set_ylabel('价格', fontsize=12)
            ax.legend(loc='best')
            ax.grid(True, alpha=0.3)
            
            # 优化X轴刻度显示(使用合并后的日期)
            self._optimize_xticks(ax, all_dates)
            plt.tight_layout()
            
            # 保存图表
            filepath = self.generate_chart_filename('arima_prediction')
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close(fig)
            
            print(f"预测图表已保存: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"生成预测图表失败: {str(e)}")
            return None
    
    def generate_prophet_components_chart(self, dates, trend, weekly, yearly, 
                                         title='Prophet组件分解图'):
        """
        生成Prophet组件分解图
        
        Args:
            dates: 日期列表
            trend: 趋势分量
            weekly: 周季节性分量
            yearly: 年季节性分量
            title: 图表标题
            
        Returns:
            str: 图表文件路径
        """
        try:
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 12))
            
            # 趋势
            ax1.plot(dates, trend, 'b-', linewidth=2)
            ax1.set_title('趋势 (Trend)', fontsize=12, fontweight='bold')
            ax1.set_ylabel('值', fontsize=10)
            ax1.grid(True, alpha=0.3)
            
            # 周季节性
            ax2.plot(dates, weekly, 'g-', linewidth=2)
            ax2.set_title('周季节性 (Weekly)', fontsize=12, fontweight='bold')
            ax2.set_ylabel('值', fontsize=10)
            ax2.grid(True, alpha=0.3)
            
            # 年季节性
            ax3.plot(dates, yearly, 'r-', linewidth=2)
            ax3.set_title('年季节性 (Yearly)', fontsize=12, fontweight='bold')
            ax3.set_xlabel('日期', fontsize=10)
            ax3.set_ylabel('值', fontsize=10)
            ax3.grid(True, alpha=0.3)
            
            plt.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
            
            # 优化X轴刻度显示(三个子图使用相同的刻度)
            self._optimize_xticks(ax3, dates)
            ax1.set_xticks(ax3.get_xticks())
            ax1.set_xticklabels(ax3.get_xticklabels(), rotation=45, ha='right')
            ax2.set_xticks(ax3.get_xticks())
            ax2.set_xticklabels(ax3.get_xticklabels(), rotation=45, ha='right')
            
            plt.tight_layout()
            
            # 保存图表
            filepath = self.generate_chart_filename('prophet_components')
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close(fig)
            
            print(f"Prophet组件图已保存: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"生成Prophet组件图失败: {str(e)}")
            return None


if __name__ == '__main__':
    # 测试图表生成
    import numpy as np
    
    generator = ChartGenerator()
    
    # 测试折线图
    dates = pd.date_range('2024-01-01', periods=30, freq='D')
    prices = np.random.randn(30).cumsum() + 100
    
    filepath = generator.generate_line_chart(
        dates, prices, 
        title='测试折线图',
        x_label='日期',
        y_label='价格'
    )
    
    if filepath:
        print(f"测试成功: {filepath}")
