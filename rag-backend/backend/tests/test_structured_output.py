#!/usr/bin/env python3
"""
测试 RetrievalNeedDecision 结构化输出功能
"""

import sys
import os


# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.agent.prompts.raggraph_prompt import RAGGraphPrompts, RetrievalNeedDecision
from backend.tests.test_model import load_chat_model, register_model_provider

from langchain_qwq import ChatQwen
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
load_dotenv()
def test_structured_output():
    """测试结构化输出功能"""
    print("=" * 60)
    print("测试 RetrievalNeedDecision 结构化输出")
    print("=" * 60)
    
    # qwenmodel = ChatQwen(
    #     model="qwen3-max-preview",
    #     api_key="sk-",
    #     base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    #     temperature=0.1  # 降低温度获得更稳定的输出
    # )
    # 1. 注册和加载模型
    print("1. 初始化模型...")
    register_model_provider(
        provider_name="qwen",
        chat_model=ChatQwen
    )

    chat_model = load_chat_model(
        "qwen:qwen3-max-preview",
        temperature=0.1 # 降低温度获得更稳定的输出
    )
    
    
    
    # chat_model=ChatOpenAI(
    #     model="deepseek-v3.1",
    #     api_key="sk-",
    #     base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    #     temperature=0.1  # 降低温度获得更稳定的输出
    # )
    
    print("✓ 模型加载成功")

    # 2. 准备测试用例
    question = "明天天气怎么样"

    print(f"\n2. 测试用例: {question}")

    try:
        # 3. 构建提示词
        prompt_template = RAGGraphPrompts.get_retrieval_need_judgment_prompt()
        prompt = prompt_template.format(question=question)

        print("✓ 提示词构建完成")
        print(f"提示词长度: {len(prompt)} 字符")

        # 4. 测试结构化输出
        print("正在调用结构化输出...")
        structured_llm = chat_model.with_structured_output(RetrievalNeedDecision)
        decision = structured_llm.invoke(prompt)

        # 5. 验证结果
        print("✓ 结构化输出成功!")
        print(f"  - 是否需要检索: {decision.need_retrieval}")
        print(f"  - 提取的问题: {decision.extracted_question}")
        print(f"  - 数据类型: {type(decision)}")

        # 验证字段类型
        assert isinstance(decision.need_retrieval, bool), f"need_retrieval应为bool，实际为{type(decision.need_retrieval)}"
        assert isinstance(decision.extracted_question, str), f"extracted_question应为str，实际为{type(decision.extracted_question)}"

        print("✓ 数据验证通过")

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        print(f"错误类型: {type(e).__name__}")

        # 尝试普通调用看看原始输出
        try:
            print("\n尝试普通调用查看原始输出...")
            raw_response = chat_model.invoke(prompt)
            raw_content = raw_response.content if hasattr(raw_response, 'content') else str(raw_response)
            print(f"原始输出: {raw_content}")
            print(f"输出长度: {len(raw_content)} 字符")

        except Exception as raw_error:
            print(f"普通调用也失败: {raw_error}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    try:

        # 再测试结构化输出
        test_structured_output()

    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()