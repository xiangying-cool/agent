"""
响应压缩插件 - 智能答案精简
在保持信息完整的前提下压缩响应长度，提升传输速度
"""
from typing import Dict, Any
import re


class Plugin:
    """响应压缩插件"""
    
    @property
    def name(self) -> str:
        return "response_compressor"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "智能压缩响应内容，去除冗余信息，提升传输效率"
    
    def on_load(self):
        print(f"[{self.name}] 响应压缩引擎已启动")
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行响应压缩
        
        输入 context:
        {
            "answer": "原始答案",
            "compression_level": "low|medium|high",  # 压缩等级
            "preserve_format": True  # 是否保留格式
        }
        
        输出:
        {
            "compressed_answer": "压缩后的答案",
            "original_length": 1000,
            "compressed_length": 600,
            "compression_ratio": 0.40,
            "tokens_saved": 400
        }
        """
        answer = context.get("answer", "")
        compression_level = context.get("compression_level", "medium")
        preserve_format = context.get("preserve_format", True)
        
        if not answer.strip():
            return {
                "compressed_answer": answer,
                "original_length": 0,
                "compressed_length": 0,
                "compression_ratio": 0.0,
                "tokens_saved": 0
            }
        
        original_length = len(answer)
        compressed = answer
        
        # 根据压缩等级应用不同策略
        if compression_level == "high":
            compressed = self._high_compression(compressed, preserve_format)
        elif compression_level == "medium":
            compressed = self._medium_compression(compressed, preserve_format)
        else:  # low
            compressed = self._low_compression(compressed, preserve_format)
        
        compressed_length = len(compressed)
        compression_ratio = (original_length - compressed_length) / original_length if original_length > 0 else 0.0
        tokens_saved = original_length - compressed_length
        
        return {
            "compressed_answer": compressed,
            "original_length": original_length,
            "compressed_length": compressed_length,
            "compression_ratio": round(compression_ratio, 2),
            "tokens_saved": tokens_saved
        }
    
    def _low_compression(self, text: str, preserve_format: bool) -> str:
        """低压缩 - 只去除明显冗余"""
        # 去除多余空行
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 去除多余空格
        text = re.sub(r' {2,}', ' ', text)
        
        return text.strip()
    
    def _medium_compression(self, text: str, preserve_format: bool) -> str:
        """中压缩 - 平衡信息与长度"""
        text = self._low_compression(text, preserve_format)
        
        # 简化重复的客套话
        text = re.sub(r'(根据|依据|按照)(相关|最新|现行)政策(规定|要求|标准)', '根据政策', text)
        
        # 简化冗长表述
        replacements = {
            "您可以通过以下方式": "可通过",
            "需要满足以下条件": "需满足",
            "请您按照以下步骤": "步骤",
            "具体如下所示": "如下",
            "详细信息如下": "详情",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text.strip()
    
    def _high_compression(self, text: str, preserve_format: bool) -> str:
        """高压缩 - 极致精简"""
        text = self._medium_compression(text, preserve_format)
        
        # 移除示例说明（保留核心信息）
        if not preserve_format:
            text = re.sub(r'(举例|例如|比如)[:：][^。\n]+[。\n]', '', text)
        
        # 移除补充说明
        text = re.sub(r'(注意|提示|温馨提示)[:：][^。\n]+[。\n]', '', text)
        
        # 压缩列表格式
        text = re.sub(r'第[一二三四五六七八九十]+[、，]', '', text)
        text = re.sub(r'^\d+[、．.]', '•', text, flags=re.MULTILINE)
        
        return text.strip()
