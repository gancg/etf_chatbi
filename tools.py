"""
ETF ChatBI 助手 - 分析工具集
包含所有注册给qwen-agent的工具函数
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from database import DatabaseManager
from chart_generator import ChartGenerator


def ExcSql(query_description: str) -> str:
    """
    执行SQL查询工具
    
    Args:
        query_description: 自然语言描述的查询需求
        
    Returns:
        str: Markdown格式的查询结果和图表路径
    """
    try:
        db = DatabaseManager()
        conn = db.connect()
        
        # TODO: 这里应该集成LLM将自然语言转换为SQL
        # 目前使用简单的示例查询
        cursor = conn.cursor()
        
        # 解析查询描述,提取ETF代码和时间范围
        ts_code = None
        days = 30  # 默认30天
        
        # ETF代码映射
        etf_mapping = {
            '512400': '512400',
            '有色金属': '512400',
            '588200': '588200',
            '科创芯片': '588200',
            '588790': '588790',
            '科创AI': '588790',
            '159108': '159108',
            '工业软件': '159108',
            '159158': '159158',
            '电力': '159158',
        }
        
        # 从查询描述中识别ETF代码
        for keyword, code in etf_mapping.items():
            if keyword in query_description:
                ts_code = code
                break
        
        # 如果未识别到ETF代码,默认为第一个
        if not ts_code:
            ts_code = '512400'
        
        # 识别时间范围
        if '一个月' in query_description or '1个月' in query_description:
            days = 30
        elif '三个月' in query_description or '3个月' in query_description:
            days = 90
        elif '半年' in query_description:
            days = 180
        elif '一年' in query_description or '1年' in query_description:
            days = 365
        
        # 生成SQL查询
        if '收盘价' in query_description:
            sql = '''
                SELECT trade_date, close 
                FROM stock_history 
                WHERE ts_code = ?
                AND trade_date >= DATE('now', '-' || ? || ' days')
                ORDER BY trade_date DESC
            '''
            params = (ts_code, days)
        else:
            sql = '''
                SELECT * FROM stock_history 
                WHERE ts_code = ?
                ORDER BY trade_date DESC
                LIMIT ?
            '''
            params = (ts_code, 10)
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        
        db.close()
        
        if not rows:
            return f"未查询到 {ts_code} 的数据"
        
        # 转换为DataFrame
        df = pd.DataFrame(rows, columns=columns)
        
        # 获取ETF名称
        etf_info = next((etf for etf in [
            {'ts_code': '512400', 'ts_name': '有色金属ETF南方'},
            {'ts_code': '588200', 'ts_name': '科创芯片ETF嘉实'},
            {'ts_code': '588790', 'ts_name': '科创AIETF博时'},
            {'ts_code': '159108', 'ts_name': '工业软件ETF博时'},
            {'ts_code': '159158', 'ts_name': '电力ETF景顺'}
        ] if etf['ts_code'] == ts_code), None)
        
        etf_name = etf_info['ts_name'] if etf_info else ts_code
        
        # 生成Markdown表格
        markdown_table = df.to_markdown(index=False)
        
        # 如果数据适合绘图,生成图表
        chart_path = None
        if len(df) <= 100 and 'close' in df.columns and 'trade_date' in df.columns:
            generator = ChartGenerator()
            chart_path = generator.generate_line_chart(
                df['trade_date'].tolist(),
                df['close'].tolist(),
                title='价格走势图'
            )
        
        result = f"查询结果 - {etf_name}({ts_code}):\n\n{markdown_table}\n\n"
        if chart_path:
            result += f"![图表]({chart_path})\n"
        
        return result
        
    except Exception as e:
        return f"查询失败: {str(e)}"


def macd_stock(ts_code: str = '512400', period: int = 365) -> str:
    """
    MACD分析工具
    
    Args:
        ts_code: ETF代码
        period: 分析周期(天数)
        
    Returns:
        str: MACD分析结果
    """
    try:
        db = DatabaseManager()
        conn = db.connect()
        
        # 获取历史数据
        query = '''
            SELECT trade_date, close 
            FROM stock_history 
            WHERE ts_code = ? 
            ORDER BY trade_date ASC 
            LIMIT ?
        '''
        
        df = pd.read_sql_query(query, conn, params=(ts_code, period))
        db.close()
        
        if df.empty:
            return f"未找到 {ts_code} 的数据"
        
        # 计算MACD
        close_prices = df['close'].values
        dates = df['trade_date'].tolist()
        
        # EMA计算
        def ema(data, span):
            return pd.Series(data).ewm(span=span, adjust=False).mean().values
        
        ema12 = ema(close_prices, 12)
        ema26 = ema(close_prices, 26)
        
        # DIF
        dif = ema12 - ema26
        
        # DEA (DIF的9日EMA)
        dea = pd.Series(dif).ewm(span=9, adjust=False).mean().values
        
        # MACD柱
        macd_bar = 2 * (dif - dea)
        
        # 识别金叉和死叉
        signals = []
        for i in range(1, len(dif)):
            if dif[i-1] <= dea[i-1] and dif[i] > dea[i]:
                signals.append({
                    'date': dates[i],
                    'type': 'buy',
                    'price': close_prices[i]
                })
            elif dif[i-1] >= dea[i-1] and dif[i] < dea[i]:
                signals.append({
                    'date': dates[i],
                    'type': 'sell',
                    'price': close_prices[i]
                })
        
        # 模拟交易策略
        initial_capital = 10000
        capital = initial_capital
        position = 0
        
        for signal in signals:
            if signal['type'] == 'buy' and position == 0:
                position = capital / signal['price']
                capital = 0
            elif signal['type'] == 'sell' and position > 0:
                capital = position * signal['price']
                position = 0
        
        # 计算最终收益
        if position > 0:
            final_value = position * close_prices[-1]
        else:
            final_value = capital
        
        return_rate = ((final_value - initial_capital) / initial_capital) * 100
        
        # 生成图表
        generator = ChartGenerator()
        chart_path = generator.generate_macd_chart(
            dates, close_prices.tolist(),
            dif.tolist(), dea.tolist(), macd_bar.tolist(),
            signals=signals,
            title=f'{ts_code} MACD分析图'
        )
        
        # 构建结果
        result = f"## MACD分析结果\n\n"
        result += f"**ETF代码**: {ts_code}\n"
        result += f"**分析周期**: {period}天\n\n"
        result += f"**信号点数量**: {len(signals)}\n"
        result += f"- 买入信号: {sum(1 for s in signals if s['type'] == 'buy')}\n"
        result += f"- 卖出信号: {sum(1 for s in signals if s['type'] == 'sell')}\n\n"
        result += f"**交易收益率**: {return_rate:.2f}%\n"
        result += f"**初始资金**: {initial_capital}元\n"
        result += f"**最终价值**: {final_value:.2f}元\n\n"
        
        if chart_path:
            result += f"![MACD图表]({chart_path})\n"
        
        return result
        
    except Exception as e:
        return f"MACD分析失败: {str(e)}"


def boll_stock(ts_code: str = '588790', window: int = 20, num_std: float = 2.0) -> str:
    """
    布林带分析工具
    
    Args:
        ts_code: ETF代码
        window: 窗口大小
        num_std: 标准差倍数
        
    Returns:
        str: 布林带分析结果
    """
    try:
        db = DatabaseManager()
        conn = db.connect()
        
        query = '''
            SELECT trade_date, close 
            FROM stock_history 
            WHERE ts_code = ? 
            ORDER BY trade_date ASC
        '''
        
        df = pd.read_sql_query(query, conn, params=(ts_code,))
        db.close()
        
        if df.empty:
            return f"未找到 {ts_code} 的数据"
        
        close_prices = df['close'].values
        dates = df['trade_date'].tolist()
        
        # 计算布林带
        rolling_mean = pd.Series(close_prices).rolling(window=window).mean()
        rolling_std = pd.Series(close_prices).rolling(window=window).std()
        
        upper_band = rolling_mean + (rolling_std * num_std)
        middle_band = rolling_mean
        lower_band = rolling_mean - (rolling_std * num_std)
        
        # 检测超买超卖信号
        signals = []
        for i in range(window, len(close_prices)):
            if close_prices[i] > upper_band.iloc[i]:
                signals.append({
                    'date': dates[i],
                    'type': 'overbought',
                    'price': close_prices[i]
                })
            elif close_prices[i] < lower_band.iloc[i]:
                signals.append({
                    'date': dates[i],
                    'type': 'oversold',
                    'price': close_prices[i]
                })
        
        # 生成图表
        generator = ChartGenerator()
        chart_path = generator.generate_bollinger_chart(
            dates, close_prices.tolist(),
            upper_band.tolist(), middle_band.tolist(), lower_band.tolist(),
            signals=signals,
            title=f'{ts_code} 布林带分析图'
        )
        
        # 构建结果
        result = f"## 布林带分析结果\n\n"
        result += f"**ETF代码**: {ts_code}\n"
        result += f"**参数**: 窗口={window}, 标准差倍数={num_std}\n\n"
        result += f"**信号点数量**: {len(signals)}\n"
        result += f"- 超买信号: {sum(1 for s in signals if s['type'] == 'overbought')}\n"
        result += f"- 超卖信号: {sum(1 for s in signals if s['type'] == 'oversold')}\n\n"
        
        if chart_path:
            result += f"![布林带图表]({chart_path})\n"
        
        return result
        
    except Exception as e:
        return f"布林带分析失败: {str(e)}"


def arima_stock(ts_code: str = '159108', days: int = 7) -> str:
    """
    ARIMA预测工具
    
    Args:
        ts_code: ETF代码
        days: 预测天数
        
    Returns:
        str: ARIMA预测结果
    """
    try:
        from statsmodels.tsa.arima.model import ARIMA
        
        db = DatabaseManager()
        conn = db.connect()
        
        query = '''
            SELECT trade_date, close 
            FROM stock_history 
            WHERE ts_code = ? 
            ORDER BY trade_date ASC
        '''
        
        df = pd.read_sql_query(query, conn, params=(ts_code,))
        db.close()
        
        if df.empty or len(df) < 30:
            return f"未找到足够的 {ts_code} 数据进行预测"
        
        close_prices = df['close'].values
        dates = df['trade_date'].tolist()
        
        # 训练ARIMA模型
        model = ARIMA(close_prices, order=(5, 1, 5))
        model_fit = model.fit()
        
        # 预测
        forecast_result = model_fit.get_forecast(steps=days)
        forecast_mean = forecast_result.predicted_mean
        forecast_ci = forecast_result.conf_int()
        
        # 生成预测日期
        last_date = datetime.strptime(dates[-1], '%Y%m%d')
        prediction_dates = [(last_date + timedelta(days=i+1)).strftime('%Y%m%d') 
                           for i in range(days)]
        
        # 生成图表
        generator = ChartGenerator()
        chart_path = generator.generate_prediction_chart(
            dates[-30:], close_prices[-30:].tolist(),
            prediction_dates, forecast_mean.tolist(),
            upper_bound=forecast_ci[:, 1].tolist(),
            lower_bound=forecast_ci[:, 0].tolist(),
            title=f'{ts_code} ARIMA价格预测'
        )
        
        # 构建结果
        result = f"## ARIMA预测结果\n\n"
        result += f"**ETF代码**: {ts_code}\n"
        result += f"**预测天数**: {days}天\n"
        result += f"**模型**: ARIMA(5,1,5)\n\n"
        result += "**预测价格**:\n\n"
        
        for i, (date, price) in enumerate(zip(prediction_dates, forecast_mean)):
            upper = forecast_ci[i, 1]
            lower = forecast_ci[i, 0]
            result += f"- {date}: {price:.2f} (置信区间: {lower:.2f} - {upper:.2f})\n"
        
        if chart_path:
            result += f"\n![预测图表]({chart_path})\n"
        
        return result
        
    except ImportError:
        return "statsmodels库未安装,请运行: pip install statsmodels"
    except Exception as e:
        return f"ARIMA预测失败: {str(e)}"


def prophet_analysis(ts_code: str = '159158') -> str:
    """
    Prophet周期性分析工具
    
    Args:
        ts_code: ETF代码
        
    Returns:
        str: Prophet分析结果
    """
    try:
        from prophet import Prophet
        
        db = DatabaseManager()
        conn = db.connect()
        
        query = '''
            SELECT trade_date, close 
            FROM stock_history 
            WHERE ts_code = ? 
            ORDER BY trade_date ASC
        '''
        
        df = pd.read_sql_query(query, conn, params=(ts_code,))
        db.close()
        
        if df.empty or len(df) < 60:
            return f"未找到足够的 {ts_code} 数据进行Prophet分析(至少需要60天数据)"
        
        # 准备Prophet数据格式
        prophet_df = pd.DataFrame({
            'ds': pd.to_datetime(df['trade_date'], format='%Y%m%d'),
            'y': df['close'].values
        })
        
        # 创建并训练Prophet模型
        # 在Windows上禁用多进程以避免Stan CSV解析问题
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            n_changepoints=25,
            changepoint_range=0.8
        )
        
        # 添加月度季节性
        model.add_seasonality(name='monthly', period=30.5, fourier_order=5)
        
        # 训练模型(使用单进程避免Windows兼容性问题)
        import logging
        logging.getLogger('prophet').setLevel(logging.ERROR)
        model.fit(prophet_df, show_progress=False)
        
        # 创建未来数据框
        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)
        
        # 提取组件
        trend = forecast['trend'].values
        weekly = forecast['weekly'].values
        yearly = forecast['yearly'].values
        
        dates = forecast['ds'].dt.strftime('%Y%m%d').tolist()
        
        # 生成组件分解图
        generator = ChartGenerator()
        chart_path = generator.generate_prophet_components_chart(
            dates, trend.tolist(), weekly.tolist(), yearly.tolist(),
            title=f'{ts_code} Prophet组件分解'
        )
        
        # 构建结果
        result = f"## Prophet周期性分析结果\n\n"
        result += f"**ETF代码**: {ts_code}\n"
        result += f"**数据点数**: {len(prophet_df)}\n\n"
        result += "**分析组件**:\n"
        result += "- 长期趋势 (Trend)\n"
        result += "- 周季节性 (Weekly)\n"
        result += "- 年季节性 (Yearly)\n"
        result += "- 月季节性 (Monthly)\n\n"
        
        # 添加最近30天的预测摘要
        result += "**未来30天预测摘要**:\n\n"
        last_30 = forecast.tail(30)
        for _, row in last_30.iterrows():
            date_str = row['ds'].strftime('%Y-%m-%d')
            pred = row['yhat']
            lower = row['yhat_lower']
            upper = row['yhat_upper']
            result += f"- {date_str}: {pred:.2f} ({lower:.2f} - {upper:.2f})\n"
        
        if chart_path:
            result += f"\n![Prophet组件图]({chart_path})\n"
        
        return result
        
    except ImportError:
        return "prophet库未安装,请运行: pip install prophet"
    except Exception as e:
        error_msg = str(e)
        # 提供更友好的错误信息
        if 'Stan csv' in error_msg or 'parsing' in error_msg.lower():
            return f"""Prophet分析失败: Windows系统兼容性问题

建议解决方案:
1. 尝试重新安装prophet: pip uninstall prophet && pip install prophet
2. 或使用ARIMA预测替代: 调用arima_stock工具
3. 或在Linux/Mac系统上使用此功能

原始错误: {error_msg}"""
        else:
            return f"Prophet分析失败: {error_msg}"
