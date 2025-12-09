"""LangGraph ReAct 智能体的 MCP 客户端设置和管理。"""

import logging
from typing import Any, Callable, Dict, List, Optional, cast

from langchain_mcp_adapters.client import (  # type: ignore[import-untyped]
    MultiServerMCPClient,
)

logger = logging.getLogger(__name__)

# 全局 MCP 客户端和工具缓存
_mcp_client: Optional[MultiServerMCPClient] = None
_mcp_tools_cache: Dict[str, List[Callable[..., Any]]] = {}

# MCP 服务器配置
MCP_SERVERS = {
    "deepwiki": {
        "url": "https://mcp.deepwiki.com/mcp",
        "transport": "streamable_http",
    },
    "bing-cn-mcp-server": {
      "transport": "sse",
      "url": "https://mcp.api-inference.modelscope.net/991cf3a0e1a94e/sse"
    }
}


async def get_mcp_client(
    server_configs: Optional[Dict[str, Any]] = None,
) -> Optional[MultiServerMCPClient]:
    """获取或初始化具有给定服务器配置的 MCP 客户端。

    如果提供了 server_configs，则为这些特定服务器创建新客户端。
    如果未提供 server_configs，则使用具有所有已配置服务器的全局客户端。
    """
    global _mcp_client

    # 如果提供了特定的服务器配置，则为它们创建专用客户端
    if server_configs is not None:
        try:
            client = MultiServerMCPClient(server_configs)  # pyright: ignore[reportArgumentType]
            logger.info(
                f"Created MCP client with servers: {list(server_configs.keys())}"
            )
            return client
        except Exception as e:
            logger.error("Failed to create MCP client: %s", e)
            return None

    # 否则，对所有服务器使用全局客户端（向后兼容性）
    if _mcp_client is None:
        try:
            _mcp_client = MultiServerMCPClient(MCP_SERVERS)  # pyright: ignore[reportArgumentType]
            logger.info(
                f"Initialized global MCP client with servers: {list(MCP_SERVERS.keys())}"
            )
        except Exception as e:
            logger.error("Failed to initialize global MCP client: %s", e)
            return None
    return _mcp_client


async def get_mcp_tools(server_name: str) -> List[Callable[..., Any]]:
    """获取特定服务器的 MCP 工具，如果需要则初始化客户端。"""
    global _mcp_tools_cache

    # 如果可用，返回缓存的工具
    if server_name in _mcp_tools_cache:
        return _mcp_tools_cache[server_name]

    # 检查服务器是否存在于配置中
    if server_name not in MCP_SERVERS:
        logger.warning(f"MCP server '{server_name}' not found in configuration")
        _mcp_tools_cache[server_name] = []
        return []

    try:
        # 创建特定于服务器的客户端，而不是使用全局单例
        server_config = {server_name: MCP_SERVERS[server_name]}
        client = await get_mcp_client(server_config)
        if client is None:
            _mcp_tools_cache[server_name] = []
            return []

        # 从此特定服务器获取所有工具
        all_tools = await client.get_tools()
        tools = cast(List[Callable[..., Any]], all_tools)

        _mcp_tools_cache[server_name] = tools
        logger.info(f"Loaded {len(tools)} tools from MCP server '{server_name}'")
        return tools
    except Exception as e:
        logger.warning(f"Failed to load tools from MCP server '{server_name}': %s", e)
        _mcp_tools_cache[server_name] = []
        return []



async def get_all_mcp_tools() -> List[Callable[..., Any]]:
    """从所有已配置的 MCP 服务器获取所有工具。"""
    all_tools = []
    for server_name in MCP_SERVERS.keys():
        tools = await get_mcp_tools(server_name)
        all_tools.extend(tools)
    return all_tools


def add_mcp_server(name: str, config: Dict[str, Any]) -> None:
    """添加新的 MCP 服务器配置。"""
    MCP_SERVERS[name] = config
    # 清除客户端以强制使用新配置重新初始化
    clear_mcp_cache()


def remove_mcp_server(name: str) -> None:
    """删除 MCP 服务器配置。"""
    if name in MCP_SERVERS:
        del MCP_SERVERS[name]
        # 清除客户端以强制使用新配置重新初始化
        clear_mcp_cache()


def clear_mcp_cache() -> None:
    """清除 MCP 客户端和工具缓存（对测试有用）。"""
    global _mcp_client, _mcp_tools_cache
    _mcp_client = None
    _mcp_tools_cache = {}
