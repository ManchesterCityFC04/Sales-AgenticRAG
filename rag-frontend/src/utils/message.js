import { ElMessage } from 'element-plus'

/**
 * 全局消息提示工具函数
 */
export const message = {
  /**
   * 成功消息
   * @param {string} text 消息内容
   * @param {number} duration 显示时长(ms)，默认3000
   */
  success(text, duration = 3000) {
    ElMessage({
      message: text,
      type: 'success',
      duration
    })
  },

  /**
   * 错误消息
   * @param {string} text 消息内容
   * @param {number} duration 显示时长(ms)，默认3000
   */
  error(text, duration = 3000) {
    ElMessage({
      message: text,
      type: 'error',
      duration
    })
  },

  /**
   * 警告消息
   * @param {string} text 消息内容
   * @param {number} duration 显示时长(ms)，默认3000
   */
  warning(text, duration = 3000) {
    ElMessage({
      message: text,
      type: 'warning',
      duration
    })
  },

  /**
   * 信息消息
   * @param {string} text 消息内容
   * @param {number} duration 显示时长(ms)，默认3000
   */
  info(text, duration = 3000) {
    ElMessage({
      message: text,
      type: 'info',
      duration
    })
  }
}

// 默认导出
export default message