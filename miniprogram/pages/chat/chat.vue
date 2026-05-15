<template>
  <view class="chat-container">
    <view class="chat-messages">
      <view class="empty-state" v-if="messages.length === 0">
        <text class="empty-icon">🤖</text>
        <text class="empty-title">AI营养顾问</text>
        <text class="empty-desc">您好！我是您的智能营养顾问，请问有什么可以帮您？</text>
      </view>

      <view 
        class="message-item" 
        v-for="(msg, index) in messages" 
        :key="index"
        :class="msg.role"
      >
        <view class="message-avatar">
          <text class="avatar-icon">{{ msg.role === 'user' ? '👤' : '🤖' }}</text>
        </view>
        <view class="message-content">
          <text class="message-text">{{ msg.content }}</text>
          <text class="message-time" v-if="msg.time">{{ msg.time }}</text>
        </view>
      </view>

      <view class="message-item assistant" v-if="isTyping">
        <view class="message-avatar">
          <text class="avatar-icon">🤖</text>
        </view>
        <view class="message-content">
          <view class="typing-indicator">
            <view class="typing-dot"></view>
            <view class="typing-dot"></view>
            <view class="typing-dot"></view>
          </view>
        </view>
      </view>
    </view>

    <view class="quick-questions" v-if="messages.length === 0">
      <text class="quick-title">快捷问题</text>
      <view 
        class="quick-item" 
        v-for="(q, index) in quickQuestions" 
        :key="index"
        @click="sendQuickQuestion(q)"
      >
        <text class="quick-text">{{ q }}</text>
      </view>
    </view>

    <view class="chat-input">
      <input 
        class="input" 
        v-model="inputMessage" 
        placeholder="输入您的问题..."
        placeholder-class="placeholder"
        confirm-type="send"
        @confirm="sendMessage"
      />
      <button class="send-btn" @click="sendMessage" :disabled="!inputMessage.trim() || isTyping">
        <text class="send-icon">➤</text>
      </button>
    </view>
  </view>
</template>

<script>
import { chatAPI } from '@/utils/api.js'

export default {
  data() {
    return {
      messages: [],
      inputMessage: '',
      isTyping: false,
      quickQuestions: [
        '我应该如何控制体重？',
        '糖尿病患者适合吃什么？',
        '每天需要摄入多少蛋白质？',
        '怎样饮食有助于睡眠？',
        '健身期间应该如何饮食？',
        '素食者如何补充营养？'
      ]
    }
  },
  methods: {
    async sendMessage() {
      const message = this.inputMessage.trim()
      if (!message || this.isTyping) return

      this.messages.push({
        role: 'user',
        content: message,
        time: this.getCurrentTime()
      })
      this.inputMessage = ''
      this.isTyping = true
      this.scrollToBottom()

      try {
        const res = await chatAPI.sendMessage(message)
        this.messages.push({
          role: 'assistant',
          content: res.answer,
          time: this.formatTime(res.created_at)
        })
      } catch (error) {
        this.messages.push({
          role: 'assistant',
          content: '抱歉，回复失败，请稍后再试',
          time: this.getCurrentTime()
        })
      } finally {
        this.isTyping = false
        this.scrollToBottom()
      }
    },
    sendQuickQuestion(question) {
      this.inputMessage = question
      this.sendMessage()
    },
    scrollToBottom() {
      this.$nextTick(() => {
        uni.pageScrollTo({
          scrollTop: 99999,
          duration: 200
        })
      })
    },
    getCurrentTime() {
      const now = new Date()
      return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
    },
    formatTime(timeStr) {
      if (!timeStr) return this.getCurrentTime()
      const date = new Date(timeStr)
      return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
    }
  }
}
</script>

<style scoped>
.chat-container {
  min-height: 100vh;
  background: #f5f5f5;
  display: flex;
  flex-direction: column;
  padding-bottom: 120rpx;
}

.chat-messages {
  flex: 1;
  padding: 20rpx 30rpx;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 120rpx 0;
}

.empty-icon {
  font-size: 120rpx;
  margin-bottom: 30rpx;
}

.empty-title {
  font-size: 40rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 16rpx;
}

.empty-desc {
  font-size: 28rpx;
  color: #666;
  text-align: center;
  line-height: 1.6;
}

.message-item {
  display: flex;
  margin-bottom: 30rpx;
  gap: 16rpx;
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.avatar-icon {
  font-size: 56rpx;
}

.message-content {
  max-width: 600rpx;
  background: #fff;
  border-radius: 20rpx;
  padding: 20rpx 24rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.user .message-content {
  background: linear-gradient(135deg, #10b981, #059669);
}

.message-text {
  font-size: 28rpx;
  line-height: 1.6;
  color: #333;
  word-wrap: break-word;
}

.user .message-text {
  color: #fff;
}

.message-time {
  font-size: 22rpx;
  color: #999;
  margin-top: 8rpx;
  display: block;
}

.user .message-time {
  color: rgba(255, 255, 255, 0.7);
  text-align: right;
}

.typing-indicator {
  display: flex;
  gap: 8rpx;
  padding: 10rpx 0;
}

.typing-dot {
  width: 12rpx;
  height: 12rpx;
  background: #999;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-dot:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.5;
  }
  30% {
    transform: translateY(-10rpx);
    opacity: 1;
  }
}

.quick-questions {
  padding: 0 30rpx 30rpx;
}

.quick-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 20rpx;
  display: block;
}

.quick-item {
  background: #fff;
  border-radius: 16rpx;
  padding: 20rpx 24rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.quick-text {
  font-size: 26rpx;
  color: #666;
  line-height: 1.4;
}

.chat-input {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 20rpx 30rpx;
  background: #fff;
  box-shadow: 0 -4rpx 12rpx rgba(0, 0, 0, 0.05);
}

.input {
  flex: 1;
  height: 80rpx;
  background: #f5f5f5;
  border-radius: 40rpx;
  padding: 0 30rpx;
  font-size: 28rpx;
}

.placeholder {
  color: #999;
}

.send-btn {
  width: 80rpx;
  height: 80rpx;
  background: linear-gradient(135deg, #10b981, #059669);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  padding: 0;
}

.send-btn::after {
  border: none;
}

.send-btn[disabled] {
  background: #ccc;
}

.send-icon {
  color: #fff;
  font-size: 32rpx;
}
</style>
