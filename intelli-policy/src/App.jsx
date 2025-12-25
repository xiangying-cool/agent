import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { 
  MessageSquare, 
  Calculator, 
  FileText, 
  Send, 
  Sparkles, 
  CheckCircle2, 
  Search,
  ChevronRight,
  ArrowRight,
  Bot,
  User,
  Cpu,
  ShieldCheck,
  Zap,
  Globe,
  X,
  Play,
  Users,
  Layers,
  Database
} from 'lucide-react';
import { VisualizationPanel } from './Charts';

/**
 * 智策通 (IntelliPolicy) - 旗舰演示版 V2.0
 * * 更新日志：
 * 1. 新增：视频播放模态框，点击“查看演示视频”弹出。
 * 2. 新增：首页长滚动布局，增加“核心技术”、“解决方案”、“团队介绍”板块。
 * 3. 交互：顶部导航栏点击可平滑滚动至对应区域。
 */

// --- 模拟数据 (保持不变) ---
const MOCK_POLICIES = [
  { id: 1, title: "国务院关于印发《推动大规模设备更新和消费品以旧换新行动方案》的通知", source: "国务院", date: "2024-03-07", tag: "国家级", status: "执行中" },
  { id: 2, title: "济南市2025年消费品以旧换新实施细则", source: "济南市商务局", date: "2025-01-15", tag: "市级", status: "最新" },
  { id: 3, title: "关于调整汽车以旧换新补贴标准的公告", source: "财政部", date: "2024-04-20", tag: "部委", status: "重要" },
  { id: 4, title: "山东省家电消费补贴实施方案", source: "山东省商务厅", date: "2024-05-10", tag: "省级", status: "执行中" },
];

const CHAT_SCRIPTS = {
  "default": "您好！我是您的智能政策顾问 **“智策通”**。\n\n我已实时连接至 **国家政务服务平台** 及 **济南市大数据局** 政策库。\n您可以问我：\n\n🔹 **想换台空调，一级能效能补多少钱？**\n🔹 **名下旧车报废更新的流程是什么？**\n🔹 **我有1万元预算，怎么买家电组合最划算？**",
  "补贴标准": "已为您检索到 **《济南市2025年消费品以旧换新实施细则》** 第四章内容：\n\n🏠 **家电类补贴标准**：\n- **一级能效**：补贴产品最终销售价格的 **20%**\n- **二级能效**：补贴产品最终销售价格的 **15%**\n\n💰 **补贴上限**：每位消费者每类产品可补贴1件，单件最高不超过 **2000元**。\n\n💡 **智策通提示**：该政策有效期截至2025年12月31日，建议尽早申请。",
  "计算": "正在启动 **【多模态决策优化引擎】** 为您规划...\n\n✅ **最优省钱方案已生成**\n基于您的 **15,000元** 预算，通过对比全网比价与补贴规则，建议组合如下：\n\n1. **一级能效空调 x2** (总价6000，补贴20% → 省1200元)\n2. **一级能效冰箱 x1** (总价6000，补贴20% → 省1200元)\n3. **智能手机 x1** (总价3000，补贴15% → 省450元)\n\n📊 **方案收益分析**：\n- **预计获得总补贴：2,850元**\n- **实际净支出：12,150元**\n\n🚀 **结论**：此方案比普通购买多节省了约 **19%** 的资金，资金利用率极高！"
};

// --- 组件部分 ---

// 视频模态框组件
const VideoModal = ({ isOpen, onClose }) => {
  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/80 backdrop-blur-sm animate-fade-in">
      <div className="bg-black rounded-2xl w-[90%] max-w-4xl aspect-video relative shadow-2xl border border-slate-700">
        <button 
          onClick={onClose}
          className="absolute -top-12 right-0 text-white hover:text-blue-400 transition-colors flex items-center gap-2"
        >
          <span className="text-sm">关闭演示</span>
          <div className="bg-white/10 p-2 rounded-full"><X size={20} /></div>
        </button>
        <div className="w-full h-full flex flex-col items-center justify-center text-slate-500">
          <Play size={64} className="mb-4 opacity-50" />
          <p>此处为演示视频播放区域</p>
          <p className="text-sm text-slate-600">(复赛答辩时可在此插入录制好的 .mp4 文件)</p>
        </div>
      </div>
    </div>
  );
};

// 1. 首页欢迎屏 (功能增强版)
const LandingPage = ({ onStart }) => {
  const [showVideo, setShowVideo] = useState(false);

  // 平滑滚动函数
  const scrollToSection = (id) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col relative font-sans selection:bg-blue-100 overflow-x-hidden">
      {/* 视频弹窗 */}
      <VideoModal isOpen={showVideo} onClose={() => setShowVideo(false)} />

      {/* 动态背景光斑 */}
      <div className="fixed top-[-20%] left-[-10%] w-[50vw] h-[50vw] bg-blue-400/20 rounded-full blur-[120px] animate-pulse pointer-events-none"></div>
      <div className="fixed bottom-[-10%] right-[-5%] w-[40vw] h-[40vw] bg-indigo-400/20 rounded-full blur-[100px] animate-pulse delay-1000 pointer-events-none"></div>
      
      {/* 顶部导航 */}
      <header className="sticky top-0 z-40 bg-white/70 backdrop-blur-md border-b border-slate-200/50">
        <div className="flex justify-between items-center px-8 py-4 max-w-7xl mx-auto w-full">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white shadow-lg shadow-blue-500/30">
              <Cpu size={18} />
            </div>
            <span className="font-bold text-xl text-slate-800 tracking-tight">IntelliPolicy</span>
          </div>
          <div className="flex gap-8 text-sm font-medium text-slate-600">
            <button onClick={() => scrollToSection('tech')} className="hover:text-blue-600 transition-colors">核心技术</button>
            <button onClick={() => scrollToSection('solutions')} className="hover:text-blue-600 transition-colors">解决方案</button>
            <button onClick={() => scrollToSection('team')} className="hover:text-blue-600 transition-colors">关于团队</button>
          </div>
          <button 
            onClick={onStart}
            className="px-5 py-2 bg-slate-900 text-white text-sm font-bold rounded-full hover:bg-blue-600 transition-all hover:shadow-lg"
          >
            进入系统
          </button>
        </div>
      </header>

      {/* Hero 区域 */}
      <section className="relative pt-20 pb-32 flex flex-col items-center justify-center text-center px-4 max-w-5xl mx-auto">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white border border-blue-100 shadow-sm text-blue-600 text-xs font-bold mb-8 animate-fade-in-up">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
          </span>
          全球校园人工智能算法精英大赛 · 参赛作品
        </div>

        <h1 className="text-6xl md:text-7xl font-extrabold text-slate-900 tracking-tight mb-6 animate-fade-in-up delay-100">
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">智策通</span>
        </h1>
        
        <h2 className="text-2xl md:text-3xl font-medium text-slate-600 mb-8 animate-fade-in-up delay-200">
          AI 政策动态咨询智能体
        </h2>

        <p className="text-lg text-slate-500 max-w-2xl mx-auto mb-12 leading-relaxed animate-fade-in-up delay-300">
          基于多模态大模型与 RAG 检索增强生成技术，<br/>
          为您提供 7x24小时 精准、高效的以旧换新政策解读与最优购买决策支持。
        </p>

        <div className="flex flex-col sm:flex-row gap-4 animate-fade-in-up delay-400">
          <button 
            onClick={onStart}
            className="group relative inline-flex items-center justify-center px-8 py-4 text-lg font-bold text-white transition-all duration-200 bg-blue-600 rounded-full focus:outline-none hover:bg-blue-700 hover:shadow-xl hover:shadow-blue-500/30 hover:-translate-y-1"
          >
            立即开启咨询
            <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>
          <button 
            onClick={() => setShowVideo(true)}
            className="inline-flex items-center justify-center px-8 py-4 text-lg font-medium text-slate-700 transition-all duration-200 bg-white border border-slate-200 rounded-full hover:bg-slate-50 hover:border-blue-300 hover:text-blue-600 group"
          >
            <Play size={20} className="mr-2 fill-slate-700 group-hover:fill-blue-600 transition-colors" />
            查看演示视频
          </button>
        </div>
      </section>

      {/* 核心技术板块 */}
      <section id="tech" className="py-24 bg-white relative z-10">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h3 className="text-blue-600 font-bold tracking-wider uppercase mb-2">Core Technology</h3>
            <h2 className="text-3xl md:text-4xl font-extrabold text-slate-900">核心技术架构</h2>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { icon: Database, title: "RAG 检索增强", desc: "结合向量数据库与知识图谱，实现政策文档的精准召回与溯源。" },
              { icon: Layers, title: "多Agent协同", desc: "Planner、Retrieval、Calculator 多智能体协作，解决复杂推理任务。" },
              { icon: Zap, title: "实时增量更新", desc: "构建 T+0 数据同步管道，确保政策信息与官方发布分秒不差。" }
            ].map((item, i) => (
              <div key={i} className="p-8 rounded-2xl bg-slate-50 hover:bg-blue-50/50 transition-colors border border-slate-100">
                <div className="w-14 h-14 bg-white rounded-xl shadow-sm flex items-center justify-center text-blue-600 mb-6">
                  <item.icon size={28} />
                </div>
                <h4 className="text-xl font-bold text-slate-800 mb-3">{item.title}</h4>
                <p className="text-slate-600 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 解决方案板块 */}
      <section id="solutions" className="py-24 bg-slate-50 relative z-10">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h3 className="text-indigo-600 font-bold tracking-wider uppercase mb-2">Solutions</h3>
            <h2 className="text-3xl md:text-4xl font-extrabold text-slate-900">全场景解决方案</h2>
          </div>
          <div className="grid md:grid-cols-2 gap-8">
            <div className="p-8 bg-white rounded-2xl shadow-sm border border-slate-200/60 flex gap-6 items-start hover:shadow-md transition-shadow">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 flex-shrink-0">
                <User size={32} />
              </div>
              <div>
                <h4 className="text-xl font-bold text-slate-800 mb-2">面向普通市民</h4>
                <ul className="space-y-2 text-slate-600">
                  <li className="flex items-center gap-2"><CheckCircle2 size={16} className="text-green-500" /> 7x24小时政策答疑</li>
                  <li className="flex items-center gap-2"><CheckCircle2 size={16} className="text-green-500" /> 最优购买组合计算</li>
                  <li className="flex items-center gap-2"><CheckCircle2 size={16} className="text-green-500" /> 补贴申领流程指引</li>
                </ul>
              </div>
            </div>
            <div className="p-8 bg-white rounded-2xl shadow-sm border border-slate-200/60 flex gap-6 items-start hover:shadow-md transition-shadow">
              <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 flex-shrink-0">
                <Globe size={32} />
              </div>
              <div>
                <h4 className="text-xl font-bold text-slate-800 mb-2">面向政府部门</h4>
                <ul className="space-y-2 text-slate-600">
                  <li className="flex items-center gap-2"><CheckCircle2 size={16} className="text-green-500" /> 政策热度实时监测</li>
                  <li className="flex items-center gap-2"><CheckCircle2 size={16} className="text-green-500" /> 市民诉求聚类分析</li>
                  <li className="flex items-center gap-2"><CheckCircle2 size={16} className="text-green-500" /> 政策落地效果评估</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 团队介绍板块 */}
      <section id="team" className="py-24 bg-white relative z-10 border-t border-slate-100">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h3 className="text-slate-400 font-bold tracking-wider uppercase mb-2">Our Team</h3>
            <h2 className="text-3xl md:text-4xl font-extrabold text-slate-900">团队分工</h2>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { role: "知识库与数据架构", task: "负责政策数据采集、增量更新闭环、表格/文本知识库构建。", icon: Database },
              { role: "智能体核心编排", task: "工作流智能体设计、多Agent协作逻辑、意图识别与大模型调优。", icon: Cpu },
              { role: "系统全栈开发", task: "前端交互设计、系统测试与调试、多轮交互验证与演示录制。", icon: Layers }
            ].map((member, i) => (
              <div key={i} className="text-center p-6 rounded-2xl hover:bg-slate-50 transition-colors">
                <div className="w-20 h-20 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-6 text-slate-600">
                  <member.icon size={32} />
                </div>
                <h4 className="text-lg font-bold text-slate-800 mb-2">小组成员 {i+1}</h4>
                <p className="text-blue-600 font-medium text-sm mb-4">{member.role}</p>
                <p className="text-slate-500 text-sm leading-relaxed">{member.task}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
      
      <footer className="py-8 bg-slate-900 text-center text-slate-500 text-sm relative z-10">
        <div className="mb-4 flex justify-center gap-4">
          <span className="w-2 h-2 rounded-full bg-slate-700"></span>
          <span className="w-2 h-2 rounded-full bg-slate-700"></span>
          <span className="w-2 h-2 rounded-full bg-slate-700"></span>
        </div>
        © 2025 IntelliPolicy Team. Powered by React & Tailwind CSS.
      </footer>
    </div>
  );
};

// 2. 主应用界面 (保持原样，仅做微调)
const MainApp = ({ onBack }) => {
  const [activeModule, setActiveModule] = useState('chat'); // chat, calculator, policies
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  const [health, setHealth] = useState({ status: 'unknown', agent_ready: false });
  const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
  
  console.log('MainApp 渲染, activeModule:', activeModule);
  
  useEffect(() => {
      const loadHealth = () => {
        fetch(`${API_BASE}/api/health`).then(r => r.json()).then(setHealth).catch(() => setHealth({ status: 'error', agent_ready: false }));
      };
      loadHealth();
      const t = setInterval(loadHealth, 10000);
      return () => clearInterval(t);
    }, []);

  return (
    <div className="flex h-screen bg-slate-50 font-sans overflow-hidden animate-fade-in">
      {/* 侧边导航 */}
      <aside className="hidden md:flex flex-col w-64 bg-white border-r border-slate-200 z-20 transition-all duration-300 shadow-sm">
        <div className="h-20 flex items-center px-6 border-b border-slate-100 cursor-pointer hover:bg-slate-50 transition-colors" onClick={onBack}>
          <div className="w-10 h-10 bg-gradient-to-tr from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg shadow-blue-500/20">
            <Cpu size={20} className="text-white" />
          </div>
          <div className="ml-3">
            <h1 className="font-bold text-lg text-slate-800 tracking-tight">智策通</h1>
            <p className="text-[10px] text-slate-400 font-medium uppercase tracking-wider">IntelliPolicy</p>
          </div>
        </div>

        <nav className="flex-1 py-6 px-4 space-y-2">
          {[
            { id: 'chat', icon: MessageSquare, label: '智能政策咨询' },
            { id: 'calculator', icon: Calculator, label: '最优组合计算' },
            { id: 'policies', icon: FileText, label: '政策公示大厅' },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveModule(item.id)}
              className={`w-full flex items-center px-4 py-3.5 rounded-xl transition-all duration-200 group ${
                activeModule === item.id
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-200'
                  : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900'
              }`}
            >
              <item.icon size={20} className={activeModule === item.id ? 'text-white' : 'text-slate-400 group-hover:text-slate-600'} />
              <span className="ml-3 font-medium text-sm">{item.label}</span>
              {activeModule === item.id && <ChevronRight size={16} className="ml-auto opacity-70" />}
            </button>
          ))}
        </nav>

        {/* 系统状态展示区 */}
        <div className="p-4 border-t border-slate-100">
          <div className="bg-slate-50 border border-slate-100 p-4 rounded-2xl">
            <p className="text-xs font-bold text-slate-400 uppercase mb-3 tracking-wider">System Status</p>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Globe size={14} className="text-blue-500" />
                  <span className="text-xs font-medium text-slate-600">知识库</span>
                </div>
                {health.agent_ready ? (
                  <span className="text-[10px] bg-green-100 text-green-700 px-1.5 py-0.5 rounded font-bold">已就绪</span>
                ) : (
                  <span className="text-[10px] bg-yellow-100 text-yellow-700 px-1.5 py-0.5 rounded font-bold">未就绪</span>
                )}
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Zap size={14} className="text-orange-500" />
                  <span className="text-xs font-medium text-slate-600">服务状态</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="relative flex h-1.5 w-1.5">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-green-500"></span>
                  </span>
                  <span className="text-[10px] text-slate-500">{health.status || 'unknown'}</span>
                </div>
              </div>
            </div>

            <div className="mt-4 flex gap-2">
              <button
                onClick={() => fetch(`${API_BASE}/api/clear_history`, { method: 'POST' }).then(() => alert('对话历史已清空')).catch(() => alert('清空失败'))}
                className="px-3 py-1.5 text-xs rounded-lg bg-slate-800 text-white hover:bg-blue-600 transition-colors"
              >
                清空历史
              </button>
              <button
                onClick={() => fetch(`${API_BASE}/api/rebuild_kb`, { method: 'POST' }).then(() => alert('知识库重建成功')).catch(() => alert('重建失败'))}
                className="px-3 py-1.5 text-xs rounded-lg bg-slate-200 text-slate-700 hover:bg-blue-50 hover:text-blue-600 border border-slate-300 transition-colors"
              >
                重建知识库
              </button>
            </div>
          </div>
        </div>
      </aside>

      {/* 主内容区 */}
      <main className="flex-1 relative flex flex-col h-full overflow-hidden bg-slate-50/50">
        {/* 顶部移动端导航 */}
        <header className="md:hidden h-16 bg-white border-b border-slate-200 flex items-center justify-between px-4 z-30">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <Cpu size={18} className="text-white" />
            </div>
            <span className="font-bold text-lg text-slate-800">智策通</span>
          </div>
          <button onClick={() => setShowMobileMenu(!showMobileMenu)} className="p-2 text-slate-600">
            {showMobileMenu ? <X size={24} /> : <div className="space-y-1.5"><div className="w-6 h-0.5 bg-current rounded-full"></div><div className="w-6 h-0.5 bg-current rounded-full"></div></div>}
          </button>
        </header>

        {/* 移动端菜单 */}
        {showMobileMenu && (
          <div className="absolute top-16 left-0 w-full bg-white border-b border-slate-200 shadow-xl z-20 md:hidden p-4 space-y-2 animate-fade-in">
             {[
                { id: 'chat', label: '智能政策咨询' },
                { id: 'calculator', label: '最优组合计算' },
                { id: 'policies', label: '政策公示大厅' },
              ].map((item) => (
                <button
                  key={item.id}
                  onClick={() => { setActiveModule(item.id); setShowMobileMenu(false); }}
                  className={`w-full text-left px-4 py-4 rounded-xl font-medium flex items-center justify-between ${
                    activeModule === item.id ? 'bg-blue-50 text-blue-600' : 'text-slate-600'
                  }`}
                >
                  {item.label}
                  {activeModule === item.id && <CheckCircle2 size={16} />}
                </button>
              ))}
          </div>
        )}

        {/* 内容容器 */}
        <div className="flex-1 overflow-hidden relative">
          {activeModule === 'chat' && <ChatModule />}
          {activeModule === 'calculator' && <CalculatorModule />}
          {activeModule === 'policies' && <PoliciesModule />}
        </div>
      </main>
    </div>
  );
};

// 2.1 聊天模块 (极致体验版)
const ChatModule = () => {
  const [messages, setMessages] = useState([
    { id: 1, type: 'bot', text: CHAT_SCRIPTS['default'] }
  ]);
  const [input, setInput] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const [userLocation, setUserLocation] = useState(null); // 新增：用户位置
  const bottomRef = useRef(null);

  // 新增：获取用户地理位置
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          // 这里可以调用逆地理编码API来获取城市名
          // 暂时使用默认值
          setUserLocation({
            province: '山东省',
            city: '济南市',
            district: null,
            latitude,
            longitude
          });
          console.log('获取位置成功:', { latitude, longitude });
        },
        (error) => {
          console.warn('无法获取地理位置:', error.message);
          // 使用默认位置
          setUserLocation({
            province: '山东省',
            city: '济南市',
            district: null
          });
        }
      );
    } else {
      console.warn('浏览器不支持地理位置');
      setUserLocation({
        province: '山东省',
        city: '济南市',
        district: null
      });
    }
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isThinking]);

  // 打字机效果状态
  const [typingMessage, setTypingMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const typingIndex = useRef(0);
  const typingInterval = useRef(null);

  // 清除打字机效果
  const clearTyping = () => {
    if (typingInterval.current) {
      clearInterval(typingInterval.current);
      typingInterval.current = null;
    }
    setIsTyping(false);
    setTypingMessage('');
    typingIndex.current = 0;
  };

  // 实现打字机效果
  const typeMessage = (message) => {
    clearTyping();
    setIsTyping(true);
    setTypingMessage('');
    typingIndex.current = 0;

    typingInterval.current = setInterval(() => {
      if (typingIndex.current < message.length) {
        setTypingMessage(prev => prev + message.charAt(typingIndex.current));
        typingIndex.current++;
      } else {
        clearTyping();
      }
    }, 30); // 打字速度，30ms per character
  };

  // 语音识别状态
  const [isListening, setIsListening] = useState(false);
  const [recognition, setRecognition] = useState(null);

  // 初始化语音识别
  useEffect(() => {
    // 检查浏览器是否支持语音识别
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      console.warn('浏览器不支持 Web Speech API');
      return;
    }
    
    const recognitionInstance = new SpeechRecognition();
    recognitionInstance.continuous = false;  // 单次识别模式
    recognitionInstance.interimResults = true;  // 开启中间结果，实时显示
    recognitionInstance.lang = 'zh-CN';  // 中文识别
    recognitionInstance.maxAlternatives = 1;  // 只返回最佳结果
    
    recognitionInstance.onstart = () => {
      console.log('语音识别已启动');
      setIsListening(true);
    };
    
    recognitionInstance.onresult = (event) => {
      console.log(`语音识别结果 (isFinal: ${event.results[0].isFinal}):`, event);
      
      // 获取最新的识别结果
      const lastResultIndex = event.results.length - 1;
      const result = event.results[lastResultIndex][0];
      const transcript = result.transcript;
      const isFinal = event.results[lastResultIndex].isFinal;
      
      console.log(`识别文本: "${transcript}" (最终结果: ${isFinal})`);
      
      // 实时更新输入框
      setInput(transcript);
      
      // 如果是最终结果，自动停止
      if (isFinal) {
        console.log('最终结果已获取，停止识别');
      }
    };
    
    recognitionInstance.onerror = (event) => {
      console.error('语音识别错误:', event.error);
      alert(`语音识别错误: ${event.error}`);
      setIsListening(false);
    };
    
    recognitionInstance.onend = () => {
      console.log('语音识别已结束');
      setIsListening(false);
    };
    
    setRecognition(recognitionInstance);
    
    return () => {
      if (recognitionInstance) {
        try {
          recognitionInstance.stop();
        } catch (e) {
          console.log('清理时停止识别:', e);
        }
      }
    };
  }, []);

  // 开始/停止语音识别
  const toggleVoiceInput = () => {
    if (!recognition) {
      alert('您的浏览器不支持语音识别功能，请使用 Chrome 或 Edge 浏览器');
      return;
    }
    
    if (isListening) {
      console.log('停止语音识别');
      try {
        recognition.stop();
      } catch (e) {
        console.error('停止识别失败:', e);
        setIsListening(false);
      }
    } else {
      console.log('开始语音识别');
      try {
        recognition.start();
      } catch (e) {
        console.error('启动识别失败:', e);
        alert(`启动失败: ${e.message}`);
      }
    }
  };

  const handleSend = (text = input) => {
    if (!text.trim()) return;
    
    setMessages(prev => [...prev, { id: Date.now(), type: 'user', text }]);
    setInput('');
    setIsThinking(true);

    const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

    // 构建带位置参数的URL
    let streamUrl = `${API_BASE}/api/stream_query?question=${encodeURIComponent(text)}`;
    if (userLocation && userLocation.city) {
      streamUrl += `&city=${encodeURIComponent(userLocation.city)}`;
      if (userLocation.province) {
        streamUrl += `&province=${encodeURIComponent(userLocation.province)}`;
      }
      if (userLocation.district) {
        streamUrl += `&district=${encodeURIComponent(userLocation.district)}`;
      }
    }

    // 尝试使用流式API
    const eventSource = new EventSource(streamUrl);
    let hasReceivedData = false;
    let isCompleted = false;
    let accumulatedText = '';  // 累积文本
    
    eventSource.onmessage = (event) => {
      hasReceivedData = true;
      const data = JSON.parse(event.data);
      
      switch (data.type) {
        case 'chunk':
          // 处理流式文本块(优化:直接累积不再重复调用typeMessage)
          accumulatedText += data.content;
          setTypingMessage(accumulatedText);
          setIsTyping(true);
          break;
        case 'complete':
          // 完成消息
          isCompleted = true;
          eventSource.close();
          clearTyping();
          const result = data.result;
          const confidencePercent = Math.round(((result.confidence || 0) * 1000)) / 10;
          const sourcesText = Array.isArray(result.sources) && result.sources.length
            ? '\n\n参考来源:\n' + result.sources.slice(0, 2).map((s, i) => `${i + 1}. ${s.source} (相关度: ${Math.round(((s.similarity || 0) * 1000)) / 10}%)`).join('\n')
            : '';
          const reply = `${result.answer}\n\n置信度: ${confidencePercent}%${sourcesText}`;
          setMessages(prev => [...prev, { id: Date.now() + 1, type: 'bot', text: reply }]);
          setIsThinking(false);
          break;
        case 'error':
          // 错误处理
          isCompleted = true;
          eventSource.close();
          clearTyping();
          setMessages(prev => [...prev, { id: Date.now() + 1, type: 'bot', text: `错误: ${data.message}` }]);
          setIsThinking(false);
          break;
      }
    };
    
    eventSource.onerror = () => {
      eventSource.close();
      
      // 只有在未收到任何数据时才回退到普通API
      if (!hasReceivedData && !isCompleted) {
        clearTyping();
        
        fetch(`${API_BASE}/api/query`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            question: text, 
            return_sources: true,
            location: userLocation  // 添加位置信息
          })
        })
          .then(async (res) => {
            if (!res.ok) throw new Error('网络错误');
            const data = await res.json();
            const confidencePercent = Math.round(((data.confidence || 0) * 1000)) / 10;
            const sourcesText = Array.isArray(data.sources) && data.sources.length
              ? '\n\n参考来源:\n' + data.sources.slice(0, 2).map((s, i) => `${i + 1}. ${s.source} (相关度: ${Math.round(((s.similarity || 0) * 1000)) / 10}%)`).join('\n')
              : '';
            const reply = `${data.answer}\n\n置信度: ${confidencePercent}%${sourcesText}`;
            setMessages(prev => [...prev, { id: Date.now() + 1, type: 'bot', text: reply }]);
          })
          .catch(() => {
            setMessages(prev => [...prev, { id: Date.now() + 1, type: 'bot', text: '抱歉，服务暂时不可用，请稍后重试。' }]);
          })
          .finally(() => setIsThinking(false));
      } else if (!isCompleted) {
        // 如果已收到数据但未完成，也需要结束思考状态
        setIsThinking(false);
      }
    };
  };

  // 组件卸载时清除定时器
  useEffect(() => {
    return () => {
      clearTyping();
    };
  }, []);

  return (
    <div className="flex flex-col h-full w-full bg-white md:bg-transparent">
      {/* 聊天记录区域 */}
      <div className="flex-1 overflow-y-auto px-4 md:px-12 py-6 space-y-8 scroll-smooth">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in-up`}>
            <div className={`flex gap-4 max-w-[90%] md:max-w-[80%] ${msg.type === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
              {/* 头像 */}
              <div className={`w-10 h-10 rounded-full flex-shrink-0 flex items-center justify-center shadow-md border-2 border-white ${
                msg.type === 'user' ? 'bg-slate-200' : 'bg-gradient-to-tr from-blue-600 to-indigo-600'
              }`}>
                {msg.type === 'user' ? <User size={20} className="text-slate-500" /> : <Bot size={20} className="text-white" />}
              </div>
              
              {/* 气泡 */}
              <div className={`group relative p-5 rounded-2xl text-sm md:text-[15px] leading-relaxed shadow-sm ${
                msg.type === 'user' 
                  ? 'bg-blue-600 text-white rounded-tr-sm' 
                  : 'bg-white text-slate-700 border border-slate-100 rounded-tl-sm shadow-slate-100'
              }`}>
                {msg.type === 'user' ? (
                  <div className="whitespace-pre-wrap">{msg.text}</div>
                ) : (
                  <ReactMarkdown 
                    remarkPlugins={[remarkGfm]}
                    components={{
                      p: ({node, ...props}) => <p className="mb-2 last:mb-0" {...props} />,
                      strong: ({node, ...props}) => <strong className="font-bold text-slate-900" {...props} />,
                      em: ({node, ...props}) => <em className="italic" {...props} />,
                      ul: ({node, ...props}) => <ul className="list-disc ml-4 mb-2" {...props} />,
                      ol: ({node, ...props}) => <ol className="list-decimal ml-4 mb-2" {...props} />,
                      li: ({node, ...props}) => <li className="mb-1" {...props} />,
                      code: ({node, inline, ...props}) => 
                        inline ? (
                          <code className="bg-slate-100 px-1.5 py-0.5 rounded text-sm font-mono" {...props} />
                        ) : (
                          <code className="block bg-slate-100 p-2 rounded text-sm font-mono overflow-x-auto" {...props} />
                        ),
                      a: ({node, ...props}) => <a className="text-blue-600 hover:underline" {...props} />,
                      h1: ({node, ...props}) => <h1 className="text-xl font-bold mb-2" {...props} />,
                      h2: ({node, ...props}) => <h2 className="text-lg font-bold mb-2" {...props} />,
                      h3: ({node, ...props}) => <h3 className="text-base font-bold mb-1" {...props} />,
                      blockquote: ({node, ...props}) => <blockquote className="border-l-4 border-blue-600 pl-3 italic" {...props} />,
                    }}
                  >
                    {msg.text}
                  </ReactMarkdown>
                )}
              </div>
            </div>
          </div>
        ))}
        
        {/* 打字机效果显示 */}
        {isTyping && (
          <div className="flex justify-start px-1 animate-fade-in">
            <div className="flex gap-4 items-center">
              <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center shadow-md border-2 border-white">
                <Bot size={20} className="text-white" />
              </div>
              <div className="px-5 py-4 bg-white border border-slate-100 rounded-2xl rounded-tl-sm shadow-sm">
                <div className="text-slate-700">
                  <ReactMarkdown 
                    remarkPlugins={[remarkGfm]}
                    components={{
                      p: ({node, ...props}) => <span {...props} />,
                      strong: ({node, ...props}) => <strong className="font-bold text-slate-900" {...props} />,
                      em: ({node, ...props}) => <em className="italic" {...props} />,
                    }}
                  >
                    {typingMessage}
                  </ReactMarkdown>
                  <span className="inline-block w-2 h-5 bg-slate-400 ml-1 animate-pulse align-middle"></span>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {isThinking && !isTyping && (
          <div className="flex justify-start px-1 animate-fade-in">
            <div className="flex gap-4 items-center">
              <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center shadow-md border-2 border-white">
                <Bot size={20} className="text-white" />
              </div>
              <div className="px-5 py-4 bg-white border border-slate-100 rounded-2xl rounded-tl-sm shadow-sm flex items-center gap-2">
                <span className="flex gap-1">
                  <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce"></span>
                  <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce delay-100"></span>
                  <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce delay-200"></span>
                </span>
                <span className="text-xs font-medium text-slate-400 ml-2">正在解析政策意图...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} className="h-4" />
      </div>

      {/* 底部输入栏 */}
      <div className="p-4 md:p-6 bg-white/80 backdrop-blur-md border-t border-slate-100 md:mb-4 md:mx-8 md:rounded-2xl md:shadow-lg md:border-none z-10">
        <div className="max-w-4xl mx-auto space-y-4">
          {/* 快捷提问 */}
          {messages.length < 3 && (
            <div className="flex gap-3 overflow-x-auto pb-1 scrollbar-hide">
              {['济南市家电以旧换新补贴标准是多少？', '我有15000元预算，推荐一个最划算的家电换新方案', '手机购新补贴如何申请？'].map((q, i) => (
                <button 
                  key={i} 
                  onClick={() => handleSend(q)}
                  className="flex-shrink-0 px-4 py-2 bg-blue-50 text-blue-600 text-xs md:text-sm font-medium rounded-full hover:bg-blue-100 hover:scale-105 transition-all"
                >
                  {q}
                </button>
              ))}
            </div>
          )}
          
          <div className="relative flex items-end gap-2 bg-slate-50 border border-slate-200 rounded-2xl p-2 focus-within:ring-2 focus-within:ring-blue-500/20 focus-within:border-blue-500 transition-all">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="请输入您的政策疑问..."
              className="w-full bg-transparent border-none focus:ring-0 resize-none max-h-32 min-h-[48px] py-3 px-3 text-slate-700 placeholder:text-slate-400"
              rows={1}
            />
            <button 
              onClick={toggleVoiceInput}
              disabled={isThinking}
              className={`p-3 rounded-xl flex-shrink-0 transition-all duration-200 ${
                isListening
                  ? 'bg-red-500 text-white animate-pulse' 
                  : 'bg-slate-200 text-slate-600 hover:bg-blue-100 hover:text-blue-600'
              }`}
              title="语音输入"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                <line x1="12" x2="12" y1="19" y2="22"/>
              </svg>
            </button>
            <button 
              onClick={() => handleSend()}
              disabled={!input.trim() || isThinking}
              className={`p-3 rounded-xl flex-shrink-0 transition-all duration-200 ${
                input.trim() && !isThinking 
                  ? 'bg-blue-600 text-white shadow-lg hover:bg-blue-700 hover:-translate-y-0.5' 
                  : 'bg-slate-200 text-slate-400 cursor-not-allowed'
              }`}
            >
              <Send size={20} />
            </button>
          </div>
          <p className="text-center text-[10px] text-slate-300">
            智策通 AI 可能生成不准确的信息，请以政府官方发布文件为准
          </p>
        </div>
      </div>
    </div>
  );
};

// 2.2 计算器模块 (保持逻辑不变，适配布局)
const CalculatorModule = () => {
  const [budget, setBudget] = useState(15000);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [selectedTags, setSelectedTags] = useState([]);
  const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  const calculate = () => {
    setLoading(true);
    setResult(null);

    const buildPlan = () => {
      const TAGS = selectedTags.length ? selectedTags : ['一级能效空调','冰箱'];
      const PRICES = { '一级能效空调': 3000, '冰箱': 3000, '洗衣机': 2000, '电视': 2500, '笔记本电脑': 5000, '热水器': 1500 };
      const RATES = { '一级能效空调': 0.20, '冰箱': 0.20, '洗衣机': 0.15, '电视': 0.15, '笔记本电脑': 0.15, '热水器': 0.15 };
      let items = []; let spend = 0; let totalSub = 0;
      for (const tag of TAGS) {
        const price = PRICES[tag] || 3000;
        const rate = RATES[tag] ?? 0.15;
        let count = 0;
        while (spend + price <= budget) {
          count++; spend += price; totalSub += Math.round(price * rate);
        }
        if (count > 0) items.push({ name: tag, count, price, subsidy: Math.round(price * rate) });
      }
      const net = Math.max(spend - totalSub, 0);
      const util = spend > 0 ? (spend / budget) : 0;
      return { items, total_subsidy: totalSub, net_spend: net, utilization: util, notes: '基于预算与品类的估算，最终以政策规则为准' };
    };

    const tagsText = selectedTags.length ? selectedTags.join('、') : '（未指定，按家电优先）';
    const question = `我有${budget}元预算，推荐一个最划算的换新方案${tagsText !== '（未指定，按家电优先）' ? '，意向品类：' + tagsText : ''}`;

    fetch(`${API_BASE}/api/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, return_sources: true })
    })
      .then(async (res) => {
        if (!res.ok) throw new Error('网络错误');
        const data = await res.json();
        
        // 优先使用后端返回的 recommendation 字段（动态规划结果）
        if (data.recommendation && data.recommendation.selected_products) {
          const rec = data.recommendation;
          const items = rec.selected_products.map(p => ({
            name: p.name,
            count: 1,
            price: p.price,
            subsidy: p.subsidy
          }));
          
          setResult({
            type: 'json',
            data: {
              items,
              total_subsidy: rec.total_subsidy,
              net_spend: rec.final_cost,
              utilization: rec.utilization_rate,
              notes: `动态规划算法（全局最优）：选中${rec.selected_products.length}件产品，总补贴￥${rec.total_subsidy}，资金利用率${(rec.utilization_rate * 100).toFixed(1)}%`
            },
            confidence: data.confidence,
            sources: data.sources || [],
            algorithm: data.algorithm,
            is_optimal: data.is_optimal,
            recommendation: rec,  // 保存完整的推荐数据
            price_comparison: data.price_comparison  // 保存价格比较数据
          });
        } else {
          // 回退到解析 LLM 返回的 JSON
          try {
            const match = (data.answer || '').match(/\{[\s\S]*\}/);
            const parsed = match ? JSON.parse(match[0]) : null;
            if (parsed && Array.isArray(parsed.items)) {
              setResult({ type: 'json', data: parsed, confidence: data.confidence, sources: data.sources || [] });
            } else {
              const fb = buildPlan();
              setResult({ type: 'json', data: fb, confidence: data.confidence, sources: data.sources || [] });
            }
          } catch (e) {
            setResult({ type: 'text', content: data.answer, confidence: data.confidence, sources: data.sources || [] });
          }
        }
      })
      .catch(() => {
        const fb = buildPlan();
        setResult({ type: 'json', data: fb });
      })
      .finally(() => setLoading(false));
  };

  return (
    <div className="h-full overflow-y-auto p-4 md:p-8 md:pb-20">
      <div className="max-w-5xl mx-auto">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
            <Calculator className="text-blue-600" /> 智能换新规划师
          </h2>
          <p className="text-slate-500 text-sm mt-1">输入您的总预算，AI将基于最新补贴政策，为您计算性价比最高的购买组合。</p>
        </div>

        <div className="grid md:grid-cols-12 gap-6">
          {/* 左侧配置 */}
          <div className="md:col-span-5 bg-white rounded-2xl p-6 shadow-sm border border-slate-100 h-fit">
            <div className="mb-8">
              <label className="block text-sm font-bold text-slate-700 mb-4">您的总预算 (元)</label>
              <div className="text-5xl font-extrabold text-blue-600 mb-6 tracking-tight">
                ¥ {budget.toLocaleString()}
              </div>
              <input 
                type="range" min="2000" max="50000" step="1000" value={budget}
                onChange={(e) => setBudget(Number(e.target.value))}
                className="w-full h-3 bg-slate-100 rounded-lg appearance-none cursor-pointer accent-blue-600 hover:accent-blue-700"
              />
              <div className="flex justify-between text-xs text-slate-400 mt-2 font-medium">
                <span>¥2,000</span>
                <span>¥50,000</span>
              </div>
            </div>
            
            <div className="mb-8">
              <label className="block text-sm font-bold text-slate-700 mb-3">意向品类 (多选)</label>
              <div className="flex flex-wrap gap-2">
                {['一级能效空调', '冰箱', '洗衣机', '电视', '笔记本电脑', '热水器'].map(tag => (
                  <button
                    key={tag}
                    onClick={() => setSelectedTags(prev => prev.includes(tag) ? prev.filter(t => t !== tag) : [...prev, tag])}
                    className={`px-3 py-1.5 text-sm font-medium rounded-lg border transition-all ${selectedTags.includes(tag) ? 'bg-blue-50 text-blue-600 border-blue-500' : 'bg-slate-50 text-slate-600 border-slate-200 hover:border-blue-500 hover:text-blue-600 hover:bg-blue-50'}`}
                  >
                    {tag}
                  </button>
                ))}
              </div>
            </div>

            <button 
              onClick={calculate}
              disabled={loading}
              className="w-full py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-bold text-lg shadow-lg shadow-blue-500/30 hover:shadow-xl hover:-translate-y-0.5 transition-all disabled:opacity-70 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  智能规划中...
                </>
              ) : (
                <>
                  <Sparkles size={20} />
                  生成最优方案
                </>
              )}
            </button>
          </div>

          {/* 右侧结果 */}
          <div className="md:col-span-7">
            {result ? (
              <div className="bg-white rounded-2xl p-6 md:p-8 shadow-xl border border-blue-100 h-full animate-fade-in-up relative overflow-hidden">
                {/* 装饰背景 */}
                <div className="absolute top-0 right-0 w-48 h-48 bg-gradient-to-bl from-blue-50 to-transparent rounded-bl-full -mr-10 -mt-10 opacity-50"></div>
                
                <div className="relative z-10">
                  <div className="flex justify-between items-end mb-8 pb-6 border-b border-dashed border-slate-200">
                    <div>
                      <span className="inline-block px-3 py-1 bg-green-100 text-green-700 text-xs font-bold rounded-full mb-2">
                        资金利用率 {(result.type === 'json' ? Math.round(((result.data.utilization || ((budget - (result.data.total_subsidy || 0)) / budget)) * 1000)) / 10 : 0)}%
                      </span>
                      <p className="text-sm text-slate-500">预计可获得补贴</p>
                      <p className="text-4xl font-extrabold text-red-500 mt-1">¥ {(result.type === 'json' ? (result.data.total_subsidy || result.data.items?.reduce((sum, i) => sum + (i.subsidy || 0), 0) || 0) : 0).toLocaleString()}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-slate-500 mb-1">实际净支出</p>
                      <p className="text-2xl font-bold text-slate-800">¥ {(result.type === 'json' ? (result.data.net_spend || (budget - (result.data.total_subsidy || 0))) : budget).toLocaleString()}</p>
                    </div>
                  </div>

                  <h4 className="font-bold text-slate-800 mb-4 flex items-center gap-2">
                    <CheckCircle2 size={18} className="text-blue-600" /> 推荐组合清单
                  </h4>
                  
                  <div className="space-y-3 mb-8">
                    {(result.type === 'json' ? (result.data.items || []) : [
                      { name: "一级能效空调 (海尔/格力)", count: 2, price: 6000, sub: 1200 },
                      { name: "一级能效冰箱 (500L+)", count: 1, price: 6000, sub: 1200 },
                      { name: "智能手机 (5G)", count: 1, price: 3000, sub: 450 },
                    ]).map((item, i) => (
                      <div key={i} className="flex justify-between items-center p-4 rounded-xl bg-slate-50 hover:bg-blue-50 transition-colors border border-transparent hover:border-blue-100">
                        <div className="flex items-center gap-4">
                          <div className="w-6 h-6 rounded-full bg-white border border-slate-200 flex items-center justify-center text-slate-400 font-bold text-xs shadow-sm">
                            {i+1}
                          </div>
                          <div>
                            <p className="font-bold text-slate-700">{item.name}</p>
                            <p className="text-xs text-slate-400 mt-0.5">数量: x{item.count}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-medium text-slate-800">¥ {item.price}</p>
                          <p className="text-xs text-red-500 font-bold bg-red-50 px-2 py-0.5 rounded mt-1">
                            补 ¥{(item.subsidy ?? item.sub ?? 0)}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="p-4 bg-indigo-50 rounded-XL flex gap-3 border border-indigo-100">
                    <div className="mt-0.5 bg-indigo-100 p-1 rounded-md text-indigo-600 h-fit">
                      <Sparkles size={16} />
                    </div>
                    <div>
                      <p className="text-xs font-bold text-indigo-800 mb-1">AI 决策建议</p>
                      <p className="text-sm text-indigo-900/80 leading-relaxed">
                        {result.type === 'json' && result.data?.notes ? result.data.notes : '本方案优先配置了一级能效家电。虽然单价略高，但能享受最高档位（20%）补贴，且全生命周期电费更低，是综合性价比最高的选择。'}
                      </p>
                    </div>
                  </div>
                  
                  {/* 添加可视化面板 */}
                  <VisualizationPanel 
                    recommendation={result.recommendation}
                    priceComparison={result.price_comparison}
                  />
                </div>
              </div>
            ) : (
              <div className="h-full flex flex-col items-center justify-center bg-white rounded-2xl border-2 border-dashed border-slate-200 text-slate-400 p-12">
                <div className="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center mb-6">
                  <Calculator size={32} className="text-slate-300" />
                </div>
                <p className="text-lg font-medium text-slate-500">等待生成计算结果...</p>
                <p className="text-sm mt-2 opacity-70">请在左侧调整预算并点击生成</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// 2.3 政策库模块
const PoliciesModule = () => {
  const [keyword, setKeyword] = useState('');
  const [policySources, setPolicySources] = useState([]);
  const [loadingPolicies, setLoadingPolicies] = useState(false);
  const [batchInput, setBatchInput] = useState('');
  const [batchResults, setBatchResults] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
  useEffect(() => {
    fetch(`${API_BASE}/api/metrics`).then(r => r.json()).then(setMetrics).catch(() => {});
  }, []);
  useEffect(() => {
    fetch(`${API_BASE}/api/policies`).then(r => r.json()).then(d => setPolicySources(Array.isArray(d.policies) ? d.policies : [])).catch(() => {});
  }, []);
  return (
    <div className="h-full overflow-y-auto p-4 md:p-8">
      <div className="max-w-5xl mx-auto bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
        <div className="p-6 md:p-8 border-b border-slate-100">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
            <div>
              <h2 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
                <FileText className="text-blue-600" /> 政策文件库
              </h2>
              <p className="text-slate-500 text-sm mt-1">已接入 4 个权威数据源，数据实时同步 (T+0)</p>
            </div>
            <div className="relative w-full md:w-72">
              <input 
                type="text" 
                placeholder="输入关键词搜索政策..." 
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                className="w-full pl-10 pr-24 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all"
              />
              <button
                onClick={() => {
                  setLoadingPolicies(true);
                  fetch(`${API_BASE}/sync_policies`, { method: 'POST' })
                    .then(() => fetch(`${API_BASE}/policies`).then(r => r.json()).then(d => setPolicySources(Array.isArray(d.policies) ? d.policies : [])))
                    .catch(() => {})
                    .finally(() => setLoadingPolicies(false));
                }}
                className="absolute right-20 top-1.5 px-3 py-1.5 text-xs rounded-lg bg-slate-200 text-slate-700 hover:bg-blue-50 hover:text-blue-600 border border-slate-300 transition-colors"
              >刷新</button>
              <button
                onClick={() => {
                  if (!keyword.trim()) return;
                  setLoadingPolicies(true);
                  fetch(`${API_BASE}/api/query`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question: `请围绕关键词“${keyword}”检索并返回相关政策摘要，附带sources。`, return_sources: true })
                  })
                    .then(async (res) => {
                      const data = await res.json();
                      setPolicySources(Array.isArray(data.sources) ? data.sources : []);
                    })
                    .catch(() => setPolicySources([]))
                    .finally(() => setLoadingPolicies(false));
                }}
                className="absolute right-2 top-1.5 px-3 py-1.5 text-xs rounded-lg bg-slate-800 text-white hover:bg-blue-600 transition-colors"
              >搜索</button>
            </div>
          </div>

          <div className="mt-4 grid md:grid-cols-2 gap-4">
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
              <p className="text-xs font-bold text-slate-400 uppercase mb-2 tracking-wider">批量咨询</p>
              <textarea
                value={batchInput}
                onChange={(e) => setBatchInput(e.target.value)}
                placeholder="每行一个问题..."
                className="w-full bg-white border border-slate-200 rounded-lg p-3 text-sm text-slate-700"
                rows={3}
              />
              <div className="mt-2 flex gap-2">
                <button
                  onClick={() => {
                    const questions = batchInput.split(/\n+/).map(s => s.trim()).filter(Boolean);
                    if (!questions.length) return;
                    fetch(`${API_BASE}/api/batch_query`, {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify({ questions })
                    }).then(async (res) => {
                      const data = await res.json();
                      setBatchResults(Array.isArray(data.results) ? data.results : []);
                    }).catch(() => setBatchResults([]));
                  }}
                  className="px-3 py-1.5 text-xs rounded-lg bg-slate-800 text-white hover:bg-blue-600 transition-colors"
                >批量咨询</button>
                <span className="text-xs text-slate-400">共 {batchResults.length} 条结果</span>
              </div>
            </div>
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
              <p className="text-xs font-bold text-slate-400 uppercase mb-2 tracking-wider">系统指标</p>
              <div className="text-xs text-slate-600 space-y-1">
                <div>会话数: {metrics?.sessions ?? '-'}</div>
                <div>平均延迟(ms): {metrics?.avg_latency_ms ?? '-'}</div>
                <div>错误率: {metrics?.error_rate ?? '-'}</div>
              </div>
            </div>
          </div>

          {/* 标签过滤器 */}
          <div className="flex gap-2">
            {['全部', '国家级', '省市级', '汽车', '家电'].map((tab, i) => (
              <button key={i} className={`px-4 py-1.5 rounded-full text-xs font-medium transition-colors ${
                i === 0 ? 'bg-slate-800 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}>
                {tab}
              </button>
            ))}
          </div>
        </div>
        
        {policySources.length > 0 && (
          <div className="p-6">
            <h4 className="text-sm font-bold text-slate-700 mb-3">搜索结果{loadingPolicies ? '（加载中...）' : ''}</h4>
            <div className="space-y-2">
              {policySources.map((s, i) => (
                <div key={i} className="p-4 rounded-xl bg-white border border-slate-100 flex items-center justify-between">
                  <div className="text-sm text-slate-700">{i + 1}. {s.source}</div>
                  <div className="text-xs text-slate-400">相关度 {Math.round(((s.similarity || 0) * 1000)) / 10}%</div>
                </div>
              ))}
            </div>
          </div>
        )}
        {batchResults.length > 0 && (
          <div className="p-6">
            <h4 className="text-sm font-bold text-slate-700 mb-3">批量咨询结果</h4>
            <div className="space-y-3">
              {batchResults.map((r, i) => (
                <div key={i} className="p-4 rounded-xl bg-white border border-slate-100">
                  <div className="text-sm font-bold text-slate-800">Q{i + 1}: {r.question}</div>
                  <div className="mt-2 text-sm text-slate-700 whitespace-pre-wrap">{r.answer}</div>
                </div>
              ))}
            </div>
          </div>
        )}
        <div className="divide-y divide-slate-50">
          {policySources.length === 0 ? (
            <div className="p-6 text-sm text-slate-500">暂无政策数据，请点击上方“搜索”或在后端重建知识库。</div>
          ) : (
            policySources.map((s, i) => (
              <div key={i} className="p-6 hover:bg-blue-50/30 transition-all cursor-pointer group flex items-start gap-4">
                <div className="mt-1">
                  <div className="w-10 h-10 rounded-lg flex items-center justify-center text-xs font-bold bg-blue-50 text-blue-600">
                    文档
                  </div>
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-bold text-slate-700 text-base group-hover:text-blue-600 transition-colors">
                      {s.source}
                    </h3>
                    <span className="px-2 py-0.5 bg-green-100 text-green-700 text-[10px] font-bold rounded">相似度 {Math.round(((s.similarity || 0) * 1000)) / 10}%</span>
                  </div>
                  {s.snippet && (
                    <p className="text-xs text-slate-500 mt-1">{s.snippet}</p>
                  )}
                </div>
                <div className="self-center opacity-0 group-hover:opacity-100 transition-opacity transform translate-x-[-10px] group-hover:translate-x-0">
                  <ChevronRight size={20} className="text-blue-400" />
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

// 主程序入口
const App = () => {
  const [started, setStarted] = useState(false);

  // 调试日志
  useEffect(() => {
    console.log('App 组件加载, started:', started);
  }, [started]);

  // 全局动画样式
  useEffect(() => {
    const style = document.createElement('style');
    style.innerHTML = `
      @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
      }
      @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
      }
      html { scroll-behavior: smooth; }
      .animate-fade-in-up { animation: fadeInUp 0.6s ease-out forwards; }
      .animate-fade-in { animation: fadeIn 0.4s ease-out forwards; }
      .scrollbar-hide::-webkit-scrollbar { display: none; }
    `;
    document.head.appendChild(style);
    return () => document.head.removeChild(style);
  }, []);

  console.log('App 渲染, started:', started);

  if (started) {
    console.log('渲染 MainApp');
    return <MainApp onBack={() => setStarted(false)} />;
  } else {
    console.log('渲染 LandingPage');
    return <LandingPage onStart={() => setStarted(true)} />;
  }
};

export default App;