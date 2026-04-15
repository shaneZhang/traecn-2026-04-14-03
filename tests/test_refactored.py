"""
重构后代码的单元测试
"""
import sys
import os
import unittest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.data_manager import DataManager, DataChangeType
from src.models.config_manager import ConfigManager
from src.models.logger import Logger
from src.services.data_service import DataService
from src.services.processing_service import ProcessingService
from src.services.analysis_service import AnalysisService
from src.services.visualization_service import VisualizationService
from src.utils.exceptions import DataLoadError, DataProcessError, DataAnalysisError


class TestDataManager(unittest.TestCase):
    """测试数据管理器"""

    def setUp(self):
        self.dm = DataManager()
        self.test_data = pd.DataFrame({
            'name': ['张三', '李四', '王五'],
            'age': [25, 30, 35],
            'salary': [5000, 8000, 12000]
        })

    def test_load_data(self):
        self.dm.load_data(self.test_data, source='test')
        self.assertTrue(self.dm.has_data())
        self.assertEqual(self.dm.get_row_count(), 3)

    def test_get_data(self):
        self.dm.load_data(self.test_data)
        data = self.dm.get_data()
        self.assertIsNotNone(data)
        self.assertEqual(len(data), 3)

    def test_reset_data(self):
        self.dm.load_data(self.test_data)
        original = self.dm.get_data()
        # 修改数据
        modified = original.copy()
        modified['age'] = [100, 200, 300]
        self.dm.update_data(modified)
        # 重置
        self.dm.reset_data()
        reset_data = self.dm.get_data()
        self.assertEqual(reset_data['age'].tolist(), [25, 30, 35])

    def test_data_change_subscription(self):
        events = []

        def callback(event):
            events.append(event)

        self.dm.subscribe(callback)
        self.dm.load_data(self.test_data)

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].change_type, DataChangeType.LOADED)


class TestConfigManager(unittest.TestCase):
    """测试配置管理器"""

    def setUp(self):
        self.cm = ConfigManager()

    def test_get_field_mapping(self):
        mapping = self.cm.get_field_mapping()
        self.assertIn('姓名', mapping)
        self.assertEqual(mapping['姓名'], 'name')

    def test_get_grouping_config(self):
        age_config = self.cm.get_grouping_config('age')
        self.assertIn('bins', age_config)
        self.assertIn('labels', age_config)

    def test_get_set(self):
        self.cm.set('test.key', 'value')
        self.assertEqual(self.cm.get('test.key'), 'value')
        self.assertEqual(self.cm.get('nonexistent.key', 'default'), 'default')


class TestDataService(unittest.TestCase):
    """测试数据服务"""

    def setUp(self):
        self.ds = DataService()

    def test_validate_data(self):
        data = pd.DataFrame({
            'age': [25, 30, 'invalid'],
            'salary': [5000, 8000, 10000]
        })
        is_valid, errors = self.ds.validate_data(data)
        self.assertFalse(is_valid)
        self.assertTrue(len(errors) > 0)

    def test_get_data_info(self):
        data = pd.DataFrame({
            'name': ['张三', '李四'],
            'age': [25, 30]
        })
        info = self.ds.get_data_info(data)
        self.assertEqual(info['rows'], 2)
        self.assertEqual(info['columns'], 2)


class TestProcessingService(unittest.TestCase):
    """测试处理服务"""

    def setUp(self):
        self.ps = ProcessingService()
        self.test_data = pd.DataFrame({
            'name': ['张三', '李四', '王五', '张三'],
            'age': [25, 30, 35, 25],
            'salary': [5000, 8000, 12000, 5000]
        })

    def test_remove_duplicates(self):
        result, count = self.ps.remove_duplicates(self.test_data)
        self.assertEqual(count, 1)
        self.assertEqual(len(result), 3)

    def test_handle_missing_values_drop(self):
        data = pd.DataFrame({
            'name': ['张三', '李四', None],
            'age': [25, None, 35]
        })
        result, info = self.ps.handle_missing_values(data, strategy='drop')
        # 第3行没有缺失值（name为None在pandas中是NaN，但这里只有age列有35）
        # 实际上第3行name=None是NaN，所以所有行都有缺失值
        # 但pandas中None会被识别为缺失值，所以第3行也有缺失值
        # 修正：第1行name='张三'无缺失，age=25无缺失
        # 第2行name='李四'无缺失，age=None有缺失
        # 第3行name=None有缺失，age=35无缺失
        # 所以只有第1行完全无缺失
        self.assertEqual(len(result), 1)  # 只有第1行无缺失值

    def test_create_age_group(self):
        data = pd.DataFrame({
            'age': [22, 28, 32, 45, 55]
        })
        result = self.ps.create_age_group(data)
        self.assertIn('age_group', result.columns)

    def test_create_salary_group(self):
        data = pd.DataFrame({
            'pre_tax_salary': [3000, 8000, 15000, 25000, 40000]
        })
        result = self.ps.create_salary_group(data)
        self.assertIn('salary_group', result.columns)


class TestAnalysisService(unittest.TestCase):
    """测试分析服务"""

    def setUp(self):
        self.aservice = AnalysisService()
        self.test_data = pd.DataFrame({
            'salary': [5000, 6000, 7000, 8000, 9000, 10000],
            'age': [25, 28, 30, 32, 35, 40],
            'department': ['IT', 'HR', 'IT', 'HR', 'IT', 'HR']
        })

    def test_get_descriptive_stats(self):
        stats = self.aservice.get_descriptive_stats(self.test_data, 'salary')
        self.assertIn('mean', stats)
        self.assertIn('median', stats)
        self.assertIn('std', stats)
        self.assertEqual(stats['count'], 6)

    def test_get_frequency_analysis(self):
        freq = self.aservice.get_frequency_analysis(self.test_data, 'department')
        self.assertEqual(len(freq), 2)  # IT和HR两个部门
        self.assertIn('count', freq.columns)
        self.assertIn('percentage', freq.columns)

    def test_get_grouped_stats(self):
        grouped = self.aservice.get_grouped_stats(self.test_data, 'department', 'salary')
        self.assertEqual(len(grouped), 2)
        self.assertIn('mean', grouped.columns)

    def test_get_correlation_matrix(self):
        corr = self.aservice.get_correlation_matrix(self.test_data)
        self.assertEqual(corr.shape, (2, 2))  # salary和age

    def test_compare_by_dimension(self):
        comparison = self.aservice.compare_by_dimension(self.test_data, 'department', 'salary')
        self.assertEqual(len(comparison), 2)
        self.assertIn('平均薪资', comparison.columns)


class TestVisualizationService(unittest.TestCase):
    """测试可视化服务"""

    def setUp(self):
        self.vs = VisualizationService()

    def test_create_bar_chart(self):
        fig = self.vs.create_bar_chart(
            x_data=['A', 'B', 'C'],
            y_data=[10, 20, 30],
            title='Test Bar Chart'
        )
        self.assertIsNotNone(fig)

    def test_create_pie_chart(self):
        fig = self.vs.create_pie_chart(
            data=[30, 40, 30],
            labels=['A', 'B', 'C'],
            title='Test Pie Chart'
        )
        self.assertIsNotNone(fig)

    def test_create_histogram(self):
        data = np.random.normal(100, 15, 100)
        fig = self.vs.create_histogram(data, bins=10, title='Test Histogram')
        self.assertIsNotNone(fig)


class TestExceptions(unittest.TestCase):
    """测试异常类"""

    def test_exception_hierarchy(self):
        self.assertTrue(issubclass(DataLoadError, Exception))
        self.assertTrue(issubclass(DataProcessError, Exception))
        self.assertTrue(issubclass(DataAnalysisError, Exception))


if __name__ == '__main__':
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestDataManager))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigManager))
    suite.addTests(loader.loadTestsFromTestCase(TestDataService))
    suite.addTests(loader.loadTestsFromTestCase(TestProcessingService))
    suite.addTests(loader.loadTestsFromTestCase(TestAnalysisService))
    suite.addTests(loader.loadTestsFromTestCase(TestVisualizationService))
    suite.addTests(loader.loadTestsFromTestCase(TestExceptions))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 输出结果
    if result.wasSuccessful():
        print("\n✅ 所有测试通过!")
    else:
        print("\n❌ 部分测试失败!")
        sys.exit(1)
