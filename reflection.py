"""
反思链模块 - 自我纠错与答案优化
实现 ReAct (Reasoning + Acting) 模式
"""
from typing import Dict, List
from llm_client import LLMClient
import json


class ReflectionAgent:
    """反思Agent - 自我检查与纠错"""
    
    def __init__(self, llm: LLMClient = None):
        self.llm = llm or LLMClient()
        self.max_iterations = 3  # 最大反思次数
    
    def reflect_and_refine(self, question: str, answer: str, sources: List[Dict]) -> Dict:
        """
        反思链处理流程
        
        1. 生成初始答案
        2. 自我批判（找问题）
        3. 改进答案
        4. 重复 2-3 直到满意或达到最大次数
        
        Returns:
            {
                "final_answer": str,
                "iterations": int,
                "reflection_history": [...]
            }
        """
        current_answer = answer
        reflection_history = []
        
        for iteration in range(self.max_iterations):
            print(f"\n[反思 {iteration+1}/{self.max_iterations}]")
            
            # 步骤1: 自我批判
            critique = self._critique(question, current_answer, sources)
            print(f"批判: {critique.get('issues', [])}")
            
            reflection_history.append({
                "iteration": iteration + 1,
                "answer": current_answer,
                "critique": critique
            })
            
            # 如果没有问题，直接返回
            if critique.get("is_good", False):
                print("✓ 答案通过验证")
                break
            
            # 步骤2: 改进答案
            improved_answer = self._improve(question, current_answer, critique, sources)
            
            # 如果改进后与原答案相同，停止
            if improved_answer == current_answer:
                print("✓ 答案无法进一步改进")
                break
            
            current_answer = improved_answer
        
        return {
            "final_answer": current_answer,
            "iterations": len(reflection_history),
            "reflection_history": reflection_history,
            "improved": len(reflection_history) > 0 and not reflection_history[0]["critique"].get("is_good", False)
        }
    
    def _critique(self, question: str, answer: str, sources: List[Dict]) -> Dict:
        """
        自我批判：检查答案问题
        
        Returns:
            {
                "is_good": bool,
                "issues": List[str],
                "suggestions": List[str]
            }
        """
        sources_text = "\n\n".join([
            f"来源{i+1}：{s.get('content', '')[:200]}"
            for i, s in enumerate(sources[:3])
        ])
        
        prompt = f"""作为一个严格的审查员，请批判性地检查以下答案。

问题：{question}

答案：
{answer}

参考来源：
{sources_text}

请检查：
1. 答案是否准确回答了问题？
2. 是否存在与来源矛盾的信息？
3. 是否存在幻觉（无依据的陈述）？
4. 数字、金额、比例等是否准确？
5. 是否遗漏了重要信息？
6. 表达是否清晰、专业？

请以 JSON 格式回答：
{{
    "is_good": true/false,
    "issues": ["问题1", "问题2"],
    "suggestions": ["建议1", "建议2"]
}}

只返回 JSON，不要其他内容。"""

        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.llm.chat(messages)
            
            # 提取 JSON
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                critique = json.loads(json_match.group())
                return critique
        except Exception as e:
            print(f"批判失败: {e}")
        
        # 默认认为答案没问题
        return {
            "is_good": True,
            "issues": [],
            "suggestions": []
        }
    
    def _improve(self, question: str, current_answer: str, critique: Dict, sources: List[Dict]) -> str:
        """
        基于批判意见改进答案
        """
        issues = critique.get("issues", [])
        suggestions = critique.get("suggestions", [])
        
        if not issues and not suggestions:
            return current_answer
        
        sources_text = "\n\n".join([
            f"来源{i+1}：{s.get('content', '')[:200]}"
            for i, s in enumerate(sources[:3])
        ])
        
        prompt = f"""请根据批判意见改进答案。

问题：{question}

当前答案：
{current_answer}

批判意见：
- 问题：{', '.join(issues)}
- 建议：{', '.join(suggestions)}

参考来源：
{sources_text}

请生成改进后的答案（直接输出答案内容，不要解释）："""

        try:
            messages = [{"role": "user", "content": prompt}]
            improved = self.llm.chat(messages)
            return improved.strip()
        except Exception as e:
            print(f"改进失败: {e}")
            return current_answer


class ReActAgent:
    """ReAct Agent - 推理与行动结合"""
    
    def __init__(self, llm: LLMClient = None):
        self.llm = llm or LLMClient()
    
    def solve(self, question: str, tools: Dict) -> Dict:
        """
        ReAct 模式求解
        
        流程：
        Thought 1 -> Action 1 -> Observation 1 ->
        Thought 2 -> Action 2 -> Observation 2 ->
        ...
        -> Final Answer
        
        Args:
            question: 用户问题
            tools: 可用工具字典 {"search": func, "calculate": func}
        """
        max_steps = 5
        trajectory = []
        
        for step in range(max_steps):
            print(f"\n[Step {step+1}]")
            
            # 生成下一步行动
            action_plan = self._generate_action(question, trajectory)
            
            thought = action_plan.get("thought", "")
            action = action_plan.get("action", "")
            action_input = action_plan.get("action_input", {})
            
            print(f"Thought: {thought}")
            print(f"Action: {action}")
            
            # 如果决定结束
            if action == "FINISH":
                final_answer = action_input.get("answer", "")
                return {
                    "answer": final_answer,
                    "trajectory": trajectory,
                    "steps": step + 1
                }
            
            # 执行动作
            observation = self._execute_action(action, action_input, tools)
            print(f"Observation: {observation[:200]}...")
            
            # 记录轨迹
            trajectory.append({
                "step": step + 1,
                "thought": thought,
                "action": action,
                "action_input": action_input,
                "observation": observation
            })
        
        # 达到最大步数，强制结束
        return {
            "answer": "抱歉，问题过于复杂，无法在有限步骤内完成。",
            "trajectory": trajectory,
            "steps": max_steps
        }
    
    def _generate_action(self, question: str, trajectory: List[Dict]) -> Dict:
        """生成下一步行动"""
        history = "\n".join([
            f"Thought {t['step']}: {t['thought']}\nAction: {t['action']}\nObservation: {t['observation'][:100]}"
            for t in trajectory
        ])
        
        prompt = f"""你是一个智能助手，需要通过推理和行动来回答问题。

问题：{question}

已执行步骤：
{history if history else "（无）"}

可用工具：
- SEARCH: 检索政策文档
- CALCULATE: 计算补贴金额
- FINISH: 结束并给出最终答案

请按以下格式回答（JSON）：
{{
    "thought": "当前思考和推理",
    "action": "SEARCH/CALCULATE/FINISH",
    "action_input": {{"query": "..."}} 或 {{"amount": 3000}} 或 {{"answer": "最终答案"}}
}}

只返回 JSON，不要其他内容。"""

        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.llm.chat(messages)
            
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                plan = json.loads(json_match.group())
                return plan
        except Exception as e:
            print(f"行动生成失败: {e}")
        
        # 默认结束
        return {
            "thought": "无法继续",
            "action": "FINISH",
            "action_input": {"answer": "抱歉，处理出错。"}
        }
    
    def _execute_action(self, action: str, action_input: Dict, tools: Dict) -> str:
        """执行工具调用"""
        if action == "SEARCH" and "search" in tools:
            query = action_input.get("query", "")
            results = tools["search"](query)
            return f"检索到 {len(results)} 条结果：" + str(results[:2])
        
        elif action == "CALCULATE" and "calculate" in tools:
            amount = action_input.get("amount", 0)
            result = tools["calculate"](amount)
            return f"计算结果：{result}"
        
        else:
            return "无法执行该动作"


if __name__ == "__main__":
    # 测试反思链
    from llm_client import LLMClient
    
    llm = LLMClient()
    reflection_agent = ReflectionAgent(llm)
    
    question = "济南市家电以旧换新补贴标准是多少？"
    initial_answer = "济南市家电补贴标准为购买金额的10%，最高1000元。"
    sources = [
        {"content": "根据济南市实施细则，家电类产品补贴比例为购买金额的10%，单台最高补贴1000元..."}
    ]
    
    result = reflection_agent.reflect_and_refine(question, initial_answer, sources)
    
    print("\n" + "="*60)
    print("【最终答案】")
    print(result["final_answer"])
    print(f"\n【反思次数】{result['iterations']}")
    print(f"【是否改进】{result['improved']}")
    print("="*60)
