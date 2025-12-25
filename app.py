"""
Web服务 - FastAPI后端接口
企业级政策咨询智能体API
"""
from fastapi import FastAPI, HTTPException, APIRouter, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from agent import PolicyAgent
import uvicorn
import time
import os
import json
import asyncio
from collections import defaultdict
from datetime import datetime, timedelta

# 创建FastAPI应用
app = FastAPI(
    title="企业级政策咨询智能体API", 
    version="2.0.0",
    description="支持双层意图识别、混合检索、工具链计算、智能推荐"
)

# 配置CORS - 优化版
ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite开发服务器
    "http://localhost:8000",  # FastAPI
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # 限制允许的源
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],  # 只允许必要的方法
    allow_headers=["*"],
    max_age=3600  # 预检请求缓存1小时
)

# 全局智能体实例
agent = None

# 创建API路由器
api_router = APIRouter(prefix="/api")

# 限流器:基于IP的简单限流
rate_limit_store = defaultdict(list)
RATE_LIMIT = 60  # 每分钟最多60次请求
RATE_WINDOW = 60  # 60秒窗口

async def check_rate_limit(request: Request):
    """限流检查"""
    client_ip = request.client.host
    now = datetime.now()
    
    # 清理过期记录
    rate_limit_store[client_ip] = [
        ts for ts in rate_limit_store[client_ip]
        if (now - ts).total_seconds() < RATE_WINDOW
    ]
    
    # 检查是否超限
    if len(rate_limit_store[client_ip]) >= RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"请求过于频繁,每{RATE_WINDOW}秒最多{RATE_LIMIT}次请求"
        )
    
    # 记录本次请求
    rate_limit_store[client_ip].append(now)


@app.on_event("startup")
async def startup_event():
    """启动时初始化智能体"""
    global agent
    print("正在初始化政策咨询智能体...")
    agent = PolicyAgent()
    agent.initialize(force_rebuild=False)
    print("智能体初始化完成！")


# 请求模型
class LocationInfo(BaseModel):
    """  地理位置信息"""
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    latitude: Optional[float] = None  # 纬度
    longitude: Optional[float] = None  # 经度

class QuestionRequest(BaseModel):
    question: str
    return_sources: bool = True
    location: Optional[LocationInfo] = None  # 新增位置信息


class EvalCase(BaseModel):
    question: str
    expected_keywords: List[str] = []

class EvalRequest(BaseModel):
    cases: List[EvalCase]


# 响应模型
class BatchQuestionRequest(BaseModel):
    questions: List[str]

class AnswerResponse(BaseModel):
    question: str
    answer: str
    confidence: float
    intent_type: Optional[str] = None
    rejected: bool = False
    sources: Optional[List[dict]] = []
    recommendation: Optional[dict] = None  # 推荐详情
    algorithm: Optional[str] = None  # 算法类型（dp/greedy）
    is_optimal: Optional[bool] = None  # 是否全局最优


# 已由lifespan初始化


# 根路径由静态前端提供


@api_router.get("/health")
async def health_check():
    """健康检查"""
    kb_ready = False
    kb_doc_count = 0
    
    if agent is not None:
        try:
            stats = agent.kb.get_stats()
            kb_ready = stats.get('total_documents', 0) > 0
            kb_doc_count = stats.get('total_documents', 0)
        except:
            kb_ready = False
    
    return {
        "status": "healthy" if agent is not None else "initializing",
        "agent_ready": agent is not None,
        "kb_ready": kb_ready,
        "kb_doc_count": kb_doc_count
    }


@api_router.post("/query", response_model=AnswerResponse)
async def query(request: QuestionRequest):
    """
    单个问题咨询（企业级）
    支持地理位置优化
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="智能体未初始化")
    
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")
    
    try:
        start_time = time.time()
        
        # 处理位置信息
        user_location = None
        if request.location:
            user_location = {
                "province": request.location.province,
                "city": request.location.city,
                "district": request.location.district
            }
        
        result = agent.query(
            request.question,
            return_sources=request.return_sources,
            user_location=user_location
        )
        latency = time.time() - start_time
        
        # 调试日志
        print(f"\n[DEBUG] API 返回数据:")
        print(f"  - recommendation: {result.get('recommendation', {}).get('selected_products', [])}")
        print(f"  - total_subsidy: {result.get('recommendation', {}).get('total_subsidy', 0)}")
        print(f"  - algorithm: {result.get('algorithm')}")
        print(f"  - is_optimal: {result.get('is_optimal')}\n")
        
        return AnswerResponse(
            question=request.question,
            answer=result["answer"],
            confidence=result["confidence"],
            intent_type=result.get("intent_type"),
            rejected=result.get("rejected", False),
            sources=result.get("sources", []),
            recommendation=result.get("recommendation"),  # 添加推荐详情
            algorithm=result.get("algorithm"),  # 算法类型
            is_optimal=result.get("is_optimal")  # 是否最优
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理问题时出错: {str(e)}")


@api_router.post("/batch_query")
async def batch_query(request: BatchQuestionRequest):
    """
    批量问题咨询
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="智能体未初始化")
    
    if not request.questions:
        raise HTTPException(status_code=400, detail="问题列表不能为空")
    
    try:
        results = agent.batch_query(request.questions)
        return {
            "results": [
                {
                    "question": q,
                    "answer": r["answer"],
                    "confidence": r["confidence"],
                    "sources": r.get("sources", [])
                }
                for q, r in zip(request.questions, results)
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量处理问题时出错: {str(e)}")


@api_router.post("/evaluate")
async def evaluate(request: EvalRequest):
    """
    评测接口：计算准确率与平均响应时间（粗略基于关键词命中）
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="智能体未初始化")
    if not request.cases:
        raise HTTPException(status_code=400, detail="评测用例不能为空")
    try:
        eval_result = agent.evaluate([{"question": c.question, "expected_keywords": c.expected_keywords} for c in request.cases])
        return eval_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"评测时出错: {str(e)}")


@api_router.get("/history")
async def get_history():
    """
    获取对话历史
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="智能体未初始化")
    
    return {
        "history": agent.get_conversation_history()
    }


@api_router.post("/clear_history")
async def clear_history():
    """
    清空对话历史
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="智能体未初始化")
    
    agent.clear_history()
    return {"message": "对话历史已清空"}


@api_router.post("/rebuild_kb")
async def rebuild_knowledge_base():
    """
    重建知识库（用于政策更新）
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="智能体未初始化")
    
    try:
        agent.initialize(force_rebuild=True)
        return {"message": "知识库重建成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重建知识库时出错: {str(e)}")


@api_router.get("/metrics")
async def get_metrics():
    """获取性能指标"""
    if agent is None:
        raise HTTPException(status_code=503, detail="智能体未初始化")
    
    return agent.get_metrics()


@api_router.get("/kb_stats")
async def get_kb_stats():
    """获取知识库统计信息"""
    if agent is None:
        raise HTTPException(status_code=503, detail="智能体未初始化")
    try:
        stats = agent.kb.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取知识库统计信息时出错: {str(e)}")


# ========== 新增: 反馈相关API ==========
class FeedbackRequest(BaseModel):
    query: str
    answer: str
    rating: int  # 1-5
    comment: Optional[str] = None
    user_id: Optional[str] = None


@api_router.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """提交用户反馈"""
    if agent is None:
        raise HTTPException(status_code=503, detail="智能体未初始化")
    
    if not agent.feedback_system:
        raise HTTPException(status_code=501, detail="反馈系统未启用")
    
    try:
        result = agent.feedback_system.collect_feedback(
            query=feedback.query,
            answer=feedback.answer,
            rating=feedback.rating,
            comment=feedback.comment,
            user_id=feedback.user_id
        )
        return {
            "message": "感谢您的反馈！",
            "feedback_id": result["id"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提交反馈时出错: {str(e)}")


@api_router.get("/feedback/statistics")
async def get_feedback_statistics():
    """获取反馈统计"""
    if agent is None:
        raise HTTPException(status_code=503, detail="智能体未初始化")
    
    if not agent.feedback_system:
        raise HTTPException(status_code=501, detail="反馈系统未启用")
    
    try:
        stats = agent.feedback_system.get_feedback_statistics()
        suggestions = agent.feedback_system.get_improvement_suggestions()
        return {
            "statistics": stats,
            "suggestions": suggestions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取反馈统计时出错: {str(e)}")


# ========== 新增: 监控相关API ==========
@api_router.get("/monitoring/statistics")
async def get_monitoring_statistics():
    """获取监控统计数据"""
    if agent is None:
        raise HTTPException(status_code=503, detail="智能体未初始化")
    
    if not agent.monitoring_system:
        raise HTTPException(status_code=501, detail="监控系统未启用")
    
    try:
        stats = agent.monitoring_system.get_statistics(minutes=60)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取监控数据时出错: {str(e)}")


@api_router.get("/monitoring/alerts")
async def get_recent_alerts(limit: int = 10):
    """获取最近告警"""
    if agent is None:
        raise HTTPException(status_code=503, detail="智能体未初始化")
    
    if not agent.monitoring_system:
        raise HTTPException(status_code=501, detail="监控系统未启用")
    
    try:
        alerts = agent.monitoring_system.get_recent_alerts(limit=limit)
        return {"alerts": alerts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取告警信息时出错: {str(e)}")


# ========== 新增: 外部API相关 ==========
@api_router.get("/external/policy_check")
async def check_policy_status(policy_name: str, region: str = "济南市"):
    """实时核查政策状态"""
    if agent is None:
        raise HTTPException(status_code=503, detail="智能体未初始化")
    
    if not agent.external_api:
        raise HTTPException(status_code=501, detail="外部API服务未启用")
    
    try:
        result = agent.external_api.check_policy_realtime(policy_name, region)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@api_router.get("/external/price")
async def get_product_price(product: str, platform: str = "all"):
    """查询商品价格"""
    if agent is None:
        raise HTTPException(status_code=503, detail="智能体未初始化")
    
    if not agent.external_api:
        raise HTTPException(status_code=501, detail="外部API服务未启用")
    
    try:
        result = agent.external_api.get_product_price(product, platform)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@api_router.get("/external/status")
async def get_external_api_status():
    """获取外部API状态"""
    if agent is None:
        raise HTTPException(status_code=503, detail="智能体未初始化")
    
    if not agent.external_api:
        raise HTTPException(status_code=501, detail="外部API服务未启用")
    
    try:
        status = agent.external_api.get_api_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取状态失败: {str(e)}")


@api_router.get("/policies")
async def list_policies(q: Optional[str] = None, top_k: int = 10):
    """
    列出/检索政策文档
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="智能体未初始化")
    try:
        query = q.strip() if q else "以旧换新"
        results = agent.kb.search_with_score(query, top_k=top_k)
        return {
            "policies": [
                {
                    "source": doc.metadata.get("source", "Unknown"),
                    "similarity": float(score),
                    "snippet": doc.page_content[:200]
                } for doc, score in results
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检索政策文档时出错: {str(e)}")
@api_router.post("/sync_policies")
async def sync_policies():
    """
    增量同步政策库：新增文件增量入库，检测到修改则重建索引
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="智能体未初始化")
    try:
        agent.kb.sync_knowledge_base(force_rebuild_on_modified=True)
        return {"message": "政策库同步完成"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"同步政策库时出错: {str(e)}")

@api_router.post("/compare_policies")
async def compare_policies(file_a: str, file_b: str):
    """
    版本对比：传入两个文件绝对路径或相对路径，返回简要差异
    """
    try:
        from document_loader import DocumentLoader
        import difflib, os
        loader = DocumentLoader()
        # 读取文本
        text_a = loader.load_document(file_a)
        text_b = loader.load_document(file_b)
        if not text_a or not text_b:
            raise HTTPException(status_code=400, detail="文件内容为空或不可读取")
        diff_lines = list(difflib.unified_diff(
            text_a.splitlines(), text_b.splitlines(),
            fromfile=os.path.basename(file_a), tofile=os.path.basename(file_b), lineterm=""
        ))[:200]
        return {"from": file_a, "to": file_b, "diff_preview": diff_lines}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"版本对比失败: {str(e)}")

# === 知识库手动微调与T+0入口 ===
@api_router.post("/kb/index_file")
async def kb_index_file(file_path: str):
    """单文件快速入库（T+0），传入绝对或相对路径"""
    if agent is None:
        raise HTTPException(status_code=503, detail="智能体未初始化")
    try:
        result = agent.kb.index_file(file_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"单文件入库失败: {str(e)}")

@api_router.get("/kb/boosts")
async def kb_get_boosts():
    if agent is None:
        raise HTTPException(status_code=503, detail="智能体未初始化")
    return agent.kb.get_boosts()

@api_router.post("/kb/boost")
async def kb_set_boost(target_type: str, key: str, weight: float):
    """设置boost权重：target_type=source/category，weight建议0~1"""
    if agent is None:
        raise HTTPException(status_code=503, detail="智能体未初始化")
    try:
        boosts = agent.kb.set_boost(target_type, key, weight)
        return {"message": "boost更新成功", "boosts": boosts}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"设置boost失败: {str(e)}")

@api_router.delete("/kb/boost")
async def kb_clear_boost(target_type: str, key: str):
    if agent is None:
        raise HTTPException(status_code=503, detail="智能体未初始化")
    try:
        boosts = agent.kb.clear_boost(target_type, key)
        return {"message": "boost已移除", "boosts": boosts}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"移除boost失败: {str(e)}")


@api_router.get("/stream_query")
async def stream_query(
    question: str,
    province: Optional[str] = None,
    city: Optional[str] = None,
    district: Optional[str] = None
):
    """
    流式输出接口（SSE）
    前端通过 EventSource 连接
    支持地理位置参数
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="智能体未初始化")
    
    if not question.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")
    
    async def generate():
        try:
            # 处理位置信息
            user_location = None
            if city:  # 至少需要城市信息
                user_location = {
                    "province": province or "山东省",
                    "city": city,
                    "district": district
                }
            
            # 阶段1：发送开始信号
            yield f"data: {json.dumps({'type': 'start', 'message': '开始处理问题...'}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.1)
            
            # 阶段2：意图识别
            yield f"data: {json.dumps({'type': 'intent', 'message': '正在识别问题意图...'}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.2)
            
            # 阶段3：检索知识库
            if user_location:
                location_msg = f"正在检索{user_location.get('city', '')}相关政策..."
            else:
                location_msg = '正在检索相关政策...'
            yield f"data: {json.dumps({'type': 'retrieval', 'message': location_msg}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.2)
            
            # 阶段4：生成答案（在单独线程中执行）
            yield f"data: {json.dumps({'type': 'generating', 'message': '正在生成答案...'}, ensure_ascii=False)}\n\n"
            
            # 在线程池中执行同步查询
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(agent.query, question, True, user_location)
                result = future.result()
            
            # 逐字发送答案（模拟打字机效果）
            answer = result["answer"]
            chunk_size = 10  # 每次10个字符
            for i in range(0, len(answer), chunk_size):
                chunk = answer[i:i+chunk_size]
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.05)  # 模拟打字延迟
            
            # 阶段5：发送完整结果
            yield f"data: {json.dumps({'type': 'complete', 'result': result}, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

# 挂载API路由
app.include_router(api_router)

# 挂载静态文件（必须在最后）
if os.path.isdir('intelli-policy/dist'):
    app.mount('/', StaticFiles(directory='intelli-policy/dist', html=True), name='frontend')

if __name__ == "__main__":
    print("启动企业级政策咨询智能体服务...")
    print("访问 http://localhost:8000 查看API文档")
    print("访问 http://localhost:8000/docs 查看交互式API文档")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
