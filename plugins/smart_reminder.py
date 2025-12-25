"""
智能提醒插件 - 政策到期提醒、补贴申请截止提醒
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugin_manager import PluginBase
from typing import Dict, Any
from datetime import datetime, timedelta


class Plugin(PluginBase):
    """智能提醒插件"""
    
    @property
    def name(self) -> str:
        return "smart_reminder"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "提供政策到期提醒、补贴申请截止提醒等智能提醒服务"
    
    def on_load(self):
        print("智能提醒插件初始化...")
        # 可以在这里加载政策数据库或初始化API客户端
        self.policies = {
            "家电以旧换新": {
                "expire_date": "2026-12-31",
                "description": "家电以旧换新补贴政策",
                "remind_days_before": 30
            },
            "汽车以旧换新": {
                "expire_date": "2025-12-31",
                "description": "汽车以旧换新补贴政策",
                "remind_days_before": 30
            },
            "数码产品以旧换新": {
                "expire_date": "2026-06-30",
                "description": "数码产品以旧换新补贴政策",
                "remind_days_before": 30
            }
        }
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行智能提醒检查
        
        Args:
            context: {
                "user_policies": ["家电以旧换新", "汽车以旧换新"],  # 用户关注的政策
                "user_applications": [{"policy": "家电以旧换新", "apply_date": "2025-12-01"}]  # 用户申请记录
            }
        
        Returns:
            {
                "reminders": [
                    {
                        "type": "policy_expire",
                        "policy": "汽车以旧换新",
                        "message": "汽车以旧换新补贴政策将于2025-12-31到期，请尽快申请",
                        "urgency": "high",
                        "days_left": 20
                    }
                ]
            }
        """
        user_policies = context.get("user_policies", [])
        user_applications = context.get("user_applications", [])
        
        reminders = []
        today = datetime.now().date()
        
        # 检查政策到期提醒
        for policy_name in user_policies:
            if policy_name in self.policies:
                policy = self.policies[policy_name]
                expire_date = datetime.strptime(policy["expire_date"], "%Y-%m-%d").date()
                days_left = (expire_date - today).days
                
                # 如果剩余天数小于等于提醒天数，则添加提醒
                if 0 <= days_left <= policy["remind_days_before"]:
                    urgency = "high" if days_left <= 7 else "medium" if days_left <= 15 else "low"
                    reminders.append({
                        "type": "policy_expire",
                        "policy": policy_name,
                        "message": f"{policy['description']}将于{policy['expire_date']}到期，请尽快申请",
                        "urgency": urgency,
                        "days_left": days_left
                    })
        
        # 检查申请截止提醒（假设申请后有一定期限需要完成）
        for application in user_applications:
            policy_name = application.get("policy")
            apply_date_str = application.get("apply_date")
            
            if policy_name and apply_date_str and policy_name in self.policies:
                policy = self.policies[policy_name]
                apply_date = datetime.strptime(apply_date_str, "%Y-%m-%d").date()
                expire_date = datetime.strptime(policy["expire_date"], "%Y-%m-%d").date()
                days_since_apply = (today - apply_date).days
                days_left = (expire_date - today).days
                
                # 假设申请后需要在政策到期前30天内完成
                if 0 <= days_left <= 30 and days_since_apply >= 0:
                    urgency = "high" if days_left <= 7 else "medium" if days_left <= 15 else "low"
                    reminders.append({
                        "type": "application_deadline",
                        "policy": policy_name,
                        "message": f"您申请的{policy['description']}需要在{policy['expire_date']}前完成，请尽快办理",
                        "urgency": urgency,
                        "days_left": days_left
                    })
        
        return {
            "status": "success",
            "reminders": reminders
        }