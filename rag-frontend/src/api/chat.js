/**
 * 聊天相关API接口
 * 对接后端 /workspace/rag-zxj/rag-demo/backend/api/chat.py
 */

import { httpClient } from './config.js'

/**
 * 发送聊天消息（非流式）
 * @param {Object} chatData - 聊天数据
 * @param {string} chatData.content - 消息内容
 * @param {string} [chatData.conversation_id] - 会话ID（可选）
 * @param {string} [chatData.user_id] - 用户ID（可选）
 * @returns {Promise<Object>} 聊天响应
 */
export async function sendMessage(chatData) {
  try {
    const response = await httpClient.post('/api/llm/chat', chatData)
    return response
  } catch (error) {
    console.error('发送消息失败:', error)
    throw new Error(error.message || '发送消息失败')
  }
}

/**
 * 发送聊天消息（流式响应）
 * @param {Object} chatData - 聊天数据
 * @param {string} chatData.content - 消息内容
 * @param {string} [chatData.conversation_id] - 会话ID
 * @param {string} [chatData.user_id] - 用户ID
 * @param {string} [chatData.collection_id] - 知识库ID
 * @param {boolean} [chatData.sales_mode] - 是否启用销售模式
 * @param {string} [chatData.sales_scenario] - 销售场景
 * @param {Function} onMessage - 消息回调函数
 * @param {Function} [onError] - 错误回调函数
 * @param {Function} [onComplete] - 完成回调函数
 * @returns {Promise<void>}
 */
export async function sendMessageStream(chatData, onMessage, onError, onComplete) {
  try {
    const url = `/api/llm/chat/stream`
    console.log('🚀 开始流式请求:', url, chatData)
    
    // 添加默认销售模式参数
    const requestData = {
      ...chatData,
      sales_mode: chatData.sales_mode !== undefined ? chatData.sales_mode : false,
      sales_scenario: chatData.sales_scenario || 'automotive'
    }
    
    console.log('📋 完整请求数据:', requestData)
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...httpClient.getHeaders()
      },
      body: JSON.stringify(requestData)
    })

    console.log('📡 收到响应:', response.status, response.statusText)
    console.log('📋 响应头:', Object.fromEntries(response.headers.entries()))

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    console.log('🔄 开始读取流式数据...')

    try {
      let chunkCount = 0
      while (true) {
        const { done, value } = await reader.read()
        
        if (done) {
          console.log('✅ 流式数据读取完成，总共处理了', chunkCount, '个数据块')
          onComplete && onComplete()
          break
        }

        chunkCount++
        const chunk = decoder.decode(value, { stream: true })
        console.log(`📦 收到第${chunkCount}个数据块:`, chunk)
        
        const lines = chunk.split('\n')
        console.log('📄 分割后的行数:', lines.length, lines)

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const jsonStr = line.slice(6)
              console.log('🔍 解析JSON字符串:', jsonStr)
              const data = JSON.parse(jsonStr)
              console.log('✨ 解析成功的数据:', data)
              
              if (data.type === 'error') {
                console.error('❌ 收到错误数据:', data)
                onError && onError(new Error(data.message || data.error))
              } else {
                console.log('📨 调用onMessage回调，数据类型:', data.type)
                onMessage && onMessage(data)
              }
            } catch (parseError) {
              console.warn('⚠️ 解析流式数据失败:', parseError, '原始行:', line)
            }
          } else if (line.trim()) {
            console.log('🔸 非data行:', line)
          }
        }
      }
    } finally {
      reader.releaseLock()
      console.log('🔓 释放reader锁')
    }
  } catch (error) {
    console.error('💥 流式聊天请求失败:', error)
    onError && onError(error)
  }
}

/**
 * 获取聊天历史记录
 * @param {string} userId - 用户ID
 * @param {string} [conversationId] - 会话ID（可选）
 * @returns {Promise<Object>} 聊天历史响应
 */
export async function getChatHistory(userId, conversationId = null) {
  try {
    const params = conversationId ? { conversation_id: conversationId } : {}
    const response = await httpClient.get(`/api/llm/history/${userId}`, params)
    return response
  } catch (error) {
    console.error('获取聊天历史失败:', error)
    throw new Error(error.message || '获取聊天历史失败')
  }
}

/**
 * 获取单轮对话历史记录
 * @param {string} conversationId - 会话ID
 * @returns {Promise<Object>} 单轮对话历史响应
 */
export async function getSingleConversationHistory(conversationId) {
  try {
    const response = await httpClient.get(`/api/llm/history/single/${conversationId}`)
    return response
  } catch (error) {
    console.error('获取单轮对话历史失败:', error)
    throw new Error(error.message || '获取单轮对话历史失败')
  }
}

/**
 * 获取所有历史记录标题列表
 * @param {string} userId - 用户ID
 * @returns {Promise<Object>} 历史记录标题列表响应
 */
export async function getChatHistoryTitles(userId) {
  try {
    const response = await httpClient.get(`/api/llm/history/titles/${userId}`)
    return response
  } catch (error) {
    console.error('获取历史记录标题列表失败:', error)
    throw new Error(error.message || '获取历史记录标题列表失败')
  }
}

/**
 * 获取签名URL
 * @returns {Promise<Object>} 签名URL响应
 */
export async function getSignatureUrl() {
  try {
    const response = await httpClient.post('/api/llm/get-url')
    return response
  } catch (error) {
    console.error('获取签名URL失败:', error)
    throw new Error(error.message || '获取签名URL失败')
  }
}

/**
 * 添加聊天历史记录
 * @param {string} userId - 用户ID
 * @param {string} conversationId - 会话ID
 * @param {Array} messages - 消息列表
 * @returns {Promise<Object>} 响应结果
 */
export async function addChatHistory(userId, conversationId, messages) {
  try {
    const response = await httpClient.post('/api/llm/history', {
      user_id: userId,
      conversation_id: conversationId,
      messages: messages
    })
    return response
  } catch (error) {
    console.error('添加聊天历史记录失败:', error)
    throw new Error(error.message || '添加聊天历史记录失败')
  }
}

/**
 * 创建新对话
 * @param {string} userId - 用户ID
 * @param {string} [title] - 对话标题（可选）
 * @returns {Promise<Object>} 创建结果
 */
export async function createConversation(userId, title = null) {
  try {
    const response = await httpClient.post('/api/llm/conversation', {
      user_id: userId,
      title: title
    })
    return response
  } catch (error) {
    console.error('创建对话失败:', error)
    throw new Error(error.message || '创建对话失败')
  }
}

/**
 * 删除对话
 * @param {string} conversationId - 对话ID
 * @returns {Promise<Object>} 删除结果
 */
export async function deleteConversation(conversationId) {
  try {
    const response = await httpClient.delete(`/api/llm/conversation/${conversationId}`)
    return response
  } catch (error) {
    console.error('删除对话失败:', error)
    throw new Error(error.message || '删除对话失败')
  }
}

/**
 * 导出对话历史
 * @param {string} conversationId - 会话ID
 * @param {string} format - 导出格式 (markdown/json/text)
 * @returns {Promise<void>} 下载文件
 */
export async function exportConversation(conversationId, format = 'markdown') {
  try {
    const url = `/api/llm/conversation/${conversationId}/export?format=${format}`
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        ...httpClient.getHeaders()
      }
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    // 获取文件名
    const contentDisposition = response.headers.get('Content-Disposition')
    let filename = `conversation_${conversationId}.${format === 'markdown' ? 'md' : format === 'json' ? 'json' : 'txt'}`
    if (contentDisposition) {
      // 优先解析 RFC 5987 格式：filename*=UTF-8''encoded_filename
      const rfc5987Match = contentDisposition.match(/filename\*=UTF-8''(.+)/)
      if (rfc5987Match) {
        filename = decodeURIComponent(rfc5987Match[1])
      } else {
        // 回退到传统格式：filename="filename"
        const filenameMatch = contentDisposition.match(/filename="(.+)"/)
        if (filenameMatch) {
          filename = filenameMatch[1]
        }
      }
    }

    // 获取文件内容
    const blob = await response.blob()
    
    // 创建下载链接
    const downloadUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(downloadUrl)

    return { success: true, filename }
  } catch (error) {
    console.error('导出对话失败:', error)
    throw new Error(error.message || '导出对话失败')
  }
}

/**
 * 流式聊天辅助类
 * 用于管理流式聊天的状态和事件
 */
export class StreamChatManager {
  constructor() {
    this.isStreaming = false
    this.currentMessage = ''
    this.onMessageCallbacks = []
    this.onErrorCallbacks = []
    this.onCompleteCallbacks = []
  }

  /**
   * 添加消息回调
   * @param {Function} callback - 回调函数
   */
  onMessage(callback) {
    this.onMessageCallbacks.push(callback)
  }

  /**
   * 添加错误回调
   * @param {Function} callback - 回调函数
   */
  onError(callback) {
    this.onErrorCallbacks.push(callback)
  }

  /**
   * 添加完成回调
   * @param {Function} callback - 回调函数
   */
  onComplete(callback) {
    this.onCompleteCallbacks.push(callback)
  }

  /**
   * 开始流式聊天
   * @param {Object} chatData - 聊天数据
   */
  async startStream(chatData) {
    if (this.isStreaming) {
      throw new Error('已有流式聊天正在进行中')
    }

    this.isStreaming = true
    this.currentMessage = ''

    try {
      await sendMessageStream(
        chatData,
        (data) => {
          this.currentMessage += data.content || ''
          this.onMessageCallbacks.forEach(callback => callback(data, this.currentMessage))
        },
        (error) => {
          this.isStreaming = false
          this.onErrorCallbacks.forEach(callback => callback(error))
        },
        () => {
          this.isStreaming = false
          this.onCompleteCallbacks.forEach(callback => callback(this.currentMessage))
        }
      )
    } catch (error) {
      this.isStreaming = false
      throw error
    }
  }

  /**
   * 停止流式聊天
   */
  stopStream() {
    this.isStreaming = false
  }

  /**
   * 清理回调函数
   */
  clearCallbacks() {
    this.onMessageCallbacks = []
    this.onErrorCallbacks = []
    this.onCompleteCallbacks = []
  }
}