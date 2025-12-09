/**
 * API模块统一导出
 * 提供所有API接口的统一入口
 */

// 导出HTTP客户端配置
export { httpClient, setAuthToken, getAuthToken } from './config.js'

// 导出认证相关函数
export {
  login,
  register,
  getCurrentUser,
  accessProtected,
  logout,
  isAuthenticated,
  getToken
} from './auth.js'

// 导出聊天相关函数
export {
  sendMessage,
  sendMessageStream,
  getChatHistory,
  getSingleConversationHistory,
  getChatHistoryTitles,
  getSignatureUrl,
  addChatHistory,
  createConversation,
  StreamChatManager
} from './chat.js'

/**
 * API状态码常量
 */
export const API_STATUS = {
  SUCCESS: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  INTERNAL_SERVER_ERROR: 500
}

/**
 * API响应类型常量
 */
export const RESPONSE_TYPE = {
  SUCCESS: 'success',
  ERROR: 'error'
}

/**
 * 聊天消息类型常量
 */
export const MESSAGE_TYPE = {
  USER: 'user',
  ASSISTANT: 'assistant',
  SYSTEM: 'system'
}

/**
 * 流式聊天事件类型
 */
export const STREAM_EVENT_TYPE = {
  MESSAGE: 'message',
  ERROR: 'error',
  COMPLETE: 'complete',
  START: 'start'
}