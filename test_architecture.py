import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np

print("=" * 60)
print("开始架构测试")
print("=" * 60)

# 1. 测试数据模型层
print("\n1. 测试数据模型层...")
from src.models import DataManager, ConfigManager, Logger

dm1 = DataManager()
dm2 = DataManager()
assert dm1 is dm2, "DataManager应该是单例"
print("  ✓ DataManager单例正常")

cm1 = ConfigManager()
cm2 = ConfigManager()
assert cm1 is cm2, "ConfigManager应该是单例"
field_mapping = cm1.get('field_mapping')
assert "姓名" in field_mapping, "配置应该包含字段映射"
print("  ✓ ConfigManager单例和配置正常")

logger1 = Logger()
logger2 = Logger()
assert logger1 is logger2, "Logger应该是单例"
print("  ✓ Logger单例正常")

# 2. 测试核心业务模块
print("\n2. 测试核心业务模块...")
from src.core import DataProcessorCore, DataAnalyzerCore

processor = DataProcessorCore()
analyzer = DataAnalyzerCore()

test_data = pd.DataFrame({
    'age': [25, 30, 35, 40, 45, 30, 30],
    'pre_tax_salary': [8000, 12000, 15000, 20000, 25000, 12000, 12000],
    'gender': ['男', '女', '男', '女', '男', '女', '女']
})

cleaned, dup_count = processor.remove_duplicates(test_data)
assert dup_count == 2, f"应该删除2条重复数据，实际删除了{dup_count}条"
print("  ✓ DataProcessorCore 去重功能正常")

stats = analyzer.get_descriptive_stats(test_data, 'pre_tax_salary')
assert stats['mean'] > 0, "统计结果应该有有效值"
print("  ✓ DataAnalyzerCore 统计功能正常")

# 3. 测试服务层
print("\n3. 测试服务层...")
from src.services import DataService, ProcessingService, AnalysisService

DataManager().set_data(test_data, 'test')
data_service = DataService()
assert data_service.has_data(), "DataService应该有数据"
info = data_service.get_data_info()
assert info['rows'] == 7, f"应该有7行记录，实际有{info['rows']}行"
print("  ✓ DataService服务正常")

processing_service = ProcessingService()
count = processing_service.remove_duplicates()
assert count == 2, f"应该删除2条重复数据，实际删除了{count}条"
print("  ✓ ProcessingService服务正常")

analysis_service = AnalysisService()
stats = analysis_service.get_descriptive_stats('pre_tax_salary')
assert stats['mean'] > 0, "统计服务应该有有效值"
print("  ✓ AnalysisService服务正常")

# 4. 测试控制器层
print("\n4. 测试控制器层...")
from src.controllers import DataController, AnalysisController

data_controller = DataController()
assert data_controller.has_data(), "DataController应该有数据"
print("  ✓ DataController初始化正常")

analysis_controller = AnalysisController()
assert analysis_controller.has_data(), "AnalysisController应该有数据"
print("  ✓ AnalysisController初始化正常")

print("\n" + "=" * 60)
print("✅ 所有架构测试通过！")
print("=" * 60)
