"""
监控告警系统 - 实时运行状态监控与智能告警
"""
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import deque
import config


class MonitoringSystem:
    """系统监控与告警"""
    
    def __init__(self):
        self.metrics_history = deque(maxlen=1000)  # 保留最近1000条记录
        self.alert_records = []
        self.metrics_file = os.path.join(config.LOG_DIR, "metrics.json")
        self.alert_file = os.path.join(config.LOG_DIR, "alerts.json")
        
        # 确保日志目录存在
        os.makedirs(config.LOG_DIR, exist_ok=True)
        
        # 告警阈值配置
        self.thresholds = {
            "error_rate": config.ALERT_THRESHOLD.get("error_rate", 0.05),
            "latency_ms": config.ALERT_THRESHOLD.get("latency_ms", 5000),
            "max_queue_size": 100,
            "min_success_rate": 0.90
        }
    
    def record_query(self, query_data: Dict):
        """
        记录单次查询的性能指标
        
        Args:
            query_data: {
                "query": "用户问题",
                "status": "success/error",
                "latency_ms": 响应时间（毫秒）,
                "confidence": 置信度,
                "error_msg": 错误信息（可选）
            }
        """
        metric = {
            "timestamp": datetime.now().isoformat(),
            "query": query_data.get("query", "")[:100],  # 只记录前100字符
            "status": query_data.get("status", "unknown"),
            "latency_ms": query_data.get("latency_ms", 0),
            "confidence": query_data.get("confidence", 0),
            "error_msg": query_data.get("error_msg", "")
        }
        
        self.metrics_history.append(metric)
        
        # 检查是否需要告警
        self._check_alerts(metric)
    
    def _check_alerts(self, current_metric: Dict):
        """检查是否触发告警"""
        alerts = []
        
        # 1. 延迟告警
        if current_metric["latency_ms"] > self.thresholds["latency_ms"]:
            alerts.append({
                "level": "WARNING",
                "type": "HIGH_LATENCY",
                "message": f"响应时间过长: {current_metric['latency_ms']}ms (阈值: {self.thresholds['latency_ms']}ms)",
                "metric": current_metric
            })
        
        # 2. 错误率告警（计算最近50次请求）
        if len(self.metrics_history) >= 50:
            recent_50 = list(self.metrics_history)[-50:]
            error_count = sum(1 for m in recent_50 if m["status"] == "error")
            error_rate = error_count / 50
            
            if error_rate > self.thresholds["error_rate"]:
                alerts.append({
                    "level": "CRITICAL",
                    "type": "HIGH_ERROR_RATE",
                    "message": f"错误率过高: {error_rate:.2%} (阈值: {self.thresholds['error_rate']:.2%})",
                    "detail": f"最近50次请求中有{error_count}次失败"
                })
        
        # 3. 置信度告警
        if current_metric["status"] == "success" and current_metric["confidence"] < 0.5:
            alerts.append({
                "level": "INFO",
                "type": "LOW_CONFIDENCE",
                "message": f"回答置信度较低: {current_metric['confidence']:.2%}",
                "query": current_metric["query"]
            })
        
        # 记录告警
        for alert in alerts:
            self._save_alert(alert)
    
    def _save_alert(self, alert: Dict):
        """保存告警记录"""
        alert["timestamp"] = datetime.now().isoformat()
        self.alert_records.append(alert)
        
        # 打印告警
        level_emoji = {
            "INFO": "ℹ️",
            "WARNING": "⚠️",
            "CRITICAL": "🚨"
        }
        emoji = level_emoji.get(alert["level"], "📢")
        print(f"{emoji} [{alert['level']}] {alert['type']}: {alert['message']}")
        
        # 保存到文件
        try:
            with open(self.alert_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(alert, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"告警保存失败: {e}")
    
    def get_statistics(self, minutes: int = 60) -> Dict:
        """
        获取统计数据
        
        Args:
            minutes: 统计最近N分钟的数据
        
        Returns:
            统计报告
        """
        if not self.metrics_history:
            return {"message": "暂无数据"}
        
        # 筛选时间范围内的数据
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_metrics = [
            m for m in self.metrics_history
            if datetime.fromisoformat(m["timestamp"]) > cutoff_time
        ]
        
        if not recent_metrics:
            return {"message": f"最近{minutes}分钟无数据"}
        
        # 计算统计指标
        total = len(recent_metrics)
        success_count = sum(1 for m in recent_metrics if m["status"] == "success")
        error_count = sum(1 for m in recent_metrics if m["status"] == "error")
        
        latencies = [m["latency_ms"] for m in recent_metrics]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        max_latency = max(latencies) if latencies else 0
        
        confidences = [m["confidence"] for m in recent_metrics if m["confidence"] > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return {
            "time_range": f"最近{minutes}分钟",
            "total_requests": total,
            "success_count": success_count,
            "error_count": error_count,
            "success_rate": f"{(success_count / total * 100):.2f}%",
            "error_rate": f"{(error_count / total * 100):.2f}%",
            "avg_latency_ms": round(avg_latency, 2),
            "max_latency_ms": max_latency,
            "avg_confidence": f"{(avg_confidence * 100):.2f}%",
            "status": "正常" if error_count / total < self.thresholds["error_rate"] else "异常"
        }
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict]:
        """获取最近的告警记录"""
        return self.alert_records[-limit:]
    
    def export_metrics(self):
        """导出性能指标到文件"""
        try:
            with open(self.metrics_file, "w", encoding="utf-8") as f:
                json.dump(list(self.metrics_history), f, ensure_ascii=False, indent=2)
            print(f"✓ 性能指标已导出到: {self.metrics_file}")
        except Exception as e:
            print(f"导出失败: {e}")


# 全局监控实例
monitoring_system = MonitoringSystem() if config.ENABLE_MONITORING else None


if __name__ == "__main__":
    # 测试监控系统
    monitor = MonitoringSystem()
    
    print("=" * 60)
    print("监控系统测试")
    print("=" * 60)
    
    # 模拟一些查询记录
    import random
    
    for i in range(100):
        status = "success" if random.random() > 0.1 else "error"
        monitor.record_query({
            "query": f"测试查询{i}",
            "status": status,
            "latency_ms": random.randint(500, 8000),
            "confidence": random.random(),
            "error_msg": "测试错误" if status == "error" else ""
        })
    
    # 查看统计
    print("\n统计报告:")
    stats = monitor.get_statistics(minutes=60)
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 查看告警
    print("\n最近告警:")
    alerts = monitor.get_recent_alerts(5)
    for alert in alerts:
        print(f"  [{alert['level']}] {alert['message']}")
    
    # 导出数据
    monitor.export_metrics()
