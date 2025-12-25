"""
政策验证模块 - 验证政策的时效性和权威性
"""
from typing import Dict, Optional
from datetime import datetime, timedelta
import re


class PolicyValidator:
    """政策验证器"""
    
    def __init__(self):
        # 政策有效期模式
        self.date_patterns = [
            r'有效期至(\d{4})年(\d{1,2})月(\d{1,2})日',
            r'(\d{4})年(\d{1,2})月(\d{1,2})日起施行',
            r'自(\d{4})年(\d{1,2})月(\d{1,2})日起',
        ]
        
        # 权威来源列表
        self.authoritative_sources = [
            "国务院", "发改委", "财政部", "商务部",
            "济南市人民政府", "济南市商务局", "济南市财政局",
            "山东省人民政府", "山东省商务厅",
            "青岛市人民政府", "烟台市人民政府"
        ]
        
        # 废止关键词
        self.obsolete_keywords = ["废止", "失效", "停止执行", "已终止", "不再执行"]
    
    def validate(self, policy: Dict) -> Dict:
        """
        验证政策
        
        Args:
            policy: {
                "content": "政策内容",
                "source": "来源",
                "date": "发布日期"
            }
        
        Returns:
            {
                "is_valid": bool,
                "is_expired": bool,
                "is_authoritative": bool,
                "expiry_date": "过期日期",
                "days_until_expiry": int,
                "warnings": ["警告列表"],
                "status": "有效/即将过期/已过期/已废止"
            }
        """
        content = policy.get("content", "")
        source = policy.get("source", "")
        
        warnings = []
        
        # 1. 检查是否已废止
        is_obsolete = any(keyword in content for keyword in self.obsolete_keywords)
        if is_obsolete:
            return {
                "is_valid": False,
                "is_expired": True,
                "is_authoritative": self._is_authoritative(source),
                "expiry_date": None,
                "days_until_expiry": -999,
                "warnings": ["政策已被明确废止"],
                "status": "已废止"
            }
        
        # 2. 检查有效期
        expiry_info = self._extract_expiry_date(content)
        is_expired = False
        days_until_expiry = 999
        
        if expiry_info:
            expiry_date = expiry_info["date"]
            days_until_expiry = (expiry_date - datetime.now()).days
            is_expired = days_until_expiry < 0
            
            if is_expired:
                warnings.append(f"政策已于{expiry_info['date_str']}过期")
            elif days_until_expiry < 30:
                warnings.append(f"政策即将于{expiry_info['date_str']}过期（剩余{days_until_expiry}天）")
        else:
            warnings.append("未找到明确的有效期信息")
        
        # 3. 检查权威性
        is_authoritative = self._is_authoritative(source)
        if not is_authoritative:
            warnings.append(f"来源'{source}'不在权威来源列表中")
        
        # 4. 确定状态
        if is_expired:
            status = "已过期"
        elif days_until_expiry < 30 and days_until_expiry >= 0:
            status = "即将过期"
        else:
            status = "有效"
        
        return {
            "is_valid": not is_expired and not is_obsolete,
            "is_expired": is_expired,
            "is_authoritative": is_authoritative,
            "expiry_date": expiry_info["date_str"] if expiry_info else None,
            "days_until_expiry": days_until_expiry,
            "warnings": warnings,
            "status": status
        }
    
    def _extract_expiry_date(self, text: str) -> Optional[Dict]:
        """提取过期日期"""
        for pattern in self.date_patterns:
            match = re.search(pattern, text)
            if match:
                year = int(match.group(1))
                month = int(match.group(2))
                day = int(match.group(3))
                
                try:
                    date = datetime(year, month, day)
                    return {
                        "date": date,
                        "date_str": f"{year}年{month}月{day}日"
                    }
                except ValueError:
                    continue
        return None
    
    def _is_authoritative(self, source: str) -> bool:
        """判断来源是否权威"""
        return any(auth in source for auth in self.authoritative_sources)
    
    def batch_validate(self, policies: list) -> Dict:
        """批量验证政策"""
        results = []
        stats = {
            "total": len(policies),
            "valid": 0,
            "expired": 0,
            "obsolete": 0,
            "expiring_soon": 0,
            "non_authoritative": 0
        }
        
        for policy in policies:
            result = self.validate(policy)
            results.append({
                "policy": policy,
                "validation": result
            })
            
            if result["is_valid"]:
                stats["valid"] += 1
            if result["is_expired"]:
                stats["expired"] += 1
            if result["status"] == "已废止":
                stats["obsolete"] += 1
            if result["status"] == "即将过期":
                stats["expiring_soon"] += 1
            if not result["is_authoritative"]:
                stats["non_authoritative"] += 1
        
        return {
            "results": results,
            "statistics": stats
        }
    
    def generate_recommendation(self, validation: Dict) -> str:
        """生成建议"""
        if not validation["is_valid"]:
            return "建议: 该政策已失效，请查阅最新政策文件。"
        
        if validation["status"] == "即将过期":
            return f"建议: 该政策即将过期（剩余{validation['days_until_expiry']}天），请关注最新政策动态。"
        
        if not validation["is_authoritative"]:
            return "建议: 该政策来源需要进一步核实，建议咨询官方渠道。"
        
        return "该政策当前有效，可以放心参考。"


# 全局实例
policy_validator = PolicyValidator()


if __name__ == "__main__":
    # 测试政策验证
    validator = PolicyValidator()
    
    print("=" * 60)
    print("政策验证模块测试")
    print("=" * 60)
    
    # 测试政策
    test_policies = [
        {
            "content": "济南市2025年家电以旧换新补贴政策，有效期至2025年12月31日。一级能效补贴20%。",
            "source": "济南市商务局",
            "date": "2025-01-15"
        },
        {
            "content": "青岛市汽车补贴标准，有效期至2024年6月30日。",
            "source": "青岛市政府",
            "date": "2024-01-01"
        },
        {
            "content": "本政策自2023年起施行，已于2024年废止。",
            "source": "某区商务局",
            "date": "2023-05-01"
        },
        {
            "content": "山东省家电补贴指导意见。",
            "source": "非官方来源",
            "date": "2024-01-01"
        }
    ]
    
    print("\n单个政策验证:")
    for i, policy in enumerate(test_policies, 1):
        print(f"\n--- 政策 {i} ---")
        print(f"内容: {policy['content'][:50]}...")
        print(f"来源: {policy['source']}")
        
        result = validator.validate(policy)
        print(f"\n验证结果:")
        print(f"  状态: {result['status']}")
        print(f"  有效: {'是' if result['is_valid'] else '否'}")
        print(f"  权威: {'是' if result['is_authoritative'] else '否'}")
        if result['expiry_date']:
            print(f"  有效期至: {result['expiry_date']}")
            print(f"  剩余天数: {result['days_until_expiry']}")
        if result['warnings']:
            print(f"  警告: {', '.join(result['warnings'])}")
        print(f"  建议: {validator.generate_recommendation(result)}")
    
    # 批量验证
    print("\n\n批量验证统计:")
    print("-" * 60)
    batch_result = validator.batch_validate(test_policies)
    stats = batch_result["statistics"]
    
    print(f"总政策数: {stats['total']}")
    print(f"有效: {stats['valid']}")
    print(f"已过期: {stats['expired']}")
    print(f"已废止: {stats['obsolete']}")
    print(f"即将过期: {stats['expiring_soon']}")
    print(f"非权威来源: {stats['non_authoritative']}")
    
    print("\n✅ 政策验证测试完成")
