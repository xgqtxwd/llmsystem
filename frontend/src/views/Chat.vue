<template>
  <div class="chat-container">
    <van-nav-bar title="营养咨询" left-arrow @click-left="$router.back()" />

    <div class="chat-messages" ref="messagesContainer">
      <div v-if="messages.length === 0" class="empty-state">
        <div class="empty-icon-wrapper">
          <van-icon name="chat-o" size="48" color="#d1d5db" />
        </div>
        <h3>AI 营养顾问</h3>
        <p>有什么营养健康问题，随时问我</p>

        <div class="quick-questions">
          <span
            v-for="(q, index) in quickQuestions"
            :key="index"
            class="quick-tag"
            :style="{ animationDelay: (index * 0.1) + 's' }"
            @click="selectQuestion(q)"
          >
            {{ q }}
          </span>
        </div>
      </div>

      <template v-else>
        <div
          v-for="msg in messages"
          :key="msg.id"
          :class="['message-item', msg.isSelf ? 'message-self' : 'message-ai']"
        >
          <div class="message-avatar">
            <div :class="['avatar-circle', msg.isSelf ? 'avatar-user' : 'avatar-ai']">
              <van-icon :name="msg.isSelf ? 'user-o' : 'service-o'" size="18" />
            </div>
          </div>
          <div class="message-body">
            <div class="message-bubble">{{ msg.content }}</div>
            <span class="message-time">{{ formatTime(msg.time) }}</span>
          </div>
        </div>

        <div v-if="loading" class="message-item message-ai">
          <div class="message-avatar">
            <div class="avatar-circle avatar-ai">
              <van-icon name="service-o" size="18" />
            </div>
          </div>
          <div class="message-body">
            <div class="message-bubble typing-bubble">
              <span class="dot"></span>
              <span class="dot"></span>
              <span class="dot"></span>
            </div>
          </div>
        </div>
      </template>
    </div>

    <div class="chat-input-area">
      <div class="input-wrapper">
        <input
          v-model="inputMessage"
          type="text"
          placeholder="输入您的问题..."
          @keyup.enter="sendMessage"
          :disabled="loading"
          class="chat-input"
        />
        <button
          class="send-btn"
          :class="{ active: inputMessage.trim() && !loading }"
          :disabled="!inputMessage.trim() || loading"
          @click="sendMessage"
        >
          <van-icon name="guide-o" size="20" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { chatAPI } from '@/api'
import { showToast } from 'vant'

const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const messagesContainer = ref(null)

const quickQuestions = [
  '什么是BMI？如何计算？',
  '减肥期间应该怎么吃？',
  '哪些食物富含蛋白质？',
  '如何控制血糖？',
  '健康的饮食习惯有哪些？'
]

function formatTime(time) {
  const date = new Date(time)
  return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

async function sendMessage() {
  if (!inputMessage.value.trim() || loading.value) return

  const userMessage = inputMessage.value.trim()
  inputMessage.value = ''

  messages.value.push({
    id: Date.now(),
    content: userMessage,
    isSelf: true,
    time: new Date()
  })

  loading.value = true
  scrollToBottom()

  try {
    const response = await chatAPI.sendMessage(userMessage)

    messages.value.push({
      id: response.id,
      content: response.answer,
      isSelf: false,
      time: response.created_at
    })
  } catch (error) {
    showToast('发送失败，请重试')
    messages.value.push({
      id: Date.now(),
      content: '抱歉，现在无法回答您的问题。请稍后重试。',
      isSelf: false,
      time: new Date()
    })
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

function selectQuestion(question) {
  inputMessage.value = question
  sendMessage()
}

async function loadHistory() {
  try {
    const history = await chatAPI.getHistory(1, 50)
    messages.value = history.reverse().map(msg => ({
      id: msg.id,
      content: msg.question,
      isSelf: true,
      time: msg.created_at
    })).concat(
      history.reverse().map(msg => ({
        id: msg.id + '-answer',
        content: msg.answer,
        isSelf: false,
        time: new Date(new Date(msg.created_at).getTime() + 1000)
      }))
    ).sort((a, b) => new Date(a.time) - new Date(b.time))
  } catch (error) {
    console.log('暂无历史记录')
  }
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f0fdf4;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  padding-bottom: 20px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 40px 24px;
  text-align: center;
}

.empty-icon-wrapper {
  width: 90px;
  height: 90px;
  border-radius: 28px;
  background: linear-gradient(135deg, #ecfdf5, #d1fae5);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.empty-state h3 {
  margin: 0 0 6px;
  font-size: 19px;
  font-weight: 700;
  color: var(--text-primary);
}

.empty-state p {
  margin: 0 0 28px;
  font-size: 14px;
  color: var(--text-muted);
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  max-width: 340px;
}

.quick-tag {
  padding: 10px 16px;
  border-radius: 20px;
  background: white;
  font-size: 13px;
  color: var(--text-secondary);
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  transition: var(--transition);
  animation: fadeInUp 0.4s ease-out both;
}

.quick-tag:active {
  transform: scale(0.95);
  background: #ecfdf5;
  color: #059669;
}

.message-item {
  display: flex;
  gap: 10px;
  margin-bottom: 18px;
  animation: fadeInUp 0.3s ease-out;
}

.message-self {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.avatar-circle {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.avatar-user {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
}

.avatar-ai {
  background: linear-gradient(135deg, #10b981, #059669);
}

.message-body {
  max-width: 72%;
  display: flex;
  flex-direction: column;
}

.message-self .message-body {
  align-items: flex-end;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.7;
  word-break: break-word;
  white-space: pre-wrap;
  box-shadow: var(--shadow-sm);
}

.message-self .message-bubble {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border-bottom-right-radius: 4px;
}

.message-ai .message-bubble {
  background: white;
  color: var(--text-primary);
  border-bottom-left-radius: 4px;
}

.typing-bubble {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 14px 20px;
  min-width: 60px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #94a3b8;
  animation: typingBounce 1.4s ease-in-out infinite;
}

.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes typingBounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-6px); opacity: 1; }
}

.message-time {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 4px;
  padding: 0 4px;
}

.chat-input-area {
  padding: 12px 16px;
  padding-bottom: calc(12px + env(safe-area-inset-bottom));
  background: white;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.06);
}

.input-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #f1f5f9;
  border-radius: 24px;
  padding: 6px 6px 6px 18px;
  transition: var(--transition);
}

.input-wrapper:focus-within {
  background: white;
  box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2), var(--shadow-md);
}

.chat-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 15px;
  color: var(--text-primary);
  background: transparent;
  padding: 8px 0;
}

.chat-input::placeholder {
  color: #c4cbd5;
}

.send-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: #e2e8f0;
  color: #94a3b8;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition);
  flex-shrink: 0;
}

.send-btn.active {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  box-shadow: 0 3px 10px rgba(16, 185, 129, 0.35);
}

.send-btn:active:not(:disabled) {
  transform: scale(0.92);
}
</style>
