from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
import os
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
from psycopg_pool import ConnectionPool

from ..states.raggraph_state import RAGGraphState, create_initial_rag_state
from ..contexts.raggraph_context import RAGContext
from .raggraph_node import RAGNodes
from ...rag.storage.milvus_storage import MilvusStorage
from ...rag.storage.lightrag_storage import LightRAGStorage


class RAGGraph:
    """RAG图计算框架

    基于流程图设计的RAG系统，包含以下节点：
    - start: 开始节点
    - check_retrieval_needed: 判断是否需要检索
    - direct_answer: 直接回答常规问题（不需要检索）
    - expand_subquestions: 由原始问题扩展子问题
    - classify_question_type: 判断检索类型（向量检索/图检索）
    - vector_db_retrieval: 适合使用向量数据库检索
    - graph_db_retrieval: 适合使用图数据库检索
    - generate_answer: 生成答案节点
    - end: 结束节点
    """

    def __init__(self, llm=None, embedding_model=None, enable_checkpointer=True, workspace="kb12_1760260169325"):
        """初始化RAG图

        Args:
            llm: 用户配置的语言模型，用于问题分类、相关性检查、答案生成等
            embedding_model: 用户配置的嵌入模型，用于向量检索
            enable_checkpointer: 是否启用PostgreSQL checkpoint持久化存储，LangGraph Studio环境下应设为False
        """
        self.graph = None
        self.checkpointer = None
        self.enable_checkpointer = enable_checkpointer
        self.conn_pool = None  # 初始化连接池引用

        # 存储用户配置的模型
        self.llm = llm
        self.embedding_model = embedding_model

        # 初始化PostgreSQL Store用于langmem记忆持久化
        self.memory_store = None

        # 初始化MilvusStorage
        self.milvus_storage = None
        if self.embedding_model:
            try:

                self.milvus_storage = MilvusStorage(
                    embedding_function=self.embedding_model,  # 必需参数，放在第一位
                    collection_name=workspace,
                )
                print("[RAG Graph] MilvusStorage初始化成功")
            except Exception as e:
                print(f"[RAG Graph] MilvusStorage初始化失败: {e}")
                self.milvus_storage = None
        else:
            print("[RAG Graph] 警告：未提供embedding_model，跳过MilvusStorage初始化")

        # 初始化LightRAG存储
        self.lightrag_storage = None
        try:
            self.lightrag_storage = LightRAGStorage(workspace=workspace)
            print(f"[RAG Graph] LightRAG存储初始化成功，workspace: {workspace}")
        except Exception as e:
            print(f"[RAG Graph] LightRAG存储初始化失败: {e}")
            self.lightrag_storage = None

        # 从环境变量读取数据库连接配置
        self.db_config = {
            "host": os.getenv("POSTGRES_HOST", "localhost"),
            "port": int(os.getenv("POSTGRES_PORT", "5432")),
            "database": os.getenv("POSTGRES_DATABASE", "rag_checkpoint"),
            "user": os.getenv("POSTGRES_USER", "postgres"),
            "password": os.getenv("POSTGRES_PASSWORD", "123456")
        }

        # 只在启用checkpointer时才设置checkpoint和memory store
        if self.enable_checkpointer:
            try:
                # 创建数据库连接字符串
                connection_string = (
                    f"postgresql://{self.db_config['user']}:{self.db_config['password']}"
                    f"@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}"
                )

                # 创建连接池
                conn_pool = ConnectionPool(connection_string, min_size=1, max_size=5)
                self.conn_pool = conn_pool

                # 1. 设置PostgreSQL checkpoint
                try:
                    self.checkpointer = PostgresSaver(conn=conn_pool)
                    self.checkpointer.setup()
                    print(f"[RAG Graph] PostgresSaver已启用", self.checkpointer)
                except Exception as checkpoint_error:
                    print(f"[RAG Graph] PostgresSaver设置失败: {checkpoint_error}")
                    self.checkpointer = None

                # 2. 设置PostgreSQL memory store
                try:
                    self.memory_store = PostgresStore(conn=conn_pool)
                    self.memory_store.setup()
                    if self.memory_store:
                        print(f"[RAG Graph] PostgresStore初始化成功", self.memory_store)
                    else:
                        print(f"[RAG Graph] PostgresStore初始化失败")
                except Exception as store_error:
                    print(f"[RAG Graph] PostgresStore设置失败: {store_error}")
                    self.memory_store = None

                print(f"[RAG Graph] PostgreSQL服务已启用: {self.db_config['host']}:{self.db_config['port']}")

            except Exception as e:
                print(f"[RAG Graph] PostgreSQL服务设置失败: {e}")
                print("[RAG Graph] 将在无持久化模式下运行")
                self.checkpointer = None
                self.memory_store = None
        else:
            print("[RAG Graph] Checkpointer和Memory Store已禁用")

        # 创建节点实例
        self.nodes = RAGNodes(
            llm=self.llm,
            embedding_model=self.embedding_model,
            milvus_storage=self.milvus_storage,
            memory_store=self.memory_store,
            checkpointer=self.checkpointer,
            lightrag_storage=self.lightrag_storage
        )

        self._build_graph()

    def _build_graph(self) -> None:
        """构建状态图"""
        # 创建状态图，指定context_schema
        workflow = StateGraph(
            RAGGraphState,
            context_schema=RAGContext
        )

        # 添加节点
        workflow.add_node("start", self.nodes.start_node)
        workflow.add_node("check_retrieval_needed", self.nodes.check_retrieval_needed_node)
        workflow.add_node("direct_answer", self.nodes.direct_answer_node)
        workflow.add_node("expand_subquestions", self.nodes.expand_subquestions_node)
        workflow.add_node("classify_question_type", self.nodes.classify_question_type_node)
        workflow.add_node("vector_db_retrieval", self.nodes.vector_db_retrieval_node)
        workflow.add_node("graph_db_retrieval", self.nodes.graph_db_retrieval_node)
        workflow.add_node("generate_answer", self.nodes.generate_answer_node)

        # 设置入口点
        workflow.set_entry_point("start")

        # 添加边和条件边
        self._add_edges(workflow)

        # 编译图，启用checkpoint
        self.graph = workflow.compile(checkpointer=self.checkpointer,store=self.memory_store)

    def _add_edges(self, workflow: StateGraph) -> None:
        """添加图的边和条件边"""
        # 开始 -> 是否需要检索
        workflow.add_edge("start", "check_retrieval_needed")

        # 是否需要检索的条件边
        workflow.add_conditional_edges(
            "check_retrieval_needed",
            self.nodes.route_retrieval_needed,
            {
                "need_retrieval": "expand_subquestions",
                "no_retrieval": "direct_answer"
            }
        )

        # 扩展子问题 -> 判断检索类型
        workflow.add_edge("expand_subquestions", "classify_question_type")

        # 判断检索类型的条件边
        workflow.add_conditional_edges(
            "classify_question_type",
            self.nodes.route_question_type,
            {
                "vector_db": "vector_db_retrieval",
                "graph_db": "graph_db_retrieval"
            }
        )

        # 向量数据库检索 -> 生成答案
        workflow.add_edge("vector_db_retrieval", "generate_answer")

        # 图数据库检索 -> 生成答案
        workflow.add_edge("graph_db_retrieval", "generate_answer")

        # 直接回答 -> 结束
        workflow.add_edge("direct_answer", END)

        # 生成答案 -> 结束
        workflow.add_edge("generate_answer", END)

    # ==================== 节点实现已移至 raggraph_node.py ====================
    # 所有节点方法和路由方法现在由 self.nodes (RAGNodes实例) 提供

    # ==================== 公共接口 ====================

    def invoke(self, input_data: Dict[str, Any], context: RAGContext, config: Optional[Dict[str, Any]] = None) -> RAGGraphState:
        """执行RAG图计算

        Args:
            input_data: 输入数据，包含question等字段
            context: RAG上下文配置
            config: 配置参数，包含thread_id等checkpoint相关配置

        Returns:
            最终状态
        """
        if self.graph is None:
            raise RuntimeError("图未正确初始化")

        # 如果启用checkpoint且未提供config，使用context的配置
        if self.checkpointer and config is None:
            config = context.get_langgraph_config()

        # 使用初始化函数创建初始状态
        initial_state = create_initial_rag_state(
            context=context,
            input_data=input_data
        )

        result = self.graph.invoke(initial_state, context=context, config=config)
        return result

    def stream(self, input_data: Dict[str, Any], context: RAGContext, config: Optional[Dict[str, Any]] = None, stream_mode: str = "updates"):
        """流式执行RAG图计算

        Args:
            input_data: 输入数据，包含question等字段
            context: RAG上下文配置
            config: 配置参数，包含thread_id等checkpoint相关配置
            stream_mode: 流式输出模式，支持 "updates", "values", "messages", "debug"

        Yields:
            每个步骤的状态更新
        """
        if self.graph is None:
            raise RuntimeError("图未正确初始化")

        # 如果启用checkpoint且未提供config，使用context的配置
        if self.checkpointer and config is None:
            config = context.get_langgraph_config()
            # 如果context也没有session_id，使用默认值
            if not config:
                config = {"configurable": {"thread_id": "default"}}

        # 使用初始化函数创建初始状态
        initial_state = create_initial_rag_state(
            context=context,
            input_data=input_data
        )

        # 根据stream_mode调用不同的流式方法
        try:
            if stream_mode == "values":
                # 流式输出完整状态值
                for step in self.graph.stream(initial_state, context=context, config=config, stream_mode="values"):
                    yield step
            elif stream_mode == "messages":
                # 流式输出LLM消息
                for step in self.graph.stream(initial_state, context=context, config=config, stream_mode="messages"):
                    yield step
            elif stream_mode == "mix":
                # 混合模式，同时输出messages和updates
                for step in self.graph.stream(initial_state, context=context, config=config, stream_mode=["messages","updates"]):
                    # mode,chunk=step
                    # if mode == "messages":
                    #     msg,metadata=chunk
                    #     if msg.content:
                    #         print(f"消息: {msg.content}")
                    yield step
            else:
                # 默认使用updates模式
                for step in self.graph.stream(initial_state, context=context, config=config, stream_mode="updates"):
                    yield step
        except TypeError as e:
            # 如果LangGraph版本不支持stream_mode参数，回退到基本模式
            print(f"[RAG Graph] 警告：stream_mode参数不被支持，回退到基本流式模式: {e}")
            for step in self.graph.stream(initial_state, context=context, config=config):
                yield step

    async def astream(self, input_data: Dict[str, Any], context: RAGContext, config: Optional[Dict[str, Any]] = None, stream_mode: str = "updates"):
        """异步流式执行RAG图计算

        Args:
            input_data: 输入数据，包含question等字段
            context: RAG上下文配置
            config: 配置参数，包含thread_id等checkpoint相关配置
            stream_mode: 流式输出模式，支持 "updates", "values", "messages", "debug"

        Yields:
            每个步骤的状态更新
        """
        if self.graph is None:
            raise RuntimeError("图未正确初始化")

        # 如果启用checkpoint且未提供config，使用context的配置
        if self.checkpointer and config is None:
            config = context.get_langgraph_config()
            # 如果context也没有session_id，使用默认值
            if not config:
                config = {"configurable": {"thread_id": "default"}}

        # 使用初始化函数创建初始状态
        initial_state = create_initial_rag_state(
            context=context,
            input_data=input_data
        )

        # 根据stream_mode调用不同的异步流式方法
        try:
            if stream_mode == "values":
                # 流式输出完整状态值
                async for step in self.graph.astream(initial_state, context=context, config=config, stream_mode="values"):
                    yield step
            elif stream_mode == "messages":
                # 流式输出LLM消息
                async for step in self.graph.astream(initial_state, context=context, config=config, stream_mode="messages"):
                    yield step
            elif stream_mode == "mix":
                # 混合模式，同时输出messages和updates
                async for step in self.graph.astream(initial_state, context=context, config=config, stream_mode=["messages","updates"]):
                    yield step
            else:
                # 默认使用updates模式
                async for step in self.graph.astream(initial_state, context=context, config=config, stream_mode="updates"):
                    yield step
        except TypeError as e:
            # 如果LangGraph版本不支持stream_mode参数，回退到基本模式
            print(f"[RAG Graph] 警告：stream_mode参数不被支持，回退到基本流式模式: {e}")
            async for step in self.graph.astream(initial_state, context=context, config=config):
                yield step

    def get_state(self, thread_id: str) -> Optional[RAGGraphState]:
        """获取指定线程的状态

        Args:
            thread_id: 线程ID

        Returns:
            状态对象，如果不存在则返回None
        """
        if not self.checkpointer:
            return None

        try:
            config = {"configurable": {"thread_id": thread_id}}
            state_snapshot = self.graph.get_state(config)
            return state_snapshot.values if state_snapshot else None
        except Exception as e:
            print(f"[RAG Graph] 获取状态失败: {e}")
            return None

    def update_state(self, thread_id: str, state_update: Dict[str, Any]) -> bool:
        """更新指定线程的状态

        Args:
            thread_id: 线程ID
            state_update: 状态更新数据

        Returns:
            是否更新成功
        """
        if not self.checkpointer:
            return False

        try:
            config = {"configurable": {"thread_id": thread_id}}
            self.graph.update_state(config, state_update)
            return True
        except Exception as e:
            print(f"[RAG Graph] 更新状态失败: {e}")
            return False

    def get_state_history(self, thread_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取指定线程的状态历史

        Args:
            thread_id: 线程ID
            limit: 返回的历史记录数量限制

        Returns:
            状态历史列表
        """
        if not self.checkpointer:
            return []

        try:
            config = {"configurable": {"thread_id": thread_id}}
            history = []
            for state in self.graph.get_state_history(config, limit=limit):
                history.append({
                    "values": state.values,
                    "next": state.next,
                    "config": state.config,
                    "created_at": state.created_at,
                    "parent_config": state.parent_config
                })
            return history
        except Exception as e:
            print(f"[RAG Graph] 获取状态历史失败: {e}")
            return []

    def __del__(self):
        """析构方法，清理连接池资源"""
        if hasattr(self, 'conn_pool') and self.conn_pool:
            try:
                self.conn_pool.close()
                print("[RAG Graph] PostgreSQL连接池已关闭")
            except Exception as e:
                print(f"[RAG Graph] 关闭连接池时出错: {e}")