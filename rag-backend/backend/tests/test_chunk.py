from rag.chunks.chunks import ChunkResult, TextChunker
from rag.chunks.models import ChunkConfig, ChunkStrategy, DocumentContent
from config.embedding import get_embedding_model
from rag.storage.milvus_storage import MilvusStorage
milvus_storage = MilvusStorage(
        embedding_function=get_embedding_model()
    )
if __name__ == "__main__":
    md_content = """
    # 标题1
    这是标题1的内容。

    ## 标题2
    这是标题2的内容。

    ### 标题3
    这是标题3的内容。
    
    #### 标题4
    这是标题4的内容。
    
    ##### 标题5
    这是标题5的内容。
    """

    chunker = TextChunker()
    md_config = ChunkConfig(
        strategy=ChunkStrategy.MARKDOWN_HEADER
    )
    document = DocumentContent(content=md_content, document_name="crawled_document")
    md_result = chunker.chunk_document(document, md_config)
    result = milvus_storage.store_chunks_batch([md_result])
    #print(md_result)
    print(result)