import os
from pymilvus import MilvusClient, DataType, Function, FunctionType
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

client = MilvusClient(
    uri=os.getenv('MILVUS_URI', 'http://localhost:19530'),
    db_name=os.getenv('MILVUS_DB_NAME', 'rag'),
    token=os.getenv('MILVUS_TOKEN') or None
)

def create_text_chunks_collection(collection_name: str = None, embedding_dim: int = 1536):
    """创建用于存储文本块的collection，支持混合检索"""
    
    # 从环境变量获取collection名称
    collection_name = collection_name or os.getenv('MILVUS_COLLECTION_NAME', 'text_chunks')
    
    # 检查collection是否已存在，如果存在则删除重建
    if client.has_collection(collection_name):
        print(f"Collection '{collection_name}' 已存在，正在删除重建...")
        client.drop_collection(collection_name)
        print(f"已删除旧的Collection '{collection_name}'")
    
    # 定义schema
    schema = client.create_schema(
        auto_id=True,
        enable_dynamic_field=False,  # 禁用动态字段，确保数据结构一致性和查询性能
        description="文本块存储collection，支持向量检索和BM25全文检索"
    )
    
    # 添加字段
    # 主键字段
    schema.add_field(
        field_name="chunk_id", 
        datatype=DataType.INT64, 
        is_primary=True,  # 设置为主键，用于唯一标识每个文本块
        auto_id=True,     # 自动生成ID，无需手动指定
        description="文本块唯一ID"
    )
    
    # 文本内容字段 - 用于BM25检索
    schema.add_field(
        field_name="text_content", 
        datatype=DataType.VARCHAR,
        max_length=8192,
        enable_analyzer=True,  # 启用全文检索
        description="分块后的文本内容"
    )
    
    # 向量字段 - 用于相似度检索
    schema.add_field(
        field_name="embedding", 
        datatype=DataType.FLOAT_VECTOR, 
        dim=embedding_dim,
        description="文本向量表示"
    )
    
    # 文档名称字段 - 用于过滤
    schema.add_field(
        field_name="document_name", 
        datatype=DataType.VARCHAR,
        max_length=512,
        description="原文档名称"
    )
    
    # 元数据字段
    schema.add_field(
        field_name="chunk_index", 
        datatype=DataType.INT32,
        description="块在文档中的序号"
    )
    
    schema.add_field(
        field_name="chunk_size", 
        datatype=DataType.INT32,
        description="文本块字符数"
    )
    
    # 创建索引参数
    index_params = client.prepare_index_params()
    
    # 1. 向量索引 - 使用HNSW算法
    index_params.add_index(
        field_name="embedding",
        index_type="HNSW",        # 层次化小世界图算法，高性能近似最近邻搜索
        metric_type="COSINE",     # 余弦相似度，适合文本向量计算
        params={
            "M": 16,              # 每个节点的最大连接数，影响索引大小和查询精度
            "efConstruction": 200 # 构建索引时的搜索宽度，值越大精度越高但构建越慢
        }
    )
    
    # 2. 全文检索索引 - BM25
    index_params.add_index(
        field_name="text_content",
        index_type="INVERTED",    # 倒排索引，支持BM25全文检索算法
        params={
            "analyzer": "standard"  # 标准分析器，进行分词和词干化处理
        }
    )
    
    # 3. 文档名称索引 - 用于快速过滤
    index_params.add_index(
        field_name="document_name",
        index_type="INVERTED"
    )
    
    # 统一创建collection和索引
    client.create_collection(
        collection_name=collection_name,
        schema=schema,
        index_params=index_params
    )
    
    print(f"Collection '{collection_name}' 创建成功，索引已自动建立")

def load_collection(collection_name: str = None):
    """加载collection到内存"""
    collection_name = collection_name or os.getenv('MILVUS_COLLECTION_NAME', 'text_chunks')
    client.load_collection(collection_name)
    print(f"Collection '{collection_name}' 已加载到内存")

if __name__ == "__main__":
    #print(os.getenv('MILVUSAI_DASHSCOPE_API_KEY'))
    # 创建collection和索引
    create_text_chunks_collection()
    
    # 加载collection
    load_collection()
    
    print("混合检索collection设置完成！")
