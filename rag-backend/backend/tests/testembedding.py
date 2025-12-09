from backend.agent import (
    load_chat_model,
    load_embeddings,
    register_embeddings_provider,
    register_model_provider
)
'''
豆包
# 注册自定义embedding提供商
register_embeddings_provider(
    provider_name="doubao_embeddings",
    embeddings_model="openai",
    base_url="https://ark.cn-beijing.volces.com/api/v3"
)

# 加载embedding模型（必需）
embeddings_model = load_embeddings(
    "doubao_embeddings:doubao-embedding-text-240715",
    api_key="your-api-key-here",
    tiktoken_enabled=False,                 # 关键：禁止提前 tokenize
    check_embedding_ctx_length=False,       # 可选：跳过长度检查
    dimensions=2048
)
'''
#阿里
# 注册自定义embedding提供商
register_embeddings_provider(
    provider_name="ali",
    embeddings_model="openai",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 加载embedding模型（必需）
embeddings_model = load_embeddings(
    "ali:text-embedding-v4",
    api_key="sk-",
    #tiktoken_enabled=False,                 # 关键：禁止提前 tokenize
    check_embedding_ctx_length=False,       # 可选：跳过长度检查
    dimensions=1536
)

if __name__ == "__main__":
    #print(embeddings_model)
    docs = embeddings_model.embed_documents(["hello world"])
    print(len(docs[0]))  # 向量的维度
