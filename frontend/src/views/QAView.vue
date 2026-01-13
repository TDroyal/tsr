<template>
  <ContentComponent>
    <div class="chat-container">
      <div class="card">
        <div class="card-header">
          <h5 class="mb-0">🤖 智能时序分析助手</h5>
          <small class="text-muted">基于大模型的时间序列预测与异常检测专家系统</small>
        </div>
        <div class="card-body">
          <!-- 聊天区域 -->
          <div class="chat-area" ref="chatArea">
            <div v-if="messages.length === 0" class="welcome-message">
              <div class="welcome-icon">
                <i class="fas fa-chart-line fa-4x"></i>
              </div>
              <h4>欢迎使用时序分析助手！</h4>
              <p class="text-muted mb-3">我可以帮助您进行时间序列预测、异常检测和数据分析</p>
              <div class="examples">
                <h6>快速开始：</h6>
                <div class="example-buttons">
                  <button class="btn btn-primary-gradient mb-2" 
                          @click="sendExample('在ETTh1数据集上预测一下未来96步长')">
                    <i class="fas fa-chart-line me-2"></i>预测ETTh1数据
                  </button>
                  <button class="btn btn-secondary-gradient mb-2" 
                          @click="sendExample('检测SMD数据集中的异常')">
                    <i class="fas fa-exclamation-triangle me-2"></i>检测SMD异常
                  </button>
                  <button class="btn btn-info-gradient mb-2" 
                          @click="sendExample('有哪些可用的数据集？')">
                    <i class="fas fa-database me-2"></i>查看数据集列表
                  </button>
                </div>
              </div>
            </div>
            
            <div v-else class="messages" ref="messagesContainer">
              <div v-for="(message, index) in messages" :key="index" 
                   :class="['message-wrapper', message.sender]">
                <!-- 消息气泡 -->
                <div class="message-bubble" :class="message.sender">
                  <!-- 用户消息 -->
                  <div v-if="message.sender === 'user'" class="user-message">
                    <!-- 用户头像和名称在右侧 -->
                    <div class="message-header">
                      <span class="message-time">{{ message.time }}</span>
                      <span class="sender-name">您</span>
                      <span class="sender-avatar">
                        <img :src="message_avatar" alt="用户头像" 
                             class="avatar-img" @error="handleAvatarError">
                      </span>
                    </div>
                    <!-- 消息内容 -->
                    <div class="message-content">
                      <div class="content-text">
                        {{ message.content }}
                      </div>
                    </div>
                  </div>
                  
                  <!-- 助手消息 -->
                  <div v-else class="assistant-message">
                    <!-- 助手头像和名称在左侧 -->
                    <div class="message-header">
                      <span class="sender-avatar">
                        <i class="fas fa-robot avatar-icon"></i>
                      </span>
                      <span class="sender-name">时序助手</span>
                      <span class="message-time">{{ message.time }}</span>
                    </div>
                    <!-- 消息内容 -->
                    <div class="message-content">
                      <!-- 加载状态 -->
                      <div v-if="message.loading" class="loading-message">
                        <div class="typing-indicator">
                          <span></span>
                          <span></span>
                          <span></span>
                        </div>
                        <small class="text-muted">正在分析中...</small>
                      </div>
                      
                      <!-- 正常消息 -->
                      <div v-else>
                        <!-- Markdown 渲染 -->
                        <div v-if="message.displayContent" class="markdown-content" v-html="renderMarkdown(message.displayContent)"></div>
                        
                        <!-- 图表显示 - 只在文字打完后再显示 -->
                        <div v-if="message.typingComplete && message.rawToolResult && message.rawToolResult.chart_base64" 
                             class="chart-container">
                          <div class="chart-header">
                            <i class="fas fa-chart-line me-2"></i>
                            <strong>分析图表</strong>
                          </div>
                          <div class="chart-content">
                            <img :src="'data:image/png;base64,' + message.rawToolResult.chart_base64" 
                                 :alt="message.rawToolResult.chart_type === 'prediction' ? '预测结果图' : '异常检测图'"
                                 class="chart-image"
                                 @load="handleImageLoad">
                          </div>
                        </div>

                        <!-- 工具调用信息 - 只在文字打完后再显示 -->
                        <div v-if="message.typingComplete && message.toolUsed" class="tool-call-badge">
                          <i class="fas fa-toolbox me-1"></i>
                          <span>已调用: {{ message.toolUsed }}</span>
                          <i v-if="message.rawToolResult && message.rawToolResult.success" 
                             class="fas fa-check text-success ms-1"></i>
                        </div>
                        
                        <!-- 数据统计卡片 - 只在文字打完后再显示 -->
                        <div v-if="message.typingComplete && message.rawToolResult && message.rawToolResult.stats" 
                             class="stats-cards">
                          <!-- 预测结果统计 -->
                          <div v-if="message.toolUsed === 'predict'" class="stats-card primary">
                            <div class="stats-icon">
                              <i class="fas fa-chart-line"></i>
                            </div>
                            <div class="stats-content">
                              <h6>预测结果统计</h6>
                              <div class="stats-grid">
                                <div class="stat-item">
                                  <span class="stat-label">数据长度</span>
                                  <span class="stat-value">{{ getDataLength(message.rawToolResult) }}</span>
                                </div>
                                <div class="stat-item">
                                  <span class="stat-label">最小值</span>
                                  <span class="stat-value">{{ formatNumber(getDataMin(message.rawToolResult), 4) }}</span>
                                </div>
                                <div class="stat-item">
                                  <span class="stat-label">最大值</span>
                                  <span class="stat-value">{{ formatNumber(getDataMax(message.rawToolResult), 4) }}</span>
                                </div>
                                <div class="stat-item">
                                  <span class="stat-label">平均值</span>
                                  <span class="stat-value">{{ formatNumber(getDataMean(message.rawToolResult), 4) }}</span>
                                </div>
                              </div>
                            </div>
                          </div>
                          
                          <!-- 异常检测统计 -->
                          <div v-if="message.toolUsed === 'anomaly_detection'" class="stats-card warning">
                            <div class="stats-icon">
                              <i class="fas fa-exclamation-triangle"></i>
                            </div>
                            <div class="stats-content">
                              <h6>异常检测结果</h6>
                              <div class="stats-grid">
                                <div class="stat-item">
                                  <span class="stat-label">异常阈值</span>
                                  <span class="stat-value">{{ formatNumber(getAnomalyThreshold(message.rawToolResult), 6) }}</span>
                                </div>
                                <div class="stat-item">
                                  <span class="stat-label">异常点数</span>
                                  <span class="stat-value text-danger">{{ getAnomalyCount(message.rawToolResult) }}</span>
                                </div>
                                <div class="stat-item">
                                  <span class="stat-label">异常比例</span>
                                  <span class="stat-value text-danger">{{ getAnomalyRatio(message.rawToolResult) }}%</span>
                                </div>
                                <div class="stat-item">
                                  <span class="stat-label">总数据点</span>
                                  <span class="stat-value">{{ getDataLength(message.rawToolResult) }}</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                        
                        <!-- 工具响应详情折叠面板 - 只在文字打完后再显示 -->
                        <div v-if="message.typingComplete && message.rawToolResult" class="tool-response-collapse">
                          <div class="collapse-header" @click="toggleToolResponse(message)">
                            <i class="fas fa-code me-2"></i>
                            <span>查看原始数据</span>
                            <i class="fas fa-chevron-down ms-auto transition-icon" 
                               :class="{ 'fa-rotate-180': message.showToolResponse }"></i>
                          </div>
                          
                          <div v-if="message.showToolResponse" class="collapse-content">
                            <div class="json-viewer">
                              <pre><code>{{ JSON.stringify(message.rawToolResult, null, 2) }}</code></pre>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 输入区域固定定位 -->
              <div class="input-area-wrapper">
                <div class="input-area">
                  <!-- 快捷操作按钮 -->
                  <div class="quick-actions">
                    <button class="btn btn-outline-primary quick-btn" 
                            @click="sendExample('在ETTh1数据集上预测一下未来96步长')">
                      <i class="fas fa-chart-line me-1"></i>预测
                    </button>
                    <button class="btn btn-outline-success quick-btn" 
                            @click="sendExample('检测SMD数据集中的异常')">
                      <i class="fas fa-exclamation-triangle me-1"></i>异常检测
                    </button>
                    <button class="btn btn-outline-info quick-btn" 
                            @click="sendExample('有哪些可用的数据集？')">
                      <i class="fas fa-database me-1"></i>数据集
                    </button>
                  </div>
                  
                  <!-- 输入框区域 -->
                  <div class="input-group-wrapper">
                    <div class="input-group">
                      <textarea v-model="userInput" 
                               @keydown.enter.exact.prevent="sendMessage"
                               @keydown.enter.shift.exact="userInput += '\n'"
                               placeholder="请输入您的问题，例如：在ETTh1数据集上预测一下未来96步长..."
                               class="form-control"
                               rows="1"
                               ref="inputTextarea"
                               :disabled="loading"></textarea>
                      <button class="btn btn-send" @click="sendMessage" :disabled="loading">
                        <i v-if="loading" class="fas fa-spinner fa-spin"></i>
                        <i v-else class="fas fa-paper-plane"></i>
                      </button>
                    </div>
                    
                    <!-- 输入提示 -->
                    <div class="input-hint">
                      <small class="text-muted">
                        <i class="fas fa-info-circle me-1"></i>
                        按 Enter 发送，Shift + Enter 换行
                      </small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </ContentComponent>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import ContentComponent from '@/components/ContentComponent.vue'
import $ from 'jquery'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { BackendRootURL } from '@/config/config'
import { useStore } from 'vuex'

// 配置marked
marked.setOptions({
  breaks: true,
  gfm: true
})

export default {
  name: 'QAView',
  components: {
    ContentComponent,
  },
  setup() {
    const store = useStore()
    const chatArea = ref(null)
    const messagesContainer = ref(null)
    const inputTextarea = ref(null)
    const userInput = ref('')
    const loading = ref(false)
    const message_avatar = BackendRootURL + '/static/avatar.jpg'
    
    // 打字机效果定时器
    const typingTimers = new Map()
    
    // 聊天消息
    const messages = ref([
      {
        id: 1,
        sender: 'assistant',
        content: '您好！我是时序分析助手 🤖\n\n我可以帮助您进行：\n\n- **时间序列预测**：在ETT数据集上进行多步预测\n- **异常检测**：识别SMD、PSM、MSL数据集中的异常模式\n- **数据分析**：提供数据统计和可视化图表\n\n请问您需要什么帮助？',
        displayContent: '',
        time: getCurrentTime(),
        loading: false,
        typingComplete: false
      }
    ])
    
    // 自动调整输入框高度
    const adjustTextareaHeight = () => {
      if (inputTextarea.value) {
        inputTextarea.value.style.height = 'auto'
        const newHeight = Math.min(inputTextarea.value.scrollHeight, 120)
        inputTextarea.value.style.height = newHeight + 'px'
      }
    }
    
    // 获取当前时间
    function getCurrentTime() {
      const now = new Date()
      return now.getHours().toString().padStart(2, '0') + ':' + 
             now.getMinutes().toString().padStart(2, '0')
    }
    
    // 渲染Markdown
    const renderMarkdown = (content) => {
      if (!content) return ''
      try {
        const rawMarkdown = marked(content)
        return DOMPurify.sanitize(rawMarkdown)
      } catch (error) {
        console.error('Markdown渲染失败:', error)
        return content
      }
    }
    
    // 滚动到底部
    const scrollToBottom = () => {
      nextTick(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
        } else if (chatArea.value) {
          chatArea.value.scrollTop = chatArea.value.scrollHeight
        }
      })
    }
    
    // 处理图片加载
    const handleImageLoad = () => {
      scrollToBottom()
    }
    
    // 打字机效果
    const startTypingEffect = (message, fullContent) => {
      // 清理旧定时器
      if (typingTimers.has(message.id)) {
        clearInterval(typingTimers.get(message.id))
        typingTimers.delete(message.id)
      }

      message.displayContent = ''
      message.typingComplete = false
      messages.value = [...messages.value]

      let index = 0

      const timer = setInterval(() => {
        if (index >= fullContent.length) {
          clearInterval(timer)
          typingTimers.delete(message.id)
          message.typingComplete = true
          messages.value = [...messages.value]
          return
        }

        message.displayContent += fullContent[index]
        index++

        messages.value = [...messages.value]
        scrollToBottom()
      }, 20)

      typingTimers.set(message.id, timer)
    }
    
    // // 根据字符类型设置不同的打字延迟
    // const getTypingDelay = (char) => {
    //   if (char === '.' || char === '。' || char === '!' || char === '！') {
    //     return 100 // 标点符号后稍作停顿
    //   } else if (char === ',' || char === '，' || char === ';' || char === '；') {
    //     return 50
    //   } else if (char === '\n' || char === '\r') {
    //     return 20 // 换行符
    //   } else {
    //     return 20 // 普通字符
    //   }
    // }
    
    // 处理头像加载错误
    const handleAvatarError = (event) => {
      event.target.style.display = 'none'
      event.target.parentElement.innerHTML = '<i class="fas fa-user avatar-icon"></i>'
    }
    
    // 切换工具响应显示
    const toggleToolResponse = (message) => {
      message.showToolResponse = !message.showToolResponse
    }
    
    // 数据统计相关方法
    const getDataLength = (toolResponse) => {
      if (!toolResponse) return 0
      
      if (toolResponse.data && toolResponse.data.stats && toolResponse.data.stats.length) {
        return toolResponse.data.stats.length
      }
      
      if (toolResponse.stats) {
        if (toolResponse.stats.history_data && toolResponse.stats.history_data.length) {
          return toolResponse.stats.history_data.length
        }
        if (toolResponse.stats.length) {
          return toolResponse.stats.length
        }
      }
      
      return 0
    }
    
    const getDataMin = (toolResponse) => {
      if (!toolResponse) return 0
      
      if (toolResponse.data && toolResponse.data.stats && toolResponse.data.stats.min !== undefined) {
        return toolResponse.data.stats.min
      }
      
      if (toolResponse.stats) {
        if (toolResponse.stats.history_data && toolResponse.stats.history_data.min !== undefined) {
          return toolResponse.stats.history_data.min
        }
        if (toolResponse.stats.min !== undefined) {
          return toolResponse.stats.min
        }
      }
      
      return 0
    }
    
    const getDataMax = (toolResponse) => {
      if (!toolResponse) return 0
      
      if (toolResponse.data && toolResponse.data.stats && toolResponse.data.stats.max !== undefined) {
        return toolResponse.data.stats.max
      }
      
      if (toolResponse.stats) {
        if (toolResponse.stats.history_data && toolResponse.stats.history_data.max !== undefined) {
          return toolResponse.stats.history_data.max
        }
        if (toolResponse.stats.max !== undefined) {
          return toolResponse.stats.max
        }
      }
      
      return 0
    }
    
    const getDataMean = (toolResponse) => {
      if (!toolResponse) return 0
      
      if (toolResponse.data && toolResponse.data.stats && toolResponse.data.stats.mean !== undefined) {
        return toolResponse.data.stats.mean
      }
      
      if (toolResponse.stats) {
        if (toolResponse.stats.history_data && toolResponse.stats.history_data.mean !== undefined) {
          return toolResponse.stats.history_data.mean
        }
        if (toolResponse.stats.mean !== undefined) {
          return toolResponse.stats.mean
        }
      }
      
      return 0
    }
    
    const getDataDimensions = (toolResponse) => {
      if (!toolResponse) return 0
      
      if (toolResponse.data && toolResponse.data.stats && toolResponse.data.stats.dimensions) {
        return toolResponse.data.stats.dimensions
      }
      
      if (toolResponse.stats && toolResponse.stats.dimensions) {
        return toolResponse.stats.dimensions
      }
      
      return 0
    }
    
    const getAnomalyThreshold = (toolResponse) => {
      if (!toolResponse || !toolResponse.stats) return 0
      
      if (toolResponse.stats.threshold !== undefined) {
        return toolResponse.stats.threshold
      }
      
      if (toolResponse.threshold !== undefined) {
        return toolResponse.threshold
      }
      
      return 0
    }
    
    const getAnomalyCount = (toolResponse) => {
      if (!toolResponse || !toolResponse.stats) return 0
      
      if (toolResponse.stats.anomaly_count !== undefined) {
        return toolResponse.stats.anomaly_count
      }
      
      if (toolResponse.pred_labels && Array.isArray(toolResponse.pred_labels)) {
        return toolResponse.pred_labels.filter(label => label === 1).length
      }
      
      return 0
    }
    
    const getAnomalyRatio = (toolResponse) => {
      if (!toolResponse || !toolResponse.stats) return 0
      
      if (toolResponse.stats.anomaly_ratio) {
        const ratioStr = toolResponse.stats.anomaly_ratio.toString()
        const match = ratioStr.match(/([\d.]+)/)
        return match ? parseFloat(match[1]) : 0
      }
      
      const anomalyCount = getAnomalyCount(toolResponse)
      if (toolResponse.pred_labels && toolResponse.pred_labels.length > 0) {
        return (anomalyCount / toolResponse.pred_labels.length * 100).toFixed(2)
      }
      
      return 0
    }
    
    const formatNumber = (num, decimals = 4) => {
      if (num === null || num === undefined || isNaN(num)) return '0.0000'
      return parseFloat(num).toFixed(decimals)
    }
    
    // 发送消息
    const sendMessage = async () => {
      const message = userInput.value.trim()
      if (!message || loading.value) return
      
      // 添加用户消息
      const userMessage = {
        id: Date.now(),
        sender: 'user',
        content: message,
        time: getCurrentTime()
      }
      
      messages.value.push(userMessage)
      
      // 清空输入框
      userInput.value = ''
      adjustTextareaHeight()
      
      // 添加助手消息（加载中）
      const assistantMessage = {
        id: Date.now() + 1,
        sender: 'assistant',
        content: '',
        displayContent: '',
        time: getCurrentTime(),
        loading: true,
        toolUsed: null,
        rawToolResult: null,
        showToolResponse: false,
        typingComplete: false
      }
      
      messages.value.push(assistantMessage)
      
      loading.value = true
      
      // 立即滚动到底部
      scrollToBottom()
      
      try {
        // 调用聊天API
        const response = await $.ajax({
          url: BackendRootURL + "/apiv2/chat",
          type: 'POST',
          headers: {
            'Authorization': "Bearer " + store.state.user.token,
          },
          contentType: 'application/json',
          data: JSON.stringify({ message: message }),
          timeout: 60000
        })
        
        console.log('聊天响应:', response)
        
        // 立即更新助手消息的基本信息
        if (response.success) {
          assistantMessage.content = response.reply || '抱歉，我没有理解您的问题。'
          assistantMessage.toolUsed = response.tool_used || null
          assistantMessage.rawToolResult = response.raw_tool_result || null
          assistantMessage.loading = false
          
          // 使用$nextTick确保DOM更新后再开始打字效果
          nextTick(() => {
            startTypingEffect(assistantMessage, assistantMessage.content)
          })
        } else {
          assistantMessage.content = response.error || '抱歉，我遇到了一个错误。请稍后再试。'
          assistantMessage.loading = false
          // 使用$nextTick确保DOM更新后再开始打字效果
          nextTick(() => {
            startTypingEffect(assistantMessage, assistantMessage.content)
          })
        }
        
      } catch (error) {
        console.error('聊天请求失败:', error)
        assistantMessage.content = '抱歉，我遇到了一个错误。请稍后再试。'
        assistantMessage.loading = false
        // 使用$nextTick确保DOM更新后再开始打字效果
        nextTick(() => {
          startTypingEffect(assistantMessage, assistantMessage.content)
        })
      } finally {
        loading.value = false
      }
    }
    
    // 发送示例消息
    const sendExample = (example) => {
      userInput.value = example
      sendMessage()
    }
    
    // 监听输入框变化
    watch(userInput, adjustTextareaHeight)
    
    // 监听messages变化，自动滚动到底部
    watch(() => messages.value.length, () => {
      scrollToBottom()
    })
    
    // 监听助手消息的displayContent变化
    watch(() => messages.value.map(m => m.displayContent), () => {
      scrollToBottom()
    }, { deep: true })
    
    // 监听typingComplete变化
    watch(() => messages.value.map(m => m.typingComplete), () => {
      scrollToBottom()
    }, { deep: true })
    
    // 生命周期
    onMounted(() => {
      adjustTextareaHeight()
      
      // 使用setTimeout确保DOM完全渲染后再开始打字
      setTimeout(() => {
        if (messages.value[0]) {
          startTypingEffect(messages.value[0], messages.value[0].content)
        }
        scrollToBottom()
        
        // 聚焦输入框
        if (inputTextarea.value) {
          inputTextarea.value.focus()
        }
      }, 300)
    })
    
    onUnmounted(() => {
      // 清理所有打字机定时器
      typingTimers.forEach(timer => {
        clearTimeout(timer)
      })
      typingTimers.clear()
    })
    
    return {
      chatArea,
      messagesContainer,
      inputTextarea,
      userInput,
      loading,
      messages,
      sendMessage,
      sendExample,
      renderMarkdown,
      adjustTextareaHeight,
      handleAvatarError,
      handleImageLoad,
      toggleToolResponse,
      getDataLength,
      getDataMin,
      getDataMax,
      getDataMean,
      getDataDimensions,
      getAnomalyThreshold,
      getAnomalyCount,
      getAnomalyRatio,
      formatNumber,
      message_avatar
    }
  }
}
</script>

<style scoped>
/* 样式保持与之前相同 */
.chat-container {
  padding: 20px;
  height: calc(100vh - 80px);
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea0d 0%, #764ba20d 100%);
}

.card {
  border: none;
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background: white;
}

.card-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px 30px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.card-header h5 {
  font-weight: 600;
  font-size: 1.25rem;
  margin-bottom: 5px;
}

.card-header small {
  opacity: 0.9;
  font-size: 0.9rem;
}

.card-body {
  padding: 0;
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
  background: white;
}

.welcome-message {
  text-align: center;
  padding: 60px 20px;
  max-width: 600px;
  margin: 0 auto;
  color: #333;
}

.welcome-icon {
  margin-bottom: 25px;
  color: #667eea;
  opacity: 0.9;
}

.welcome-message h4 {
  font-weight: 600;
  margin-bottom: 15px;
  color: #333;
  font-size: 1.5rem;
}

.welcome-message p {
  font-size: 1.1rem;
  margin-bottom: 30px;
  color: #666;
}

.examples {
  margin-top: 30px;
  padding: 25px;
  background: linear-gradient(135deg, #667eea08 0%, #764ba208 100%);
  border-radius: 12px;
  border: 1px solid rgba(102, 126, 234, 0.1);
}

.examples h6 {
  font-weight: 600;
  margin-bottom: 20px;
  color: #555;
  font-size: 1.1rem;
}

.example-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 300px;
  margin: 0 auto;
}

.btn-primary-gradient, .btn-secondary-gradient, .btn-info-gradient {
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 20px;
  font-weight: 500;
  transition: all 0.3s ease;
  text-align: left;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-primary-gradient {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.btn-secondary-gradient {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.btn-info-gradient {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.btn-primary-gradient:hover, .btn-secondary-gradient:hover, .btn-info-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

/* 消息区域 */
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  padding-bottom: 180px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message-wrapper {
  display: flex;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.message-wrapper.user {
  justify-content: flex-end;
}

.message-wrapper.assistant {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 70%;
  min-width: 300px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.message-bubble.user {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 4px;
}

.message-bubble.assistant {
  background: white;
  border: 1px solid #eef2f7;
  border-bottom-left-radius: 4px;
}

/* 用户消息样式 */
.user-message {
  padding: 16px 20px;
}

.user-message .message-header {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  margin-bottom: 12px;
}

.user-message .message-time {
  font-size: 0.85rem;
  opacity: 0.8;
}

.user-message .sender-name {
  font-weight: 500;
  font-size: 0.9rem;
}

.user-message .sender-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.user-message .avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-message .content-text {
  font-size: 1rem;
  line-height: 1.5;
  text-align: right;
}

/* 助手消息样式 */
.assistant-message {
  padding: 16px 20px;
}

.assistant-message .message-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.assistant-message .sender-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
}

.assistant-message .sender-name {
  font-weight: 600;
  color: #333;
  font-size: 1rem;
}

.assistant-message .message-time {
  color: #666;
  font-size: 0.85rem;
  margin-left: auto;
}

/* 消息内容 */
.message-content {
  font-size: 0.95rem;
  line-height: 1.6;
  color: #333;
}

/* Markdown 内容样式 */
.markdown-content {
  line-height: 1.7;
  color: #333;
}

.markdown-content h1, 
.markdown-content h2, 
.markdown-content h3, 
.markdown-content h4, 
.markdown-content h5, 
.markdown-content h6 {
  margin-top: 1.2em;
  margin-bottom: 0.6em;
  font-weight: 600;
  color: #222;
}

.markdown-content h1 { font-size: 1.5em; border-bottom: 2px solid #667eea; padding-bottom: 0.3em; }
.markdown-content h2 { font-size: 1.3em; color: #667eea; }
.markdown-content h3 { font-size: 1.1em; color: #764ba2; }

.markdown-content p {
  margin-bottom: 1em;
  color: #444;
}

.markdown-content ul, 
.markdown-content ol {
  padding-left: 1.8em;
  margin-bottom: 1em;
}

.markdown-content li {
  margin-bottom: 0.5em;
}

.markdown-content code {
  background-color: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 0.9em;
  color: #e74c3c;
}

.markdown-content pre {
  background-color: #282c34;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  margin-bottom: 1.2em;
}

.markdown-content pre code {
  background-color: transparent;
  padding: 0;
  color: #abb2bf;
}

.markdown-content blockquote {
  border-left: 4px solid #667eea;
  margin: 1em 0;
  padding: 0.5em 1em;
  background-color: #f8f9fa;
  color: #666;
  font-style: italic;
}

.markdown-content table {
  border-collapse: collapse;
  width: 100%;
  margin-bottom: 1em;
}

.markdown-content table th,
.markdown-content table td {
  border: 1px solid #dee2e6;
  padding: 8px 12px;
  text-align: left;
}

.markdown-content table th {
  background-color: #f8f9fa;
  font-weight: 600;
}

/* 加载动画 */
.loading-message {
  text-align: center;
  padding: 20px 0;
  color: #666;
}

.typing-indicator {
  display: flex;
  justify-content: center;
  margin-bottom: 12px;
  gap: 4px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
  opacity: 0.7;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% { 
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% { 
    transform: scale(1.2);
    opacity: 1;
  }
}

/* 图表容器 */
.chart-container {
  margin-top: 20px;
  border: 1px solid #eef2f7;
  border-radius: 12px;
  overflow: hidden;
  background: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.chart-header {
  background: linear-gradient(135deg, #667eea0d 0%, #764ba20d 100%);
  padding: 12px 20px;
  border-bottom: 1px solid #eef2f7;
  color: #333;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
}

.chart-content {
  padding: 15px;
}

.chart-image {
  width: 100%;
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  display: block;
  box-shadow: 0 2px 4px rgba(0,0,0,0.08);
  transition: transform 0.3s ease;
}

.chart-image:hover {
  transform: scale(1.01);
}

/* 工具调用徽章 */
.tool-call-badge {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  background: linear-gradient(135deg, #667eea0f 0%, #764ba20f 100%);
  color: #667eea;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
  margin-top: 15px;
  border: 1px solid rgba(102, 126, 234, 0.2);
  animation: fadeIn 0.5s ease 0.1s both;
}

/* 统计卡片 */
.stats-cards {
  margin-top: 20px;
  display: grid;
  gap: 12px;
  animation: fadeIn 0.5s ease 0.2s both;
}

.stats-card {
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: flex-start;
  gap: 15px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  animation: fadeIn 0.5s ease 0.3s both;
}

.stats-card.primary {
  background: linear-gradient(135deg, #667eea08 0%, #764ba208 100%);
  border-left: 4px solid #667eea;
}

.stats-card.warning {
  background: linear-gradient(135deg, #f093fb08 0%, #f5576c08 100%);
  border-left: 4px solid #f5576c;
}

.stats-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.stats-card.primary .stats-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stats-card.warning .stats-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.stats-content {
  flex: 1;
}

.stats-content h6 {
  font-weight: 600;
  margin-bottom: 12px;
  color: #333;
  font-size: 0.95rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 10px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  padding: 8px 10px;
  background: white;
  border-radius: 8px;
  border: 1px solid #eef2f7;
  transition: all 0.2s ease;
}

.stat-item:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.05);
}

.stat-label {
  font-size: 0.8rem;
  color: #666;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stat-value {
  font-weight: 600;
  color: #333;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 0.9rem;
}

/* 工具响应折叠面板 */
.tool-response-collapse {
  margin-top: 20px;
  border: 1px solid #eef2f7;
  border-radius: 8px;
  overflow: hidden;
  animation: fadeIn 0.5s ease 0.4s both;
}

.collapse-header {
  background: linear-gradient(135deg, #667eea08 0%, #764ba208 100%);
  padding: 12px 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  color: #667eea;
  font-weight: 500;
  font-size: 0.9rem;
  user-select: none;
  transition: all 0.2s ease;
}

.collapse-header:hover {
  background: linear-gradient(135deg, #667eea12 0%, #764ba212 100%);
}

.transition-icon {
  transition: transform 0.3s ease;
}

.collapse-content {
  background: #f8f9fa;
  max-height: 200px;
  overflow-y: auto;
}

.json-viewer {
  padding: 12px;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 0.85rem;
  line-height: 1.4;
  color: #495057;
  background: white;
}

.json-viewer pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.json-viewer code {
  font-family: inherit;
}

/* 输入区域 */
.input-area-wrapper {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to bottom, transparent, white 30px);
  padding: 20px;
  padding-top: 40px;
}

.input-area {
  background: white;
  padding: 20px;
  border-radius: 16px;
  box-shadow: 0 -2px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #eef2f7;
  backdrop-filter: blur(10px);
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 15px;
  justify-content: center;
}

.quick-btn {
  border-radius: 20px;
  padding: 6px 16px;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  transition: all 0.2s ease;
  border-width: 1px;
}

.quick-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.input-group-wrapper {
  position: relative;
}

.input-group {
  display: flex;
  align-items: flex-end;
  gap: 10px;
}

.form-control {
  border: 2px solid #eef2f7;
  border-radius: 12px;
  padding: 14px 18px;
  resize: none;
  font-size: 0.95rem;
  line-height: 1.5;
  min-height: 56px;
  max-height: 120px;
  transition: all 0.3s ease;
  background: #f8f9fa;
  color: #333;
}

.form-control:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
  background: white;
  outline: none;
}

.form-control:disabled {
  background: #f8f9fa;
  cursor: not-allowed;
}

.btn-send {
  height: 56px;
  width: 56px;
  min-width: 56px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  color: white;
  font-size: 1.2rem;
}

.btn-send:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
}

.btn-send:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.input-hint {
  margin-top: 8px;
  text-align: center;
  color: #666;
  font-size: 0.85rem;
}

/* 滚动条样式 */
.chat-area::-webkit-scrollbar,
.collapse-content::-webkit-scrollbar,
.json-viewer::-webkit-scrollbar {
  width: 6px;
}

.chat-area::-webkit-scrollbar-track,
.collapse-content::-webkit-scrollbar-track,
.json-viewer::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.chat-area::-webkit-scrollbar-thumb,
.collapse-content::-webkit-scrollbar-thumb,
.json-viewer::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.chat-area::-webkit-scrollbar-thumb:hover,
.collapse-content::-webkit-scrollbar-thumb:hover,
.json-viewer::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-container {
    padding: 10px;
    height: calc(100vh - 60px);
  }
  
  .messages {
    padding: 15px;
    padding-bottom: 180px;
  }
  
  .message-bubble {
    max-width: 85%;
    min-width: 250px;
  }
  
  .input-area-wrapper {
    padding: 15px;
    padding-top: 30px;
  }
  
  .input-area {
    padding: 15px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .quick-actions {
    justify-content: center;
  }
  
  .quick-btn {
    font-size: 0.8rem;
    padding: 5px 12px;
  }
  
  .form-control {
    font-size: 0.9rem;
    padding: 12px 16px;
  }
  
  .btn-send {
    height: 50px;
    width: 50px;
    min-width: 50px;
  }
}

@media (max-width: 576px) {
  .chat-container {
    padding: 0;
  }
  
  .card {
    border-radius: 0;
  }
  
  .messages {
    padding: 10px;
    padding-bottom: 170px;
  }
  
  .message-bubble {
    max-width: 90%;
    min-width: 200px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .form-control {
    font-size: 0.85rem;
  }
  
  .btn-send {
    height: 44px;
    width: 44px;
    min-width: 44px;
  }
}
</style>