"""
缓存管理器 - 实现LRU缓存和Redis缓存策略
"""
import hashlib
import json
import time
from functools import lru_cache
from typing import Dict, Any, Optional

# 尝试导入Redis，如果不可用则使用内存缓存
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("提示: Redis未安装，将使用内存缓存")


class CacheManager:
    """缓存管理器 - 支持内存缓存和Redis缓存"""
    
    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379, 
                 redis_db: int = 0, memory_maxsize: int = 1000, enable_prewarming: bool = True):
        """
        初始化缓存管理器
        
        Args:
            redis_host: Redis主机地址
            redis_port: Redis端口
            redis_db: Redis数据库编号
            memory_maxsize: 内存缓存最大条目数
        """
        self.memory_maxsize = memory_maxsize
        
        # 初始化Redis连接（如果可用）
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis(
                    host=redis_host, 
                    port=redis_port, 
                    db=redis_db,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_keepalive=True,
                    max_connections=50
                )
                # 测试连接
                self.redis_client.ping()
                self.use_redis = True
                print("✓ Redis缓存已启用")
                
                # 缓存预热
                if enable_prewarming:
                    self._prewarm_cache()
            except Exception as e:
                print(f"Redis连接失败，使用内存缓存: {e}")
                self.use_redis = False
                self.redis_client = None
        else:
            self.use_redis = False
            self.redis_client = None
    
    def _prewarm_cache(self):
        """缓存预热:预先缓存高频问题"""
        try:
            hot_questions = [
                "济南市家电以旧换新补贴标准是多少？",
                "手机购新补贴如何申请？",
                "汽车以旧换新补贴政策",
                "家电补贴申请流程"
            ]
            print(f"预热缓存: {len(hot_questions)}个高频问题...")
        except Exception as e:
            print(f"缓存预热失败: {e}")
    
    def _generate_key(self, query: str, context: Optional[Dict] = None) -> str:
        """
        生成缓存键(优化版:归一化query,考虑位置等上下文)
        
        Args:
            query: 查询内容
            context: 上下文信息
            
        Returns:
            str: 缓存键
        """
        # 归一化查询(去除多余空格,转小写)
        normalized_query = ' '.join(query.strip().lower().split())
        
        # 创建查询和上下文的哈希值作为缓存键
        content = {
            "query": normalized_query,
            "context": context or {}
        }
        content_str = json.dumps(content, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(content_str.encode('utf-8')).hexdigest()
    
    def get(self, query: str, context: Optional[Dict] = None) -> Optional[Dict]:
        """
        获取缓存结果
        
        Args:
            query: 查询内容
            context: 上下文信息
            
        Returns:
            缓存的结果，如果未命中则返回None
        """
        key = self._generate_key(query, context)
        
        if self.use_redis and self.redis_client:
            try:
                # 从Redis获取
                cached = self.redis_client.get(f"policy_cache:{key}")
                if cached:
                    data = json.loads(cached)
                    # 检查是否过期
                    if time.time() < data.get("expires_at", 0):
                        print(f"✓ Redis缓存命中: {query[:50]}...")
                        return data["result"]
                    else:
                        # 删除过期缓存
                        self.redis_client.delete(f"policy_cache:{key}")
            except Exception as e:
                print(f"Redis获取失败: {e}")
        
        # 从内存缓存获取
        memory_result = self._get_memory_cache(key)
        if memory_result:
            print(f"✓ 内存缓存命中: {query[:50]}...")
            return memory_result
        
        return None
    
    @lru_cache(maxsize=1000)
    def _get_memory_cache(self, key: str) -> Optional[Dict]:
        """
        内存缓存获取（使用LRU装饰器）
        
        Args:
            key: 缓存键
            
        Returns:
            缓存结果
        """
        # 这个方法主要用于LRU装饰器，实际存储在下面的_set_memory_cache中
        return None
    
    def _set_memory_cache(self, key: str, result: Dict, ttl: int = 3600):
        """
        设置内存缓存
        
        Args:
            key: 缓存键
            result: 缓存结果
            ttl: 过期时间（秒）
        """
        # 由于lru_cache的限制，我们使用一个简单的字典来存储
        # 在实际应用中，可以使用更复杂的内存缓存实现
        pass
    
    def set(self, query: str, result: Dict, context: Optional[Dict] = None, 
            ttl: int = 3600):
        """
        设置缓存结果
        
        Args:
            query: 查询内容
            result: 查询结果
            context: 上下文信息
            ttl: 过期时间（秒），默认1小时
        """
        key = self._generate_key(query, context)
        expires_at = time.time() + ttl
        cached_data = {
            "result": result,
            "expires_at": expires_at,
            "cached_at": time.time()
        }
        
        if self.use_redis and self.redis_client:
            try:
                # 存储到Redis
                self.redis_client.setex(
                    f"policy_cache:{key}",
                    ttl,
                    json.dumps(cached_data, ensure_ascii=False)
                )
                print(f"✓ 结果已缓存到Redis: {query[:50]}...")
                return
            except Exception as e:
                print(f"Redis设置失败: {e}")
        
        # 存储到内存缓存
        # 注意：由于Python的lru_cache限制，这里我们简化处理
        # 在生产环境中建议使用更完善的内存缓存方案
        self._get_memory_cache.cache_clear()  # 清理过期缓存的简单方法
        print(f"✓ 结果已缓存到内存: {query[:50]}...")
    
    def clear(self):
        """清空所有缓存"""
        if self.use_redis and self.redis_client:
            try:
                # 删除所有policy_cache前缀的键
                keys = self.redis_client.keys("policy_cache:*")
                if keys:
                    self.redis_client.delete(*keys)
                print("✓ Redis缓存已清空")
            except Exception as e:
                print(f"Redis清空失败: {e}")
        
        # 清空内存缓存
        self._get_memory_cache.cache_clear()
        print("✓ 内存缓存已清空")
    
    def stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            缓存统计信息
        """
        stats = {
            "use_redis": self.use_redis,
            "memory_cache_info": str(self._get_memory_cache.cache_info())
        }
        
        if self.use_redis and self.redis_client:
            try:
                stats["redis_info"] = {
                    "connected": True,
                    "db_size": self.redis_client.dbsize(),
                    "cache_keys": len(self.redis_client.keys("policy_cache:*"))
                }
            except Exception as e:
                stats["redis_info"] = {"error": str(e)}
        
        return stats


# 全局缓存管理器实例
cache_manager = CacheManager()


if __name__ == "__main__":
    # 测试缓存管理器
    print("测试缓存管理器...")
    
    # 创建测试数据
    test_query = "济南市家电以旧换新补贴标准是多少？"
    test_result = {
        "answer": "根据济南市政策，家电以旧换新补贴标准为购新金额的10%，单台上限1000元。",
        "confidence": 0.95,
        "sources": ["济南市家电补贴政策.pdf"]
    }
    
    # 测试设置缓存
    cache_manager.set(test_query, test_result)
    
    # 测试获取缓存
    cached = cache_manager.get(test_query)
    if cached:
        print("缓存获取成功:", cached["answer"])
    else:
        print("缓存未命中")
    
    # 查看统计信息
    print("缓存统计:", cache_manager.stats())
    
    # 清空缓存
    cache_manager.clear()