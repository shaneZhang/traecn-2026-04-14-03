import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Tuple
from matplotlib.figure import Figure
import platform


if platform.system() == 'Darwin':
    plt.rcParams['font.sans-serif'] = ['PingFang SC', 'Hiragino Sans GB', 'Heiti SC', 'Arial Unicode MS', 'sans-serif']
elif platform.system() == 'Windows':
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial', 'sans-serif']
else:
    plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'SimHei', 'sans-serif']

plt.rcParams['axes.unicode_minus'] = False


class VisualizerCore:
    def __init__(self):
        self.config = {
            'figure_size': (10, 6),
            'dpi': 100,
            'title_fontsize': 14,
            'label_fontsize': 12,
            'tick_fontsize': 10,
            'legend_fontsize': 10,
            'colors': ['#3498db', '#e74c3c', '#2ecc71', '#f39c12',
                      '#9b59b6', '#1abc9c', '#e67e22', '#34495e']
        }

    def create_figure(self, figsize: Tuple[float, float] = None, dpi: int = None) -> Figure:
        if figsize is None:
            figsize = self.config['figure_size']
        if dpi is None:
            dpi = self.config['dpi']
        return Figure(figsize=figsize, dpi=dpi)

    def create_bar_chart(self, figure: Figure, x_data: List, y_data: List,
                         title: str = '', xlabel: str = '', ylabel: str = '',
                         labels: Optional[List[str]] = None,
                         color: Optional[str] = None,
                         horizontal: bool = False) -> Figure:
        figure.clf()
        ax = figure.add_subplot(111)

        if color is None:
            color = self.config['colors'][0]

        if horizontal:
            bars = ax.barh(x_data, y_data, color=color, edgecolor='white')
            ax.invert_yaxis()
        else:
            bars = ax.bar(x_data, y_data, color=color, edgecolor='white')

        if labels:
            for bar, label in zip(bars, labels):
                if horizontal:
                    ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                           f'{label}', va='center', fontsize=self.config['tick_fontsize'])
                else:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2, height,
                           f'{label}', ha='center', va='bottom', fontsize=self.config['tick_fontsize'])

        ax.set_title(title, fontsize=self.config['title_fontsize'], pad=10)
        ax.set_xlabel(xlabel, fontsize=self.config['label_fontsize'])
        ax.set_ylabel(ylabel, fontsize=self.config['label_fontsize'])
        ax.tick_params(axis='both', labelsize=self.config['tick_fontsize'])

        figure.tight_layout()
        return figure

    def create_line_chart(self, figure: Figure, x_data: List, y_data_list: List[List],
                          title: str = '', xlabel: str = '', ylabel: str = '',
                          labels: Optional[List[str]] = None,
                          colors: Optional[List[str]] = None,
                          marker: str = 'o') -> Figure:
        figure.clf()
        ax = figure.add_subplot(111)

        if colors is None:
            colors = self.config['colors']

        for i, y_data in enumerate(y_data_list):
            label = labels[i] if labels and i < len(labels) else None
            color = colors[i % len(colors)]
            ax.plot(x_data, y_data, marker=marker, label=label, color=color, linewidth=2, markersize=6)

        ax.set_title(title, fontsize=self.config['title_fontsize'], pad=10)
        ax.set_xlabel(xlabel, fontsize=self.config['label_fontsize'])
        ax.set_ylabel(ylabel, fontsize=self.config['label_fontsize'])
        ax.tick_params(axis='both', labelsize=self.config['tick_fontsize'])

        if labels:
            ax.legend(fontsize=self.config['legend_fontsize'], loc='best')

        ax.grid(True, linestyle='--', alpha=0.7)
        figure.tight_layout()
        return figure

    def create_pie_chart(self, figure: Figure, data: List, labels: List[str],
                         title: str = '', colors: Optional[List[str]] = None,
                         explode: Optional[List[float]] = None,
                         autopct: str = '%1.1f%%') -> Figure:
        figure.clf()
        ax = figure.add_subplot(111)

        if colors is None:
            colors = self.config['colors'][:len(data)]

        wedges, texts, autotexts = ax.pie(
            data, labels=labels, colors=colors,
            explode=explode, autopct=autopct,
            startangle=90, pctdistance=0.75
        )

        for autotext in autotexts:
            autotext.set_fontsize(self.config['tick_fontsize'])
            autotext.set_color('white')
            autotext.set_weight('bold')

        ax.set_title(title, fontsize=self.config['title_fontsize'], pad=10)
        figure.tight_layout()
        return figure

    def create_scatter_chart(self, figure: Figure, x_data: List, y_data: List,
                             title: str = '', xlabel: str = '', ylabel: str = '',
                             color: Optional[str] = None, size: float = 50,
                             alpha: float = 0.6) -> Figure:
        figure.clf()
        ax = figure.add_subplot(111)

        if color is None:
            color = self.config['colors'][0]

        valid_data = [(x, y) for x, y in zip(x_data, y_data) if pd.notna(x) and pd.notna(y)]
        if len(valid_data) < 2:
            ax.set_title('数据不足，无法绘制散点图', fontsize=self.config['title_fontsize'])
            figure.tight_layout()
            return figure

        x_clean = [d[0] for d in valid_data]
        y_clean = [d[1] for d in valid_data]

        ax.scatter(x_clean, y_clean, c=color, s=size, alpha=alpha, edgecolors='white')

        if len(x_clean) >= 2:
            try:
                z = np.polyfit(x_clean, y_clean, 1)
                p = np.poly1d(z)
                x_sorted = sorted(x_clean)
                ax.plot(x_sorted, p(x_sorted), "r--", alpha=0.8, linewidth=2, label='Trend Line')
                ax.legend(fontsize=self.config['legend_fontsize'])
            except np.linalg.LinAlgError:
                pass

        ax.set_title(title, fontsize=self.config['title_fontsize'], pad=10)
        ax.set_xlabel(xlabel, fontsize=self.config['label_fontsize'])
        ax.set_ylabel(ylabel, fontsize=self.config['label_fontsize'])
        ax.tick_params(axis='both', labelsize=self.config['tick_fontsize'])
        ax.grid(True, linestyle='--', alpha=0.7)

        figure.tight_layout()
        return figure

    def create_boxplot(self, figure: Figure, data_dict: Dict[str, List],
                       title: str = '', xlabel: str = '', ylabel: str = '') -> Figure:
        figure.clf()
        ax = figure.add_subplot(111)

        labels = list(data_dict.keys())
        data = list(data_dict.values())

        bp = ax.boxplot(data, labels=labels, patch_artist=True)

        for patch, color in zip(bp['boxes'], self.config['colors'][:len(labels)]):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        for median in bp['medians']:
            median.set_color('red')
            median.set_linewidth(2)

        ax.set_title(title, fontsize=self.config['title_fontsize'], pad=10)
        ax.set_xlabel(xlabel, fontsize=self.config['label_fontsize'])
        ax.set_ylabel(ylabel, fontsize=self.config['label_fontsize'])
        ax.tick_params(axis='both', labelsize=self.config['tick_fontsize'])
        ax.grid(True, linestyle='--', alpha=0.7, axis='y')

        figure.tight_layout()
        return figure

    def create_histogram(self, figure: Figure, data: List, bins: int = 30,
                         title: str = '', xlabel: str = '', ylabel: str = 'Frequency',
                         color: Optional[str] = None) -> Figure:
        figure.clf()
        ax = figure.add_subplot(111)

        if color is None:
            color = self.config['colors'][0]

        ax.hist(data, bins=bins, color=color, edgecolor='white', alpha=0.7)

        ax.set_title(title, fontsize=self.config['title_fontsize'], pad=10)
        ax.set_xlabel(xlabel, fontsize=self.config['label_fontsize'])
        ax.set_ylabel(ylabel, fontsize=self.config['label_fontsize'])
        ax.tick_params(axis='both', labelsize=self.config['tick_fontsize'])

        figure.tight_layout()
        return figure

    def create_heatmap(self, figure: Figure, data: pd.DataFrame,
                       title: str = '', cmap: str = 'YlOrRd',
                       annot: bool = True) -> Figure:
        figure.clf()
        ax = figure.add_subplot(111)

        im = ax.imshow(data.values, cmap=cmap, aspect='auto')

        ax.set_xticks(np.arange(len(data.columns)))
        ax.set_yticks(np.arange(len(data.index)))
        ax.set_xticklabels(data.columns, rotation=45, ha='right')
        ax.set_yticklabels(data.index)

        if annot:
            for i in range(len(data.index)):
                for j in range(len(data.columns)):
                    ax.text(j, i, f'{data.values[i, j]:.2f}',
                           ha="center", va="center", color="black", fontsize=8)

        ax.set_title(title, fontsize=self.config['title_fontsize'], pad=10)

        cbar = figure.colorbar(im, ax=ax)
        cbar.ax.tick_params(labelsize=self.config['tick_fontsize'])

        figure.tight_layout()
        return figure

    def save_figure(self, figure: Figure, output_path: str,
                    dpi: int = 300, format: str = 'png') -> bool:
        try:
            figure.savefig(output_path, dpi=dpi, format=format,
                          bbox_inches='tight', facecolor='white')
            return True
        except Exception:
            return False
