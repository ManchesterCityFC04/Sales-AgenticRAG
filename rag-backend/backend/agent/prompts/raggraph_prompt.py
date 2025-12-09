"""RAG Graph 相关提示词管理

本模块包含RAG图中各个节点使用的提示词模板。
"""

from typing import Dict, Any
from pydantic import BaseModel, Field
from typing import List


class RetrievalNeedDecision(BaseModel):
    """检索需求判断结果"""
    need_retrieval: bool = Field(description="是否需要进行检索")
    extracted_question: str = Field(description="提取的核心问题")
    reasoning: str = Field(description="判断是否需要检索的理由")


class SubquestionExpansion(BaseModel):
    """子问题扩展结果"""
    subquestions: List[str] = Field(description="扩展出的子问题列表")


class RetrievalTypeDecision(BaseModel):
    """检索类型判断结果"""
    retrieval_type: str = Field(description="推荐的检索类型：vector_only或graph_only")
    reasoning: str = Field(description="选择该检索类型的理由")


class RAGGraphPrompts:
    """RAG Graph 提示词集合"""

    @staticmethod
    def get_direct_answer_prompt() -> str:
        """获取直接回答节点的提示词（简化版，不使用记忆功能）
        
        Returns:
            直接回答的提示词模板
        """
        return """你是一个专业且热情的销售顾问。请根据用户的问题提供专业、友好的回答。

用户问题：
{question}

请直接回答用户的问题，保持回答的专业性和热情。如果用户询问产品相关问题，请突出产品优势；如果是问候或闲聊，请友好回应并引导到产品咨询。如果问题不清楚，可以礼貌地要求用户提供更多信息。
"""

    @staticmethod
    def get_direct_answer_memory_prompt() -> str:
        """获取直接回答节点的记忆管理提示词（已弃用）
        """
        return f"""你是一个智能助手，拥有长期记忆功能。
    回答任何问题前一定要先对记忆进行回忆。
在回答用户问题前，请先调用 search_memory 工具，检查是否有相关记忆。
然后再决定是否需要调用 manage_memory 更新记忆。"""

    @staticmethod
    def get_retrieval_need_judgment_prompt() -> str:
        """获取判断是否需要检索的提示词
        
        Returns:
            判断检索需求的提示词模板
        """
        return """
你是一个智能的检索需求判断助手。你的任务是分析用户的问题，判断是否需要进行产品知识库检索来回答这个问题。

请根据以下标准进行判断：

**需要检索的情况：**
1. 问题涉及产品的具体参数、配置、规格、价格
2. 问题询问产品的功能、特性、优势
3. 问题涉及竞品对比、市场定位
4. 问题询问售后服务、政策、保修信息
5. 问题涉及产品版本、配置差异
6. 问题需要引用产品文档或官方资料
7. 问题询问用户评价、案例、使用体验

**不需要检索的情况：**
1. 纯粹的问候、寒暄、闲聊
2. 简单的感谢、告别等社交用语
3. 一般性的概念解释或常识问题
4. 个人观点或主观判断
5. 与产品无关的通用问题

**用户问题：**
{question}

请分析这个问题，判断是否需要进行检索，并提取出核心问题。

**请按照以下格式输出你的判断结果：**

need_retrieval: [true/false] - 是否需要进行检索
extracted_question: [提取的核心问题] - 从用户问题中提取出的关键问题
reasoning: [判断理由] - 详细说明为什么需要或不需要检索的原因

确保你的回答准确反映问题的性质，并提供清晰的判断依据。

"""
    
    @staticmethod
    def get_retrieval_type_judgment_prompt() -> str:
        """获取判断检索类型的提示词
        
        Returns:
            判断检索类型的提示词模板
        """
        return """
你是一个智能的检索类型判断助手。你的任务是分析用户的问题，判断应该使用向量检索还是图检索来获取最相关的信息。

**向量检索 (vector_only) 适用场景：**
1. 语义相似性查询：寻找意思相近的内容
2. 模糊匹配：关键词不完全匹配但语义相关
3. 概念性问题：需要理解概念含义的查询
4. 文本内容检索：主要基于文档内容进行匹配
5. 跨语言查询：不同语言但相同含义的查询
6. 长文本查询：复杂的自然语言描述

**图检索 (graph_only) 适用场景：**
1. 关系查询：询问实体之间的关系
2. 路径查询：需要通过多个节点找到答案
3. 结构化查询：基于明确的实体和属性
4. 精确匹配：需要准确的实体或属性值
5. 层次查询：涉及分类、层级关系的问题
6. 连接查询：需要连接多个相关实体的信息

**用户问题：**
{question}

请分析这个问题的特点，判断应该使用哪种检索方式，并说明理由。

请按照以下JSON格式返回结果：
{{
    "retrieval_type": "vector_only" 或 "graph_only",
    "reasoning": "选择该检索类型的详细理由"
}}
"""
    
    @staticmethod
    def get_subquestion_expansion_prompt() -> str:
        """获取子问题扩展提示词"""
        return """
你是一个专业的问题分析助手。请根据用户的原始问题，将其分解为多个具体的子问题，以便更好地进行信息检索和回答。

分解原则：
1. 子问题应该涵盖原始问题的各个方面
2. 每个子问题应该具体明确，便于检索
3. 子问题之间应该相互补充，避免重复
4. 子问题数量通常在2-5个之间
5. 如果原始问题已经足够具体，可以只生成1个子问题（即原问题本身）

原始问题：{question}

请将上述问题分解为具体的子问题列表。
"""
    

    
    @staticmethod
    def get_answer_generation_prompt() -> str:
        """获取答案生成的提示词
        
        Returns:
            答案生成的提示词模板
        """
        return """
你是一个专业的销售助手，负责根据用户的问题和提供的参考内容生成回答。请严格按照以下要求生成回答：

**回答要求：**
1. 基于提供的参考内容进行回答，如果原文没有参考内容，根据你自己的知识进行回答
2. 你需要用有打动力的销售的语言进行输出，突出产品的优势
3. 回答要专业、热情、有说服力
4. 针对用户的具体需求，提供个性化的产品推荐和话术
5. 如果涉及竞品对比，要客观但突出自身优势
6. 保持回答的准确性和可读性

**用户问题：**
{question}

**检索到的相关文档（共{doc_count}个）：**
{documents}

请基于以上信息，生成专业的销售话术回答。

"""

    # ==================== 销售场景专用Prompt ====================
    
    @staticmethod
    def get_sales_intent_classification_prompt() -> str:
        """销售意图识别Prompt"""
        return """你是一个专业的销售意图识别专家。请分析客户的问题，判断其销售意图。

客户问题：{question}

意图类型：
1. product_inquiry: 产品咨询（询问产品参数、功能、配置等）
2. price_negotiation: 价格谈判（询问价格、优惠、付款方式等）
3. competitor_comparison: 竞品对比（对比其他品牌或型号）
4. objection_handling: 异议处理（表达疑虑、担忧、拒绝）
5. chitchat: 闲聊寒暄（问候、闲聊、建立关系）
6. test_drive_booking: 预约试驾（询问试驾相关）

请只输出意图类型（如：product_inquiry），不要输出其他内容。
"""

    @staticmethod
    def get_sales_needs_analysis_prompt() -> str:
        """客户需求分析Prompt"""
        return """你是一个专业的客户需求分析专家。基于客户的问题，分析客户的真实需求。

客户问题：{question}

请分析客户的需求，输出JSON格式：
{{
    "budget_range": "预算区间",
    "usage_scenario": "使用场景",
    "key_concerns": ["关注点1", "关注点2"],
    "decision_stage": "awareness/consideration/decision"
}}

只输出JSON，不要其他内容。
"""

    @staticmethod
    def get_sales_product_recommendation_prompt() -> str:
        """产品推荐Prompt"""
        return """你是一个专业的汽车销售顾问。基于客户需求和检索结果，推荐最合适的产品配置。

客户需求：{customer_needs}

检索结果：{retrieval_results}

请推荐最匹配的产品，输出JSON格式：
{{
    "product_name": "产品名称",
    "match_score": 95,
    "reasons": ["理由1", "理由2"],
    "key_features": ["特征1", "特征2"]
}}

只输出JSON，不要其他内容。
"""

    @staticmethod
    def get_sales_script_generation_prompt() -> str:
        """销售话术生成Prompt"""
        return """你是一个顶尖的销售话术专家。基于客户需求和产品推荐，生成个性化的销售话术。

客户需求：{customer_needs}

产品推荐：{product_recommendation}

检索结果：{retrieval_results}

请生成专业的销售话术，要求：
1. 使用SPIN提问法和FAB法则
2. 场景化描述，打动客户
3. 专业热情，突出产品优势
4. 语言自然，易于理解

请生成销售话术：
"""


class SalesIntentClassification(BaseModel):
    """销售意图识别结果"""
    sales_intent: str = Field(description="销售意图类型")
    confidence: float = Field(description="置信度", ge=0.0, le=1.0, default=0.8)
    reasoning: str = Field(description="识别理由", default="")


class CustomerNeedsAnalysis(BaseModel):
    """客户需求分析结果"""
    budget_range: str = Field(description="预算范围", default="未知")
    usage_scenario: str = Field(description="使用场景", default="家庭通勤")
    key_concerns: List[str] = Field(description="关注点列表", default_factory=list)
    decision_stage: str = Field(description="决策阶段", default="consideration")