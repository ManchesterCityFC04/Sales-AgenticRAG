"""销售场景扩展模块

为RAGNodes添加销售场景专用方法
"""

from ..states.raggraph_state import RAGGraphState
from ..prompts.raggraph_prompt import RAGGraphPrompts
from ...config.log import get_logger

logger = get_logger(__name__)


def identify_sales_intent(state: RAGGraphState) -> RAGGraphState:
    """识别销售意图
    
    Args:
        state: 当前状态
        
    Returns:
        更新后的状态
    """
    try:
        messages = state.get("messages", [])
        if not messages:
            state["sales_intent"] = "unknown"
            return state
        
        latest_message = messages[-1].content if hasattr(messages[-1], 'content') else str(messages[-1])
        question_lower = latest_message.lower()
        
        # 使用规则识别意图
        if any(word in question_lower for word in ["多少钱", "价格", "优惠", "折扣", "贵不贵"]):
            state["sales_intent"] = "price_negotiation"
        elif any(word in question_lower for word in ["对比", "相比", "区别", "和", "vs", "哪个好"]):
            state["sales_intent"] = "competitor_comparison"
        elif any(word in question_lower for word in ["担心", "疑虑", "不满意", "不好", "缺点"]):
            state["sales_intent"] = "objection_handling"
        elif any(word in question_lower for word in ["你好", "谢谢", "再见", "hello", "hi"]):
            state["sales_intent"] = "chitchat"
        elif any(word in question_lower for word in ["试驾", "看车", "体验", "预约"]):
            state["sales_intent"] = "test_drive_booking"
        else:
            state["sales_intent"] = "product_inquiry"
        
        logger.info(f"[销售意图] {state['sales_intent']}")
        
    except Exception as e:
        logger.error(f"意图识别失败: {e}")
        state["sales_intent"] = "product_inquiry"
    
    return state


def analyze_customer_needs(state: RAGGraphState) -> RAGGraphState:
    """分析客户需求
    
    Args:
        state: 当前状态
        
    Returns:
        更新后的状态
    """
    try:
        messages = state.get("messages", [])
        if not messages:
            return state
        
        latest_message = messages[-1].content if hasattr(messages[-1], 'content') else str(messages[-1])
        question_lower = latest_message.lower()
        
        # 简单的需求分析
        needs = {
            "budget_range": "未知",
            "usage_scenario": "家庭通勤",
            "key_concerns": [],
            "decision_stage": "consideration"
        }
        
        # 预算分析
        if any(word in question_lower for word in ["20万", "30万"]):
            needs["budget_range"] = "20-30万"
        elif any(word in question_lower for word in ["30万", "40万"]):
            needs["budget_range"] = "30-40万"
        
        # 场景分析
        if any(word in question_lower for word in ["家庭", "家用", "通勤"]):
            needs["usage_scenario"] = "家庭通勤"
        elif any(word in question_lower for word in ["商务", "接待"]):
            needs["usage_scenario"] = "商务接待"
        
        # 关注点分析
        if "续航" in question_lower:
            needs["key_concerns"].append("续航")
        if any(word in question_lower for word in ["空间", "大"]):
            needs["key_concerns"].append("空间")
        if any(word in question_lower for word in ["智能", "科技"]):
            needs["key_concerns"].append("智能化")
        if any(word in question_lower for word in ["安全"]):
            needs["key_concerns"].append("安全")
        
        state["customer_needs"] = needs
        logger.info(f"[客户需求] {needs}")
        
    except Exception as e:
        logger.error(f"需求分析失败: {e}")
    
    return state


def generate_sales_script(state: RAGGraphState, llm) -> RAGGraphState:
    """生成销售话术
    
    Args:
        state: 当前状态
        llm: 语言模型
        
    Returns:
        更新后的状态
    """
    try:
        # 获取客户需求和检索结果
        customer_needs = state.get("customer_needs", {})
        retrieved_docs = state.get("retrieved_docs", [])
        
        # 构建检索结果摘要
        docs_summary = "\n".join([
            f"- {doc.get('content', '')[:200]}..." 
            for doc in retrieved_docs[:3]
        ]) if retrieved_docs else "暂无相关文档"
        
        # 构建Prompt
        prompt = RAGGraphPrompts.get_sales_script_generation_prompt().format(
            customer_needs=str(customer_needs),
            product_recommendation=str(state.get("product_recommendation", {})),
            retrieval_results=docs_summary
        )
        
        # 调用LLM生成话术
        if llm:
            response = llm.invoke(prompt)
            state["sales_script"] = response.content if hasattr(response, 'content') else str(response)
            logger.info(f"[销售话术] 已生成，长度: {len(state['sales_script'])}")
        else:
            state["sales_script"] = "销售话术生成功能暂未启用"
        
    except Exception as e:
        logger.error(f"销售话术生成失败: {e}")
        state["sales_script"] = ""
    
    return state


def enhance_answer_with_sales_mode(state: RAGGraphState) -> str:
    """使用销售模式增强回答
    
    Args:
        state: 当前状态
        
    Returns:
        增强后的回答
    """
    try:
        final_answer = state.get("final_answer", "")
        sales_intent = state.get("sales_intent", "unknown")
        customer_needs = state.get("customer_needs", {})
        
        # 根据意图添加销售话术
        if sales_intent == "price_negotiation":
            prefix = "💰 **价格咨询**\n\n"
        elif sales_intent == "competitor_comparison":
            prefix = "📊 **产品对比**\n\n"
        elif sales_intent == "product_inquiry":
            prefix = "🚗 **产品介绍**\n\n"
        else:
            prefix = ""
        
        # 添加客户需求摘要（如果有）
        needs_summary = ""
        if customer_needs.get("key_concerns"):
            concerns = "、".join(customer_needs["key_concerns"])
            needs_summary = f"\n\n*根据您关注的{concerns}，我为您推荐：*\n\n"
        
        enhanced_answer = prefix + needs_summary + final_answer
        
        # 添加引导语
        if sales_intent != "chitchat":
            enhanced_answer += "\n\n---\n\n💡 如果您还有其他问题，欢迎随时咨询！我可以帮您：\n"
            enhanced_answer += "- 详细介绍产品配置和参数\n"
            enhanced_answer += "- 对比不同版本的优劣势\n"
            enhanced_answer += "- 提供购车优惠和金融方案\n"
            enhanced_answer += "- 安排试驾体验"
        
        return enhanced_answer
        
    except Exception as e:
        logger.error(f"销售模式增强失败: {e}")
        return state.get("final_answer", "")

