/**
 * API配置文件
 * 包含基础的HTTP请求配置和拦截器
 */

// API基础配置
export const API_CONFIG = {
  // 使用相对路径，通过Vite代理转发到后端
  BASE_URL: '',
  
  // 请求超时时间（毫秒）
  TIMEOUT: 30000,
  
  // 默认请求头
  DEFAULT_HEADERS: {
    'Content-Type': 'application/json',
  }
}

/**
 * HTTP请求工具类
 */
class HttpClient {
  constructor() {
    this.token = null
  }

  /**
   * 设置认证token
   * @param {string} token - JWT token
   */
  setToken(token) {
    this.token = token
    // 存储到localStorage
    if (token) {
      localStorage.setItem('auth_token', token)
    } else {
      localStorage.removeItem('auth_token')
    }
  }

  /**
   * 获取认证token
   * @returns {string|null} JWT token
   */
  getToken() {
    if (!this.token) {
      this.token = localStorage.getItem('auth_token')
    }
    return this.token
  }

  /**
   * 获取请求头
   * @returns {Object} 请求头对象
   */
  getHeaders() {
    const headers = { ...API_CONFIG.DEFAULT_HEADERS }
    const token = this.getToken()
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
    
    return headers
  }

  /**
   * 发送HTTP请求
   * @param {string} url - 请求URL
   * @param {Object} options - 请求选项
   * @returns {Promise} 请求Promise
   */
  async request(url, options = {}) {
    const fullUrl = url.startsWith('http') ? url : `${API_CONFIG.BASE_URL}${url}`
    
    const config = {
      method: 'GET',
      headers: this.getHeaders(),
      ...options
    }

    // 如果有body数据且不是FormData，转换为JSON字符串
    if (config.body && !(config.body instanceof FormData)) {
      config.body = JSON.stringify(config.body)
    }

    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.TIMEOUT)
      
      const response = await fetch(fullUrl, {
        ...config,
        signal: controller.signal
      })
      
      clearTimeout(timeoutId)

      // 检查响应状态
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`)
      }

      // 尝试解析JSON响应
      const contentType = response.headers.get('content-type')
      if (contentType && contentType.includes('application/json')) {
        return await response.json()
      }
      
      return await response.text()
    } catch (error) {
      if (error.name === 'AbortError') {
        throw new Error('请求超时')
      }
      
      // 如果是401错误，清除token
      if (error.message.includes('401')) {
        this.setToken(null)
      }
      
      throw error
    }
  }

  /**
   * GET请求
   * @param {string} url - 请求URL
   * @param {Object} params - 查询参数
   * @returns {Promise} 请求Promise
   */
  async get(url, params = {}) {
    const queryString = new URLSearchParams(params).toString()
    const fullUrl = queryString ? `${url}?${queryString}` : url
    
    return this.request(fullUrl, { method: 'GET' })
  }

  /**
   * POST请求
   * @param {string} url - 请求URL
   * @param {Object} data - 请求数据
   * @returns {Promise} 请求Promise
   */
  async post(url, data = {}) {
    return this.request(url, {
      method: 'POST',
      body: data
    })
  }

  /**
   * PUT请求
   * @param {string} url - 请求URL
   * @param {Object} data - 请求数据
   * @returns {Promise} 请求Promise
   */
  async put(url, data = {}) {
    return this.request(url, {
      method: 'PUT',
      body: data
    })
  }

  /**
   * DELETE请求
   * @param {string} url - 请求URL
   * @returns {Promise} 请求Promise
   */
  async delete(url) {
    return this.request(url, { method: 'DELETE' })
  }
}

// 创建HTTP客户端实例
export const httpClient = new HttpClient()

// 导出token管理函数
export const setAuthToken = (token) => httpClient.setToken(token)
export const getAuthToken = () => httpClient.getToken()

// 导出便捷方法
export const { get, post, put, delete: del } = httpClient