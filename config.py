"""
企业级政策咨询智能体 - 核心配置文件
支持双层意图识别、混合检索、工具链计算、多Agent协作
"""

# ========== AI模型配置 ==========
# 选项1: 使用百度千帆 (推荐，支持免费ERNIE-Speed-128K)
USE_QIANFAN = False
QIANFAN_AK = "your_api_key"  # 替换为你的千帆API Key
QIANFAN_SK = "your_secret_key"  # 替换为你的千帆Secret Key
QIANFAN_MODEL = "ERNIE-Speed-128K"  # 免费模型

# 选项2: 使用OpenAI兼容接口 (DeepSeek、通义千问等)
USE_OPENAI_COMPATIBLE = True
OPENAI_API_KEY = "sk-edac2ec3e60842e889a956b15e86f26b"  # 通义千问密钥
OPENAI_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"  # 通义千问兼容接口
OPENAI_MODEL = "qwen-plus"  # 通义千问模型

# ========== 向量模型配置 ==========
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # 轻量级英文模型，约80MB

# ========== 知识库配置 ==========
DOCS_DIR = "./市级消费活动政策"  # 文档目录
TEXT_KB_DIR = "./knowledge_base/text_kb"  # 文本知识库
TABLE_KB_DIR = "./knowledge_base/table_kb"  # 表格知识库
METADATA_KB_DIR = "./knowledge_base/metadata_kb"  # 元数据知识库
CHROMA_DB_DIR = "./chroma_db"  # 向量数据库存储路径
CHUNK_SIZE = 500  # 文档切片大小
CHUNK_OVERLAP = 100  # 切片重叠

# ========== 检索配置(性能优化) ==========
TOP_K = 10  # 初次检索数量(从15降低到10)
RERANK_TOP_K = 5  # 重排序后保留数量(从10降低到5)
SIMILARITY_THRESHOLD = 0.6  # 相似度阈值(从0.5提高到0.6)

# ========== 双层意图识别配置 ==========
# 意图识别-1: 基础相关性判定
INTENT_L1_THRESHOLD = 0.7  # 相关性阈值

# 意图识别-2: 任务路由
INTENT_TYPES = {
    "POLICY_QA": "政策文本问答",  # 流程、条件、范围等
    "DATA_QUERY": "数据/型号查询",  # 补贴金额、型号条件等
    "COMPLEX": "复杂综合类",  # 跨政策对比、多条件计算
    "RECOMMENDATION": "智能推荐",  # 最优换新方案
    "CALCULATION": "补贴计算"  # 精确数值计算
}

# ========== 工具链配置 ==========
ENABLE_CALCULATOR = True  # 启用精确计算工具
ENABLE_RECOMMENDER = True  # 启用智能推荐
ENABLE_MULTI_AGENT = True  # 启用多Agent协作

# ========== 输出格式化配置 ==========
OUTPUT_FORMAT = {
    "add_source": True,  # 添加政策出处
    "add_date": True,  # 添加日期信息
    "add_confidence": True,  # 添加置信度
    "structured_output": True  # 结构化输出
}

# ========== Reranker配置 ==========
USE_RERANKER = True  # 启用重排序
RERANKER_MODEL = "cross-encoder"  # 重排序模型类型

# ========== 拒绝机制配置 ==========
REJECTION_KEYWORDS = [
    "违法", "欺诈", "作弊", "漏洞", "黑产",
    "政治", "敏感", "色情", "暴力"
]

# ========== 系统提示词(优化版:精简同时保持效果) ==========
SYSTEM_PROMPT = """你是政策咨询AI，专注“消费品以旧换新”政策。

能力：
1. 精准政策问答 - 基于官方文件
2. 补贴精确测算 - 工具链计算，绝不编造
3. 智能方案推荐 - 最优换新组合
4. 多轮对话 - 理解上下文

原则：
1. 准确性优先 - 所有答案必须有政策依据
2. 数值零幻觉 - 所有金额由工具计算
3. 结构化输出 - 使用分点、序号
4. 可解释性 - 说明推理过程

输出格式：
- 开头：简洁概括
- 主体：分点详细说明
- 结尾：补充提醒
- 附注：政策来源、生效时间
"""

# ========== 多Agent配置 ==========
AGENTS = {
    "task_decomposer": "任务分解Agent",
    "policy_retriever": "政策检索Agent", 
    "data_retriever": "数据检索Agent",
    "calculator": "计算Agent",
    "conflict_detector": "冲突检测Agent",
    "aggregator": "结果汇总Agent"
}

# ========== 监控配置 ==========
ENABLE_MONITORING = True
LOG_DIR = "./logs"
ALERT_THRESHOLD = {
    "error_rate": 0.05,  # 错误率阈值
    "latency_ms": 5000  # 响应延迟阈值
}
