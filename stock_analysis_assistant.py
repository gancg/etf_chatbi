"""
ETF ChatBI 助手 - 主程序入口
基于 qwen-agent 构建智能对话机器人
"""

import os
import sys
from qwen_agent.agents import Assistant
from qwen_agent.gui import WebUI

# 导入自定义工具类
from agent_tools import ExcSql, macd_stock, boll_stock, arima_stock, prophet_analysis


def init_agent():
    """
    初始化AI Agent
    
    Returns:
        Assistant: 配置好的Assistant实例
    """
    # 从环境变量获取API Key
    api_key = os.getenv('DASHSCOPE_API_KEY', '')
    
    if not api_key:
        print("警告: 未设置 DASHSCOPE_API_KEY 环境变量")
    
    # 定义系统提示
    system_prompt = """你是ETF ChatBI智能数据分析助手,专门帮助用户分析ETF数据。

你可以执行以下操作:
1. SQL查询 - 使用自然语言查询ETF历史数据
2. MACD分析 - 技术指标分析,识别买卖信号
3. 布林带分析 - 检测超买超卖信号
4. ARIMA预测 - 短期价格趋势预测
5. Prophet分析 - 中长期周期性分析

监控的ETF列表:
- 512400: 有色金属ETF南方
- 588200: 科创芯片ETF嘉实
- 588790: 科创AIETF博时
- 159108: 工业软件ETF博时
- 159158: 电力ETF景顺

请用简洁、专业的语言回答用户问题。如果生成图表,请提供图片链接。
"""
    
    # 创建Assistant
    agent = Assistant(
        llm={
            'model': 'qwen-max',
            'api_key': api_key,
        },
        system_message=system_prompt,
        function_list=[
            ExcSql(),
            macd_stock(),
            boll_stock(),
            arima_stock(),
            prophet_analysis()
        ]
    )
    
    return agent


def main():
    """主函数"""
    print("="*60)
    print("ETF ChatBI 助手启动中...")
    print("="*60)
    
    # 确保数据库表已创建
    from database import DatabaseManager
    db = DatabaseManager()
    db.create_tables()
    db.close()
    
    # 确保image_show目录存在
    if not os.path.exists('image_show'):
        os.makedirs('image_show')
    
    # 初始化Agent
    agent = init_agent()
    
    # 配置聊天建议
    chatbot_config = {
        'prompt.suggestions': [
            "查询科创芯片ETF最近一个月的收盘价",
            "对有色金属ETF进行MACD分析",
            "分析科创AIETF的布林带",
            "预测工业软件ETF未来7天价格",
            "分析电力ETF的趋势和周期性"
        ]
    }
    
    # 启动Web UI
    print("\n正在启动Web UI...")
    print("请在浏览器中访问: http://localhost:7860\n")
    
    bot = WebUI(agent, chatbot_config=chatbot_config)
    bot.run()


if __name__ == '__main__':
    main()
