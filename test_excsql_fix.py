"""
测试ExcSql工具的ETF代码识别功能
"""

from agent_tools import ExcSql


def test_etf_recognition():
    """测试不同ETF的识别"""
    
    tool = ExcSql()
    
    test_cases = [
        {
            'query': '查询电力ETF最近一个月收盘价',
            'expected_code': '159158',
            'expected_name': '电力ETF景顺'
        },
        {
            'query': '查询有色金属ETF最近一个月收盘价',
            'expected_code': '512400',
            'expected_name': '有色金属ETF南方'
        },
        {
            'query': '查询科创芯片ETF最近一个月收盘价',
            'expected_code': '588200',
            'expected_name': '科创芯片ETF嘉实'
        },
        {
            'query': '查询科创AIETF最近一个月收盘价',
            'expected_code': '588790',
            'expected_name': '科创AIETF博时'
        },
        {
            'query': '查询工业软件ETF最近一个月收盘价',
            'expected_code': '159108',
            'expected_name': '工业软件ETF博时'
        },
    ]
    
    print("="*60)
    print("测试ExcSql工具的ETF代码识别")
    print("="*60)
    print()
    
    for i, test_case in enumerate(test_cases, 1):
        query = test_case['query']
        expected_code = test_case['expected_code']
        expected_name = test_case['expected_name']
        
        print(f"测试 {i}: {query}")
        print(f"预期ETF: {expected_code} ({expected_name})")
        
        try:
            result = tool.call({'query_description': query})
            
            # 检查结果中是否包含正确的ETF代码
            if expected_code in result or expected_name in result:
                print(f"✅ 通过 - 返回了正确的ETF数据")
            else:
                print(f"❌ 失败 - 未找到预期的ETF代码 {expected_code}")
                print(f"   返回结果前200字符: {result[:200]}")
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
        
        print()
    
    print("="*60)
    print("测试完成")
    print("="*60)


if __name__ == '__main__':
    test_etf_recognition()
