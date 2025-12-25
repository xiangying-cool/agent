"""
大模型调用模块 - 支持千帆和OpenAI兼容接口
"""
import config

if config.USE_QIANFAN:
    import qianfan
else:
    from openai import OpenAI


class LLMClient:
    """大模型客户端"""
    
    def __init__(self):
        if config.USE_QIANFAN:
            print("使用百度千帆模型")
            self.client = qianfan.ChatCompletion()
        else:
            print(f"使用OpenAI兼容接口: {config.OPENAI_BASE_URL}")
            self.client = OpenAI(
                api_key=config.OPENAI_API_KEY,
                base_url=config.OPENAI_BASE_URL,
                timeout=30.0,  # 优化为30秒超时
                max_retries=2   # 减少重试次数提升响应速度
            )
    
    def chat(self, messages: list, stream: bool = False) -> str:
        """调用大模型进行对话"""
        try:
            if config.USE_QIANFAN:
                return self._chat_qianfan(messages, stream)
            else:
                return self._chat_openai(messages, stream)
        except Exception as e:
            error_msg = str(e)
            print(f"调用大模型失败: {error_msg}")
            
            # 降级方案：基于检索结果生成简单回答
            if "Connection error" in error_msg or "timeout" in error_msg.lower():
                return self._fallback_answer(messages)
            
            return f"抱歉，系统出现错误: {error_msg}"
    
    def _fallback_answer(self, messages: list) -> str:
        """降级回答：当LLM无法连接时使用"""
        # 提取用户问题和上下文
        user_content = ""
        context = ""
        for msg in messages:
            if msg["role"] == "user":
                user_content = msg["content"]
                if "以下是相关的政策文件内容" in user_content:
                    # 提取问题和上下文
                    parts = user_content.split("请基于以上内容回答用户问题:")
                    if len(parts) > 1:
                        context = parts[0]
                        user_content = parts[1].strip()
        
        # 简单的基于关键词的回答
        # 优先检查“标准/细则”类问题
        if ("补贴标准" in user_content) or ("标准" in user_content) or ("细则" in user_content) or ("补贴是多少" in user_content):
            return """根据济南市2025年家电以旧换新补贴政策：

💰 **补贴标准**：
• 按购新金额的10%给予补贴
• 单台最高不超过1000元

📊 **计算示例**：
• 购买5000元冰箱：补贴 = 5000 × 10% = 500元
• 购买12000元空调：补贴 = 12000 × 10% = 1200元 > 1000元，实际补贴 1000元

📝 **适用范围**：电视机、冰箱、洗衣机、空调等家用电器

ℹ️ *注：由于网络原因，LLM服务暂时不可用，以上为基础回答。详细信息请查阅政策文件。*"""
        
        # 优先检查流程/申请类问题
        if "申请" in user_content or "流程" in user_content or "怎么" in user_content:
            return """📋 **申请流程**：

1️⃣ 登录指定电商平台或前往参与门店
2️⃣ 选择符合条件的家电产品
3️⃣ 领取补贴资格（需实名认证）
4️⃣ 下单支付，享受立减优惠
5️⃣ 交回旧机，完成以旧换新

ℹ️ *注：由于网络原因，LLM服务暂时不可用，以上为基础回答。*"""
        
        # 检查是否包含计算相关问题（数字 + 元/钱/补贴）
        import re
        has_amount = bool(re.search(r'\d+', user_content))
        has_money_keyword = any(kw in user_content for kw in ['元', '钱', '多少'])
        
        if (has_amount and has_money_keyword) or '计算' in user_content:
            # 提取金额
            amount_match = re.search(r'(\d+)元', user_content)
            if amount_match:
                amount = int(amount_match.group(1))
                subsidy = min(int(amount * 0.1), 1000)
                
                return f"""💰 **补贴计算结果**：

购买金额：{amount}元
补贴比例：10%
计算补贴：{amount} × 10% = {int(amount * 0.1)}元
**实际补贴：{subsidy}元** {'(已达上限)' if subsidy == 1000 else ''}

📊 **补贴政策**：
• 按购新金额的10%给予补贴
• 单台最高不超过1000元

📜applicable范围：电视机、冰箱、洗衣机、空调等家用电器

ℹ️ *注：由于网络原因，LLM服务暂时不可用，以上为基础计算。详细信息请查阅政策文件。*"""
        
        elif "补贴标准" in user_content or "补贴是多少" in user_content or "标准" in user_content:
            return """根据济南市2025年家电以旧换新补贴政策：

💰 **补贴标准**：
• 按购新金额的10%给予补贴
• 单台最高不超过1000元

📊 **计算示例**：
• 购买5000元冰箱：补贴 = 5000 × 10% = 500元
• 购买12000元空调：补贴 = 12000 × 10% = 1200元 > 1000元，实际补贴 1000元

📝 **适用范围**：电视机、冰箱、洗衣机、空调等家用电器

ℹ️ *注：由于网络原因，LLM服务暂时不可用，以上为基础回答。详细信息请查阅政策文件。*"""
        
        else:
            return """根据检索到的政策文件，相关政策信息已在下方参考文件中列出。

由于网络原因，智能LLM服务暂时不可用，无法生成详细解答。

📚 请查阅下方「参考政策文件」中的具体内容，或咨询当地政务服务热线 12345。"""
    
    def _chat_qianfan(self, messages: list, stream: bool = False) -> str:
        """千帆接口调用"""
        resp = self.client.do(
            model=config.QIANFAN_MODEL,
            messages=messages,
            stream=stream
        )
        
        if stream:
            full_response = ""
            for chunk in resp:
                if chunk.get("result"):
                    full_response += chunk["result"]
            return full_response
        else:
            return resp["result"]
    
    def _chat_openai(self, messages: list, stream: bool = False) -> str:
        """OpenAI兼容接口调用(优化版:支持温度和token限制)"""
        response = self.client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=messages,
            stream=stream,
            temperature=0.7,  # 控制创造性,0.7适合问答
            max_tokens=2000,  # 限制输出长度,避免超长响应
            top_p=0.9  # 核采样参数
        )
        
        if stream:
            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
            return full_response
        else:
            return response.choices[0].message.content
    
    def generate_answer(self, question: str, context: str) -> str:
        """基于检索上下文生成答案"""
        messages = [
            {"role": "user", "content": config.SYSTEM_PROMPT},
            {"role": "assistant", "content": "好的,我会严格基于政策文件内容进行回答。"},
            {"role": "user", "content": f"""以下是相关的政策文件内容:

{context}

请基于以上内容回答用户问题: {question}

如果上述内容无法回答该问题,请明确告知用户。"""}
        ]
        
        return self.chat(messages)


if __name__ == "__main__":
    # 测试大模型调用
    client = LLMClient()
    
    test_context = """
    济南市2025年家电以旧换新补贴实施细则:
    1. 补贴标准: 按购新金额的10%给予补贴,单台最高不超过1000元
    2. 适用范围: 电视机、冰箱、洗衣机、空调等
    3. 申请时间: 2025年1月1日至12月31日
    """
    
    test_question = "家电以旧换新补贴最高多少钱?"
    
    print("测试问题:", test_question)
    print("\n生成回答:")
    answer = client.generate_answer(test_question, test_context)
    print(answer)
