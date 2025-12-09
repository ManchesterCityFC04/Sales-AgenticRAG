/**
 * 知识库API服务模块
 * 提供知识库和文档的增删改查功能
 */

import { httpClient } from './config.js'

/**
 * 知识库API服务类
 */
class KnowledgeLibraryAPI {
  
  /**
   * 获取用户的知识库列表
   * @returns {Promise} API响应
   */
  async getLibraries() {
    try {
      const response = await httpClient.get('/api/knowledge/libraries')
      return response
    } catch (error) {
      console.error('获取知识库列表失败:', error)
      throw error
    }
  }

  /**
   * 获取知识库详情
   * @param {number} libraryId - 知识库ID
   * @returns {Promise} API响应
   */
  async getLibraryDetail(libraryId) {
    try {
      const response = await httpClient.get(`/api/knowledge/libraries/${libraryId}`)
      return response
    } catch (error) {
      console.error('获取知识库详情失败:', error)
      throw error
    }
  }

  /**
   * 创建知识库
   * @param {Object} libraryData - 知识库数据
   * @param {string} libraryData.title - 知识库标题
   * @param {string} libraryData.description - 知识库描述
   * @returns {Promise} API响应
   */
  async createLibrary(libraryData) {
    try {
      const response = await httpClient.post('/api/knowledge/libraries', libraryData)
      return response
    } catch (error) {
      console.error('创建知识库失败:', error)
      throw error
    }
  }

  /**
   * 更新知识库
   * @param {number} libraryId - 知识库ID
   * @param {Object} libraryData - 知识库数据
   * @returns {Promise} API响应
   */
  async updateLibrary(libraryId, libraryData) {
    try {
      const response = await httpClient.put(`/api/knowledge/libraries/${libraryId}`, libraryData)
      return response
    } catch (error) {
      console.error('更新知识库失败:', error)
      throw error
    }
  }

  /**
   * 删除知识库
   * @param {number} libraryId - 知识库ID
   * @returns {Promise} API响应
   */
  async deleteLibrary(libraryId) {
    try {
      const response = await httpClient.delete(`/api/knowledge/libraries/${libraryId}`)
      return response
    } catch (error) {
      console.error('删除知识库失败:', error)
      throw error
    }
  }

  /**
   * 添加文档到知识库
   * @param {Object} documentData - 文档数据
   * @param {number} documentData.library_id - 知识库ID
   * @param {string} documentData.title - 文档标题
   * @param {string} documentData.content - 文档内容
   * @returns {Promise} API响应
   */
  async addDocument(documentData) {
    try {
      const response = await httpClient.post('/api/knowledge/documents', documentData)
      return response
    } catch (error) {
      console.error('添加文档失败:', error)
      throw error
    }
  }

  /**
   * 更新文档
   * @param {number} documentId - 文档ID
   * @param {Object} documentData - 文档数据
   * @returns {Promise} API响应
   */
  async updateDocument(documentId, documentData) {
    try {
      const response = await httpClient.put(`/api/knowledge/documents/${documentId}`, documentData)
      return response
    } catch (error) {
      console.error('更新文档失败:', error)
      throw error
    }
  }

  /**
   * 删除文档
   * @param {number} documentId - 文档ID
   * @returns {Promise} API响应
   */
  async deleteDocument(documentId) {
    try {
      const response = await httpClient.delete(`/api/knowledge/documents/${documentId}`)
      return response
    } catch (error) {
      console.error('删除文档失败:', error)
      throw error
    }
  }

  /**
   * 获取文件上传URL
   * @param {string} documentName - 文档名称
   * @returns {Promise} API响应
   */
  async getUploadUrl(documentName) {
    try {
      // 不对文件名进行额外编码，让后端处理
      const response = await httpClient.post('/api/knowledge/upload-url', {
        document_name: documentName
      })
      return response
    } catch (error) {
      console.error('获取上传URL失败:', error)
      throw error
    }
  }

  /**
   * 上传文件到OSS
   * @param {string} uploadUrl - 上传URL
   * @param {File} file - 文件对象
   * @returns {Promise} 上传响应
   */
  async uploadFileToOSS(uploadUrl, file) {
    try {
      return new Promise(async (resolve, reject) => {
        try {
          const xhr = new XMLHttpRequest();
          
          xhr.open('PUT', uploadUrl, true);
          
          // 关键：读取文件为ArrayBuffer，然后创建无类型的Blob
          // 这样浏览器不会自动添加Content-Type header
          const arrayBuffer = await file.arrayBuffer();
          const blob = new Blob([arrayBuffer]); // 不指定type，创建无类型Blob
          
          xhr.onload = function() {
            if (xhr.status >= 200 && xhr.status < 300) {
              console.log('OSS上传成功，状态码:', xhr.status);
              resolve({
                success: true,
                url: uploadUrl.split('?')[0]
              });
            } else {
              console.error('OSS上传失败，状态码:', xhr.status);
              console.error('响应内容:', xhr.responseText);
              reject(new Error(`上传失败: ${xhr.status} ${xhr.statusText}`));
            }
          };
          
          xhr.onerror = function() {
            console.error('OSS上传网络错误');
            reject(new Error('网络错误'));
          };
          
          xhr.onabort = function() {
            console.warn('OSS上传被中止');
            reject(new Error('上传被中止'));
          };
          
          // 发送无类型的Blob，避免Content-Type header
          console.log('开始上传到OSS，文件大小:', blob.size, 'bytes');
          xhr.send(blob);
        } catch (error) {
          console.error('准备上传时出错:', error);
          reject(error);
        }
      });
    } catch (error) {
      console.error('上传文件到OSS失败:', error);
      throw error;
    }
  }

  /**
   * 爬取网站内容
   * @param {Object} crawlData - 爬取数据
   * @param {string} crawlData.url - 网站URL
   * @param {number} crawlData.library_id - 知识库ID
   * @param {number} [crawlData.max_pages] - 最大页面数
   * @returns {Promise} API响应
   */
  async crawlSite(crawlData) {
    try {
      const response = await httpClient.post('/api/crawl/site', crawlData)
      return response
    } catch (error) {
      console.error('爬取网站失败:', error)
      throw error
    }
  }

  /**
   * 获取知识图谱数据
   * @param {string} collectionId - 集合ID
   * @param {string} label - 标签过滤器
   * @returns {Promise} API响应
   */
  async getKnowledgeGraph(collectionId, label = '*') {
    try {
      const response = await httpClient.get(`/api/visual/graph/${collectionId}`, {
        label: label
      })
      return response
    } catch (error) {
      console.error('获取知识图谱失败:', error)
      throw error
    }
  }

  /**
   * 处理已上传的文档
   * @param {Object} processData - 处理数据
   * @param {string} processData.url - 文档URL
   * @param {string} processData.collection_id - 集合ID
   * @param {string} processData.user_id - 用户ID
   * @param {string} processData.title - 文档标题
   * @returns {Promise} API响应
   */
  async processDocument(processData) {
    try {
      const response = await httpClient.post('/api/crawl/load-document', {
        url: processData.url,
        collection_id: processData.collection_id,
        user_id: processData.user_id || "default_user",
        title: processData.title || "未命名文档"
      })
      return response
    } catch (error) {
      console.error('处理文档失败:', error)
      throw error
    }
  }
}

// 创建并导出API实例
export const knowledgeAPI = new KnowledgeLibraryAPI()

// 导出默认实例
export default knowledgeAPI