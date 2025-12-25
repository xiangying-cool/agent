"""
数据可视化代码生成器 - 自动生成图表代码
根据数据自动选择合适的图表类型并生成代码
"""
from typing import Dict, List, Any
import json


class VizCodeGenerator:
    """可视化代码生成器"""
    
    def __init__(self):
        # 图表类型推荐规则
        self.chart_rules = {
            "comparison": {  # 对比类
                "types": ["bar", "column"],
                "use_case": "比较不同类别的数值"
            },
            "proportion": {  # 占比类
                "types": ["pie", "donut"],
                "use_case": "展示部分与整体的关系"
            },
            "trend": {  # 趋势类
                "types": ["line", "area"],
                "use_case": "展示数据随时间的变化"
            },
            "distribution": {  # 分布类
                "types": ["histogram", "scatter"],
                "use_case": "展示数据的分布情况"
            }
        }
    
    def generate(self, data: Dict, chart_type: str = "auto") -> Dict:
        """
        生成可视化代码
        
        Args:
            data: {
                "title": "图表标题",
                "labels": ["标签1", "标签2", ...],
                "datasets": [
                    {
                        "label": "数据集名称",
                        "data": [1, 2, 3, ...]
                    }
                ],
                "type": "bar/pie/line"  # 可选，不提供则自动推荐
            }
            chart_type: 指定图表类型或"auto"自动选择
        
        Returns:
            {
                "chart_type": "推荐的图表类型",
                "code": {
                    "python": "Python代码",
                    "javascript": "JS代码",
                    "config": "配置对象"
                },
                "description": "图表说明"
            }
        """
        # 自动推荐图表类型
        if chart_type == "auto":
            chart_type = self._recommend_chart_type(data)
        
        # 生成代码
        python_code = self._generate_python_code(data, chart_type)
        js_code = self._generate_js_code(data, chart_type)
        config = self._generate_config(data, chart_type)
        
        return {
            "chart_type": chart_type,
            "code": {
                "python": python_code,
                "javascript": js_code,
                "config": config
            },
            "description": self._generate_description(data, chart_type)
        }
    
    def _recommend_chart_type(self, data: Dict) -> str:
        """推荐图表类型"""
        labels = data.get("labels", [])
        datasets = data.get("datasets", [])
        
        if not datasets:
            return "bar"
        
        # 规则1: 如果只有一个数据集且标签数量<=6，推荐饼图
        if len(datasets) == 1 and len(labels) <= 6:
            return "pie"
        
        # 规则2: 如果标签是时间序列，推荐折线图
        if self._is_time_series(labels):
            return "line"
        
        # 规则3: 默认柱状图
        return "bar"
    
    def _is_time_series(self, labels: List) -> bool:
        """判断是否为时间序列"""
        time_keywords = ["年", "月", "日", "季度", "周"]
        if not labels:
            return False
        return any(keyword in str(labels[0]) for keyword in time_keywords)
    
    def _generate_python_code(self, data: Dict, chart_type: str) -> str:
        """生成Python代码（matplotlib）"""
        title = data.get("title", "数据可视化")
        labels = data.get("labels", [])
        datasets = data.get("datasets", [])
        
        code = f"""import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 中文字体
matplotlib.rcParams['axes.unicode_minus'] = False  # 负号显示

# 数据
labels = {labels}
"""
        
        if chart_type == "pie":
            if datasets:
                values = datasets[0].get("data", [])
                code += f"""values = {values}

# 创建饼图
plt.figure(figsize=(8, 6))
plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
plt.title('{title}')
plt.axis('equal')
plt.tight_layout()
plt.show()
"""
        
        elif chart_type == "line":
            code += f"""
# 创建折线图
plt.figure(figsize=(10, 6))
"""
            for ds in datasets:
                label = ds.get("label", "数据")
                values = ds.get("data", [])
                code += f"plt.plot(labels, {values}, marker='o', label='{label}')\n"
            
            code += f"""plt.title('{title}')
plt.xlabel('类别')
plt.ylabel('数值')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
"""
        
        else:  # bar
            code += f"""
# 创建柱状图
plt.figure(figsize=(10, 6))
"""
            if len(datasets) == 1:
                values = datasets[0].get("data", [])
                code += f"""plt.bar(labels, {values})
plt.title('{title}')
plt.xlabel('类别')
plt.ylabel('数值')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
"""
            else:
                code += f"""import numpy as np
x = np.arange(len(labels))
width = {0.8 / len(datasets):.2f}

"""
                for i, ds in enumerate(datasets):
                    label = ds.get("label", f"数据{i+1}")
                    values = ds.get("data", [])
                    code += f"plt.bar(x + {i * 0.8 / len(datasets):.2f}, {values}, width, label='{label}')\n"
                
                code += f"""plt.title('{title}')
plt.xlabel('类别')
plt.ylabel('数值')
plt.xticks(x + width * {len(datasets)/2:.1f}, labels)
plt.legend()
plt.tight_layout()
plt.show()
"""
        
        return code
    
    def _generate_js_code(self, data: Dict, chart_type: str) -> str:
        """生成JavaScript代码（Chart.js）"""
        config = self._generate_config(data, chart_type)
        
        code = f"""// Chart.js 配置
const ctx = document.getElementById('myChart').getContext('2d');
const config = {json.dumps(config, ensure_ascii=False, indent=2)};

const myChart = new Chart(ctx, config);
"""
        return code
    
    def _generate_config(self, data: Dict, chart_type: str) -> Dict:
        """生成Chart.js配置对象"""
        title = data.get("title", "数据可视化")
        labels = data.get("labels", [])
        datasets = data.get("datasets", [])
        
        # 准备数据集
        chart_datasets = []
        colors = [
            'rgba(59, 130, 246, 0.8)',   # blue
            'rgba(99, 102, 241, 0.8)',   # indigo
            'rgba(139, 92, 246, 0.8)',   # violet
            'rgba(236, 72, 153, 0.8)',   # pink
            'rgba(251, 146, 60, 0.8)',   # orange
            'rgba(34, 197, 94, 0.8)',    # green
        ]
        
        for i, ds in enumerate(datasets):
            chart_ds = {
                "label": ds.get("label", f"数据{i+1}"),
                "data": ds.get("data", []),
                "backgroundColor": colors[i % len(colors)] if chart_type == "pie" else colors[:len(labels)] if chart_type == "pie" else colors[i % len(colors)],
                "borderColor": colors[i % len(colors)].replace('0.8', '1'),
                "borderWidth": 1
            }
            chart_datasets.append(chart_ds)
        
        config = {
            "type": chart_type,
            "data": {
                "labels": labels,
                "datasets": chart_datasets
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": title
                    },
                    "legend": {
                        "display": True,
                        "position": "top"
                    }
                }
            }
        }
        
        # 根据图表类型添加特定配置
        if chart_type == "line":
            for ds in config["data"]["datasets"]:
                ds["tension"] = 0.1  # 线条平滑度
        
        elif chart_type == "pie":
            config["data"]["datasets"][0]["backgroundColor"] = colors[:len(labels)]
        
        return config
    
    def _generate_description(self, data: Dict, chart_type: str) -> str:
        """生成图表说明"""
        title = data.get("title", "数据可视化")
        labels = data.get("labels", [])
        datasets = data.get("datasets", [])
        
        desc = f"图表类型: {chart_type}\n"
        desc += f"标题: {title}\n"
        desc += f"类别数: {len(labels)}\n"
        desc += f"数据集数: {len(datasets)}\n"
        
        if chart_type == "pie":
            desc += "适用场景: 展示各部分占比关系\n"
        elif chart_type == "line":
            desc += "适用场景: 展示数据趋势变化\n"
        elif chart_type == "bar":
            desc += "适用场景: 对比不同类别的数值\n"
        
        return desc


# 全局实例
viz_code_generator = VizCodeGenerator()


if __name__ == "__main__":
    # 测试可视化代码生成
    generator = VizCodeGenerator()
    
    print("=" * 60)
    print("数据可视化代码生成测试")
    print("=" * 60)
    
    # 测试1: 补贴占比饼图
    print("\n测试1: 补贴占比饼图")
    print("-" * 60)
    data1 = {
        "title": "各类产品补贴占比",
        "labels": ["空调", "冰箱", "洗衣机", "电视"],
        "datasets": [{
            "label": "补贴金额",
            "data": [1200, 800, 600, 400]
        }]
    }
    
    result1 = generator.generate(data1, "auto")
    print(f"推荐图表: {result1['chart_type']}")
    print(f"\n{result1['description']}")
    print(f"\nPython代码预览:\n{result1['code']['python'][:200]}...")
    
    # 测试2: 趋势折线图
    print("\n\n测试2: 补贴趋势折线图")
    print("-" * 60)
    data2 = {
        "title": "月度补贴发放趋势",
        "labels": ["1月", "2月", "3月", "4月", "5月"],
        "datasets": [
            {
                "label": "家电补贴",
                "data": [50, 65, 80, 90, 100]
            },
            {
                "label": "汽车补贴",
                "data": [200, 220, 250, 240, 260]
            }
        ]
    }
    
    result2 = generator.generate(data2, "auto")
    print(f"推荐图表: {result2['chart_type']}")
    print(f"\n{result2['description']}")
    
    # 测试3: 对比柱状图
    print("\n\n测试3: 城市对比柱状图")
    print("-" * 60)
    data3 = {
        "title": "各城市补贴标准对比",
        "labels": ["济南", "青岛", "烟台"],
        "datasets": [
            {
                "label": "一级能效",
                "data": [2000, 1800, 1500]
            },
            {
                "label": "二级能效",
                "data": [1500, 1200, 1000]
            }
        ]
    }
    
    result3 = generator.generate(data3, "bar")
    print(f"图表类型: {result3['chart_type']}")
    config = result3['code']['config']
    print(f"\nChart.js配置预览:")
    print(json.dumps(config, ensure_ascii=False, indent=2)[:300] + "...")
    
    print("\n\n✅ 代码生成测试完成")
