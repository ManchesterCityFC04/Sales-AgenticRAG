import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuthStore } from './auth'
import { 
  sendMessage as apiSendMessage, 
  sendMessageStream, 
  getChatHistory, 
  getSingleConversationHistory,
  getChatHistoryTitles,
  createConversation as apiCreateConversation,
  deleteConversation as apiDeleteConversation
} from '../api/chat.js'

export const useChatStore = defineStore('chat', () => {
  const conversations = ref([])
  const currentConversation = ref(null)
  const messages = ref([])
  const loading = ref(false)
  const streaming = ref(false)
  const hasUnsavedConversation = ref(false) // 标记是否有未保存的新对话

  // 创建本地临时对话（不调用后端API）
  const createLocalConversation = () => {
    // 如果已经有未保存的对话，直接选中它
    if (hasUnsavedConversation.value && currentConversation.value && !currentConversation.value.saved) {
      return currentConversation.value
    }

    const conversation = {
      id: `temp_${Date.now()}`, // 临时ID
      title: '新对话',
      createdAt: new Date(),
      updatedAt: new Date(),
      saved: false, // 标记为未保存
      messages: [] // 为临时对话添加本地消息存储
    }
    
    // 如果有未保存的对话，先移除它
    if (hasUnsavedConversation.value) {
      const tempIndex = conversations.value.findIndex(c => !c.saved)
      if (tempIndex > -1) {
        conversations.value.splice(tempIndex, 1)
      }
    }
    
    conversations.value.unshift(conversation)
    currentConversation.value = conversation
    messages.value = []
    hasUnsavedConversation.value = true
    
    console.log('创建本地临时对话:', conversation)
    return conversation
  }

  // 保存对话到后端（在首次发送消息时调用）
  const saveConversationToBackend = async (title) => {
    try {
      const authStore = useAuthStore()
      const userId = String(authStore.user?.id || 'default_user')
      
      // 调用后端API创建对话
      const response = await apiCreateConversation(userId, title)
      
      if (response.status === 200 && response.data) {
        const conversationData = response.data
        const savedConversation = {
          id: conversationData.conversation_id,
          title: conversationData.title,
          createdAt: new Date(conversationData.created_at),
          updatedAt: new Date(conversationData.updated_at),
          saved: true
        }
        
        // 更新当前对话
        if (currentConversation.value && !currentConversation.value.saved) {
          // 找到临时对话并替换
          const tempIndex = conversations.value.findIndex(c => c.id === currentConversation.value.id)
          if (tempIndex > -1) {
            conversations.value[tempIndex] = savedConversation
          }
          currentConversation.value = savedConversation
          hasUnsavedConversation.value = false
        }
        
        console.log('成功保存对话到后端:', savedConversation)
        return savedConversation
      } else {
        throw new Error('保存对话失败')
      }
    } catch (error) {
      console.error('保存对话到后端失败:', error)
      throw error
    }
  }

  const createConversation = async (title = '新对话') => {
    try {
      const authStore = useAuthStore()
      const userId = String(authStore.user?.id || 'default_user')
      
      // 调用后端API创建对话
      const response = await apiCreateConversation(userId, title)
      
      if (response.status === 200 && response.data) {
        const conversationData = response.data
        const conversation = {
          id: conversationData.conversation_id,
          title: conversationData.title,
          createdAt: new Date(conversationData.created_at),
          updatedAt: new Date(conversationData.updated_at),
          saved: true
        }
        
        conversations.value.unshift(conversation)
        currentConversation.value = conversation
        messages.value = []
        
        console.log('成功创建对话:', conversation)
        return conversation
      } else {
        throw new Error('创建对话失败')
      }
    } catch (error) {
      console.error('创建对话失败:', error)
      
      // 如果API调用失败，回退到本地创建
      const conversation = {
        id: Date.now().toString(),
        title,
        createdAt: new Date(),
        updatedAt: new Date(),
        saved: false
      }
      conversations.value.unshift(conversation)
      currentConversation.value = conversation
      messages.value = []
      
      console.warn('API创建对话失败，使用本地创建:', conversation)
      return conversation
    }
  }

  const selectConversation = async (conversationId) => {
    const conversation = conversations.value.find(c => c.id === conversationId)
    if (conversation) {
      currentConversation.value = conversation
      
      // 检查是否是临时对话（ID以temp_开头）或者saved属性为false
      const isTemporaryConversation = conversationId.startsWith('temp_') || !conversation.saved
      
      if (isTemporaryConversation) {
        // 未保存的对话使用本地存储的消息，确保数组存在
        messages.value = conversation.messages || []
        console.log('切换到临时对话，使用本地消息:', messages.value)
      } else {
        // 只有已保存的对话才需要从后端加载消息历史
        console.log('切换到已保存对话，从后端加载消息历史')
        await loadConversationMessages(conversationId)
      }
    }
  }

  const loadConversationMessages = async (conversationId) => {
    try {
      loading.value = true
      const response = await getSingleConversationHistory(conversationId)
      
      if (response.status === 200 && response.data) {
        // 检查响应数据结构
        let historyData = response.data
        
        // 如果data是嵌套结构，提取history数组
        if (historyData.success && historyData.history) {
          historyData = historyData.history
        }
        
        // 确保historyData是数组
        if (Array.isArray(historyData)) {
          messages.value = historyData.map((msg, index) => {
            // 基础消息对象
            const baseMessage = {
              id: msg.id || `${Date.now()}-${index}`,
              content: msg.content,
              timestamp: msg.timestamp ? new Date(msg.timestamp) : new Date()
            }
            
            // 格式转换逻辑：统一历史记录和实时消息的格式
            if (msg.type === 'updates' && msg.role === 'system') {
              // 历史记录中的节点更新消息：type: "updates", role: "system"
              // 转换为实时消息格式：role: "node_update"
              return {
                ...baseMessage,
                role: 'node_update',
                node_name: msg.node_name,
                expanded: false // 默认折叠状态
              }
            } else if (msg.type === 'messages') {
              // 历史记录中的普通消息：type: "messages"
              // 保持原有的role（user或assistant）
              return {
                ...baseMessage,
                role: msg.role
              }
            } else {
              // 其他情况保持原格式
              return {
                ...baseMessage,
                role: msg.role
              }
            }
          })
        } else {
          console.warn('历史记录数据格式不正确:', historyData)
          messages.value = []
        }
      }
    } catch (error) {
      console.error('加载对话消息失败:', error)
      messages.value = []
    } finally {
      loading.value = false
    }
  }

  const sendMessage = async (messageData) => {
    // 解析messageData参数
    let content, ragMode, selectedLibrary, conversationIdOverride, collectionId, maxRetrievalDocs, systemPrompt
    if (typeof messageData === 'string') {
      // 兼容旧的字符串参数
      content = messageData
    } else if (typeof messageData === 'object' && messageData.content) {
      // 新的对象参数格式
      content = messageData.content
      ragMode = messageData.ragMode
      selectedLibrary = messageData.selectedLibrary
      maxRetrievalDocs = messageData.maxRetrievalDocs
      systemPrompt = messageData.systemPrompt
      conversationIdOverride = messageData.conversation_id
      collectionId = messageData.collection_id
    } else {
      throw new Error('Invalid message data format')
    }

    // 如果没有当前对话，创建本地临时对话
    if (!currentConversation.value) {
      createLocalConversation()
    }

    // 如果当前对话是未保存的临时对话，先保存到后端
    if (currentConversation.value && !currentConversation.value.saved) {
      try {
        // 使用用户的第一句话作为对话标题（截取前20个字符）
        const title = content.length > 20 ? content.substring(0, 20) + '...' : content
        await saveConversationToBackend(title)
      } catch (error) {
        console.error('保存对话失败，继续使用本地对话:', error)
        // 即使保存失败，也继续发送消息
      }
    }

    const userMessage = {
      id: Date.now().toString(),
      content,
      role: 'user',
      timestamp: new Date()
    }
    messages.value.push(userMessage)
    
    // 如果是未保存的对话，同时保存到本地存储
    if (currentConversation.value && !currentConversation.value.saved) {
      if (!currentConversation.value.messages) {
        currentConversation.value.messages = []
      }
      currentConversation.value.messages.push(userMessage)
    }

    try {
      streaming.value = true

      // 不在开始时创建AI消息占位符，而是在收到第一个token时创建
      // 这样可以确保AI消息显示在所有node_update消息之后
      let aiMessage = null

      // 构造聊天请求数据
      const authStore = useAuthStore()
      const chatData = {
        content: content,
        conversation_id: conversationIdOverride || currentConversation.value.id,
        user_id: String(authStore.user?.id || 'default_user')
      }
      
      // 如果有RAG相关参数，添加到请求数据中
      if (ragMode) {
        chatData.retrieval_mode = ragMode
      }
      if (selectedLibrary) {
        chatData.selected_library = selectedLibrary
      }
      if (collectionId) {
        chatData.collection_id = collectionId
      }
      
      console.log('发送到后端的数据:', chatData)
      if (maxRetrievalDocs !== undefined) {
        chatData.max_retrieval_docs = maxRetrievalDocs
      }
      if (systemPrompt) {
        chatData.system_prompt = systemPrompt
      }
      
      // 使用流式API发送消息
      await sendMessageStream(
        chatData,
        (data) => {
          // 处理流式响应数据
          console.log('收到流式数据:', data)
          
          if (data.type === 'start') {
            // 开始处理聊天请求
            console.log('开始处理聊天请求:', data.message)
          } else if (data.type === 'token') {
            // 实时追加token内容(包括空格和换行符)
            if (data.content !== undefined && data.content !== null) {
              console.log('🔄 收到token:', JSON.stringify(data.content))

              // 如果还没有创建AI消息，在收到第一个token时创建
              // 这样可以确保AI消息显示在所有node_update消息之后
              if (!aiMessage) {
                aiMessage = {
                  id: (Date.now() + 1).toString(),
                  content: '',
                  role: 'assistant',
                  timestamp: new Date()
                }
                messages.value.push(aiMessage)

                // 如果是未保存的对话，同时保存AI消息到本地存储
                if (currentConversation.value && !currentConversation.value.saved) {
                  if (!currentConversation.value.messages) {
                    currentConversation.value.messages = []
                  }
                  currentConversation.value.messages.push(aiMessage)
                }
              }

              // 找到消息在数组中的索引
              const messageIndex = messages.value.findIndex(m => m.id === aiMessage.id)
              if (messageIndex !== -1) {
                // 创建新对象以确保Vue响应式更新
                const currentMsg = messages.value[messageIndex]
                const updatedMsg = {
                  ...currentMsg,
                  content: currentMsg.content + data.content
                }
                messages.value.splice(messageIndex, 1, updatedMsg)

                console.log('🔄 更新: 长度从', currentMsg.content.length, '到', updatedMsg.content.length)
                console.log('🔄 新增内容:', JSON.stringify(data.content))
              } else {
                console.warn('⚠️ 未找到AI消息，aiMessage.id:', aiMessage.id)
              }

              // 如果是未保存的对话，同时更新本地存储
              if (currentConversation.value && !currentConversation.value.saved) {
                const localAiMessage = currentConversation.value.messages?.find(m => m.id === aiMessage.id)
                if (localAiMessage) {
                  localAiMessage.content += data.content
                }
              }
            }
          } else if (data.type === 'node_update') {
            // 处理节点更新消息
            console.log('收到节点更新:', data)
            const nodeUpdateMessage = {
              id: `node-${Date.now()}-${Math.random()}`,
              content: data.content,
              role: 'node_update',
              node_name: data.node_name,
              timestamp: new Date(),
              expanded: false // 默认折叠状态
            }
            messages.value.push(nodeUpdateMessage)
            
            // 如果是未保存的对话，同时保存到本地存储
            if (currentConversation.value && !currentConversation.value.saved) {
              if (!currentConversation.value.messages) {
                currentConversation.value.messages = []
              }
              currentConversation.value.messages.push(nodeUpdateMessage)
            }
          } else if (data.type === 'complete') {
            // 处理完成
            console.log('聊天处理完成:', data.message)
          } else if (data.type === 'answer' && data.content) {
            // 完整答案（备用处理）
            if (aiMessage) {
              aiMessage.content = data.content
            }
          } else if (data.type === 'message' && data.content) {
            // 消息内容（备用处理）
            if (aiMessage) {
              aiMessage.content = data.content
            }
          }
        },
        (error) => {
          console.error('流式消息发送失败:', error)
          if (aiMessage) {
            aiMessage.content = '抱歉，消息发送失败，请重试。'
          }
          streaming.value = false
        },
        () => {
          streaming.value = false
          currentConversation.value.updatedAt = new Date()
          console.log('流式响应完成，最终内容:', aiMessage?.content)
        }
      )
      
      // 处理流式响应已在上面的回调函数中处理
      
    } catch (error) {
      console.error('发送消息失败:', error)
      streaming.value = false
      
      // 如果流式失败，尝试普通API
      try {
        const authStore = useAuthStore()
        const chatData = {
          content: content,
          conversation_id: currentConversation.value.id,
          user_id: authStore.user?.id || 'default_user'
        }
        
        const response = await apiSendMessage(chatData)
        if (response.status === 200 && response.data) {
          const aiMessage = messages.value[messages.value.length - 1]
          aiMessage.content = response.data.content || response.data.message || '收到回复'
        }
      } catch (fallbackError) {
        console.error('备用API也失败:', fallbackError)
        const aiMessage = messages.value[messages.value.length - 1]
        aiMessage.content = '抱歉，消息发送失败，请重试。'
      }
    }
  }

  // 新增：支持销售模式的流式消息发送
  const sendStreamMessage = async (
    content,
    collectionId,
    retrievalMode,
    maxRetrievalDocs,
    systemPrompt,
    salesMode = false,
    salesScenario = 'automotive'
  ) => {
    // 如果没有当前对话，创建本地临时对话
    if (!currentConversation.value) {
      createLocalConversation()
    }

    // 如果当前对话是未保存的临时对话，先保存到后端
    if (currentConversation.value && !currentConversation.value.saved) {
      try {
        const title = content.length > 20 ? content.substring(0, 20) + '...' : content
        await saveConversationToBackend(title)
      } catch (error) {
        console.error('保存对话失败，继续使用本地对话:', error)
      }
    }

    const userMessage = {
      id: Date.now().toString(),
      content,
      role: 'user',
      timestamp: new Date()
    }
    messages.value.push(userMessage)
    
    if (currentConversation.value && !currentConversation.value.saved) {
      if (!currentConversation.value.messages) {
        currentConversation.value.messages = []
      }
      currentConversation.value.messages.push(userMessage)
    }

    try {
      streaming.value = true
      let aiMessage = null

      const authStore = useAuthStore()
      const chatData = {
        content: content,
        conversation_id: currentConversation.value.id,
        user_id: String(authStore.user?.id || 'default_user'),
        collection_id: collectionId || null,
        retrieval_mode: retrievalMode || 'auto',
        max_retrieval_docs: maxRetrievalDocs || 3,
        system_prompt: systemPrompt || '你是一个专业的销售助手',
        sales_mode: salesMode,
        sales_scenario: salesScenario
      }

      console.log('📤 发送聊天数据:', chatData)

      await sendMessageStream(
        chatData,
        (data) => {
          console.log('📨 收到流式数据:', data)
          
          if (data.type === 'start') {
            console.log('🚀 开始接收流式数据')
          } else if (data.type === 'node_update') {
            console.log('📍 节点更新:', data.node_name)
            const nodeUpdateMessage = {
              id: `node-${Date.now()}-${Math.random()}`,
              content: data.content || '',
              role: 'node_update',
              node_name: data.node_name,
              timestamp: new Date(),
              expanded: false
            }
            
            // 如果包含销售信息，添加到消息中
            if (data.sales_info) {
              console.log('🎯 节点更新包含销售信息:', data.sales_info)
              nodeUpdateMessage.salesInfo = data.sales_info
            }
            
            messages.value.push(nodeUpdateMessage)
            
            if (currentConversation.value && !currentConversation.value.saved) {
              if (!currentConversation.value.messages) {
                currentConversation.value.messages = []
              }
              currentConversation.value.messages.push(nodeUpdateMessage)
            }
          } else if (data.type === 'token' || data.type === 'message') {
            if (data.content !== undefined && data.content !== null) {
              if (!aiMessage) {
                aiMessage = {
                  id: (Date.now() + 1).toString(),
                  content: '',
                  role: 'assistant',
                  timestamp: new Date()
                }
                messages.value.push(aiMessage)

                if (currentConversation.value && !currentConversation.value.saved) {
                  if (!currentConversation.value.messages) {
                    currentConversation.value.messages = []
                  }
                  currentConversation.value.messages.push(aiMessage)
                }
              }

              const messageIndex = messages.value.findIndex(m => m.id === aiMessage.id)
              if (messageIndex !== -1) {
                const currentMsg = messages.value[messageIndex]
                const updatedMsg = {
                  ...currentMsg,
                  content: currentMsg.content + data.content
                }
                messages.value.splice(messageIndex, 1, updatedMsg)

                if (currentConversation.value && !currentConversation.value.saved) {
                  const localAiMessage = currentConversation.value.messages?.find(m => m.id === aiMessage.id)
                  if (localAiMessage) {
                    localAiMessage.content += data.content
                  }
                }
              }
            }
            
            // 处理销售信息
            if (data.sales_info) {
              console.log('🎯 收到销售信息:', data.sales_info)
              const messageIndex = messages.value.findIndex(m => m.id === aiMessage?.id)
              if (messageIndex !== -1) {
                messages.value[messageIndex].salesInfo = data.sales_info
              }
            }
          } else if (data.type === 'complete') {
            console.log('✅ 流式聊天完成')
          }
        },
        (error) => {
          console.error('❌ 流式聊天错误:', error)
          streaming.value = false
          if (aiMessage) {
            aiMessage.content = '抱歉，消息发送失败，请重试。'
          }
        },
        () => {
          console.log('✅ 流式响应完成')
          streaming.value = false
          if (currentConversation.value) {
            currentConversation.value.updatedAt = new Date()
          }
        }
      )
    } catch (error) {
      console.error('发送消息失败:', error)
      streaming.value = false
      throw error
    }
  }

  const deleteConversation = async (conversationId) => {
    try {
      // 调用后端API删除对话
      const response = await apiDeleteConversation(conversationId)
      
      if (response.status === 200) {
        // API调用成功，从本地状态中移除对话
        const index = conversations.value.findIndex(c => c.id === conversationId)
        if (index > -1) {
          conversations.value.splice(index, 1)
          
          // 如果删除的是当前对话，清空当前对话和消息
          if (currentConversation.value?.id === conversationId) {
            currentConversation.value = null
            messages.value = []
          }
        }
        
        console.log('成功删除对话:', conversationId)
        return { success: true }
      } else {
        throw new Error('删除对话失败')
      }
    } catch (error) {
      console.error('删除对话失败:', error)
      
      // 即使API调用失败，也尝试从本地状态中移除（用户体验优先）
      const index = conversations.value.findIndex(c => c.id === conversationId)
      if (index > -1) {
        conversations.value.splice(index, 1)
        if (currentConversation.value?.id === conversationId) {
          currentConversation.value = null
          messages.value = []
        }
      }
      
      throw error
    }
  }

  const loadChatHistory = async () => {
    try {
      loading.value = true
      const authStore = useAuthStore()
      
      // 确保用户已登录并且有用户信息
      if (!authStore.user?.id) {
        console.warn('用户未登录或缺少用户ID')
        return
      }
      
      const response = await getChatHistory(authStore.user.id)
      
      if (response.status === 200 && response.data) {
        // 检查响应数据结构，后端返回的是 { success: true, conversations: [...] }
        let conversationsData = response.data
        
        // 如果data包含conversations数组，则使用它
        if (conversationsData.success && conversationsData.conversations) {
          conversationsData = conversationsData.conversations
        }
        
        // 确保conversationsData是数组
        if (Array.isArray(conversationsData)) {
          conversations.value = conversationsData.map(conv => ({
            id: conv.conversation_id, // 注意：后端返回的是conversation_id，不是id
            title: conv.title || '新对话',
            createdAt: new Date(conv.created_at || Date.now()),
            updatedAt: new Date(conv.updated_at || Date.now()),
            saved: true // 从后端加载的对话都是已保存的
          }))
          
          console.log('成功加载对话列表:', conversations.value)
        } else {
          console.warn('对话数据格式不正确:', conversationsData)
          conversations.value = []
        }
      }
    } catch (error) {
      console.error('加载聊天历史失败:', error)
      conversations.value = []
    } finally {
      loading.value = false
    }
  }

  return {
    conversations,
    currentConversation,
    messages,
    loading,
    streaming,
    hasUnsavedConversation,
    createConversation,
    createLocalConversation,
    saveConversationToBackend,
    selectConversation,
    sendMessage,
    sendStreamMessage,
    loadConversationMessages,
    loadChatHistory,
    deleteConversation
  }
})