import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Tuple, Any
import platform

from ..utils.exceptions import VisualizationError
from ..models.logger import Logger


if platform.system() == 'Darwin':
    plt.rcParams['font.sans-serif'] = ['PingFang SC', 'Hiragino Sans GB', 'Heiti SC', 'Arial Unicode MS', 'sans-serif']
elif platform.system() == 'Windows':
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial', 'sans-serif']
else:
    plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'SimHei', 'sans-serif']

plt.rcParams['axes.unicode_minus'] = False


class VisualizationService:
    def __init__(self):
        self.logger = Logger.get_instance()
        self.chart_config = {
            'figure_size': (10, 6),
            'dpi': 100,
            'title_fontsize': 14,
            'label_fontsize': 12,
            'tick_fontsize': 10,
            'legend_fontsize': 10,
            'colors': ['#3498db', '#e74c3c', '#2ecc71', '#f39c12',
                      '#9b59b6', '#1abc9c', '#e67e22', '#34495e']
        }

    def create_figure(self, figsize: Optional[Tuple[float, float]] = None, dpi: int = None) -> Figure:
        if figsize is None:
            figsize = self.chart_config['figure_size']
        if dpi is None:
            dpi = self.chart_config['dpi']
        
        return Figure(figsize=figsize, dpi=dpi)

    def create_bar_chart(self, x_data: List, y_data: List,
                        title: str = '', xlabel: str = '', ylabel: str = '',
                        labels: Optional[List[str]] = None,
                        color: Optional[str] = None,
                        horizontal: bool = False) -> Figure:
        try:
            fig = self.create_figure()
            ax = fig.add_subplot(111)
            
            if color is None:
                color = self.chart_config['colors'][0]
            
            if horizontal:
                bars = ax.barh(x_data, y_data, color=color, edgecolor='white')
            else:
                bars = ax.bar(x_data, y_data, color=color, edgecolor='white')
            
            if labels:
                for bar, label in zip(bars, labels):
                    if horizontal:
                        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                               f'{label}', va='center', fontsize=self.chart_config['tick_fontsize'])
                    else:
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width()/2, height,
                               f'{label}', ha='center', va='bottom', fontsize=self.chart_config['tick_fontsize'])
            
            ax.set_title(title, fontsize=self.chart_config['title_fontsize'], pad=10)
            ax.set_xlabel(xlabel, fontsize=self.chart_config['label_fontsize'])
            ax.set_ylabel(ylabel, fontsize=self.chart_config['label_fontsize'])
            ax.tick_params(axis='both', labelsize=self.chart_config['tick_fontsize'])
            
            if horizontal:
                ax.invert_yaxis()
            
            fig.tight_layout()
            return fig
        except Exception as e:
            self.logger.error(f"创建柱状图失败: {str(e)}")
            raise VisualizationError(f"创建柱状图失败: {str(e)}")

    def create_line_chart(self, x_data: List, y_data_list: List[List],
                         title: str = '', xlabel: str = '', ylabel: str = '',
                         labels: Optional[List[str]] = None,
                         colors: Optional[List[str]] = None,
                         marker: str = 'o') -> Figure:
        try:
            fig = self.create_figure()
            ax = fig.add_subplot(111)
            
            if colors is None:
                colors = self.chart_config['colors']
            
            for i, y_data in enumerate(y_data_list):
                label = labels[i] if labels and i < len(labels) else None
                color = colors[i % len(colors)]
                ax.plot(x_data, y_data, marker=marker, label=label, color=color, linewidth=2, markersize=6)
            
            ax.set_title(title, fontsize=self.chart_config['title_fontsize'], pad=10)
            ax.set_xlabel(xlabel, fontsize=self.chart_config['label_fontsize'])
            ax.set_ylabel(ylabel, fontsize=self.chart_config['label_fontsize'])
            ax.tick_params(axis='both', labelsize=self.chart_config['tick_fontsize'])
            
            if labels:
                ax.legend(fontsize=self.chart_config['legend_fontsize'], loc='best')
            
            ax.grid(True, linestyle='--', alpha=0.7)
            fig.tight_layout()
            return fig
        except Exception as e:
            self.logger.error(f"创建折线图失败: {str(e)}")
            raise VisualizationError(f"创建折线图失败: {str(e)}")

    def create_pie_chart(self, data: List, labels: List[str],
                        title: str = '',
                        colors: Optional[List[str]] = None,
                        explode: Optional[List[float]] = None,
                        autopct: str = '%1.1f%%') -> Figure:
        try:
            fig = self.create_figure()
            ax = fig.add_subplot(111)
            
            if colors is None:
                colors = self.chart_config['colors'][:len(data)]
            
            wedges, texts, autotexts = ax.pie(data, labels=labels, colors=colors,
                                              explode=explode, autopct=autopct,
                                              startangle=90, pctdistance=0.75)
            
            for autotext in autotexts:
                autotext.set_fontsize(self.chart_config['tick_fontsize'])
                autotext.set_color('white')
                autotext.set_weight('bold')
            
            ax.set_title(title, fontsize=self.chart_config['title_fontsize'], pad=10)
            fig.tight_layout()
            return fig
        except Exception as e:
            self.logger.error(f"创建饼图失败: {str(e)}")
            raise VisualizationError(f"创建饼图失败: {str(e)}")

    def create_scatter_chart(self, x_data: List, y_data: List,
                            title: str = '', xlabel: str = '', ylabel: str = '',
                            color: Optional[str] = None,
                            size: float = 50,
                            alpha: float = 0.6) -> Figure:
        try:
            fig = self.create_figure()
            ax = fig.add_subplot(111)
            
            if color is None:
                color = self.chart_config['colors'][0]
            
            valid_data = [(x, y) for x, y in zip(x_data, y_data) if pd.notna(x) and pd.notna(y)]
            if len(valid_data) < 2:
                ax.set_title('数据不足，无法绘制散点图', fontsize=self.chart_config['title_fontsize'])
                fig.tight_layout()
                return fig
            
            x_clean = [d[0] for d in valid_data]
            y_clean = [d[1] for d in valid_data]
            
            ax.scatter(x_clean, y_clean, c=color, s=size, alpha=alpha, edgecolors='white')
            
            if len(x_clean) >= 2:
                try:
                    z = np.polyfit(x_clean, y_clean, 1)
                    p = np.poly1d(z)
                    x_sorted = sorted(x_clean)
                    ax.plot(x_sorted, p(x_sorted), "r--", alpha=0.8, linewidth=2, label='Trend Line')
                    ax.legend(fontsize=self.chart_config['legend_fontsize'])
                except np.linalg.LinAlgError:
                    pass
            
            ax.set_title(title, fontsize=self.chart_config['title_fontsize'], pad=10)
            ax.set_xlabel(xlabel, fontsize=self.chart_config['label_fontsize'])
            ax.set_ylabel(ylabel, fontsize=self.chart_config['label_fontsize'])
            ax.tick_params(axis='both', labelsize=self.chart_config['tick_fontsize'])
            ax.grid(True, linestyle='--', alpha=0.7)
            fig.tight_layout()
            return fig
        except Exception as e:
            self.logger.error(f"创建散点图失败: {str(e)}")
            raise VisualizationError(f"创建散点图失败: {str(e)}")

    def create_boxplot(self, data_dict: Dict[str, List],
                      title: str = '', xlabel: str = '', ylabel: str = '') -> Figure:
        try:
            fig = self.create_figure()
            ax = fig.add_subplot(111)
            
            labels = list(data_dict.keys())
            data = list(data_dict.values())
            
            bp = ax.boxplot(data, labels=labels, patch_artist=True)
            
            for patch, color in zip(bp['boxes'], self.chart_config['colors'][:len(labels)]):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)
            
            for median in bp['medians']:
                median.set_color('red')
                median.set_linewidth(2)
            
            ax.set_title(title, fontsize=self.chart_config['title_fontsize'], pad=10)
            ax.set_xlabel(xlabel, fontsize=self.chart_config['label_fontsize'])
            ax.set_ylabel(ylabel, fontsize=self.chart_config['label_fontsize'])
            ax.tick_params(axis='both', labelsize=self.chart_config['tick_fontsize'])
            ax.grid(True, linestyle='--', alpha=0.7, axis='y')
            fig.tight_layout()
            return fig
        except Exception as e:
            self.logger.error(f"创建箱线图失败: {str(e)}")
            raise VisualizationError(f"创建箱线图失败: {str(e)}")

    def create_histogram(self, data: List, bins: int = 30,
                        title: str = '', xlabel: str = '', ylabel: str = 'Frequency',
                        color: Optional[str] = None,
                        kde: bool = False) -> Figure:
        try:
            fig = self.create_figure()
            ax = fig.add_subplot(111)
            
            if color is None:
                color = self.chart_config['colors'][0]
            
            n, bins_edges, patches = ax.hist(data, bins=bins, color=color,
                                             edgecolor='white', alpha=0.7)
            
            if kde:
                from scipy import stats
                kde_x = np.linspace(min(data), max(data), 100)
                kde_y = stats.gaussian_kde(data)(kde_x)
                ax2 = ax.twinx()
                ax2.plot(kde_x, kde_y, 'r-', linewidth=2, label='KDE')
                ax2.set_ylabel('Density', fontsize=self.chart_config['label_fontsize'])
                ax2.legend(fontsize=self.chart_config['legend_fontsize'])
            
            ax.set_title(title, fontsize=self.chart_config['title_fontsize'], pad=10)
            ax.set_xlabel(xlabel, fontsize=self.chart_config['label_fontsize'])
            ax.set_ylabel(ylabel, fontsize=self.chart_config['label_fontsize'])
            ax.tick_params(axis='both', labelsize=self.chart_config['tick_fontsize'])
            fig.tight_layout()
            return fig
        except Exception as e:
            self.logger.error(f"创建直方图失败: {str(e)}")
            raise VisualizationError(f"创建直方图失败: {str(e)}")

    def create_heatmap(self, data: pd.DataFrame,
                      title: str = '',
                      cmap: str = 'YlOrRd',
                      annot: bool = True) -> Figure:
        try:
            fig = self.create_figure()
            ax = fig.add_subplot(111)
            
            im = ax.imshow(data.values, cmap=cmap, aspect='auto')
            
            ax.set_xticks(np.arange(len(data.columns)))
            ax.set_yticks(np.arange(len(data.index)))
            ax.set_xticklabels(data.columns, rotation=45, ha='right')
            ax.set_yticklabels(data.index)
            
            if annot:
                for i in range(len(data.index)):
                    for j in range(len(data.columns)):
                        text = ax.text(j, i, f'{data.values[i, j]:.2f}',
                                      ha="center", va="center", color="black", fontsize=8)
            
            ax.set_title(title, fontsize=self.chart_config['title_fontsize'], pad=10)
            cbar = fig.colorbar(im, ax=ax)
            cbar.ax.tick_params(labelsize=self.chart_config['tick_fontsize'])
            fig.tight_layout()
            return fig
        except Exception as e:
            self.logger.error(f"创建热力图失败: {str(e)}")
            raise VisualizationError(f"创建热力图失败: {str(e)}")

    def create_comparison_chart(self, data: pd.DataFrame,
                               dimension_col: str,
                               salary_col: str = 'pre_tax_salary',
                               chart_type: str = 'bar') -> Figure:
        try:
            grouped = data.groupby(dimension_col)[salary_col].mean().sort_values(ascending=False)
            
            if chart_type == 'bar':
                return self.create_bar_chart(
                    x_data=grouped.index.tolist(),
                    y_data=grouped.values.tolist(),
                    title=f'{dimension_col} - 平均薪资对比',
                    xlabel=dimension_col,
                    ylabel='平均薪资',
                    color=self.chart_config['colors'][0]
                )
            elif chart_type == 'horizontal':
                return self.create_bar_chart(
                    x_data=grouped.index.tolist(),
                    y_data=grouped.values.tolist(),
                    title=f'{dimension_col} - 平均薪资对比',
                    xlabel='平均薪资',
                    ylabel=dimension_col,
                    horizontal=True,
                    color=self.chart_config['colors'][0]
                )
            else:
                raise VisualizationError(f"不支持的图表类型: {chart_type}")
        except Exception as e:
            self.logger.error(f"创建对比图表失败: {str(e)}")
            raise VisualizationError(f"创建对比图表失败: {str(e)}")

    def create_trend_chart(self, data: pd.DataFrame,
                          time_col: str,
                          salary_col: str = 'pre_tax_salary') -> Figure:
        try:
            trend = data.groupby(time_col)[salary_col].agg(['mean', 'median', 'count']).reset_index()
            
            x_data = trend[time_col].tolist()
            y_mean = trend['mean'].tolist()
            y_median = trend['median'].tolist()
            
            return self.create_line_chart(
                x_data=x_data,
                y_data_list=[y_mean, y_median],
                title='薪资趋势变化',
                xlabel=time_col,
                ylabel='薪资',
                labels=['平均薪资', '中位薪资']
            )
        except Exception as e:
            self.logger.error(f"创建趋势图失败: {str(e)}")
            raise VisualizationError(f"创建趋势图失败: {str(e)}")

    def create_salary_distribution_chart(self, data: pd.DataFrame,
                                        salary_col: str = 'pre_tax_salary',
                                        group_col: Optional[str] = None) -> Figure:
        try:
            if group_col and group_col in data.columns:
                box_data = {}
                for cat in data[group_col].unique():
                    values = data[data[group_col] == cat][salary_col].dropna().values
                    if len(values) > 0:
                        box_data[str(cat)] = values
                
                if box_data:
                    return self.create_boxplot(
                        data_dict=box_data,
                        title=f'{group_col} - 薪资分布',
                        xlabel=group_col,
                        ylabel='薪资'
                    )
            
            salary_data = data[salary_col].dropna().values
            return self.create_histogram(
                data=salary_data,
                bins=20,
                title='薪资分布直方图',
                xlabel='薪资'
            )
        except Exception as e:
            self.logger.error(f"创建薪资分布图失败: {str(e)}")
            raise VisualizationError(f"创建薪资分布图失败: {str(e)}")

    def save_chart(self, figure: Figure, output_path: str, dpi: int = 300, format: str = 'png'):
        try:
            figure.savefig(output_path, dpi=dpi, format=format,
                          bbox_inches='tight', facecolor='white')
            self.logger.info(f"图表已保存到: {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"保存图表失败: {str(e)}")
            raise VisualizationError(f"保存图表失败: {str(e)}")

    def set_color_scheme(self, colors: List[str]):
        self.chart_config['colors'] = colors

    def set_figure_size(self, width: float, height: float):
        self.chart_config['figure_size'] = (width, height)

    def set_dpi(self, dpi: int):
        self.chart_config['dpi'] = dpi
