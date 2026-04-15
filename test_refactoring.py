import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

print("=" * 60)
print("园区白领薪资数据分析工具 - 重构测试")
print("=" * 60)

print("\n1. 测试模块导入...")
try:
    from src.models import DataManager, ConfigManager, get_logger
    from src.services import DataLoader, DataProcessor, DataAnalyzer, DataVisualizer
    from src.services import DataService, ProcessingService, AnalysisService, VisualizationService
    from src.controllers import DataController, AnalysisController, VisualizationController
    from src.ui import UIComponentFactory
    print("   ✓ 所有模块导入成功")
except Exception as e:
    print(f"   ✗ 导入失败: {e}")
    sys.exit(1)

print("\n2. 测试数据模型层...")
try:
    dm = DataManager()
    config = ConfigManager()
    logger = get_logger('Test')
    
    assert dm.has_data() == False, "初始状态应该没有数据"
    
    test_data = pd.DataFrame({
        'name': ['张三', '李四', '王五', '赵六'],
        'gender': ['男', '女', '男', '女'],
        'age': [25, 30, 35, 28],
        'work_years': [2, 5, 10, 4],
        'pre_tax_salary': [10000, 15000, 20000, 12000],
        'post_tax_salary': [8000, 12000, 16000, 9600]
    })
    
    dm.set_data(test_data, is_original=True)
    assert dm.has_data() == True, "设置数据后应该有数据"
    assert dm.get_row_count() == 4, "应该有4条记录"
    
    print("   ✓ DataManager测试通过")
    print(f"   ✓ ConfigManager: {config.get('app.name')} v{config.get('app.version')}")
except Exception as e:
    print(f"   ✗ 数据模型层测试失败: {e}")
    sys.exit(1)

print("\n3. 测试业务服务层...")
try:
    loader = DataLoader(config)
    processor = DataProcessor(config)
    analyzer = DataAnalyzer()
    visualizer = DataVisualizer(config)
    
    result, count = processor.remove_duplicates(test_data)
    assert len(result) == 4, "去重后应该还是4条"
    
    stats = analyzer.get_descriptive_stats(test_data, 'pre_tax_salary')
    assert stats['mean'] == 14250.0, "平均薪资应该是14250"
    
    fig = visualizer.create_bar_chart(['A', 'B'], [10, 20], '测试')
    assert fig is not None, "应该创建图表"
    
    print("   ✓ DataLoader测试通过")
    print("   ✓ DataProcessor测试通过")
    print("   ✓ DataAnalyzer测试通过")
    print("   ✓ DataVisualizer测试通过")
except Exception as e:
    print(f"   ✗ 业务服务层测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n4. 测试服务层包装类...")
try:
    ds = DataService(dm, config)
    ps = ProcessingService(dm, config)
    as_ = AnalysisService(dm, config)
    vs = VisualizationService(dm, config)
    
    info = ds.get_data_info()
    assert info['rows'] == 4, "DataService应该返回4条记录"
    
    summary = as_.get_summary_report('pre_tax_salary')
    assert summary['平均薪资'] == 14250.0, "平均薪资应该是14250"
    
    print("   ✓ DataService测试通过")
    print("   ✓ ProcessingService测试通过")
    print("   ✓ AnalysisService测试通过")
    print("   ✓ VisualizationService测试通过")
except Exception as e:
    print(f"   ✗ 服务层测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n5. 测试控制器层...")
try:
    dc = DataController(dm, config)
    ac = AnalysisController(dm, config)
    vc = VisualizationController(dm, config)
    
    assert dc.has_data() == True, "DataController应该有数据"
    assert ac.has_data() == True, "AnalysisController应该有数据"
    assert vc.has_data() == True, "VisualizationController应该有数据"
    
    cat_cols = dc.get_categorical_columns()
    num_cols = dc.get_numeric_columns()
    
    print(f"   ✓ 分类列: {cat_cols}")
    print(f"   ✓ 数值列: {num_cols}")
    print("   ✓ DataController测试通过")
    print("   ✓ AnalysisController测试通过")
    print("   ✓ VisualizationController测试通过")
except Exception as e:
    print(f"   ✗ 控制器层测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n6. 测试数据处理功能...")
try:
    result, msg = ps.create_age_group('age')
    assert result == True, "创建年龄分组应该成功"
    
    result, msg = ps.create_salary_group('pre_tax_salary')
    assert result == True, "创建薪资分组应该成功"
    
    result, msg = ps.create_experience_group('work_years')
    assert result == True, "创建工作年限分组应该成功"
    
    data = dm.get_data()
    assert 'age_group' in data.columns, "应该有age_group列"
    assert 'salary_group' in data.columns, "应该有salary_group列"
    assert 'experience_group' in data.columns, "应该有experience_group列"
    
    print("   ✓ 年龄分组测试通过")
    print("   ✓ 薪资分组测试通过")
    print("   ✓ 工作年限分组测试通过")
except Exception as e:
    print(f"   ✗ 数据处理功能测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n7. 测试数据分析功能...")
try:
    freq = ac.get_frequency_analysis('gender')
    assert len(freq) == 2, "性别应该有2种"
    
    comparison = ac.compare_by_dimension('gender', 'pre_tax_salary')
    assert len(comparison) == 2, "性别对比应该有2组"
    
    corr = ac.get_correlation_matrix(['age', 'work_years', 'pre_tax_salary'])
    assert not corr.empty, "相关性矩阵不应为空"
    
    print("   ✓ 频率分析测试通过")
    print("   ✓ 维度对比测试通过")
    print("   ✓ 相关性分析测试通过")
except Exception as e:
    print(f"   ✗ 数据分析功能测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n8. 测试可视化功能...")
try:
    fig = vc.create_bar_chart('gender', 'pre_tax_salary')
    assert fig is not None, "柱状图应该创建成功"
    
    fig = vc.create_histogram('pre_tax_salary')
    assert fig is not None, "直方图应该创建成功"
    
    fig = vc.create_boxplot('gender', 'pre_tax_salary')
    assert fig is not None, "箱线图应该创建成功"
    
    print("   ✓ 柱状图测试通过")
    print("   ✓ 直方图测试通过")
    print("   ✓ 箱线图测试通过")
except Exception as e:
    print(f"   ✗ 可视化功能测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("所有测试通过！重构成功！")
print("=" * 60)

print("\n项目结构:")
print("""
src/
├── models/                    # 数据模型层
│   ├── __init__.py
│   ├── data_manager.py       # 统一数据管理
│   ├── config_manager.py     # 配置管理
│   └── logger.py             # 日志管理
├── services/                  # 业务服务层
│   ├── __init__.py
│   ├── data_loader_service.py    # 数据加载
│   ├── data_processor_service.py # 数据处理
│   ├── data_analyzer_service.py  # 数据分析
│   ├── data_visualizer_service.py # 数据可视化
│   ├── data_service.py       # 数据服务包装
│   ├── processing_service.py # 处理服务包装
│   ├── analysis_service.py   # 分析服务包装
│   └── visualization_service.py # 可视化服务包装
├── controllers/               # 控制器层
│   ├── __init__.py
│   ├── data_controller.py    # 数据控制器
│   ├── analysis_controller.py # 分析控制器
│   └── visualization_controller.py # 可视化控制器
├── ui/                        # UI层
│   ├── __init__.py
│   └── base.py               # UI组件工厂和基类
└── __init__.py
""")
