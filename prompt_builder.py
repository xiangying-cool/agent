"""
提示词构造器 - 根据不同任务类型构建专业Prompt
"""
from typing import List, Dict
from langchain.schema import Document
import config


class PromptBuilder:
    """提示词构造器"""
    
    def __init__(self):
        self.system_prompt = config.SYSTEM_PROMPT
    
    def build_policy_qa_prompt(self,
                              query: str,
                              context_docs: List[Document]) -> List[Dict]:
        """构建政策文本问答Prompt"""
        # 构建上下文
        context_parts = []
        for i, doc in enumerate(context_docs, 1):
            source = doc.metadata.get('source', 'Unknown')
            content = doc.page_content
            
            context_parts.append(f"""
【政策文件{i}】
来源：{source}
内容：
{content}
""")
        
        context = "\n".join(context_parts)
        
        user_prompt = f"""请基于以下政策文件回答用户问题。

{context}

【用户问题】
{query}

【回答要求】
1. 准确引用政策原文，标注来源
2. 使用结构化格式（分点、序号）
3. 如涉及金额、时间等关键信息，必须明确标注
4. 如果政策文件中没有明确答案，诚实告知用户
5. 结尾补充政策来源和咨询渠道

请开始回答："""
        
        return [
            {"role": "user", "content": self.system_prompt},
            {"role": "assistant", "content": "好的，我会严格基于政策文件内容，准确、专业地回答用户问题。"},
            {"role": "user", "content": user_prompt}
        ]
    
    def build_calculation_prompt(self,
                                query: str,
                                calculation_result: Dict) -> List[Dict]:
        """构建补贴计算Prompt"""
        # 将计算结果转换为自然语言
        result_text = f"""
【计算结果】
{calculation_result.get('calculation', '')}

补贴金额：¥{calculation_result.get('subsidy', 0):.2f}
"""
        
        user_prompt = f"""用户问题：{query}

我已使用精确计算工具得出结果：
{result_text}

请用专业、友好的语言向用户解释这个计算结果，包括：
1. 简洁总结补贴金额
2. 说明计算依据（补贴比例、上限等）
3. 补充注意事项
4. 提供相关建议

请开始回答："""
        
        return [
            {"role": "user", "content": self.system_prompt},
            {"role": "assistant", "content": "好的，我会清晰解释计算结果。"},
            {"role": "user", "content": user_prompt}
        ]
    
    def build_recommendation_prompt(self,
                                   query: str,
                                   recommendation: Dict) -> List[Dict]:
        """构建智能推荐Prompt（支持动态规划结果）"""
        
        # 判断是否是动态规划结果（多商品组合）
        if 'selected_products' in recommendation:
            # 动态规划结果格式
            products_list = ""
            for p in recommendation['selected_products']:
                products_list += f"\n  • {p['name']}（¥{p['price']}）→ 补贴¥{p['subsidy']}"
            
            rec_text = f"""
【最优方案】（全局最优解）
- 选中产品：{len(recommendation['selected_products'])}件{products_list}
- 总价格：¥{recommendation.get('total_price', 0)}
- 总补贴：¥{recommendation.get('total_subsidy', 0)}
- 实际支付：¥{recommendation.get('final_cost', 0)}
- 资金利用率：{recommendation.get('utilization_rate', 0):.1%}
- 算法类型：动态规划（保证全局最优）
"""
        else:
            # 贪心算法结果格式（单商品）
            rec_text = f"""
【推荐方案】
{recommendation.get('recommendation', '')}

详细信息：
- 推荐商品：{recommendation.get('best_plan', {}).get('product')}
- 购买价格：¥{recommendation.get('best_plan', {}).get('price')}
- 补贴金额：¥{recommendation.get('best_plan', {}).get('subsidy')}
- 实际支付：¥{recommendation.get('best_plan', {}).get('net_cost')}
"""
        
        user_prompt = f"""用户需求：{query}

我已分析得出最优方案：
{rec_text}

请向用户专业推荐这个方案，包括：
1. 方案亮点（为什么这是最优方案）
2. 补贴优势（对比单品购买，组合方案多获得多少补贴）
3. 性价比分析（资金利用率、产品多样性）
4. 购买建议和注意事项

请开始回答："""
        
        return [
            {"role": "user", "content": self.system_prompt},
            {"role": "assistant", "content": "好的，我会为用户推荐最优方案。"},
            {"role": "user", "content": user_prompt}
        ]
    
    def build_complex_prompt(self,
                            query: str,
                            multi_source_context: Dict) -> List[Dict]:
        """构建复杂综合类Prompt（跨政策对比等）"""
        # 整合多个来源的上下文
        contexts = []
        for source_name, docs in multi_source_context.items():
            context = f"\n【{source_name}】\n"
            for doc in docs:
                context += f"{doc.page_content}\n"
            contexts.append(context)
        
        combined_context = "\n".join(contexts)
        
        user_prompt = f"""请基于以下多个政策来源，综合分析回答用户问题。

{combined_context}

【用户问题】
{query}

【分析要求】
1. 对比不同政策的异同点
2. 识别并说明政策冲突（如有）
3. 给出综合建议
4. 标注各政策来源

请开始综合分析："""
        
        return [
            {"role": "user", "content": self.system_prompt},
            {"role": "assistant", "content": "好的，我会综合分析多个政策并给出专业建议。"},
            {"role": "user", "content": user_prompt}
        ]
    
    def build_rejection_prompt(self, reason: str) -> str:
        """构建拒绝回复（不调用LLM，直接返回模板）"""
        return f"""抱歉，{reason}

我只能为您解答"消费品以旧换新"相关的政策问题，包括：
✓ 家电、数码、汽车补贴政策
✓ 补贴标准和申请流程
✓ 产品型号和补贴金额查询
✓ 最优换新方案推荐

如需其他帮助，请咨询：
📞 政务服务热线：12345
🌐 官方政策网站

感谢您的理解！"""


class OutputFormatter:
    """输出格式化器 - 标准化LLM输出"""
    
    def __init__(self):
        self.config = config.OUTPUT_FORMAT
    
    def format(self, 
              raw_answer: str,
              metadata: Dict = None) -> str:
        """
        格式化输出
        
        Args:
            raw_answer: LLM原始回答
            metadata: 元数据（来源、时间、置信度等）
        """
        formatted = raw_answer
        
        # 1. 添加结构化标记
        if self.config["structured_output"]:
            formatted = self._add_structure(formatted)
        
        # 2. 添加元数据信息
        footer_parts = []
        
        if metadata:
            if self.config["add_source"] and "sources" in metadata:
                footer_parts.append(self._format_sources(metadata["sources"]))
            
            if self.config["add_confidence"] and "confidence" in metadata:
                footer_parts.append(
                    f"\n📊 置信度：{metadata['confidence']:.1%}"
                )
            
            if self.config["add_date"]:
                from datetime import datetime
                footer_parts.append(
                    f"\n⏰ 回答时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )
        
        # 3. 添加标准结尾
        footer_parts.append(self._get_standard_footer())
        
        # 组合输出
        if footer_parts:
            formatted += "\n\n" + "\n".join(footer_parts)
        
        return formatted
    
    def _add_structure(self, text: str) -> str:
        """添加结构化标记"""
        # 简单实现：确保有明确的段落分隔
        # 实际可以更智能地识别和格式化
        return text
    
    def _format_sources(self, sources: List[Dict]) -> str:
        """格式化来源信息"""
        if not sources:
            return ""
        
        source_text = "\n📚 参考政策文件："
        for i, source in enumerate(sources[:3], 1):
            source_name = source.get('source', 'Unknown')
            similarity = source.get('similarity', 0)
            source_text += f"\n  {i}. {source_name} (相关度: {similarity:.1%})"
        
        return source_text
    
    def _get_standard_footer(self) -> str:
        """获取标准结尾"""
        return """
---
💡 温馨提示：
• 政策具体执行以官方最新通知为准
• 如有疑问，请咨询当地政务服务热线 12345
• 本智能体提供7×24小时政策咨询服务

❓ 如需进一步帮助，请继续提问。"""


if __name__ == "__main__":
    # 测试提示词构造
    from langchain.schema import Document
    
    builder = PromptBuilder()
    formatter = OutputFormatter()
    
    print("="*60)
    print("提示词构造器测试")
    print("="*60)
    
    # 测试1: 政策问答Prompt
    print("\n【测试1】政策问答Prompt")
    test_docs = [
        Document(
            page_content="补贴标准：按购新金额的10%给予补贴，单台最高1000元",
            metadata={"source": "补贴政策.pdf"}
        )
    ]
    messages = builder.build_policy_qa_prompt(
        "家电补贴标准是多少？",
        test_docs
    )
    print(f"消息数：{len(messages)}")
    print(f"用户Prompt预览：\n{messages[-1]['content'][:200]}...")
    
    # 测试2: 输出格式化
    print("\n【测试2】输出格式化")
    raw_answer = "根据政策，家电补贴为购买金额的10%，单台最高1000元。"
    metadata = {
        "sources": [{"source": "政策文件.pdf", "similarity": 0.95}],
        "confidence": 0.92
    }
    formatted = formatter.format(raw_answer, metadata)
    print(formatted)
    
    print("\n" + "="*60)
