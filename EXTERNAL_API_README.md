# 外部API集成功能说明

## 功能概述

外部API管理器提供了统一的接口来访问多个外部数据源和服务，包括：

1. **政策实时核查** - 查询政策的最新状态和有效性
2. **商品价格比价** - 多平台价格查询和比较
3. **天气查询** - 获取实时天气信息

## 核心特性

### 1. 统一API管理
- 集中管理所有外部API配置
- 支持动态启用/禁用API
- 统一的错误处理和响应格式

### 2. 智能缓存
- 5分钟缓存机制，减少重复请求
- 自动缓存键生成
- 支持手动清除缓存

### 3. 请求限流
- 每分钟最多60次请求
- 防止API滥用
- 自动清理过期记录

### 4. 模拟模式
- API未启用时返回模拟数据
- 便于开发和测试
- 真实API配置后无缝切换

## API端点

### 1. 政策核查
```
GET /api/external/policy_check?policy_name=政策名称&region=地区
```

**响应示例**:
```json
{
  "policy_name": "济南市2025年家电补贴政策",
  "region": "济南市",
  "status": "有效",
  "last_update": "2025-12-16",
  "source_url": "http://www.jinan.gov.cn/",
  "note": "实时核查服务暂不可用，返回本地数据"
}
```

### 2. 价格查询
```
GET /api/external/price?product=商品名称&platform=all
```

**响应示例**:
```json
{
  "product": "海尔一级能效空调",
  "prices": [
    {
      "platform": "京东",
      "price": 2999.0,
      "url": "https://www.jd.com"
    },
    {
      "platform": "天猫",
      "price": 2849.05,
      "url": "https://www.tmall.com"
    }
  ],
  "lowest_price": 2849.05,
  "average_price": 2999.0,
  "note": "价格查询服务暂不可用，返回模拟数据"
}
```

### 3. 天气查询
```
GET /api/external/weather?city=济南
```

**响应示例**:
```json
{
  "city": "济南",
  "temperature": 25,
  "weather": "晴",
  "humidity": 65,
  "note": "天气服务暂不可用，返回模拟数据"
}
```

### 4. API状态查询
```
GET /api/external/status
```

**响应示例**:
```json
{
  "weather": {
    "name": "天气API",
    "enabled": false,
    "cache_entries": 0,
    "requests_last_minute": 0
  },
  "price": {
    "name": "价格比价API",
    "enabled": false,
    "cache_entries": 0,
    "requests_last_minute": 0
  },
  "policy_check": {
    "name": "政策实时核查API",
    "enabled": false,
    "cache_entries": 0,
    "requests_last_minute": 0
  }
}
```

## 使用方法

### 1. 在Python代码中使用

```python
from external_api_manager import external_api_manager

# 政策核查
result = external_api_manager.check_policy_realtime(
    "济南市家电补贴政策",
    "济南市"
)
print(f"政策状态: {result['status']}")

# 价格查询
result = external_api_manager.get_product_price(
    "海尔一级能效空调",
    "all"
)
print(f"最低价: {result['lowest_price']}")

# 天气查询
result = external_api_manager.get_weather("济南")
print(f"温度: {result['temperature']}°C")
```

### 2. 通过HTTP API调用

```bash
# 政策核查
curl "http://localhost:8000/api/external/policy_check?policy_name=济南市家电补贴政策&region=济南市"

# 价格查询
curl "http://localhost:8000/api/external/price?product=海尔空调&platform=all"

# 天气查询
curl "http://localhost:8000/api/external/weather?city=济南"

# 状态查询
curl "http://localhost:8000/api/external/status"
```

### 3. 批量调用

```python
from external_api_manager import external_api_manager

requests = [
    {"api_name": "weather", "params": {"q": "济南"}},
    {"api_name": "price", "params": {"product": "冰箱"}},
    {"api_name": "policy_check", "params": {"name": "补贴政策"}}
]

results = external_api_manager.batch_call(requests)
for result in results:
    if result["success"]:
        print(f"成功: {result['data']}")
```

## 配置真实API

要启用真实的外部API，需要修改 `external_api_manager.py` 中的配置：

```python
self.apis = {
    "weather": {
        "name": "天气API",
        "base_url": "https://api.openweathermap.org/data/2.5/weather",
        "enabled": True,  # 改为True启用
        "timeout": 5,
        "api_key": "your_api_key"  # 添加API密钥
    },
    # ... 其他配置
}
```

## 性能优化

1. **缓存机制**: 默认5分钟缓存，减少API调用
2. **请求限流**: 防止过度请求，保护API稳定性
3. **超时控制**: 每个API独立超时设置
4. **批量调用**: 一次请求多个API，提高效率

## 错误处理

所有API调用都返回统一格式：

```json
{
  "success": true/false,
  "data": {...},
  "error": null/"错误信息",
  "cached": true/false,
  "response_time": 0.123
}
```

## 测试

运行测试脚本：

```bash
# 测试基础功能
python external_api_manager.py

# 测试HTTP端点（需要先启动服务器）
python app.py
python test_external_api.py
```

## 集成到智能体

外部API已自动集成到主智能体中，可以在对话中自然地调用：

- "济南市家电补贴政策还有效吗？" → 自动调用政策核查API
- "海尔空调多少钱？" → 自动调用价格查询API
- "济南今天天气怎么样？" → 自动调用天气API

## 扩展新API

添加新的外部API很简单：

1. 在 `self.apis` 中添加配置
2. 创建对应的方法（如 `get_xxx()`）
3. 在 `app.py` 中添加对应的HTTP端点
4. 更新测试用例

## 注意事项

1. 目前处于模拟模式，实际部署时需配置真实API密钥
2. 建议根据实际使用情况调整缓存时间和限流阈值
3. 生产环境建议添加API调用监控和告警
4. 敏感信息（API密钥）应使用环境变量配置
