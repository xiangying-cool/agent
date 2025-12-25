"""
数据验证插件 - 智能数据校验
验证用户输入、政策数据、计算结果的合法性和准确性
"""
from typing import Dict, Any, List
import re
from datetime import datetime


class Plugin:
    """数据验证插件"""
    
    @property
    def name(self) -> str:
        return "data_validator"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "数据合法性校验：金额、日期、条件、格式验证"
    
    def __init__(self):
        # 验证规则
        self.validation_rules = {
            "amount": {
                "min": 0,
                "max": 1000000,
                "pattern": r'^\d+(\.\d{1,2})?$'
            },
            "phone": {
                "pattern": r'^1[3-9]\d{9}$'
            },
            "id_card": {
                "pattern": r'^\d{17}[\dXx]$'
            }
        }
    
    def on_load(self):
        print(f"[{self.name}] 数据验证引擎已启动")
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行数据验证
        
        输入 context:
        {
            "data": {
                "amount": 5000,
                "phone": "13800138000",
                "date": "2025-12-31"
            },
            "validation_type": "user_input|policy_data|calculation_result",
            "strict_mode": False
        }
        
        输出:
        {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "validated_data": {...}
        }
        """
        data = context.get("data", {})
        validation_type = context.get("validation_type", "user_input")
        strict_mode = context.get("strict_mode", False)
        
        errors = []
        warnings = []
        validated_data = {}
        
        # 根据验证类型选择验证策略
        if validation_type == "user_input":
            errors, warnings, validated_data = self._validate_user_input(data, strict_mode)
        elif validation_type == "policy_data":
            errors, warnings, validated_data = self._validate_policy_data(data, strict_mode)
        elif validation_type == "calculation_result":
            errors, warnings, validated_data = self._validate_calculation_result(data, strict_mode)
        else:
            errors.append(f"未知的验证类型: {validation_type}")
        
        is_valid = len(errors) == 0
        
        return {
            "is_valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "validated_data": validated_data,
            "validation_type": validation_type
        }
    
    def _validate_user_input(self, data: Dict, strict: bool) -> tuple:
        """验证用户输入"""
        errors = []
        warnings = []
        validated = {}
        
        # 验证金额
        if "amount" in data:
            amount = data["amount"]
            try:
                amount_float = float(amount)
                if amount_float < 0:
                    errors.append("金额不能为负数")
                elif amount_float > 1000000:
                    warnings.append("金额超过100万，请确认是否正确")
                validated["amount"] = amount_float
            except ValueError:
                errors.append("金额格式错误，必须是数字")
        
        # 验证手机号
        if "phone" in data:
            phone = str(data["phone"])
            if not re.match(self.validation_rules["phone"]["pattern"], phone):
                errors.append("手机号格式不正确")
            else:
                validated["phone"] = phone
        
        # 验证身份证
        if "id_card" in data:
            id_card = str(data["id_card"])
            if not re.match(self.validation_rules["id_card"]["pattern"], id_card):
                errors.append("身份证号格式不正确")
            else:
                validated["id_card"] = id_card
        
        # 验证日期
        if "date" in data:
            date_str = data["date"]
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                validated["date"] = date_str
                
                # 检查日期合理性
                if date_obj < datetime(2020, 1, 1):
                    warnings.append("日期过早，请确认")
                elif date_obj > datetime(2030, 12, 31):
                    warnings.append("日期过晚，请确认")
            except ValueError:
                errors.append("日期格式不正确，应为 YYYY-MM-DD")
        
        return errors, warnings, validated
    
    def _validate_policy_data(self, data: Dict, strict: bool) -> tuple:
        """验证政策数据"""
        errors = []
        warnings = []
        validated = data.copy()
        
        # 验证必要字段
        required_fields = ["name", "content"]
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"缺少必要字段: {field}")
        
        # 验证内容长度
        if "content" in data:
            content_length = len(data["content"])
            if content_length < 50:
                warnings.append("政策内容过短，可能不完整")
            elif content_length > 100000:
                warnings.append("政策内容过长，建议分段")
        
        # 验证日期字段
        if "date" in data:
            try:
                datetime.strptime(data["date"], "%Y-%m-%d")
            except ValueError:
                errors.append("政策日期格式不正确")
        
        return errors, warnings, validated
    
    def _validate_calculation_result(self, data: Dict, strict: bool) -> tuple:
        """验证计算结果"""
        errors = []
        warnings = []
        validated = data.copy()
        
        # 验证补贴金额
        if "subsidy" in data:
            subsidy = data["subsidy"]
            try:
                subsidy_float = float(subsidy)
                if subsidy_float < 0:
                    errors.append("补贴金额不能为负数")
                elif subsidy_float > 10000:
                    warnings.append("补贴金额异常高，请确认计算逻辑")
                validated["subsidy"] = subsidy_float
            except ValueError:
                errors.append("补贴金额格式错误")
        
        # 验证总价和补贴的关系
        if "total_price" in data and "subsidy" in data:
            try:
                total = float(data["total_price"])
                subsidy = float(data["subsidy"])
                
                if subsidy > total:
                    errors.append("补贴金额不能超过总价")
                elif subsidy > total * 0.5:
                    warnings.append("补贴比例超过50%，请确认")
                
                validated["subsidy_ratio"] = round(subsidy / total, 3) if total > 0 else 0
            except ValueError:
                errors.append("金额数据格式错误")
        
        # 验证利用率
        if "utilization_rate" in data:
            rate = data["utilization_rate"]
            try:
                rate_float = float(rate)
                if rate_float < 0 or rate_float > 1:
                    errors.append("利用率必须在0-1之间")
                elif rate_float < 0.5:
                    warnings.append("预算利用率较低")
                validated["utilization_rate"] = rate_float
            except ValueError:
                errors.append("利用率格式错误")
        
        return errors, warnings, validated
