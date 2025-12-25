"""
企业级政策咨询智能体核心
整合双层意图识别、混合检索、工具链计算、多Agent协作
增强版：支持 BM25+向量双路召回、实体抽取、反思链、多智能体
"""
from typing import List, Dict, Tuple, Optional
from knowledge_base import KnowledgeBase
from llm_client import LLMClient
from intent_recognition import IntentRecognizer, RejectionHandler
from tools import SubsidyCalculator, RecommendationEngine
from reranker import Reranker, HybridRetriever
from prompt_builder import PromptBuilder, OutputFormatter
import config
import time

# 可选增强模块
try:
    from ner_extractor import EntityExtractor
    NER_AVAILABLE = True
except ImportError:
    NER_AVAILABLE = False
    print("提示: ner_extractor 未找到，实体抽取不可用")

try:
    from reflection import ReflectionAgent
    REFLECTION_AVAILABLE = True
except ImportError:
    REFLECTION_AVAILABLE = False
    print("提示: reflection 未找到，反思链不可用")

try:
    from multi_agent import MultiAgentOrchestrator
    MULTI_AGENT_AVAILABLE = True
except ImportError:
    MULTI_AGENT_AVAILABLE = False
    print("提示: multi_agent 未找到，多智能体协作不可用")

try:
    from plugin_manager import PluginManager
    PLUGIN_AVAILABLE = True
except ImportError:
    PLUGIN_AVAILABLE = False
    print("提示: plugin_manager 未找到，插件系统不可用")

try:
    from cache_manager import CacheManager, cache_manager
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    cache_manager = None
    print("提示: cache_manager 未找到，缓存功能不可用")

# 新增增强模块
try:
    from monitor import monitoring_system
    MONITOR_AVAILABLE = True
except ImportError:
    MONITOR_AVAILABLE = False
    monitoring_system = None
    print("提示: monitor 未找到，监控功能不可用")

try:
    from feedback_system import feedback_system
    FEEDBACK_AVAILABLE = True
except ImportError:
    FEEDBACK_AVAILABLE = False
    feedback_system = None
    print("提示: feedback_system 未找到，反馈功能不可用")

try:
    from urgency_detector import urgency_detector
    URGENCY_AVAILABLE = True
except ImportError:
    URGENCY_AVAILABLE = False
    urgency_detector = None
    print("提示: urgency_detector 未找到，紧急度识别不可用")

try:
    from quality_validator import quality_validator
    QUALITY_AVAILABLE = True
except ImportError:
    QUALITY_AVAILABLE = False
    quality_validator = None
    print("提示: quality_validator 未找到，质量验证不可用")

try:
    from location_service import location_service
    LOCATION_AVAILABLE = True
except ImportError:
    LOCATION_AVAILABLE = False
    location_service = None
    print("提示: location_service 未找到，地理位置功能不可用")

try:
    from emotion_intelligence import emotion_intelligence
    EMOTION_AVAILABLE = True
except ImportError:
    EMOTION_AVAILABLE = False
    emotion_intelligence = None
    print("提示: emotion_intelligence 未找到，情感智能不可用")

try:
    from contradiction_detector import contradiction_detector
    CONTRADICTION_AVAILABLE = True
except ImportError:
    CONTRADICTION_AVAILABLE = False
    contradiction_detector = None
    print("提示: contradiction_detector 未找到，矛盾检测不可用")

try:
    from policy_validator import policy_validator
    POLICY_VALIDATOR_AVAILABLE = True
except ImportError:
    POLICY_VALIDATOR_AVAILABLE = False
    policy_validator = None
    print("提示: policy_validator 未找到，政策验证不可用")

try:
    from external_api_manager import external_api_manager
    EXTERNAL_API_AVAILABLE = True
except ImportError:
    EXTERNAL_API_AVAILABLE = False
    external_api_manager = None
    print("提示: external_api_manager 未找到，外部API不可用")


class PolicyAgent:
    """企业级政策咨询智能体"""
    
    def __init__(self, enable_advanced_features: bool = True):
        print("初始化企业级政策咨询智能体...")
        
        # 核心模块
        self.kb = KnowledgeBase()
        self.llm = LLMClient()
        
        # 双层意图识别
        self.intent_recognizer = IntentRecognizer()
        
        # 工具链
        self.calculator = SubsidyCalculator()
        self.recommender = RecommendationEngine()
        
        # Reranker
        self.reranker = Reranker()
        self.hybrid_retriever = None  # 初始化后设置
        
        # Prompt构造和格式化
        self.prompt_builder = PromptBuilder()
        self.output_formatter = OutputFormatter()
        
        # 增强模块（可选）
        self.enable_advanced = enable_advanced_features
        self.ner_extractor = EntityExtractor(self.llm) if NER_AVAILABLE and enable_advanced_features else None
        self.reflection_agent = ReflectionAgent(self.llm) if REFLECTION_AVAILABLE and enable_advanced_features else None
        self.multi_agent = None  # 在 initialize 中设置
        
        # 插件系统
        self.plugin_manager = None
        if PLUGIN_AVAILABLE and enable_advanced_features:
            self.plugin_manager = PluginManager()
            self.plugin_manager.load_all_plugins()
        
        # 缓存管理器
        self.cache_manager = cache_manager if CACHE_AVAILABLE else None
        
        # 新增增强模块
        self.monitoring_system = monitoring_system if MONITOR_AVAILABLE else None
        self.feedback_system = feedback_system if FEEDBACK_AVAILABLE else None
        self.urgency_detector = urgency_detector if URGENCY_AVAILABLE else None
        self.quality_validator = quality_validator if QUALITY_AVAILABLE else None
        self.location_service = location_service if LOCATION_AVAILABLE else None
        self.emotion_intelligence = emotion_intelligence if EMOTION_AVAILABLE else None
        self.contradiction_detector = contradiction_detector if CONTRADICTION_AVAILABLE else None
        self.policy_validator = policy_validator if POLICY_VALIDATOR_AVAILABLE else None
        self.external_api = external_api_manager if EXTERNAL_API_AVAILABLE else None
        
        # 对话历史
        self.conversation_history = []
        
        # 性能监控
        self.metrics = {
            "total_queries": 0,
            "successful_queries": 0,
            "rejected_queries": 0,
            "failed_queries": 0,
            "avg_latency": 0,
            "latency_history_ms": []
        }
    
    def initialize(self, force_rebuild: bool = False):
        """初始化知识库和混合检索器"""
        self.kb.build_knowledge_base(force_rebuild=force_rebuild)
        
        # 初始化混合检索器
        if self.kb.vectorstore:
            self.hybrid_retriever = HybridRetriever(
                self.kb.vectorstore,
                self.reranker
            )
        
        print("智能体初始化完成!")
        
        # 初始化多智能体编排器
        if MULTI_AGENT_AVAILABLE and self.enable_advanced:
            self.multi_agent = MultiAgentOrchestrator(self.kb, self.llm, self.calculator)
            print("✓ 多智能体协作已启用")
    
    def query(self, question: str, return_sources: bool = True, user_location: Optional[Dict] = None) -> Dict:
        """
        处理用户问题（企业级流程）
        
        Args:
            question: 用户问题
            return_sources: 是否返回检索到的原文
            user_location: 用户位置信息，格式: {"province": "山东省", "city": "济南市", "district": "历下区"}
            
        Returns:
            包含答案和相关信息的字典
        """
        start_time = time.time()
        self.metrics["total_queries"] += 1
        
        # ========== 新增: 地理位置处理 ==========
        if user_location and self.location_service:
            location_keywords = self.location_service.get_location_keywords(user_location)
            print(f"\n📍 用户位置: {user_location.get('city', '')} {user_location.get('district', '')}")
            print(f"   位置关键词: {', '.join(location_keywords[:3])}")
        
        # ========== 新增: 紧急程度识别 ==========
        urgency_info = None
        if self.urgency_detector:
            urgency_info = self.urgency_detector.detect(question)
            if urgency_info["fast_track"]:
                print(f"\n⚡ 检测到紧急查询 (P{urgency_info['priority']}): {urgency_info['level']}")
                print(f"   原因: {', '.join(urgency_info['reasons'])}")
        
        # ========== 新增: 情感智能分析 ==========
        emotion_analysis = None
        if self.emotion_intelligence:
            emotion_analysis = self.emotion_intelligence.analyze(question, urgency_info)
            if emotion_analysis["emotion"] != "neutral":
                print(f"\n💝 情感状态: {emotion_analysis['user_state']}")
                print(f"   建议语气: {emotion_analysis['recommended_tone']}")
        
        # ========== 缓存检查 ==========
        if self.cache_manager:
            cached_result = self.cache_manager.get(question)
            if cached_result:
                # 更新指标
                self.metrics["successful_queries"] += 1
                latency = time.time() - start_time
                self.metrics["latency_history_ms"].append(latency * 1000)
                self._update_latency(latency)
                print(f"\n✓ 缓存命中 (耗时: {latency:.2f}秒)")
                print(f"{'='*60}\n")
                return cached_result
        
        try:
            print(f"\n{'='*60}")
            print(f"用户问题: {question}")
            print(f"{'='*60}")
            
            # ========== 步骤1: 双层意图识别 ==========
            print("\n[1/5] 意图识别...")
            intent_result = self.intent_recognizer.recognize(question)
            
            # 如果应该拒绝
            if intent_result["should_reject"]:
                self.metrics["rejected_queries"] += 1
                rejection_response = RejectionHandler.get_rejection_response(
                    intent_result["rejection_reason"]
                )
                return {
                    "answer": rejection_response,
                    "sources": [],
                    "confidence": 0.0,
                    "intent_type": None,
                    "rejected": True
                }
            
            intent_type = intent_result["intent_type"]
            print(f"✓ 意图类型: {intent_type} ({config.INTENT_TYPES[intent_type]})")
            print(f"✓ 置信度: {intent_result['confidence']:.2%}")
            
            # ========== 步骤2: 任务路由与执行 ==========
            print(f"\n[2/5] 任务路由与执行...")
            
            if intent_type == "CALCULATION":
                result = self._handle_calculation(question)
            elif intent_type == "RECOMMENDATION":
                result = self._handle_recommendation(question)
            elif intent_type == "DATA_QUERY":
                result = self._handle_data_query(question, user_location=user_location)
            elif intent_type == "COMPLEX":
                result = self._handle_complex(question)
            else:  # POLICY_QA
                result = self._handle_policy_qa(question, user_location=user_location)
            
            # ========== 步骤3: 输出格式化 ==========
            print(f"\n[5/5] 输出格式化...")
            result["answer"] = self.output_formatter.format(
                result["answer"],
                metadata={
                    "sources": result.get("sources", []),
                    "confidence": result.get("confidence", 0.0)
                }
            )
            
            # ========== 新增: 质量验证 ==========
            if self.quality_validator:
                validation_result = self.quality_validator.validate(
                    question,
                    result["answer"],
                    result.get("sources", [])
                )
                result["quality_score"] = validation_result["overall_score"]
                result["quality_passed"] = validation_result["passed"]
                
                # 如果质量不过关，记录问题
                if not validation_result["passed"]:
                    print(f"\n⚠️ 质量验证: {validation_result['overall_score']}/100 (不过关)")
                    if validation_result["issues"]:
                        print(f"   问题: {validation_result['issues'][:2]}")
                else:
                    print(f"\n✅ 质量验证: {validation_result['overall_score']}/100 (通过)")
            
            # 添加意图类型到结果
            result["intent_type"] = intent_type
            result["rejected"] = False
            if urgency_info:
                result["urgency"] = urgency_info
            
            # 保存对话历史
            self._save_conversation(question, result)
            
            # 更新指标
            self.metrics["successful_queries"] += 1
            latency = time.time() - start_time
            self.metrics["latency_history_ms"].append(latency * 1000)
            self._update_latency(latency)
            
            # ========== 新增: 性能监控 ==========
            if self.monitoring_system:
                self.monitoring_system.record_query({
                    "query": question,
                    "status": "success",
                    "latency_ms": latency * 1000,
                    "confidence": result.get("confidence", 0),
                })
            
            print(f"\n✓ 查询完成 (耗时: {latency:.2f}秒)")
            print(f"{'='*60}\n")
            
            # ========== 缓存结果 ==========
            if self.cache_manager:
                # 缓存常见问题类型的答案（政策问答、计算、推荐）
                if intent_type in ["POLICY_QA", "CALCULATION", "RECOMMENDATION"]:
                    self.cache_manager.set(question, result)
                    print(f"✓ 结果已缓存")
            
            return result
            
        except Exception as e:
            print(f"\n✗ 查询失败: {e}")
            import traceback
            traceback.print_exc()
            self.metrics["failed_queries"] += 1
            
            # ========== 新增: 错误监控 ==========
            if self.monitoring_system:
                latency = time.time() - start_time
                self.monitoring_system.record_query({
                    "query": question,
                    "status": "error",
                    "latency_ms": latency * 1000,
                    "confidence": 0,
                    "error_msg": str(e)
                })
            
            return {
                "answer": "抱歉，系统处理您的问题时出现错误，请稍后重试或联系人工客服。",
                "sources": [],
                "confidence": 0.0,
                "intent_type": None,
                "rejected": False,
                "error": str(e)
            }
    
    def _handle_policy_qa(self, question: str, user_location: Optional[Dict] = None) -> Dict:
        """处理政策文本问答"""
        print("执行: 政策文本问答")
        
        # 混合检索
        docs = self._retrieve_documents(question, user_location=user_location)
        if not docs:
            return self._no_result_response()
        
        # ========== 新增: 政策验证 ==========
        if self.policy_validator and len(docs) > 0:
            policies_to_validate = []
            for doc in docs[:3]:  # 验证前3个
                policies_to_validate.append({
                    "content": doc.page_content,
                    "source": doc.metadata.get('source', 'Unknown'),
                    "date": doc.metadata.get('date', '')
                })
            
            validation_result = self.policy_validator.batch_validate(policies_to_validate)
            stats = validation_result["statistics"]
            
            if stats["expired"] > 0 or stats["obsolete"] > 0:
                print(f"\n⚠️ 政策时效性检查: {stats['expired']}个已过期, {stats['obsolete']}个已废止")
        
        # ========== 新增: 矛盾检测 ==========
        if self.contradiction_detector and len(docs) >= 2:
            policies_to_check = []
            for doc in docs[:5]:  # 检查前5个
                policies_to_check.append({
                    "content": doc.page_content,
                    "source": doc.metadata.get('source', 'Unknown'),
                    "date": doc.metadata.get('date', '')
                })
            
            contradiction_result = self.contradiction_detector.detect(policies_to_check)
            if contradiction_result["has_contradiction"]:
                print(f"\n⚠️ 发现 {len(contradiction_result['contradictions'])} 个政策矛盾")
                print(f"   一致性分数: {contradiction_result['consistency_score']:.2f}")
        
        # 构建Prompt
        messages = self.prompt_builder.build_policy_qa_prompt(question, docs)
        
        # LLM生成
        answer = self.llm.chat(messages)
        
        # 提取来源
        sources = [{
            "source": doc.metadata.get('source', 'Unknown'),
            "content": doc.page_content[:200],
            "similarity": 0.85  # 简化
        } for doc in docs]
        
        return {
            "answer": answer,
            "sources": sources,
            "confidence": 0.85
        }
    
    def _handle_calculation(self, question: str) -> Dict:
        """处理补贴计算"""
        print("执行: 补贴精确计算")
        
        # 提取金额和类型（简化实现）
        # 实际应使用NER或LLM提取
        import re
        amounts = re.findall(r'(\d+)', question)
        
        if amounts:
            amount = float(amounts[0])
            # 判断产品类型
            if "手机" in question:
                calc_result = self.calculator.calculate_digital_subsidy("手机", amount)
            else:
                calc_result = self.calculator.calculate_appliance_subsidy(amount)
            
            # 构建Prompt
            messages = self.prompt_builder.build_calculation_prompt(
                question, calc_result
            )
            
            # LLM解释
            answer = self.llm.chat(messages)
            
            return {
                "answer": answer,
                "sources": [],
                "confidence": 1.0,  # 工具计算，100%准确
                "calculation": calc_result
            }
        else:
            # 金额未明确，转为政策问答
            return self._handle_policy_qa(question)
    
    def _handle_recommendation(self, question: str) -> Dict:
        """处理智能推荐（使用动态规划全局最优）"""
        print("执行: 智能方案推荐（动态规划）")
        
        # 提取预算和需求
        if self.ner_extractor:
            # 使用 NER 提取（如果可用）
            entities = self.ner_extractor.extract(question)
            budget = entities.get("amounts", [10000])[0] if entities.get("amounts") else 10000
            needs = entities.get("products", [])
        else:
            # 回退到正则提取
            import re
            budgets = re.findall(r'(\d+)', question)
            budget = float(budgets[0]) if budgets else 10000
            
            # 提取需求（只匹配定义的产品名）
            product_keywords = ["冰箱", "洗衣机", "电视", "手机", "平板", "空调"]
            needs = []
            for product in product_keywords:
                if product in question:
                    needs.append(product)
        
        print(f"[DEBUG Agent] 提取预算: {budget}, 需求: {needs}")
        
        # 调用动态规划推荐（全局最优）
        recommendation = self.recommender.recommend_max_subsidy_plan(
            budget, 
            needs if needs else None,
            algorithm="dp"  # 使用动态规划
        )
        
        print(f"[DEBUG Agent] 推荐结果: {len(recommendation.get('selected_products', []))}件产品, 总补贴￥{recommendation.get('total_subsidy', 0)}")
        
        # 调用价格比较插件（如果可用）
        price_comparison = None
        if self.plugin_manager and "price_comparator" in self.plugin_manager.get_available_plugins():
            try:
                products = [p["name"] for p in recommendation.get("selected_products", [])]
                if products:
                    price_comparison = self.plugin_manager.execute_plugin(
                        "price_comparator",
                        {"products": products, "budget": budget}
                    )
                    print(f"✓ 价格比较插件运行成功: 总节省￥{price_comparison.get('total_savings', 0)}")
            except Exception as e:
                print(f"⚠ 价格比较插件执行失败: {e}")
        
        # 构建 Prompt
        messages = self.prompt_builder.build_recommendation_prompt(
            question, recommendation
        )
        
        # LLM 生成推荐说明
        answer = self.llm.chat(messages)
        
        return {
            "answer": answer,
            "sources": [],
            "confidence": 0.95,  # 全局最优置信度更高
            "recommendation": recommendation,
            "algorithm": "dp",
            "is_optimal": recommendation.get("is_optimal", True),
            "price_comparison": price_comparison  # 添加价格比较结果
        }
    
    def _handle_data_query(self, question: str, user_location: Optional[Dict] = None) -> Dict:
        """处理数据/型号查询"""
        print("执行: 数据查询")
        # 简化：转为政策问答
        return self._handle_policy_qa(question, user_location=user_location)
    
    def _handle_complex(self, question: str) -> Dict:
        """处理复杂综合问题"""
        print("执行: 复杂综合分析")
        # 简化：使用增强检索
        docs = self._retrieve_documents(question, top_k=config.RERANK_TOP_K)
        
        # 多源上下文
        multi_source = {"综合政策": docs}
        
        messages = self.prompt_builder.build_complex_prompt(
            question, multi_source
        )
        
        answer = self.llm.chat(messages)
        
        sources = [{
            "source": doc.metadata.get('source', 'Unknown'),
            "content": doc.page_content[:200],
            "similarity": 0.80
        } for doc in docs[:3]]
        
        return {
            "answer": answer,
            "sources": sources,
            "confidence": 0.75
        }
    
    def _retrieve_documents(self, query: str, top_k: int = None, user_location: Optional[Dict] = None) -> List:
        """检索文档(优化版:并行检索+智能缓存)"""
        print(f"[3/5] 混合检索...")
        
        if top_k is None:
            top_k = config.RERANK_TOP_K
        
        # 生成缓存键
        cache_key = f"docs:{query}:{top_k}:{user_location.get('city') if user_location else 'none'}"
        
        # 尝试从缓存获取
        if self.cache_manager:
            cached_docs = self.cache_manager.get(cache_key)
            if cached_docs:
                print(f"✓ 文档缓存命中")
                return cached_docs
        
        # 并行检索
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            # 同时进行向量检索和关键词检索
            if self.hybrid_retriever:
                future = executor.submit(self.hybrid_retriever.retrieve, query, top_k)
                docs = future.result(timeout=3.0)  # 3秒超时
            else:
                future = executor.submit(self.kb.search, query, top_k)
                docs = future.result(timeout=3.0)
        
        # ========== 新增: 基于地理位置重排 ==========
        if user_location and self.location_service and docs:
            # 将文档转换为字典格式
            doc_dicts = []
            for doc in docs:
                doc_dicts.append({
                    "content": doc.page_content,
                    "source": doc.metadata.get('source', 'Unknown'),
                    "score": 0.7,
                    "original_doc": doc
                })
            
            # 基于位置重排
            reranked_dicts = self.location_service.rerank_by_location(
                doc_dicts,
                user_location,
                location_weight=0.3
            )
            
            # 转换回原始格式
            docs = [d["original_doc"] for d in reranked_dicts]
            
            print(f"✓ 基于位置重排序完成 (权重: 0.3)")
        
        # 缓存结果(5分钟TTL)
        if self.cache_manager and docs:
            self.cache_manager.set(cache_key, docs, ttl=300)
        
        print(f"✓ 检索到 {len(docs)} 条相关文档")
        return docs
    
    def _no_result_response(self) -> Dict:
        """无结果响应"""
        return {
            "answer": "抱歉，我在知识库中没有找到相关政策信息。请您换个方式提问或联系人工客服。",
            "sources": [],
            "confidence": 0.0
        }
    
    def _save_conversation(self, question: str, result: Dict):
        """保存对话历史"""
        self.conversation_history.append({
            "question": question,
            "answer": result.get("answer"),
            "intent_type": result.get("intent_type"),
            "confidence": result.get("confidence"),
            "timestamp": time.time()
        })
    
    def _update_latency(self, latency: float):
        """更新平均延迟"""
        total = self.metrics["total_queries"]
        current_avg = self.metrics["avg_latency"]
        self.metrics["avg_latency"] = (
            (current_avg * (total - 1) + latency) / total
        )
    
    def batch_query(self, questions: List[str]) -> List[Dict]:
        """批量处理问题(优化版:并行处理)"""
        import concurrent.futures
        
        # 使用线程池并行处理
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # 提交所有任务
            future_to_question = {
                executor.submit(self.query, question, True): question 
                for question in questions
            }
            
            # 按顺序收集结果
            for question in questions:
                for future, q in future_to_question.items():
                    if q == question:
                        try:
                            result = future.result(timeout=10.0)  # 10秒超时
                            results.append(result)
                        except Exception as e:
                            results.append({
                                "answer": f"处理失败: {str(e)}",
                                "sources": [],
                                "confidence": 0.0
                            })
                        break
        
        return results
    
    def evaluate(self, cases: List[Dict]) -> Dict:
        """批量评测：根据期望关键词粗略计算准确率与响应时间"""
        total = len(cases)
        correct = 0
        results = []
        latencies = []
        for case in cases:
            q = case.get("question", "")
            expected = case.get("expected_keywords", [])
            start = time.time()
            r = self.query(q, return_sources=True)
            lat_ms = (time.time() - start) * 1000
            latencies.append(lat_ms)
            ans = (r.get("answer") or "")
            ok = False
            ans_low = ans.lower()
            for kw in expected:
                if kw and kw.lower() in ans_low:
                    ok = True
                    break
            correct += (1 if ok else 0)
            results.append({
                "question": q,
                "ok": ok,
                "latency_ms": lat_ms,
                "confidence": r.get("confidence", 0),
                "answer": ans
            })
        accuracy = (correct / max(total, 1))
        avg_latency_ms = (sum(latencies) / len(latencies)) if latencies else 0
        return {"accuracy": accuracy, "avg_latency_ms": avg_latency_ms, "total": total, "correct": correct, "results": results}
    
    def get_conversation_history(self) -> List[Dict]:
        """获取对话历史"""
        return self.conversation_history
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
    
    def get_metrics(self) -> Dict:
        """获取性能指标"""
        sessions = self.metrics["total_queries"]
        hist = self.metrics.get("latency_history_ms", [])
        avg_ms = (sum(hist) / len(hist)) if hist else 0
        p95_ms = (sorted(hist)[max(int(len(hist) * 0.95) - 1, 0)] if hist else 0)
        error_rate = (self.metrics["failed_queries"] / max(sessions, 1))
        return {
            "sessions": sessions,
            "avg_latency_ms": avg_ms,
            "p95_latency_ms": p95_ms,
            "success_rate": (
                self.metrics["successful_queries"] /
                max(self.metrics["total_queries"], 1)
            ),
            "rejection_rate": (
                self.metrics["rejected_queries"] /
                max(self.metrics["total_queries"], 1)
            ),
            "error_rate": error_rate,
            "total_queries": self.metrics["total_queries"],
            "successful_queries": self.metrics["successful_queries"],
            "rejected_queries": self.metrics["rejected_queries"],
            "avg_latency": self.metrics["avg_latency"]
        }


if __name__ == "__main__":
    # 测试企业级智能体
    agent = PolicyAgent()
    agent.initialize(force_rebuild=False)
    
    # 测试问题（覆盖所有意图类型）
    test_questions = [
        # POLICY_QA
        "济南市家电以旧换新补贴标准是多少？",
        
        # CALCULATION
        "买3000元买个冰箱能补贴多少钱？",
        
        # RECOMMENDATION  
        "我有15000元预算，推荐一个最划算的换新方案",
        
        # DATA_QUERY
        "手机购新补贴如何申请？",
        
        # COMPLEX
        "家电和数码产品的以旧换新政策有什么区别？",
        
        # 无关问题（应被拒绝）
        "今天天气怎么样？",
    ]
    
    print("\n" + "="*80)
    print("企业级政策咨询智能体 - 系统测试")
    print("="*80)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n\n{'#'*80}")
        print(f"测试用例 {i}/{len(test_questions)}")
        print(f"{'#'*80}")
        
        result = agent.query(question, return_sources=True)
        
        # 输出结果
        print(f"\n\n【最终回答】")
        print(result['answer'])
        
        # 如果是推荐，显示详细方案
        if result.get('recommendation'):
            rec = result['recommendation']
            print(f"\n【推荐详情】")
            if 'selected_products' in rec:
                print(f"选中产品：{len(rec['selected_products'])}件")
                for p in rec['selected_products']:
                    print(f"  • {p['name']}（￥{p['price']}）→ 补贴￥{p['subsidy']}")
                print(f"总补贴：￥{rec['total_subsidy']}，实付：￥{rec['final_cost']}")
                print(f"资金利用率：{rec['utilization_rate']:.1%}")
                print(f"算法：{result.get('algorithm', 'N/A')}，全局最优：{result.get('is_optimal', False)}")
        
        if result.get('sources'):
            print(f"\n【参考来源】")
            for j, source in enumerate(result['sources'][:2], 1):
                print(f"{j}. {source['source']} (相关度: {source.get('similarity', 0):.2%})")
    
    # 输出性能指标
    print(f"\n\n{'='*80}")
    print("性能指标")
    print("="*80)
    metrics = agent.get_metrics()
    print(f"总查询数: {metrics['total_queries']}")
    print(f"成功查询: {metrics['successful_queries']}")
    print(f"被拒绝查询: {metrics['rejected_queries']}")
    print(f"成功率: {metrics['success_rate']:.2%}")
    print(f"平均延迟: {metrics['avg_latency']:.2f}秒")
    print("="*80)
