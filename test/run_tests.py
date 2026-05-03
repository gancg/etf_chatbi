"""
ETF ChatBI 助手测试套件
统一运行所有测试用例
"""

import unittest
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def run_all_tests():
    """运行所有测试用例"""
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 加载功能测试
    from test.test_functional import (
        TestStartup,
        TestSQLQuery,
        TestMACDAnalysis,
        TestBollingerBands,
        TestARIMAPrediction,
        TestProphetAnalysis,
        TestEmailNotification
    )
    
    # 加载数据完整性测试
    from test.test_data_integrity import (
        TestDatabaseCreation,
        TestMonitoredETFData,
        TestScheduledTask,
        TestChartGeneration,
        TestDataIntegrity
    )
    
    # 加载性能测试
    from test.test_performance import (
        TestSQLQueryPerformance,
        TestTechnicalAnalysisPerformance,
        TestChartGenerationPerformance,
        TestLargeDataSetPerformance,
        TestSystemResourceUsage
    )
    
    # 添加所有测试类到套件
    loader = unittest.TestLoader()
    
    # 功能测试
    test_suite.addTests(loader.loadTestsFromTestCase(TestStartup))
    test_suite.addTests(loader.loadTestsFromTestCase(TestSQLQuery))
    test_suite.addTests(loader.loadTestsFromTestCase(TestMACDAnalysis))
    test_suite.addTests(loader.loadTestsFromTestCase(TestBollingerBands))
    test_suite.addTests(loader.loadTestsFromTestCase(TestARIMAPrediction))
    test_suite.addTests(loader.loadTestsFromTestCase(TestProphetAnalysis))
    test_suite.addTests(loader.loadTestsFromTestCase(TestEmailNotification))
    
    # 数据完整性测试
    test_suite.addTests(loader.loadTestsFromTestCase(TestDatabaseCreation))
    test_suite.addTests(loader.loadTestsFromTestCase(TestMonitoredETFData))
    test_suite.addTests(loader.loadTestsFromTestCase(TestScheduledTask))
    test_suite.addTests(loader.loadTestsFromTestCase(TestChartGeneration))
    test_suite.addTests(loader.loadTestsFromTestCase(TestDataIntegrity))
    
    # 性能测试
    test_suite.addTests(loader.loadTestsFromTestCase(TestSQLQueryPerformance))
    test_suite.addTests(loader.loadTestsFromTestCase(TestTechnicalAnalysisPerformance))
    test_suite.addTests(loader.loadTestsFromTestCase(TestChartGenerationPerformance))
    test_suite.addTests(loader.loadTestsFromTestCase(TestLargeDataSetPerformance))
    test_suite.addTests(loader.loadTestsFromTestCase(TestSystemResourceUsage))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result


if __name__ == '__main__':
    print("=" * 80)
    print("ETF ChatBI 助手 - 完整测试套件")
    print("=" * 80)
    print()
    
    result = run_all_tests()
    
    print()
    print("=" * 80)
    print(f"测试结果汇总:")
    print(f"  运行测试数: {result.testsRun}")
    print(f"  成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  失败: {len(result.failures)}")
    print(f"  错误: {len(result.errors)}")
    print("=" * 80)
    
    # 如果有失败或错误,返回非零退出码
    if result.failures or result.errors:
        sys.exit(1)
