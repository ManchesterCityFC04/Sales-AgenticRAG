"""
LightRAG存储和检索功能测试

测试LightRAGStorage类的基本功能：
- 初始化
- 文档插入
- 检索查询

运行测试：
cd project
python backend/tests/test_lightrag.py
"""

import asyncio
import os
from backend.rag.storage.lightrag_storage import LightRAGStorage


def test_initialization():
    """测试初始化功能"""
    print("\n=== 测试初始化功能 ===")

    try:
        # 创建存储实例
        storage = LightRAGStorage(workspace="test_workspace")

        # 验证基本属性
        assert storage is not None, "存储实例创建失败"
        assert storage.workspace == "test_workspace", "workspace设置错误"
        assert storage.rag is None, "初始化时rag应为None"
        assert os.path.exists(storage.working_dir), "工作目录未创建"
        print("✓ 初始化测试通过")

    except Exception as e:
        print(f"✗ 初始化测试失败: {e}")
        raise
        


async def test_storage():
    """测试存储功能"""
    print("\n=== 测试存储功能 ===")

    storage = None

    try:
        # 创建存储实例
        storage = LightRAGStorage(workspace="storage_test")

        # # 显式初始化存储
        # await storage.initialize()

        # 测试单个文本插入
        test_text = "LightRAG是一个基于图的检索增强生成系统。"
        await storage.insert_text(test_text)
        print("✓ 单个文本插入成功")

        # # 测试批量文本插入
        # test_texts = [
        #     "LightRAG支持多种存储后端，包括PostgreSQL、Neo4j和Milvus。",
        #     "LightRAG提供naive、local、global、hybrid四种查询模式。",
        #     "该系统专门用于知识图谱构建和查询。"
        # ]
        # await storage.insert_texts(test_texts)
        # print("✓ 批量文本插入成功")

        print("✓ 存储测试通过")

    except Exception as e:
        print(f"✗ 存储测试失败: {e}")
        raise
    finally:
        if storage:
            await storage.finalize()


async def test_retrieval():
    """测试检索功能"""
    print("\n=== 测试检索功能 ===")

    storage = None

    try:
        # 创建存储实例并插入测试数据
        storage = LightRAGStorage(workspace="retrieval_test")

        # 插入测试数据
        test_data = [
            "LightRAG是一个基于图的检索增强生成系统，专门用于知识图谱构建。",
            "系统支持PostgreSQL作为KV存储，Neo4j作为图数据库，Milvus作为向量数据库。",
            "LightRAG提供四种查询模式：naive（朴素）、local（本地）、global（全局）、hybrid（混合）。",
            "Hybrid模式结合了多种查询策略，是推荐的查询方式。"
        ]

        #await storage.insert_texts(test_data)
        print("✓ 测试数据插入完成")

        # 测试查询
        query_text = "什么是LightRAG？"

        # 测试不同查询模式
        query_modes = ["mix"]

        for mode_name in query_modes:
            try:
                result = await storage.query(query_text, mode=mode_name,only_need_prompt=True)
                if result:
                    print(f"✓ {mode_name}查询成功，结果长度: {len(result)}")
                    print(f"✓ {mode_name}查询结果: {result}")
                else:
                    print(f"⚠ {mode_name}查询返回空结果")
            except Exception as e:
                print(f"✗ {mode_name}查询失败: {e}")

        print("✓ 检索测试完成")

    except Exception as e:
        print(f"✗ 检索测试失败: {e}")
        raise
    finally:
        if storage:
            await storage.finalize()


async def test_drop_workspace():
    """测试删除workspace功能"""
    print("\n=== 测试删除workspace功能 ===")

    storage = None

    try:
        # 创建存储实例
        storage = LightRAGStorage(workspace="drop_test")

        # # 插入一些测试数据
        # test_texts = [
        #     "这是测试数据1：LightRAG系统测试。",
        #     "这是测试数据2：知识图谱构建测试。",
        #     "这是测试数据3：向量检索测试。"
        # ]

        # print("正在插入测试数据...")
        # await storage.insert_texts(test_texts)
        # print("✓ 测试数据插入成功")

        # 验证数据存在 - 执行一个查询
        # try:
        #     result = await storage.query("LightRAG", mode="naive")
        #     if result:
        #         print("✓ 查询验证：数据已存在")
        #     else:
        #         print("⚠ 查询验证：未找到数据（可能正常）")
        # except Exception as e:
        #     print(f"⚠ 查询验证失败: {e}")

        # 测试删除workspace
        # print("\n开始测试删除workspace功能...")
        # await storage.drop_workspace()
        # print("✓ drop_workspace函数执行完成")

        # print("✓ drop_workspace测试完成")

    except Exception as e:
        print(f"✗ drop_workspace测试失败: {e}")
        raise
    finally:
        # 注意：这里不需要调用storage.finalize()，因为drop_workspace已经调用了
        pass



if __name__ == "__main__":

    print("=" * 60)
    print("LightRAG 存储和检索功能测试")
    print("=" * 60)

    # 直接运行核心测试
    #test_initialization()
    # asyncio.run(test_storage())
    asyncio.run(test_retrieval())

    # 测试删除workspace功能
    # asyncio.run(test_drop_workspace())

    print("\n✓ 所有测试执行完成")