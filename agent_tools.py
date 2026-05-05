"""
ETF ChatBI 助手 - qwen-agent工具类
将所有工具函数封装为BaseTool子类
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from database import DatabaseManager
from chart_generator import ChartGenerator
from qwen_agent.tools import BaseTool


class ExcSql(BaseTool):
    """SQL查询工具"""
    
    @property
    def name(self):
        return 'ExcSql'
    
    @property
    def description(self):
        return '执行SQL查询,支持自然语言描述查询需求'
    
    @property
    def parameters(self):
        return {
            'type': 'object',
            'properties': {
                'query_description': {
                    'type': 'string',
                    'description': '自然语言描述的查询需求,例如:查询科创芯片ETF最近一个月的收盘价'
                }
            },
            'required': ['query_description']
        }
    
    def call(self, params: dict, **kwargs) -> str:
        """执行SQL查询"""
        try:
            # 处理params可能是字符串的情况
            if isinstance(params, str):
                import json
                try:
                    params = json.loads(params)
                except:
                    params = {'query_description': params}
            
            query_description = params.get('query_description', '')
            db = DatabaseManager()
            conn = db.connect()
            cursor = conn.cursor()
            
            # 使用LLM将自然语言转换为SQL
            import os
            import dashscope
            from dashscope import Generation
            
            api_key = os.getenv('DASHSCOPE_API_KEY', '')
            dashscope.api_key = api_key
            
            # 获取数据库表结构
            table_schema = db.get_table_schema('stock_history')
            
            # 获取一些示例数据帮助LLM理解
            cursor.execute('SELECT * FROM stock_history LIMIT 3')
            sample_data = cursor.fetchall()
            sample_columns = [description[0] for description in cursor.description]
            
            # 构建Prompt
            prompt = f"""你是一个SQL专家,请将用户的自然语言查询转换为SQLite SQL语句。

数据库表: stock_history
表字段: {', '.join(table_schema)}
字段说明:
- id: 主键
- ts_code: ETF代码(如512400, 588200, 588790, 159108, 159158)
- ts_name: ETF名称(如有色金属ETF南方, 科创芯片ETF嘉实, 科创AIETF博时, 工业软件ETF博时, 电力ETF景顺)
- trade_date: 交易日期(格式:YYYYMMDD)
- open: 开盘价
- high: 最高价
- low: 最低价
- close: 收盘价
- vol: 成交量
- amount: 成交金额
- created_at: 创建时间
- updated_at: 更新时间

示例数据:
{sample_data}

ETF代码映射:
- 512400: 有色金属ETF南方
- 588200: 科创芯片ETF嘉实
- 588790: 科创AIETF博时
- 159108: 工业软件ETF博时
- 159158: 电力ETF景顺

用户查询: {query_description}

要求:
1. 只返回SQL语句,不要其他解释
2. 直接生成完整的SQL语句,不要使用?占位符,将具体的值写入SQL中
3. 日期比较使用 trade_date 字段,例如: trade_date >= '20240101'
4. 如果查询包含时间范围(如最近一个月),使用: trade_date >= strftime('%Y%m%d', 'now', '-30 days')
5. 默认按 trade_date DESC 排序
6. ts_code 是字符串类型,需要用单引号包裹,例如: ts_code = '588200'

SQL:"""
            
            # 调用LLM生成SQL
            response = Generation.call(
                model='qwen-max',
                prompt=prompt,
                max_tokens=500,
                temperature=0.1
            )
            
            if response.status_code != 200:
                return f"SQL生成失败: {response.message}"
            
            # 提取SQL语句
            generated_sql = response.output.text.strip()
            
            # 清理SQL(移除可能的```
            if generated_sql.startswith('```'):
                lines = generated_sql.split('\n')
                generated_sql = '\n'.join(lines[1:])  # 移除第一行 ```sql
                if generated_sql.endswith('```'):
                    generated_sql = generated_sql[:-3]
            generated_sql = generated_sql.strip()
            
            # 执行SQL查询
            cursor.execute(generated_sql)
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            db.close()
            
            if not rows:
                return f"未查询到数据\n\n执行的SQL:\n{generated_sql}"
            
            # 转换为DataFrame
            df = pd.DataFrame(rows, columns=columns)
            
            # 生成Markdown表格
            markdown_table = df.to_markdown(index=False)
            
            result = f"查询结果:\n\n{markdown_table}\n\n执行的SQL:\n```sql\n{generated_sql}\n```"
            
            # 如果数据包含收盘价和交易日期,且数据量适合,生成图表
            if len(df) <= 100 and 'close' in df.columns and 'trade_date' in df.columns:
                # 按交易日期升序排序,确保图表按时间顺序绘制
                df_sorted = df.sort_values('trade_date', ascending=True)
                generator = ChartGenerator()
                chart_path = generator.generate_line_chart(
                    df_sorted['trade_date'].tolist(),
                    df_sorted['close'].tolist(),
                    title=f'价格走势图'
                )
                if chart_path:
                    result += f"\n\n![图表]({chart_path})\n"
            
            return result
            
        except Exception as e:
            return f"查询失败: {str(e)}"


class macd_stock(BaseTool):
    """MACD分析工具"""
    
    @property
    def name(self):
        return 'macd_stock'
    
    @property
    def description(self):
        return 'MACD技术指标分析,识别金叉死叉信号,计算交易收益率'
    
    @property
    def parameters(self):
        return {
            'type': 'object',
            'properties': {
                'ts_code': {
                    'type': 'string',
                    'description': 'ETF代码,如512400',
                    'default': '512400'
                },
                'period': {
                    'type': 'integer',
                    'description': '分析周期(天数)',
                    'default': 365
                }
            },
            'required': []
        }
    
    def call(self, params: dict, **kwargs) -> str:
        """执行MACD分析"""
        try:
            # 处理params可能是字符串的情况
            if isinstance(params, str):
                import json
                try:
                    params = json.loads(params)
                except:
                    params = {}
            
            ts_code = params.get('ts_code', '512400')
            period = params.get('period', 365)
            
            db = DatabaseManager()
            conn = db.connect()
            
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
            
            close_prices = df['close'].values
            dates = df['trade_date'].tolist()
            
            # 计算MACD
            def ema(data, span):
                return pd.Series(data).ewm(span=span, adjust=False).mean().values
            
            ema12 = ema(close_prices, 12)
            ema26 = ema(close_prices, 26)
            dif = ema12 - ema26
            dea = pd.Series(dif).ewm(span=9, adjust=False).mean().values
            macd_bar = 2 * (dif - dea)
            
            # 识别金叉和死叉
            signals = []
            for i in range(1, len(dif)):
                if dif[i-1] <= dea[i-1] and dif[i] > dea[i]:
                    signals.append({'date': dates[i], 'type': 'buy', 'price': close_prices[i]})
                elif dif[i-1] >= dea[i-1] and dif[i] < dea[i]:
                    signals.append({'date': dates[i], 'type': 'sell', 'price': close_prices[i]})
            
            # 模拟交易
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
            
            final_value = position * close_prices[-1] if position > 0 else capital
            return_rate = ((final_value - initial_capital) / initial_capital) * 100
            
            # 生成图表(确保数据按日期升序排列)
            df_sorted = df.sort_values('trade_date', ascending=True)
            generator = ChartGenerator()
            chart_path = generator.generate_macd_chart(
                df_sorted['trade_date'].tolist(), df_sorted['close'].tolist(),
                dif.tolist(), dea.tolist(), macd_bar.tolist(),
                signals=signals,
                title=f'{ts_code} MACD分析图'
            )
            
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


class boll_stock(BaseTool):
    """布林带分析工具"""
    
    @property
    def name(self):
        return 'boll_stock'
    
    @property
    def description(self):
        return '布林带技术指标分析,检测超买超卖信号'
    
    @property
    def parameters(self):
        return {
            'type': 'object',
            'properties': {
                'ts_code': {
                    'type': 'string',
                    'description': 'ETF代码',
                    'default': '588790'
                },
                'window': {
                    'type': 'integer',
                    'description': '窗口大小',
                    'default': 20
                },
                'num_std': {
                    'type': 'number',
                    'description': '标准差倍数',
                    'default': 2.0
                }
            },
            'required': []
        }
    
    def call(self, params: dict, **kwargs) -> str:
        """执行布林带分析"""
        try:
            # 处理params可能是字符串的情况
            if isinstance(params, str):
                import json
                try:
                    params = json.loads(params)
                except:
                    params = {}
            
            ts_code = params.get('ts_code', '588790')
            window = params.get('window', 20)
            num_std = params.get('num_std', 2.0)
            
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
            
            # 确保数据按日期升序排列
            df = df.sort_values('trade_date', ascending=True)
            close_prices = df['close'].values
            dates = df['trade_date'].tolist()
            
            # 计算布林带
            rolling_mean = pd.Series(close_prices).rolling(window=window).mean()
            rolling_std = pd.Series(close_prices).rolling(window=window).std()
            upper_band = rolling_mean + (rolling_std * num_std)
            middle_band = rolling_mean
            lower_band = rolling_mean - (rolling_std * num_std)
            
            # 检测信号
            signals = []
            for i in range(window, len(close_prices)):
                if close_prices[i] > upper_band.iloc[i]:
                    signals.append({'date': dates[i], 'type': 'overbought', 'price': close_prices[i]})
                elif close_prices[i] < lower_band.iloc[i]:
                    signals.append({'date': dates[i], 'type': 'oversold', 'price': close_prices[i]})
            
            # 生成图表
            generator = ChartGenerator()
            chart_path = generator.generate_bollinger_chart(
                dates, close_prices.tolist(),
                upper_band.tolist(), middle_band.tolist(), lower_band.tolist(),
                signals=signals,
                title=f'{ts_code} 布林带分析图'
            )
            
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


class arima_stock(BaseTool):
    """ARIMA预测工具"""
    
    @property
    def name(self):
        return 'arima_stock'
    
    @property
    def description(self):
        return '基于ARIMA模型的价格预测,预测未来N个交易日的价格走势'
    
    @property
    def parameters(self):
        return {
            'type': 'object',
            'properties': {
                'ts_code': {
                    'type': 'string',
                    'description': 'ETF代码,如159108',
                    'default': '159108'
                },
                'days': {
                    'type': 'integer',
                    'description': '预测天数(交易日)',
                    'default': 7
                }
            },
            'required': []
        }
    
    def _is_trading_day(self, date):
        """
        判断是否为交易日(考虑周末和中国法定节假日)
        
        Args:
            date: datetime对象
            
        Returns:
            bool: 是否为交易日
        """
        try:
            import chinese_calendar
            
            # 判断是否为工作日(排除周末)
            if date.weekday() >= 5:  # 5=周六, 6=周日
                return False
            
            # 判断是否为法定节假日
            # chinese_calendar.is_holiday() 返回 True 表示是节假日
            if chinese_calendar.is_holiday(date):
                return False
            
            # 判断是否为调休的工作日(有些周末需要上班)
            # chinese_calendar.is_workday() 返回 True 表示需要上班
            if chinese_calendar.is_workday(date) and date.weekday() >= 5:
                return True
            
            return True
            
        except ImportError:
            # 如果库未安装,只判断周末
            return date.weekday() < 5
    
    def _get_next_trading_day(self, current_date):
        """
        获取下一个交易日(跳过周末和法定节假日)
        
        Args:
            current_date: 当前日期(datetime对象)
            
        Returns:
            datetime: 下一个交易日
        """
        next_day = current_date + timedelta(days=1)
        
        # 跳过非交易日(周末和法定节假日)
        max_attempts = 30  # 防止无限循环(比如长假)
        attempts = 0
        
        while not self._is_trading_day(next_day) and attempts < max_attempts:
            next_day += timedelta(days=1)
            attempts += 1
        
        return next_day
    
    def _generate_trading_dates(self, start_date, num_days):
        """
        生成指定数量的交易日
        
        Args:
            start_date: 起始日期(datetime对象)
            num_days: 需要生成的交易日数量
            
        Returns:
            list: 交易日列表(YYYYMMDD格式字符串)
        """
        trading_dates = []
        current_date = start_date
        
        for _ in range(num_days):
            current_date = self._get_next_trading_day(current_date)
            trading_dates.append(current_date.strftime('%Y%m%d'))
        
        return trading_dates
    
    def call(self, params: dict, **kwargs) -> str:
        """执行ARIMA预测"""
        try:
            from statsmodels.tsa.arima.model import ARIMA
            
            # 处理params可能是字符串的情况
            if isinstance(params, str):
                import json
                try:
                    params = json.loads(params)
                except:
                    params = {}
            
            ts_code = params.get('ts_code', '159108')
            days = params.get('days', 7)
            
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
            
            # 确保数据按日期升序排列
            df = df.sort_values('trade_date', ascending=True)
            close_prices = df['close'].values
            dates = df['trade_date'].tolist()
            
            # 训练ARIMA模型
            model = ARIMA(close_prices, order=(5, 1, 5))
            model_fit = model.fit()
            
            # 预测
            forecast_result = model_fit.get_forecast(steps=days)
            forecast_mean = forecast_result.predicted_mean
            forecast_ci = forecast_result.conf_int()
            
            # 生成预测日期(只包含交易日,考虑周末和法定节假日)
            last_date = datetime.strptime(dates[-1], '%Y%m%d')
            prediction_dates = self._generate_trading_dates(last_date, days)
            
            # 生成图表(使用最近30天的历史数据)
            generator = ChartGenerator()
            chart_path = generator.generate_prediction_chart(
                dates[-30:], close_prices[-30:].tolist(),
                prediction_dates, forecast_mean.tolist(),
                upper_bound=forecast_ci[:, 1].tolist(),
                lower_bound=forecast_ci[:, 0].tolist(),
                title=f'{ts_code} ARIMA价格预测'
            )
            
            result = f"## ARIMA预测结果\n\n"
            result += f"**ETF代码**: {ts_code}\n"
            result += f"**预测天数**: {days}个交易日\n"
            result += f"**模型**: ARIMA(5,1,5)\n"
            result += f"**说明**: 预测日期已自动跳过周末和法定节假日\n\n"
            result += "**预测价格**:\n\n"
            
            for i, (date, price) in enumerate(zip(prediction_dates, forecast_mean)):
                upper = forecast_ci[i, 1]
                lower = forecast_ci[i, 0]
                result += f"- {date}: {price:.2f} (置信区间: {lower:.2f} - {upper:.2f})\n"
            
            if chart_path:
                result += f"\n![预测图表]({chart_path})\n"
            
            return result
            
        except ImportError as e:
            if 'chinese_calendar' in str(e):
                return "chinese_calendar库未安装,请运行: pip install chinese_calendar"
            return "statsmodels库未安装,请运行: pip install statsmodels"
        except Exception as e:
            return f"ARIMA预测失败: {str(e)}"


class prophet_analysis(BaseTool):
    """Prophet周期性分析工具"""
    
    @property
    def name(self):
        return 'prophet_analysis'
    
    @property
    def description(self):
        return 'Prophet周期性分析,识别长期趋势和季节性模式'
    
    @property
    def parameters(self):
        return {
            'type': 'object',
            'properties': {
                'ts_code': {
                    'type': 'string',
                    'description': 'ETF代码',
                    'default': '159158'
                }
            },
            'required': []
        }
    
    def call(self, params: dict, **kwargs) -> str:
        """执行Prophet分析"""
        try:
            from prophet import Prophet
            
            # 处理params可能是字符串的情况
            if isinstance(params, str):
                import json
                try:
                    params = json.loads(params)
                except:
                    params = {}
            
            ts_code = params.get('ts_code', '159158')
            
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
            
            # 确保数据按日期升序排列
            df = df.sort_values('trade_date', ascending=True)
            
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
            model.add_seasonality(name='monthly', period=30.5, fourier_order=5)
            
            # 训练模型(使用单进程避免Windows兼容性问题)
            import logging
            logging.getLogger('prophet').setLevel(logging.ERROR)
            logging.getLogger('cmdstanpy').setLevel(logging.ERROR)
            model.fit(prophet_df)
            
            # 预测
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
            
            result = f"## Prophet周期性分析结果\n\n"
            result += f"**ETF代码**: {ts_code}\n"
            result += f"**数据点数**: {len(prophet_df)}\n\n"
            result += "**分析组件**:\n"
            result += "- 长期趋势 (Trend)\n"
            result += "- 周季节性 (Weekly)\n"
            result += "- 年季节性 (Yearly)\n"
            result += "- 月季节性 (Monthly)\n\n"
            
            # 添加最近30天的预测摘要
            result += "**最近30天预测摘要**:\n\n"
            last_30 = forecast.tail(30)
            for _, row in last_30.iterrows():
                date_str = row['ds'].strftime('%Y%m%d')
                pred = row['yhat']
                result += f"- {date_str}: {pred:.2f}\n"
            
            if chart_path:
                result += f"\n![Prophet组件图]({chart_path})\n"
            
            return result
            
        except ImportError as e:
            error_msg = str(e)
            if 'prophet' in error_msg.lower():
                return f"""Prophet库未安装

Windows系统安装步骤:
1. 先安装Visual C++ Build Tools: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - 安装时选择 "Desktop development with C++"
2. 然后安装prophet: pip install -i https://pypi.tuna.tsinghua.edu.cn/simple prophet
3. 或尝试: conda install -c conda-forge prophet (如果使用conda)

或者使用ARIMA预测替代: 调用arima_stock工具"""
            return f"依赖库导入失败: {error_msg}"
        except Exception as e:
            error_msg = str(e)
            
            # 检测常见的Windows兼容性问题
            windows_issues = [
                'Stan csv',
                'parsing',
                'cmdstan',
                'access denied',
                'permission denied',
                '编译',
                'compilation',
                'C++',
                'Microsoft Visual C++'
            ]
            
            is_windows_issue = any(keyword.lower() in error_msg.lower() 
                                   for keyword in windows_issues)
            
            if is_windows_issue:
                return f"""Prophet分析失败: Windows系统兼容性问题

错误详情: {error_msg}

建议解决方案:
1. 【推荐】使用ARIMA预测替代: 调用arima_stock工具
   - ARIMA在Windows上完全兼容
   - 预测效果相近

2. 安装Visual C++编译工具:
   - 下载: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - 安装 "Desktop development with C++" 工作负载
   - 重启后重新安装: pip uninstall prophet && pip install prophet

3. 使用conda安装(如果有conda环境):
   conda install -c conda-forge prophet

4. 在WSL(Linux子系统)或Docker中运行

注意: Prophet依赖Stan后端,在Windows上需要C++编译环境"""
            else:
                return f"Prophet分析失败: {error_msg}"
