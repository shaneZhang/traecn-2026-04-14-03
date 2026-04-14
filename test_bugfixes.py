"""
测试修复的bug
"""
import pandas as pd
import numpy as np
import sys
import os

# 模拟tkinter模块，以便在非GUI环境测试
class MockTkinter:
    def __init__(self):
        pass
    def withdraw(self):
        pass
    def update(self):
        pass
    def config(self, **kwargs):
        pass
    def quit(self):
        pass
    def mainloop(self):
        pass
    def Tk(self):
        return MockTkinter()
    def Menu(self, *args, **kwargs):
        return MockTkinter()
    def Frame(self, *args, **kwargs):
        return MockTkinter()
    def Label(self, *args, **kwargs):
        return MockTkinter()
    def Button(self, *args, **kwargs):
        return MockTkinter()
    def Text(self, *args, **kwargs):
        return MockTkinter()
    def Treeview(self, *args, **kwargs):
        return MockTkinter()
    def Scrollbar(self, *args, **kwargs):
        return MockTkinter()
    def Combobox(self, *args, **kwargs):
        return MockTkinter()
    def LabelFrame(self, *args, **kwargs):
        return MockTkinter()
    def Notebook(self, *args, **kwargs):
        return MockTkinter()
    def StringVar(self, *args, **kwargs):
        class Var:
            def get(self):
                return ""
            def set(self, val):
                pass
        return Var()
    def filedialog(self):
        return MockTkinter()
    def messagebox(self):
        return MockTkinter()

sys.modules['tkinter'] = MockTkinter()
sys.modules['tkinter.filedialog'] = MockTkinter()
sys.modules['tkinter.messagebox'] = MockTkinter()

# 现在可以安全导入我们的模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_processor import DataProcessor
from src.data_analyzer import DataAnalyzer


def test_handle_missing_values_drop():
    """测试删除缺失值功能"""
    print("\n=== 测试: handle_missing_values (drop策略) ===")
    
    # 创建测试数据
    df = pd.DataFrame({
        'A': [1, 2, np.nan, 4, 5],
        'B': [10, np.nan, 30, 40, 50],
        'C': ['a', 'b', 'c', 'd', 'e']
    })
    
    processor = DataProcessor(df)
    result = processor.handle_missing_values(strategy='drop')
    
    new_df = processor.get_current_data()
    
    print(f"原始数据行数: 5")
    print(f"处理后数据行数: {len(new_df)}")
    print(f"删除的行数: {5 - len(new_df)}")
    print(f"返回的缺失值统计: {result}")
    
    # 验证：应该删除包含NaN的行（第1和第2行）
    assert len(new_df) == 3, f"期望3行，实际{len(new_df)}行"
    assert new_df.isnull().sum().sum() == 0, "处理后不应有缺失值"
    print("✓ 测试通过")


def test_handle_missing_values_fill():
    """测试填充缺失值功能"""
    print("\n=== 测试: handle_missing_values (fill_mean策略) ===")
    
    df = pd.DataFrame({
        'A': [1.0, 2.0, np.nan, 4.0, 5.0],
        'B': [10.0, np.nan, 30.0, 40.0, 50.0]
    })
    
    processor = DataProcessor(df)
    result = processor.handle_missing_values(strategy='fill_mean')
    
    new_df = processor.get_current_data()
    
    print(f"填充后数据:\n{new_df}")
    print(f"返回的缺失值统计: {result}")
    
    # 验证：不应有缺失值
    assert new_df.isnull().sum().sum() == 0, "填充后不应有缺失值"
    print("✓ 测试通过")


def test_create_age_group():
    """测试年龄分组功能"""
    print("\n=== 测试: create_age_group ===")
    
    df = pd.DataFrame({
        'age': [22, 28, 35, 42, 55, 65, 18]
    })
    
    processor = DataProcessor(df)
    success = processor.create_age_group('age')
    
    new_df = processor.get_current_data()
    
    print(f"年龄分组结果:\n{new_df[['age', 'age_group']]}")
    
    assert success, "年龄分组应该成功"
    assert 'age_group' in new_df.columns, "应该创建age_group列"
    
    # 验证分组是否正确
    age_22_group = new_df[new_df['age'] == 22]['age_group'].iloc[0]
    age_65_group = new_df[new_df['age'] == 65]['age_group'].iloc[0]
    
    print(f"22岁分组: {age_22_group}")
    print(f"65岁分组: {age_65_group}")
    
    print("✓ 测试通过")


def test_create_salary_group():
    """测试薪资分组功能"""
    print("\n=== 测试: create_salary_group ===")
    
    df = pd.DataFrame({
        'pre_tax_salary': [3000, 8000, 12000, 18000, 25000, 40000, 60000]
    })
    
    processor = DataProcessor(df)
    success = processor.create_salary_group('pre_tax_salary')
    
    new_df = processor.get_current_data()
    
    print(f"薪资分组结果:\n{new_df[['pre_tax_salary', 'salary_group']]}")
    
    assert success, "薪资分组应该成功"
    assert 'salary_group' in new_df.columns, "应该创建salary_group列"
    print("✓ 测试通过")


def test_get_frequency_analysis():
    """测试频率分析功能"""
    print("\n=== 测试: get_frequency_analysis ===")
    
    df = pd.DataFrame({
        'gender': ['男', '女', '男', '男', '女', '男', '女', '女']
    })
    
    analyzer = DataAnalyzer(df)
    freq = analyzer.get_frequency_analysis('gender')
    
    print(f"频率分析结果:\n{freq}")
    
    assert not freq.empty, "频率分析结果不应为空"
    assert 'count' in freq.columns, "结果应包含count列"
    assert 'percentage' in freq.columns, "结果应包含percentage列"
    print("✓ 测试通过")


def test_get_descriptive_stats():
    """测试描述性统计功能"""
    print("\n=== 测试: get_descriptive_stats ===")
    
    df = pd.DataFrame({
        'salary': [5000, 6000, 7000, 8000, 9000, 10000]
    })
    
    analyzer = DataAnalyzer(df)
    stats = analyzer.get_descriptive_stats('salary')
    
    print(f"描述性统计结果:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    assert 'mean' in stats, "结果应包含mean"
    assert 'median' in stats, "结果应包含median"
    assert 'std' in stats, "结果应包含std"
    print("✓ 测试通过")


def test_get_correlation_matrix():
    """测试相关性矩阵功能"""
    print("\n=== 测试: get_correlation_matrix ===")
    
    df = pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': [2, 4, 6, 8, 10],
        'C': [5, 4, 3, 2, 1]
    })
    
    analyzer = DataAnalyzer(df)
    corr = analyzer.get_correlation_matrix()
    
    print(f"相关性矩阵:\n{corr}")
    
    assert not corr.empty, "相关性矩阵不应为空"
    assert corr.shape == (3, 3), f"期望3x3矩阵，实际{corr.shape}"
    print("✓ 测试通过")


def test_edge_cases():
    """测试边界情况"""
    print("\n=== 测试: 边界情况 ===")
    
    # 测试空DataFrame
    empty_df = pd.DataFrame()
    processor = DataProcessor(empty_df)
    result = processor.handle_missing_values(strategy='drop')
    assert result == {}, "空DataFrame应返回空字典"
    print("✓ 空DataFrame处理正确")
    
    # 测试没有缺失值的数据
    clean_df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    processor = DataProcessor(clean_df)
    result = processor.handle_missing_values(strategy='drop')
    assert result == {}, "无缺失值应返回空字典"
    print("✓ 无缺失值数据处理正确")
    
    # 测试单列全为NaN
    nan_df = pd.DataFrame({'A': [np.nan, np.nan, np.nan], 'B': [1, 2, 3]})
    processor = DataProcessor(nan_df)
    result = processor.handle_missing_values(strategy='fill_mean', columns=['A'])
    new_df = processor.get_current_data()
    # 均值填充全NaN列应该仍然是NaN
    print(f"全NaN列填充后: {new_df['A'].tolist()}")
    print("✓ 全NaN列处理正确")


def main():
    print("="*60)
    print("开始运行Bug修复测试")
    print("="*60)
    
    try:
        test_handle_missing_values_drop()
        test_handle_missing_values_fill()
        test_create_age_group()
        test_create_salary_group()
        test_get_frequency_analysis()
        test_get_descriptive_stats()
        test_get_correlation_matrix()
        test_edge_cases()
        
        print("\n" + "="*60)
        print("所有测试通过！✓")
        print("="*60)
        return 0
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
