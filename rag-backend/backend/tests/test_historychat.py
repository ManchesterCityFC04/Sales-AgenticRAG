from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
from langchain_qwq import ChatQwen
# 导入必要的模块
from backend.agent.models import (
    load_chat_model,
    load_embeddings,
    register_embeddings_provider,
    register_model_provider
)
from backend.agent.graph import RAGGraph
from langchain_core.messages import HumanMessage, AIMessage

def extract_latest_conversation(history):
    """
    从StateSnapshot历史记录中提取最新的完整对话
    
    Args:
        history: list of StateSnapshot objects
        
    Returns:
        list: 最新对话的消息列表
    """
    if not history:
        return []
    
    # 获取最新的状态快照
    latest_snapshot = history[0] if history else None
    if not latest_snapshot or not hasattr(latest_snapshot, 'values'):
        return []
    
    # 从最新快照中提取消息
    messages = latest_snapshot.values.get("messages", [])
    
    # 过滤出用户和AI的消息
    conversation_messages = []
    for msg in messages:
        if isinstance(msg, (HumanMessage, AIMessage)):
            conversation_messages.append(msg)
    
    return conversation_messages

def print_simple_chat_history(history):
    """
    简洁版聊天记录打印，只显示最新的完整对话

    Args:
        history: list of StateSnapshot objects
    """
    messages = extract_latest_conversation(history)

    print("最新对话记录:")
    print("-" * 30)

    for message in messages:
        if isinstance(message, HumanMessage):
            print(f"👤 {message.content}")
        elif isinstance(message, AIMessage):
            print(f"🤖 {message.content}")

    print("-" * 30)

if __name__ == "__main__":
    register_model_provider(
        provider_name="qwen",
        chat_model=ChatQwen
    )

    chat_model = load_chat_model(
        "qwen:qwen3-max-preview"
    )
    register_embeddings_provider(
    provider_name="ali",
    embeddings_model="openai",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    embeddings_model = load_embeddings(
    "ali:text-embedding-v4",
    api_key="sk-",
    check_embedding_ctx_length=False,
    dimensions=1536
    )
    rag_graph = RAGGraph(llm=chat_model, embedding_model=embeddings_model)
    config = {
        "configurable": {
            "thread_id": "test_streaaamss_mssessasssge1s_01"
        }
    }
    history=list(rag_graph.graph.get_state_history(config))
    print(history)
    # 仅输出最新快照的对话记录
    #print_simple_chat_history(history)