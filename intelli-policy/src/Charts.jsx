import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Bar, Pie, Line } from 'react-chartjs-2';

// 注册 Chart.js 组件 
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend
);

/**
 * 补贴占比饼图
 */
export const SubsidyPieChart = ({ recommendation }) => {
  if (!recommendation || !recommendation.selected_products) return null;

  const products = recommendation.selected_products;
  const labels = products.map(p => p.name);
  const subsidies = products.map(p => p.subsidy);

  const data = {
    labels,
    datasets: [{
      label: '补贴金额',
      data: subsidies,
      backgroundColor: [
        'rgba(59, 130, 246, 0.8)',   // blue-500
        'rgba(99, 102, 241, 0.8)',   // indigo-500
        'rgba(139, 92, 246, 0.8)',   // violet-500
        'rgba(236, 72, 153, 0.8)',   // pink-500
        'rgba(251, 146, 60, 0.8)',   // orange-500
        'rgba(34, 197, 94, 0.8)',    // green-500
      ],
      borderColor: [
        'rgba(59, 130, 246, 1)',
        'rgba(99, 102, 241, 1)',
        'rgba(139, 92, 246, 1)',
        'rgba(236, 72, 153, 1)',
        'rgba(251, 146, 60, 1)',
        'rgba(34, 197, 94, 1)',
      ],
      borderWidth: 2
    }]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          padding: 15,
          font: {
            size: 12
          }
        }
      },
      title: {
        display: true,
        text: '补贴占比分析',
        font: {
          size: 16,
          weight: 'bold'
        },
        padding: 20
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const value = context.parsed;
            const total = context.dataset.data.reduce((a, b) => a + b, 0);
            const percentage = ((value / total) * 100).toFixed(1);
            return `${context.label}: ¥${value} (${percentage}%)`;
          }
        }
      }
    }
  };

  return (
    <div className="w-full h-64">
      <Pie data={data} options={options} />
    </div>
  );
};

/**
 * 价格对比柱状图
 */
export const PriceComparisonChart = ({ recommendation, priceComparison }) => {
  if (!recommendation || !recommendation.selected_products) return null;

  const products = recommendation.selected_products;
  const labels = products.map(p => p.name);
  const prices = products.map(p => p.price);
  const subsidies = products.map(p => p.subsidy);
  const actualPrices = products.map(p => p.price - p.subsidy);

  // 如果有价格比较数据，添加电商价格
  let jdPrices = null;
  if (priceComparison && priceComparison.comparisons) {
    jdPrices = priceComparison.comparisons.map(c => c.jd_price);
  }

  const datasets = [
    {
      label: '原价',
      data: prices,
      backgroundColor: 'rgba(148, 163, 184, 0.8)', // slate-400
      borderColor: 'rgba(148, 163, 184, 1)',
      borderWidth: 2
    },
    {
      label: '实付价',
      data: actualPrices,
      backgroundColor: 'rgba(34, 197, 94, 0.8)', // green-500
      borderColor: 'rgba(34, 197, 94, 1)',
      borderWidth: 2
    },
    {
      label: '补贴',
      data: subsidies,
      backgroundColor: 'rgba(59, 130, 246, 0.8)', // blue-500
      borderColor: 'rgba(59, 130, 246, 1)',
      borderWidth: 2
    }
  ];

  if (jdPrices) {
    datasets.push({
      label: '京东价格',
      data: jdPrices,
      backgroundColor: 'rgba(239, 68, 68, 0.5)', // red-500
      borderColor: 'rgba(239, 68, 68, 1)',
      borderWidth: 2,
      borderDash: [5, 5]
    });
  }

  const data = {
    labels,
    datasets
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          padding: 15,
          font: {
            size: 12
          }
        }
      },
      title: {
        display: true,
        text: '价格对比分析',
        font: {
          size: 16,
          weight: 'bold'
        },
        padding: 20
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            return `${context.dataset.label}: ¥${context.parsed.y}`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: (value) => `¥${value}`
        }
      }
    }
  };

  return (
    <div className="w-full h-80">
      <Bar data={data} options={options} />
    </div>
  );
};

/**
 * 资金利用率折线图
 */
export const UtilizationChart = ({ recommendation }) => {
  if (!recommendation) return null;

  const utilizationRate = (recommendation.utilization_rate * 100).toFixed(1);
  
  const data = {
    labels: ['预算', '实际花费', '补贴后花费'],
    datasets: [{
      label: '金额 (元)',
      data: [
        recommendation.budget || 0,
        recommendation.total_cost || 0,
        recommendation.final_cost || 0
      ],
      borderColor: 'rgba(59, 130, 246, 1)',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      tension: 0.4,
      fill: true,
      pointRadius: 6,
      pointHoverRadius: 8,
      pointBackgroundColor: 'rgba(59, 130, 246, 1)',
      pointBorderColor: '#fff',
      pointBorderWidth: 2
    }]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      title: {
        display: true,
        text: `资金利用率: ${utilizationRate}%`,
        font: {
          size: 16,
          weight: 'bold'
        },
        padding: 20
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            return `金额: ¥${context.parsed.y}`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: (value) => `¥${value}`
        }
      }
    }
  };

  return (
    <div className="w-full h-64">
      <Line data={data} options={options} />
    </div>
  );
};

/**
 * 完整的可视化面板
 */
export const VisualizationPanel = ({ recommendation, priceComparison }) => {
  if (!recommendation || !recommendation.selected_products || recommendation.selected_products.length === 0) {
    return null;
  }

  return (
    <div className="mt-6 space-y-6">
      {/* 标题 */}
      <div className="flex items-center gap-2 text-slate-700">
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        <h3 className="font-bold text-lg">数据可视化分析</h3>
      </div>

      {/* 图表网格 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* 价格对比 */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <PriceComparisonChart 
            recommendation={recommendation} 
            priceComparison={priceComparison}
          />
        </div>

        {/* 补贴占比 */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <SubsidyPieChart recommendation={recommendation} />
        </div>

        {/* 资金利用率 - 占满一行 */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm md:col-span-2">
          <UtilizationChart recommendation={recommendation} />
        </div>
      </div>
    </div>
  );
};
