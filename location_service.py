"""
地理位置服务 - 基于位置的政策优先级推荐
"""
from typing import Dict, List, Optional, Tuple
import re


class LocationService:
    """地理位置服务"""
    
    def __init__(self):
        # 城市层级关系
        self.city_hierarchy = {
            "山东省": {
                "济南市": ["历下区", "市中区", "槐荫区", "天桥区", "历城区", "长清区", "章丘区", "济阳区", "莱芜区", "钢城区", "平阴县", "商河县"],
                "青岛市": ["市南区", "市北区", "黄岛区", "崂山区", "李沧区", "城阳区", "即墨区", "胶州市", "平度市", "莱西市"],
                "烟台市": ["芝罘区", "福山区", "牟平区", "莱山区", "龙口市", "莱阳市", "莱州市", "蓬莱市", "招远市", "栖霞市", "海阳市", "长岛县"],
                "淄博市": ["淄川区", "张店区", "博山区", "临淄区", "周村区", "桓台县", "高青县", "沂源县"],
                "潍坊市": ["潍城区", "寒亭区", "坊子区", "奎文区", "青州市", "诸城市", "寿光市", "安丘市", "高密市", "昌邑市", "临朐县", "昌乐县"],
                "威海市": ["环翠区", "文登区", "荣成市", "乳山市"],
                "临沂市": ["兰山区", "罗庄区", "河东区", "沂南县", "郯城县", "沂水县", "兰陵县", "费县", "平邑县", "莒南县", "蒙阴县", "临沭县"],
                "德州市": ["德城区", "陵城区", "乐陵市", "禹城市", "临邑县", "平原县", "夏津县", "武城县", "庆云县", "宁津县", "齐河县"],
                "聊城市": ["东昌府区", "茌平区", "临清市", "阳谷县", "莘县", "东阿县", "冠县", "高唐县"],
                "泰安市": ["泰山区", "岱岳区", "新泰市", "肥城市", "宁阳县", "东平县"],
                "济宁市": ["任城区", "兖州区", "曲阜市", "邹城市", "微山县", "鱼台县", "金乡县", "嘉祥县", "汶上县", "泗水县", "梁山县"],
                "菏泽市": ["牡丹区", "定陶区", "曹县", "单县", "成武县", "巨野县", "郓城县", "鄄城县", "东明县"],
                "日照市": ["东港区", "岚山区", "五莲县", "莒县"],
                "滨州市": ["滨城区", "沾化区", "惠民县", "阳信县", "无棣县", "博兴县", "邹平市"],
                "枣庄市": ["市中区", "薛城区", "峄城区", "台儿庄区", "山亭区", "滕州市"],
                "东营市": ["东营区", "河口区", "垦利区", "利津县", "广饶县"]
            }
        }
        
        # 政策关键词与城市的匹配
        self.policy_keywords = {
            "济南": ["济南市", "济南", "泉城"],
            "青岛": ["青岛市", "青岛", "啤酒城"],
            "烟台": ["烟台市", "烟台"],
            "淄博": ["淄博市", "淄博"],
            "潍坊": ["潍坊市", "潍坊"],
            "威海": ["威海市", "威海"],
            "临沂": ["临沂市", "临沂"],
            "德州": ["德州市", "德州"],
            "聊城": ["聊城市", "聊城"],
            "泰安": ["泰安市", "泰安"],
            "济宁": ["济宁市", "济宁"],
            "菏泽": ["菏泽市", "菏泽"],
            "日照": ["日照市", "日照"],
            "滨州": ["滨州市", "滨州"],
            "枣庄": ["枣庄市", "枣庄"],
            "东营": ["东营市", "东营"]
        }
    
    def parse_location(self, location_str: str) -> Dict:
        """
        解析位置字符串
        
        Args:
            location_str: 位置字符串，如 "山东省济南市历下区"
        
        Returns:
            {
                "province": "山东省",
                "city": "济南市",
                "district": "历下区",
                "level": "district"  # province/city/district
            }
        """
        result = {
            "province": None,
            "city": None,
            "district": None,
            "level": None
        }
        
        # 提取省份
        if "山东" in location_str or "山东省" in location_str:
            result["province"] = "山东省"
        
        # 提取城市
        for province, cities in self.city_hierarchy.items():
            for city, districts in cities.items():
                if city in location_str or city.replace("市", "") in location_str:
                    result["city"] = city
                    
                    # 提取区县
                    for district in districts:
                        if district in location_str:
                            result["district"] = district
                            result["level"] = "district"
                            return result
                    
                    result["level"] = "city"
                    return result
        
        if result["province"]:
            result["level"] = "province"
        
        return result
    
    def get_location_keywords(self, location: Dict) -> List[str]:
        """
        根据位置信息生成搜索关键词
        
        Args:
            location: parse_location 返回的位置信息
        
        Returns:
            关键词列表
        """
        keywords = []
        
        # 添加城市关键词
        if location.get("city"):
            city_name = location["city"].replace("市", "")
            if city_name in self.policy_keywords:
                keywords.extend(self.policy_keywords[city_name])
        
        # 添加区县关键词
        if location.get("district"):
            keywords.append(location["district"])
            keywords.append(location["district"].replace("区", "").replace("县", ""))
        
        # 添加省份关键词
        if location.get("province"):
            keywords.append(location["province"])
            keywords.append("山东")
        
        return keywords
    
    def calculate_location_score(self, doc_text: str, user_location: Dict) -> float:
        """
        计算文档与用户位置的匹配度
        
        Args:
            doc_text: 文档文本
            user_location: 用户位置信息
        
        Returns:
            匹配分数 (0-1)
        """
        score = 0.0
        
        # 精确匹配区县 +1.0
        if user_location.get("district") and user_location["district"] in doc_text:
            score += 1.0
        
        # 精确匹配城市 +0.7
        if user_location.get("city"):
            city_name = user_location["city"]
            city_short = city_name.replace("市", "")
            if city_name in doc_text or city_short in doc_text:
                score += 0.7
        
        # 匹配省份 +0.3
        if user_location.get("province"):
            if user_location["province"] in doc_text or "山东" in doc_text:
                score += 0.3
        
        # 限制最大值
        return min(score, 1.0)
    
    def rerank_by_location(
        self,
        documents: List[Dict],
        user_location: Dict,
        location_weight: float = 0.3
    ) -> List[Dict]:
        """
        根据地理位置重新排序文档
        
        Args:
            documents: 文档列表，每个文档包含 'content' 和 'score'
            user_location: 用户位置信息
            location_weight: 位置权重 (0-1)
        
        Returns:
            重新排序后的文档列表
        """
        if not user_location or not user_location.get("city"):
            return documents
        
        # 计算每个文档的位置得分
        for doc in documents:
            content = doc.get("content", "") + doc.get("source", "")
            location_score = self.calculate_location_score(content, user_location)
            
            # 原始得分
            original_score = doc.get("score", 0.5)
            
            # 综合得分 = 原始得分 * (1 - 权重) + 位置得分 * 权重
            combined_score = original_score * (1 - location_weight) + location_score * location_weight
            
            doc["location_score"] = location_score
            doc["original_score"] = original_score
            doc["combined_score"] = combined_score
        
        # 按综合得分排序
        documents.sort(key=lambda x: x.get("combined_score", 0), reverse=True)
        
        return documents
    
    def extract_policy_location(self, text: str) -> Optional[str]:
        """
        从政策文本中提取适用地区
        
        Args:
            text: 政策文本
        
        Returns:
            适用地区字符串
        """
        # 常见模式
        patterns = [
            r'(?:适用于|适用地区|实施范围|适用范围)[:：]?\s*([^\n。，]+)',
            r'([^，。]+(?:市|区|县))(?:范围内|区域内|地区)',
            r'本(?:办法|政策|措施|细则)适用于\s*([^\n。，]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        # 尝试提取城市名
        for city in ["济南", "青岛", "烟台", "淄博", "潍坊", "威海", "临沂", "德州", 
                     "聊城", "泰安", "济宁", "菏泽", "日照", "滨州", "枣庄", "东营"]:
            if city in text[:200]:  # 只检查前200字符
                return f"{city}市"
        
        return None
    
    def get_distance_level(self, user_location: Dict, policy_location: str) -> str:
        """
        获取用户位置与政策位置的距离级别
        
        Args:
            user_location: 用户位置
            policy_location: 政策适用地区
        
        Returns:
            "same_district" / "same_city" / "same_province" / "other"
        """
        if not policy_location:
            return "unknown"
        
        # 同区县
        if user_location.get("district") and user_location["district"] in policy_location:
            return "same_district"
        
        # 同城市
        if user_location.get("city"):
            city_name = user_location["city"]
            city_short = city_name.replace("市", "")
            if city_name in policy_location or city_short in policy_location:
                return "same_city"
        
        # 同省份
        if user_location.get("province"):
            if user_location["province"] in policy_location or "山东" in policy_location:
                return "same_province"
        
        return "other"


# 全局实例
location_service = LocationService()


if __name__ == "__main__":
    # 测试地理位置服务
    service = LocationService()
    
    print("=" * 60)
    print("地理位置服务测试")
    print("=" * 60)
    
    # 测试1: 位置解析
    print("\n1. 位置解析测试")
    test_locations = [
        "山东省济南市历下区",
        "济南市市中区",
        "青岛市",
        "山东省"
    ]
    
    for loc_str in test_locations:
        parsed = service.parse_location(loc_str)
        print(f"\n输入: {loc_str}")
        print(f"  省份: {parsed['province']}")
        print(f"  城市: {parsed['city']}")
        print(f"  区县: {parsed['district']}")
        print(f"  层级: {parsed['level']}")
    
    # 测试2: 关键词生成
    print("\n\n2. 搜索关键词生成测试")
    user_loc = service.parse_location("济南市历下区")
    keywords = service.get_location_keywords(user_loc)
    print(f"\n用户位置: 济南市历下区")
    print(f"关键词: {keywords}")
    
    # 测试3: 位置匹配度计算
    print("\n\n3. 位置匹配度测试")
    test_docs = [
        "济南市历下区家电以旧换新政策实施细则",
        "济南市2024年消费品以旧换新补贴标准",
        "山东省汽车以旧换新实施办法",
        "青岛市家电补贴政策"
    ]
    
    for doc in test_docs:
        score = service.calculate_location_score(doc, user_loc)
        print(f"\n文档: {doc}")
        print(f"  匹配分数: {score:.2f}")
    
    # 测试4: 文档重排序
    print("\n\n4. 基于位置的文档重排序测试")
    documents = [
        {"content": "济南市历下区家电补贴政策", "score": 0.6, "source": "doc1.pdf"},
        {"content": "济南市市中区补贴标准", "score": 0.8, "source": "doc2.pdf"},
        {"content": "青岛市家电补贴", "score": 0.9, "source": "doc3.pdf"},
        {"content": "山东省政策指导", "score": 0.7, "source": "doc4.pdf"}
    ]
    
    print("\n排序前:")
    for i, doc in enumerate(documents, 1):
        print(f"  {i}. {doc['content']} (分数: {doc['score']})")
    
    reranked = service.rerank_by_location(documents, user_loc, location_weight=0.3)
    
    print("\n排序后 (权重0.3):")
    for i, doc in enumerate(reranked, 1):
        print(f"  {i}. {doc['content']}")
        print(f"      原始: {doc['original_score']:.2f} | 位置: {doc['location_score']:.2f} | 综合: {doc['combined_score']:.2f}")
    
    print("\n✅ 地理位置服务测试完成")
