"""
多智能体协作系统
实现任务分解、专家协作、结果验证的多Agent工作流
"""
from typing import Dict, List
from llm_client import LLMClient
from knowledge_base import KnowledgeBase
from tools import SubsidyCalculator, RecommendationEngine
import json
import asyncio
import aiohttp
from datetime import datetime


class PlannerAgent:
    """规划Agent - 任务分解与执行计划"""
    
    def __init__(self, llm: LLMClient):
        self.llm = llm
    
    def plan(self, question: str, intent_type: str) -> Dict:
        """
        将复杂问题分解为子任务
        
        Returns:
            {
                "subtasks": [
                    {"task_id": 1, "type": "SEARCH", "query": "..."},
                    {"task_id": 2, "type": "CALCULATE", "params": {...}}
                ],
                "execution_order": [1, 2]
            }
        """
        if intent_type == "COMPLEX":
            # 使用 LLM 分解任务
            prompt = f"""请将以下复杂问题分解为可执行的子任务。

问题：{question}

请按 JSON 格式返回任务列表：
{{
    "subtasks": [
        {{"task_id": 1, "type": "SEARCH", "query": "查询家电补贴标准"}},
        {{"task_id": 2, "type": "SEARCH", "query": "查询数码补贴标准"}},
        {{"task_id": 3, "type": "COMPARE", "inputs": [1, 2]}},
        {{"task_id": 4, "type": "EVALUATE", "criteria": "性价比"}}
    ],
    "execution_order": [1, 2, 3, 4]
}}

任务类型可选：SEARCH（检索）、CALCULATE（计算）、COMPARE（对比）、EVALUATE（评估）、SUMMARIZE（总结）"""

            try:
                messages = [{"role": "user", "content": prompt}]
                response = self.llm.chat(messages)
                
                # 提取 JSON
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    plan = json.loads(json_match.group())
                    return plan
            except Exception as e:
                print(f"任务规划失败: {e}")
        
        # 简单任务直接返回单步执行
        return {
            "subtasks": [{"task_id": 1, "type": intent_type, "query": question}],
            "execution_order": [1]
        }


class ExecutorAgent:
    """执行Agent - 专业任务执行器"""
    
    def __init__(self, kb: KnowledgeBase, llm: LLMClient, calculator: SubsidyCalculator):
        self.kb = kb
        self.llm = llm
        self.calculator = calculator
    
    def execute_subtask(self, subtask: Dict) -> Dict:
        """执行单个子任务"""
        task_type = subtask.get("type")
        
        if task_type == "SEARCH" or task_type == "POLICY_QA":
            # 检索任务
            query = subtask.get("query", "")
            docs = self.kb.search(query, top_k=3)
            return {
                "task_id": subtask.get("task_id"),
                "type": "SEARCH",
                "results": [
                    {"source": doc.metadata.get("source"), "content": doc.page_content[:300]}
                    for doc in docs
                ]
            }
        
        elif task_type == "CALCULATE" or task_type == "CALCULATION":
            # 计算任务
            params = subtask.get("params", {})
            amount = params.get("amount", 0)
            result = self.calculator.calculate_appliance_subsidy(amount)
            return {
                "task_id": subtask.get("task_id"),
                "type": "CALCULATE",
                "results": result
            }
        
        elif task_type == "COMPARE":
            # 对比任务（需要依赖前置任务结果）
            return {
                "task_id": subtask.get("task_id"),
                "type": "COMPARE",
                "results": {"message": "对比任务需要前置结果"}
            }
        
        elif task_type == "EVALUATE":
            # 评估任务
            criteria = subtask.get("criteria", "性价比")
            return {
                "task_id": subtask.get("task_id"),
                "type": "EVALUATE",
                "results": {"message": f"正在根据{criteria}进行评估"}
            }
        
        else:
            return {
                "task_id": subtask.get("task_id"),
                "type": "UNKNOWN",
                "results": {"error": f"未知任务类型: {task_type}"}
            }


class VerifierAgent:
    """验证Agent - 结果一致性检查"""
    
    def __init__(self, llm: LLMClient):
        self.llm = llm
    
    def verify(self, question: str, answer: str, sources: List[Dict]) -> Dict:
        """
        验证答案是否与检索来源一致
        
        Returns:
            {
                "is_consistent": bool,
                "confidence": float,
                "issues": List[str]
            }
        """
        if not sources:
            return {
                "is_consistent": True,
                "confidence": 0.5,
                "issues": ["无来源可验证"]
            }
        
        # 使用 LLM 验证答案与来源的一致性
        sources_text = "\n\n".join([
            f"来源{i+1}：{s.get('content', '')[:200]}"
            for i, s in enumerate(sources[:3])
        ])
        
        prompt = f"""请验证答案是否与参考来源一致。

问题：{question}

答案：
{answer}

参考来源：
{sources_text}

请判断：
1. 答案是否基于来源内容？（是/否）
2. 是否存在幻觉或无依据的陈述？（是/否）
3. 置信度：0-100%

只回答：一致/不一致，置信度XX%"""

        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.llm.chat(messages)
            
            is_consistent = "一致" in response and "不一致" not in response
            
            # 提取置信度
            import re
            confidence_match = re.search(r'(\d+)%', response)
            confidence = float(confidence_match.group(1)) / 100 if confidence_match else 0.7
            
            return {
                "is_consistent": is_consistent,
                "confidence": confidence,
                "issues": [] if is_consistent else ["答案与来源不一致"]
            }
        except Exception as e:
            print(f"验证失败: {e}")
            return {
                "is_consistent": True,
                "confidence": 0.6,
                "issues": [f"验证异常: {str(e)}"]
            }


class MultiAgentOrchestrator:
    """多智能体编排器 - 协调各Agent协作"""
    
    def __init__(self, kb: KnowledgeBase, llm: LLMClient, calculator: SubsidyCalculator):
        self.planner = PlannerAgent(llm)
        self.executor = ExecutorAgent(kb, llm, calculator)
        self.verifier = VerifierAgent(llm)
        self.llm = llm
    
    def process(self, question: str, intent_type: str) -> Dict:
        """
        多智能体协作处理问题
        
        流程：
        1. Planner 分解任务
        2. Executor 执行各子任务
        3. LLM 综合结果
        4. Verifier 验证答案
        """
        print("\n[Multi-Agent] 启动多智能体协作...")
        
        # 步骤1: 规划
        print("[1/4] Planner Agent 规划任务...")
        plan = self.planner.plan(question, intent_type)
        subtasks = plan.get("subtasks", [])
        print(f"✓ 分解为 {len(subtasks)} 个子任务")
        
        # 步骤2: 执行
        print("[2/4] Executor Agent 执行子任务...")
        results = []
        for subtask in subtasks:
            result = self.executor.execute_subtask(subtask)
            results.append(result)
        print(f"✓ 完成 {len(results)} 个子任务")
        
        # 步骤3: 综合
        print("[3/4] LLM 综合结果...")
        summary_prompt = f"""基于以下子任务结果，回答用户问题。

问题：{question}

子任务结果：
{json.dumps(results, ensure_ascii=False, indent=2)}

请给出完整、准确的回答。"""
        
        messages = [{"role": "user", "content": summary_prompt}]
        answer = self.llm.chat(messages)
        
        # 步骤4: 验证
        print("[4/4] Verifier Agent 验证答案...")
        sources = []
        for result in results:
            if result.get("type") == "SEARCH":
                sources.extend(result.get("results", []))
        
        verification = self.verifier.verify(question, answer, sources)
        print(f"✓ 验证完成，置信度: {verification['confidence']:.2%}")
        
        return {
            "answer": answer,
            "sources": sources[:3],
            "confidence": verification["confidence"],
            "plan": plan,
            "verification": verification,
            "multi_agent": True
        }


if __name__ == "__main__":
    # 测试多智能体协作
    from knowledge_base import KnowledgeBase
    from llm_client import LLMClient
    from tools import SubsidyCalculator
    
    kb = KnowledgeBase()
    kb.build_knowledge_base(force_rebuild=False)
    llm = LLMClient()
    calculator = SubsidyCalculator()
    
    orchestrator = MultiAgentOrchestrator(kb, llm, calculator)
    
    # 测试复杂问题
    question = "家电和数码产品的以旧换新补贴标准有什么区别？"
    result = orchestrator.process(question, "COMPLEX")
    
    print("\n" + "="*60)
    print("【最终回答】")
    print(result["answer"])
    print("\n【置信度】", f"{result['confidence']:.2%}")
    print("="*60)
