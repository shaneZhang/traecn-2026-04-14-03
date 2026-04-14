# 园区白领薪资数据分析工具

一个基于 Python + Pandas + Matplotlib 开发的桌面应用，用于园区白领薪资数据的导入、分析与可视化。

## 项目简介

本工具专为园区管理方、入驻企业HR及求职人员设计，用于分析园区内白领员工的薪资分布情况、薪酬结构特征以及不同维度下的薪资差异。

## 功能特性

### 数据导入
- 支持读取单个或多个 Excel 文件（.xlsx, .xls）
- 支持从文件夹批量导入 Excel 文件
- 自动识别字段名称并进行映射
- 数据预览与验证

### 数据处理
- 删除重复数据
- 缺失值处理（删除、均值填充、中位数填充等）
- 异常值检测与移除
- 数据分组（年龄分组、薪资分组、工作年限分组）
- 数据筛选与过滤

### 数据分析
- 描述性统计分析（均值、中位数、标准差、最大最小值等）
- 频率分析
- 交叉分析
- 多维度对比分析
- 相关性分析
- 趋势分析

### 数据可视化
- 柱状图（垂直/水平）
- 折线图
- 饼图
- 散点图
- 箱线图
- 直方图
- 支持图表导出（PNG, JPG, PDF）

## 技术栈

| 技术 | 说明 |
|------|------|
| Python | 开发语言 |
| Pandas | 数据处理与分析 |
| Matplotlib | 数据可视化 |
| Tkinter | 桌面GUI框架（Python内置） |
| openpyxl | Excel文件读写 |

## 环境要求

- Python 3.8+
- Windows 10 及以上 / macOS / Linux

## 安装步骤

### 1. 安装 Python

如果尚未安装 Python，请从 [Python 官网](https://www.python.org/downloads/) 下载并安装（建议使用 Python 3.9 或更高版本）。

### 2. 安装依赖

打开终端（命令提示符/Terminal），运行以下命令安装所需依赖：

```bash
pip install pandas matplotlib numpy openpyxl scipy
```

### 3. 验证安装

```bash
python -c "import pandas; import matplotlib; print('安装成功')"
```

## 使用方法

### 启动应用

在项目目录下运行：

```bash
python main.py
```

### 基本操作流程

1. **导入数据**
   - 点击左侧「数据导入」按钮
   - 或点击菜单「文件 -> 打开Excel文件」
   - 选择要分析的 Excel 文件

2. **数据概览**
   - 切换到「数据概览」标签页
   - 查看导入的数据表格

3. **数据分析**
   - 切换到「统计分析」标签页
   - 选择分析维度和薪资字段
   - 点击「执行分析」查看结果

4. **数据可视化**
   - 切换到「可视化」标签页
   - 选择图表类型和分组维度
   - 点击「生成图表」查看可视化结果
   - 可点击「保存图表」导出图片

### Excel 数据格式要求

建议的 Excel 数据格式如下：

| 字段 | 说明 | 示例 |
|------|------|------|
| 姓名 | 员工姓名（可选） | 张三 |
| 性别 | 性别 | 男/女 |
| 年龄 | 年龄 | 28 |
| 学历 | 学历层次 | 本科/硕士 |
| 工作年限 | 工作年限 | 5 |
| 所在行业 | 所属行业 | 互联网/金融 |
| 岗位类型 | 岗位类别 | 技术/产品/运营 |
| 职级 | 职级等级 | 初级/中级/高级 |
| 基本工资 | 基本工资 | 15000 |
| 绩效奖金 | 绩效奖金 | 5000 |
| 补贴总和 | 补贴总和 | 1000 |
| 税前薪资 | 税前薪资总额 | 21000 |
| 税后薪资 | 税后薪资 | 16000 |
| 所属企业规模 | 企业规模 | 大型 |
| 入职年份 | 入职年份 | 2020 |

> 注意：字段名称不区分大小写，系统会自动尝试识别并映射。

### 生成示例数据

如果需要测试数据，可以运行：

```bash
python sample_data_generator.py
```

这将在 `sample_data` 目录下生成一个名为 `薪资数据样本.xlsx` 的测试数据文件。

## 项目结构

```
salary_analysis/
├── main.py                      # 主程序入口
├── sample_data_generator.py    # 示例数据生成器
├── README.md                   # 说明文档
├── requirements.txt            # 依赖列表
├── src/
│   ├── data_loader.py          # 数据导入模块
│   ├── data_processor.py       # 数据处理模块
│   ├── data_analyzer.py        # 数据分析模块
│   └── visualizer.py           # 可视化模块
└── sample_data/                # 示例数据目录
    └── 薪资数据样本.xlsx
```

## 打包发布

### 使用 PyInstaller 打包

1. 安装 PyInstaller：

```bash
pip install pyinstaller
```

2. 打包为可执行文件：

```bash
pyinstaller --onefile --windowed --name SalaryAnalysis main.py
```

3. 打包完成后，可执行文件位于 `dist` 目录下

### 打包参数说明

| 参数 | 说明 |
|------|------|
| --onefile | 打包为单个可执行文件 |
| --windowed | 隐藏控制台窗口（GUI应用） |
| --name | 指定输出文件名 |
| --icon | 指定应用图标（可选） |

## 常见问题

### 1. 图表中文显示乱码

解决方案：
- Windows: 确保系统安装了中文字体，或修改 `visualizer.py` 中的字体设置
- macOS/Linux: 安装中文字体，如 `sudo apt-get install fonts-wqy-microhei`

### 2. Excel 文件读取失败

检查项：
- 确认文件格式为 .xlsx 或 .xls
- 确认文件没有被其他程序打开
- 尝试用 Excel 重新保存文件

### 3. 图表窗口不显示

可能原因：
- 缺少 Tkinter 支持（Windows 通常已内置）
- 尝试重新安装 Python

## 界面预览

应用主界面包含以下区域：

- **左侧菜单栏**：功能导航按钮和数据信息显示
- **数据概览**：表格形式展示导入的数据
- **统计分析**：文本形式展示分析结果
- **可视化**：图表展示区域

## 扩展开发

### 添加新的图表类型

在 `src/visualizer.py` 中添加新的图表方法：

```python
def create_new_chart(self, ...):
    self.clear_figure()
    ax = self.figure.add_subplot(111)
    # 实现图表逻辑
    return self.figure
```

### 添加新的分析功能

在 `src/data_analyzer.py` 中添加新的分析方法：

```python
def new_analysis_method(self, ...):
    # 实现分析逻辑
    return result
```

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。
