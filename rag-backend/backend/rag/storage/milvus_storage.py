"""Milvus存储管理类"""

import os
import time
from typing import List, Optional, Dict, Any
from langchain_milvus import Milvus,BM25BuiltInFunction
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from dotenv import load_dotenv

from ..chunks.models import ChunkResult

# 加载环境变量
load_dotenv()


class MilvusStorage:
    """Milvus向量存储管理类
    
    负责将分块后的文档内容存储到Milvus向量数据库中，
    支持向量检索和BM25全文检索。
    """
    
    def __init__(self, 
                 embedding_function: Embeddings,
                 uri: Optional[str] = None, 
                 db_name: Optional[str] = None,
                 token: Optional[str] = None,
                 collection_name: Optional[str] = None):
        """初始化Milvus存储客户端
        
        Args:
            embedding_function: LangChain embedding模型实例（必需）
            uri: Milvus服务地址，默认从环境变量MILVUS_URI获取
            db_name: 数据库名称，默认从环境变量MILVUS_DB_NAME获取
            token: 认证令牌，默认从环境变量MILVUS_TOKEN获取（可选）
            collection_name: 集合名称，默认从环境变量MILVUS_COLLECTION_NAME获取
        """
        
        # 从环境变量读取配置，如果参数没有提供的话
        self.uri = uri or os.getenv('MILVUS_URI', 'http://localhost:19530')
        self.db_name = db_name or os.getenv('MILVUS_DB_NAME', 'rag')
        self.token = token or os.getenv('MILVUS_TOKEN') or None
        self.collection_name = collection_name or os.getenv('MILVUS_COLLECTION_NAME', 'chunks')
        
        # 设置embedding函数
        self.embedding_function = embedding_function
        
        # 初始化LangChain Milvus向量存储
        self.vector_store = Milvus(
            embedding_function=self.embedding_function,
            connection_args={
                "uri": self.uri,
                "db_name": self.db_name,
                "token": self.token
            } if self.token else {
                "uri": self.uri,
                "db_name": self.db_name
            },
            collection_name=self.collection_name,
            builtin_function=BM25BuiltInFunction(),
            consistency_level="Bounded",
            drop_old=False
        )
        
    def store_chunks(self, chunk_result: ChunkResult) -> Dict[str, Any]:
        """存储分块结果到Milvus
        
        Args:
            chunk_result: 分块结果对象
            
        Returns:
            Dict: 插入结果，包含插入状态和记录数
            
        Raises:
            ValueError: 当向量存储未初始化时
            Exception: Milvus操作异常
        """
        if not self.vector_store:
            raise ValueError("向量存储未初始化")
        
        if not chunk_result.chunks:
            return {
                "status": "success", 
                "inserted_count": 0,
                "message": "无数据需要插入"
            }
        
        try:
            # 转换为LangChain Document格式
            documents = self._convert_chunks_to_langchain_docs(chunk_result)
            
            # 为每个文档生成UUID作为主键
            from uuid import uuid4
            uuids = [str(uuid4()) for _ in range(len(documents))]
            
            # 使用LangChain Milvus添加文档，指定IDs
            ids = self.vector_store.add_documents(documents=documents, ids=uuids)
            
            return {
                "status": "success",
                "inserted_count": len(documents),
                "document_ids": ids,
                "document_name": chunk_result.document_name,
                "strategy": chunk_result.strategy.value,
                "collection_name": self.collection_name
            }
            
        except Exception as e:
            raise Exception(f"Milvus插入失败: {str(e)}")
    
    def _convert_chunks_to_langchain_docs(self, chunk_result: ChunkResult) -> List[Document]:
        """为现有Documents添加存储所需的元数据
        
        Args:
            chunk_result: 分块结果，chunks已经是Document列表
            
        Returns:
            List[Document]: 添加了元数据的Document列表
        """
        documents = []
        
        for idx, chunk in enumerate(chunk_result.chunks):
            # 创建符合Milvus集合schema的元数据
            # 注意：page_content会自动映射到text_content字段
            updated_metadata = {
                **chunk.metadata,  # 保留原有元数据
                "document_name": chunk_result.document_name,
                "chunk_index": idx,
                "chunk_size": len(chunk.page_content)
            }
            
            # 创建新Document以避免修改原始数据
            # LangChain会自动将page_content映射到Milvus的text_content字段
            # embedding字段会由embedding_function自动生成
            doc = Document(
                page_content=chunk.page_content,
                metadata=updated_metadata
            )
            documents.append(doc)
        
        return documents
    
    def store_chunks_batch(self, chunk_results: List[ChunkResult]) -> Dict[str, Any]:
        """批量存储多个分块结果到Milvus
        
        Args:
            chunk_results: 分块结果列表
            
        Returns:
            Dict: 批量插入结果
            
        Raises:
            ValueError: 当向量存储未初始化时
            Exception: Milvus操作异常
        """
        if not self.vector_store:
            raise ValueError("向量存储未初始化")
        
        if not chunk_results:
            return {
                "status": "success",
                "message": "没有分块结果需要存储",
                "total_chunks": 0,
                "document_count": 0
            }
        
        try:
            # 收集所有文档
            all_documents = []
            total_chunks = 0
            
            for chunk_result in chunk_results:
                if chunk_result.chunks:
                    documents = self._convert_chunks_to_langchain_docs(chunk_result)
                    all_documents.extend(documents)
                    total_chunks += len(documents)
            
            if not all_documents:
                return {
                    "status": "success",
                    "message": "没有文档需要存储",
                    "total_chunks": 0,
                    "document_count": len(chunk_results)
                }
            
            # 分批处理文档，每批最多8个（留一些余量）
            batch_size = 8
            all_ids = []
            
            for i in range(0, len(all_documents), batch_size):
                batch_documents = all_documents[i:i + batch_size]
                
                # 为当前批次生成UUID作为主键
                from uuid import uuid4
                batch_uuids = [str(uuid4()) for _ in range(len(batch_documents))]
                
                # 批量添加当前批次的文档
                batch_ids = self.vector_store.add_documents(documents=batch_documents, ids=batch_uuids)
                all_ids.extend(batch_ids)
            
            return {
                "status": "success",
                "message": f"成功存储 {len(chunk_results)} 个文档的 {total_chunks} 个分块",
                "total_chunks": total_chunks,
                "document_count": len(chunk_results),
                "ids": all_ids,
                "collection_name": self.collection_name
            }
            
        except Exception as e:
            raise Exception(f"Milvus批量插入失败: {str(e)}")
    
    def delete_document(self, 
                       document_name: str, 
                       collection_name: Optional[str] = None) -> Dict[str, Any]:
        """删除指定文档的所有chunks
        
        Args:
            document_name: 文档名称
            collection_name: collection名称
            
        Returns:
            Dict: 删除结果
        """
        target_collection = collection_name or self.collection_name
        
        try:
            if not self.vector_store:
                raise ValueError("向量存储未初始化")
            
            # 使用LangChain Milvus删除功能
            # 注意：LangChain Milvus可能不支持按元数据过滤删除，这里提供基本实现
            return {
                "status": "error",
                "document_name": document_name,
                "error": "LangChain Milvus不支持按文档名删除，请使用其他方式",
                "collection_name": target_collection
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "document_name": document_name,
                "error": str(e)
            }
    
    def drop_collection(self) -> Dict[str, Any]:
        """删除当前实例的 collection
        
        Returns:
            Dict: 删除结果，包含状态、消息和collection名称
        """
        try:
            if not self.vector_store:
                raise ValueError("向量存储未初始化")
            
            # 通过 LangChain Milvus 的内部客户端删除 collection
            client = self.vector_store.client
            
            # 检查 collection 是否存在
            if client.has_collection(self.collection_name):
                # 删除 collection
                client.drop_collection(self.collection_name)
                return {
                    "status": "success",
                    "message": f"成功删除 Collection '{self.collection_name}'",
                    "collection_name": self.collection_name
                }
            else:
                return {
                    "status": "warning",
                    "message": f"Collection '{self.collection_name}' 不存在",
                    "collection_name": self.collection_name
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"删除 Collection 时出错: {str(e)}",
                "collection_name": self.collection_name,
                "error": str(e)
            }

    def create_hybrid_retriever(self, **kwargs):
        """创建混合检索器
        
        Args:
            **kwargs: 传递给as_retriever方法的参数，支持的参数包括：
                - k: 返回文档数量 (默认: 4)
                - filter: 文档元数据过滤条件
            
        Returns:
            BaseRetriever: 混合检索器实例
        """
        try:
            # 固定使用similarity搜索类型和RRF排序算法
            # 这确保了混合检索的一致性和最佳性能
            kwargs['search_type'] = 'similarity'
            if 'search_kwargs' not in kwargs:
                kwargs['search_kwargs'] = {}
            kwargs['search_kwargs']['ranker_type'] = 'rrf'
            
            return self.vector_store.as_retriever(**kwargs)
        except Exception as e:
            raise Exception(f"创建混合检索器失败: {str(e)}")
    
    def hybrid_search(self, query: str, k: int = 4, **kwargs):
        """执行混合检索
        
        Args:
            query: 查询文本
            k: 返回结果数量
            **kwargs: 其他搜索参数，支持：
                - filter: 文档元数据过滤条件
                - 其他Milvus搜索参数
            
        Returns:
            List[Document]: 检索结果
        """
        try:
            # 固定使用RRF排序算法进行结果融合
            # 这确保了向量检索和BM25检索结果的最佳融合
            kwargs['ranker_type'] = 'rrf'
            return self.vector_store.similarity_search(query, k=k, **kwargs)
        except Exception as e:
            raise Exception(f"混合检索失败: {str(e)}")
    
    def hybrid_search_with_score(self, query: str, k: int = 4, **kwargs):
        """执行带分数的混合检索
        
        Args:
            query: 查询文本
            k: 返回结果数量
            **kwargs: 其他搜索参数，支持：
                - filter: 文档元数据过滤条件
                - 其他Milvus搜索参数
            
        Returns:
            List[Tuple[Document, float]]: 检索结果和分数
        """
        try:
            # 固定使用RRF排序算法进行结果融合
            # 这确保了向量检索和BM25检索结果的最佳融合
            kwargs['ranker_type'] = 'rrf'
            return self.vector_store.similarity_search_with_score(query, k=k, **kwargs)
        except Exception as e:
            raise Exception(f"带分数混合检索失败: {str(e)}")



# 使用示例
if __name__ == "__main__":
    from backend.agent.models import (
        load_chat_model,
        load_embeddings,
        register_embeddings_provider,
        register_model_provider
    )
    
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
    
    # 初始化存储（embedding_function是必需参数，支持混合检索）
    storage = MilvusStorage(
        embedding_function=embeddings_model
    )
    
    # 示例：存储分块结果
    from ..chunks.models import ChunkResult, ChunkStrategy
    from langchain_core.documents import Document
    
    # chunk_result = ChunkResult(
    #     document_name="test—chunk.txt",
    #     chunks=[
    #         Document(page_content="这是第一个分块，包含关于人工智能的内容", metadata={}),
    #         Document(page_content="这是第二个分块，讨论机器学习算法", metadata={}),
    #         Document(page_content="这是第三个分块，介绍小狗", metadata={}),
    #         Document(page_content="这是第四个分块，探讨第二次世界大战的历史", metadata={})
    #     ],
    #     strategy=ChunkStrategy.CHARACTER,  # 使用的分块策略
    #     total_chunks=4 # 总块数
    # )
    
    # # 存储到向量数据库（不再需要传入embedding_function）
    # result = storage.store_chunks(chunk_result)
    # print(f"存储结果: {result}")
    
    # # 获取文档统计信息
    # stats = storage.get_document_stats()
    # print(f"文档统计: {stats}")
    
    # # 混合检索示例
    # print("\n=== 混合检索示例 ===")
    
    # 1. 创建混合检索器
    hybrid_retriever = storage.create_hybrid_retriever(
        search_kwargs={"k": 4}
    )
    print(f"混合检索器创建成功: {type(hybrid_retriever)}")
    
    # 2. 使用混合检索器进行检索
    query = "八嘎鸭肉"
    retrieved_docs = hybrid_retriever.invoke(query)
    print(f"\n检索查询: {query}")
    print(f"检索到 {len(retrieved_docs)} 个文档:")
    for i, doc in enumerate(retrieved_docs):
        print(f"  文档 {i+1}: {doc}...")
    
    # # 3. 直接使用混合搜索方法
    # hybrid_results = storage.hybrid_search(query, k=4)
    # print(f"\n直接混合搜索结果: {len(hybrid_results)} 个文档")
    # for i, doc in enumerate(hybrid_results):
    #     print(f"  结果 {i+1}: {doc.page_content[:50]}...")
     
    #  # 4. 带分数的混合搜索
    # scored_results = storage.hybrid_search_with_score(query, k=4)
    # print(f"\n带分数的搜索结果: {len(scored_results)} 个文档")
    # for i, (doc, score) in enumerate(scored_results):
    #     print(f"  结果 {i+1} (分数: {score:.4f}): {doc.page_content[:50]}...")
     