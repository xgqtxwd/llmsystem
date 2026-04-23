<template>
  <div class="admin-container">
    <van-nav-bar title="管理员中心" left-arrow @click-left="$router.back()" />

    <div class="admin-tabs">
      <div
        v-for="tab in mainTabs"
        :key="tab.value"
        class="admin-tab-item"
        :class="{ active: activeTab === tab.value }"
        @click="switchMainTab(tab.value)"
      >
        <van-icon :name="tab.icon" size="16" />
        <span>{{ tab.label }}</span>
        <span v-if="tab.value === 'knowledge' && hasActiveTask" class="task-dot"></span>
      </div>
    </div>

    <div class="tab-content">
      <div v-if="activeTab === 'users'" class="users-content">
        <div class="sub-tabs">
          <span
            v-for="st in userSubTabs"
            :key="st.value"
            class="sub-tab"
            :class="{ active: userTab === st.value }"
            @click="switchUserSubTab(st.value)"
          >
            {{ st.label }}
          </span>
        </div>

        <div v-if="userTab === 'list'">
          <van-pull-refresh v-model="refreshing" @refresh="loadUsers">
            <van-list
              v-model:loading="loading"
              :finished="finished"
              finished-text="没有更多用户了"
              @load="loadUsers"
            >
              <div
                v-for="user in users"
                :key="user.id"
                class="user-card animate-fadeInUp"
                @click="showUserDetail(user)"
              >
                <div class="user-avatar">
                  {{ (user.username || user.email || user.phone || '?').charAt(0).toUpperCase() }}
                </div>
                <div class="user-info">
                  <h4>{{ user.username || user.email || user.phone }}</h4>
                  <p>ID: {{ user.id }}</p>
                </div>
                <van-tag :type="user.is_admin ? 'danger' : 'success'" size="medium" round>
                  {{ user.is_admin ? '管理员' : '普通用户' }}
                </van-tag>
              </div>
            </van-list>
          </van-pull-refresh>
        </div>

        <div v-else-if="userTab === 'activity'">
          <div class="stats-grid">
            <div class="stat-card stat-card-blue">
              <div class="stat-icon-wrap"><van-icon name="friends-o" size="22" /></div>
              <div class="stat-data">
                <span class="stat-num">{{ activityStats.daily_active_users }}</span>
                <span class="stat-label">日活用户</span>
              </div>
            </div>
            <div class="stat-card stat-card-green">
              <div class="stat-icon-wrap"><van-icon name="calendar-o" size="22" /></div>
              <div class="stat-data">
                <span class="stat-num">{{ activityStats.weekly_active_users }}</span>
                <span class="stat-label">周活用户</span>
              </div>
            </div>
            <div class="stat-card stat-card-orange">
              <div class="stat-icon-wrap"><van-icon name="chart-trending-o" size="22" /></div>
              <div class="stat-data">
                <span class="stat-num">{{ activityStats.monthly_active_users }}</span>
                <span class="stat-label">月活用户</span>
              </div>
            </div>
            <div class="stat-card stat-card-purple">
              <div class="stat-icon-wrap"><van-icon name="like-o" size="22" /></div>
              <div class="stat-data">
                <span class="stat-num">{{ activityStats.retention_rate }}%</span>
                <span class="stat-label">留存率</span>
              </div>
            </div>
          </div>

          <div class="behavior-section">
            <h4>功能使用分布</h4>
            <div v-for="item in behaviorData.feature_usage" :key="item.feature" class="behavior-item">
              <div class="behavior-header">
                <span>{{ item.feature }}</span>
                <strong>{{ item.percentage }}%</strong>
              </div>
              <div class="progress-track">
                <div class="progress-fill" :style="{ width: item.percentage + '%' }"></div>
              </div>
            </div>
          </div>
        </div>

        <div v-else-if="userTab === 'feedback'">
          <van-pull-refresh v-model="feedbackRefreshing" @refresh="loadFeedbacks">
            <van-list
              v-model:loading="feedbackLoading"
              :finished="feedbackFinished"
              finished-text="暂无更多反馈"
              @load="loadFeedbacks"
            >
              <div
                v-for="fb in feedbacks"
                :key="fb.id"
                class="feedback-card"
              >
                <div class="feedback-top">
                  <span class="feedback-user">{{ fb.username }}</span>
                  <van-tag :type="getFeedbackType(fb.status)" round size="small">{{ fb.status }}</van-tag>
                </div>
                <p class="feedback-text">{{ fb.content }}</p>
                <span class="feedback-time">{{ fb.created_at }}</span>
              </div>
            </van-list>
          </van-pull-refresh>
        </div>
      </div>

      <div v-else-if="activeTab === 'knowledge'" class="knowledge-content">
        <div class="section-block">
          <h4 class="block-title">文档上传配置</h4>
          <div class="config-grid">
            <div class="config-field" @click="showChunkPicker = true">
              <label>分块方式</label>
              <div class="config-value">
                <span>{{ uploadForm.chunkMethodLabel }}</span>
                <van-icon name="arrow-down" size="12" />
              </div>
            </div>
            <div class="config-field" @click="showEmbeddingPicker = true">
              <label>嵌入模型</label>
              <div class="config-value">
                <span>{{ uploadForm.embeddingModelLabel }}</span>
                <van-icon name="arrow-down" size="12" />
              </div>
            </div>
            <div class="config-field full">
              <label>知识类型</label>
              <input v-model="uploadForm.contentType" type="text" placeholder="如 nutrition" class="config-input" />
            </div>
            <div class="config-field full">
              <label>分类</label>
              <input v-model="uploadForm.category" type="text" placeholder="如 general" class="config-input" />
            </div>
          </div>
        </div>

        <div class="section-block">
          <h4 class="block-title">上传文档</h4>
          <div class="upload-info-row">
            <span class="info-tag">支持 PDF / Word / TXT / Markdown</span>
            <span class="info-tag info-tag-limit">最大 30MB</span>
          </div>

          <div v-if="!showProgressPanel" class="upload-area-admin">
            <van-uploader
              v-model="fileList"
              :max-count="1"
              accept=".pdf,.doc,.docx,.txt,.md"
              :before-read="beforeRead"
              :after-read="afterRead"
              :disabled="uploading"
            >
              <div class="upload-trigger-admin">
                <van-icon name="upgrade" size="32" color="#94a3b8" />
                <span>点击或拖拽上传文件</span>
              </div>
            </van-uploader>
          </div>

          <button
            v-if="!showProgressPanel"
            class="upload-submit-btn"
            :disabled="fileList.length === 0 || uploading"
            @click="uploadDocument"
          >
            <van-icon name="guide-o" size="18" />
            <span>上传并解析到向量数据库</span>
          </button>

          <div v-if="showProgressPanel && progressData" class="progress-panel">
            <div class="progress-header-row">
              <div class="progress-file-info">
                <van-icon name="description" size="20" color="#10b981" />
                <div class="pf-detail">
                  <strong>{{ progressData.filename }}</strong>
                  <span>{{ formatFileSize(progressData.fileSize) }}</span>
                </div>
              </div>
              <span
                v-if="progressData.status === 'completed' || progressData.status === 'failed'"
                class="close-progress-btn"
                @click="closeProgressPanel"
              >✕</span>
            </div>

            <div class="progress-stages">
              <div
                v-for="(stage, idx) in stages"
                :key="stage.key"
                class="stage-item"
                :class="{
                  active: currentStageIndex === idx,
                  done: currentStageIndex > idx,
                  error: progressData.status === 'failed'
                }"
              >
                <div class="stage-dot">
                  <van-icon
                    v-if="currentStageIndex > idx"
                    name="success"
                    size="12"
                  />
                </div>
                <span>{{ stage.label }}</span>
              </div>
            </div>

            <div class="main-progress-section">
              <div class="progress-bar-track">
                <div
                  class="progress-bar-fill"
                  :style="{ width: (progressData.progress || 0) + '%' }"
                ></div>
                <div class="progress-glow" :style="{ left: (progressData.progress || 0) + '%' }"></div>
              </div>
              <div class="progress-stats">
                <span class="progress-pct">{{ Math.round(progressData.progress || 0) }}%</span>
                <span class="progress-chunks" v-if="progressData.total_chunks">
                  {{ progressData.stored_count || 0 }} / {{ progressData.total_chunks }} 块
                </span>
                <span class="progress-elapsed">{{ elapsedText }}</span>
              </div>
            </div>

            <div v-if="progressData.message" class="progress-message">
              {{ progressData.message }}
            </div>

            <div v-if="progressData.status === 'completed'" class="progress-result-success">
              <div class="success-header">
                <van-icon name="checked" size="28" color="#10b981" />
                <div class="success-text">
                  <strong>文档解析完成</strong>
                  <span>共处理 {{ progressData.total_chunks }} 个文本块，成功存储 {{ progressData.stored_count }} 条知识</span>
                </div>
              </div>

              <div class="result-stats-row" v-if="progressData.full_text_length || progressData.chunk_method">
                <div class="rs-item" v-if="progressData.full_text_length">
                  <span class="rs-label">原文总长度</span>
                  <span class="rs-value">{{ formatTextLength(progressData.full_text_length) }}</span>
                </div>
                <div class="rs-item" v-if="progressData.chunk_method">
                  <span class="rs-label">分块方式</span>
                  <span class="rs-value">{{ getChunkMethodLabel(progressData.chunk_method) }}</span>
                </div>
                <div class="rs-item">
                  <span class="rs-label">嵌入模型</span>
                  <span class="rs-value">{{ uploadForm.embeddingModelLabel }}</span>
                </div>
              </div>

              <div class="chunks-preview-section" v-if="progressData.chunk_preview && progressData.chunk_preview.length > 0">
                <div class="cp-header">
                  <h5>📄 文本块预览 (前{{ Math.min(progressData.chunk_preview.length, 15) }}个)</h5>
                  <span class="cp-toggle" @click="showAllChunks = !showAllChunks">
                    {{ showAllChunks ? '收起' : '展开全部' }}
                    <van-icon :name="showAllChunks ? 'arrow-up' : 'arrow-down'" size="12" />
                  </span>
                </div>

                <div class="chunks-list" :class="{ expanded: showAllChunks }">
                  <div
                    v-for="(chunk, idx) in (showAllChunks ? progressData.chunk_preview : progressData.chunk_preview.slice(0, 3))"
                    :key="idx"
                    class="chunk-card"
                  >
                    <div class="chunk-card-header">
                      <span class="chunk-index">#{{ chunk.index + 1 }}</span>
                      <span class="chunk-length">{{ chunk.length }} 字符</span>
                    </div>
                    <p class="chunk-content">{{ chunk.content }}</p>
                  </div>
                </div>

                <div class="cp-more-hint" v-if="!showAllChunks && progressData.chunk_preview.length > 3">
                  还有 {{ progressData.chunk_preview.length - 3 }} 个文本块未显示，点击上方「展开全部」查看
                </div>
              </div>
            </div>

            <div v-else-if="progressData.status === 'failed'" class="progress-result-error">
              <van-icon name="cross" size="28" color="#ef4444" />
              <p>解析失败：{{ progressData.error || '未知错误' }}</p>
              <button class="retry-btn" @click="retryUpload">重新上传</button>
            </div>

            <div v-else class="progress-tips">
              <van-loading size="16" color="#10b981" />
              <span>正在{{ stageLabel }}，请耐心等待...</span>
            </div>
          </div>
        </div>

        <div class="knowledge-stats-single">
          <div class="kss-icon">
            <van-icon name="bookmark-o" size="22" />
          </div>
          <div class="kss-info">
            <span class="kss-num">{{ knowledgeStats.nutrition || 0 }}</span>
            <span class="kss-label">知识库条目</span>
          </div>
        </div>
      </div>

      <div v-else-if="activeTab === 'settings'" class="settings-content">
        <div class="section-block">
          <h4 class="block-title">大模型参数</h4>
          <div class="setting-row">
            <label>模型名称</label>
            <input v-model="llmSettings.model_name" readonly class="setting-input setting-input-readonly" />
          </div>
          <div class="setting-row">
            <label>Temperature</label>
            <input v-model="llmSettings.temperature" type="number" step="0.1" min="0" max="2" class="setting-input" />
          </div>
          <div class="setting-row">
            <label>最大Token数</label>
            <input v-model="llmSettings.max_tokens" type="number" class="setting-input" />
          </div>
          <button class="save-btn" @click="updateLLMSettings">保存设置</button>
        </div>

        <div class="section-block">
          <h4 class="block-title">Embedding 设置</h4>
          <div class="setting-row">
            <label>嵌入模型</label>
            <input v-model="embeddingSettings.embedding_model" readonly class="setting-input setting-input-readonly" />
          </div>
          <div class="setting-row clickable" @click="showChunkPicker = true">
            <label>分块方式</label>
            <div class="setting-right">
              <span>{{ embeddingSettings.current_chunk_method }}</span>
              <van-icon name="arrow" size="14" color="#c4cbd5" />
            </div>
          </div>
          <button class="save-btn save-btn-secondary" @click="updateEmbeddingSettings">保存设置</button>
        </div>

        <div class="section-block">
          <h4 class="block-title">系统日志</h4>
          <div class="log-filters">
            <span
              v-for="lt in ['all', 'INFO', 'WARNING', 'ERROR']"
              :key="lt"
              class="log-filter"
              :class="{ active: logTab === lt }"
              @click="logTab = lt; loadLogs()"
            >{{ lt }}</span>
          </div>
          <van-pull-refresh v-model="logRefreshing" @refresh="loadLogs">
            <van-list
              v-model:loading="logLoading"
              :finished="logFinished"
              finished-text=""
              @load="loadLogs"
            >
              <div
                v-for="log in logs"
                :key="log.id"
                class="log-item"
                :class="'log-' + log.level.toLowerCase()"
              >
                <span class="log-level-badge">{{ log.level }}</span>
                <span class="log-msg">{{ log.message }}</span>
                <span class="log-time">{{ log.timestamp }}</span>
              </div>
            </van-list>
          </van-pull-refresh>
        </div>
      </div>
    </div>

    <van-action-sheet
      v-model:show="showUserActions"
      :actions="userActions"
      @select="onUserAction"
    />

    <van-popup v-model:show="showChunkPicker" position="bottom" round>
      <div class="picker-header-custom">
        <span @click="showChunkPicker = false">取消</span>
        <strong>选择分块方式</strong>
        <span></span>
      </div>
      <div class="picker-options-list">
        <div
          v-for="col in chunkColumns"
          :key="col.value"
          class="picker-opt"
          :class="{ active: uploadForm.chunkMethod === col.value }"
          @click="onChunkConfirm(col)"
        >
          {{ col.text }}
          <van-icon v-if="uploadForm.chunkMethod === col.value" name="success" size="16" color="#10b981" />
        </div>
      </div>
    </van-popup>

    <van-popup v-model:show="showEmbeddingPicker" position="bottom" round>
      <div class="picker-header-custom">
        <span @click="showEmbeddingPicker = false">取消</span>
        <strong>选择嵌入模型</strong>
        <span></span>
      </div>
      <div class="picker-options-list">
        <div
          v-for="col in embeddingColumns"
          :key="col.value"
          class="picker-opt"
          :class="{ active: uploadForm.embeddingModel === col.value }"
          @click="onEmbeddingConfirm(col)"
        >
          {{ col.text }}
          <van-icon v-if="uploadForm.embeddingModel === col.value" name="success" size="16" color="#10b981" />
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { showToast, showConfirmDialog } from 'vant'
import { adminAPI } from '@/api'

const activeTab = ref('users')
const userTab = ref('list')
const logTab = ref('all')

const mainTabs = [
  { label: '用户管理', value: 'users', icon: 'manager-o' },
  { label: '知识库', value: 'knowledge', icon: 'bookmark-o' },
  { label: '系统设置', value: 'settings', icon: 'setting-o' }
]

const userSubTabs = [
  { label: '用户列表', value: 'list' },
  { label: '活跃度', value: 'activity' },
  { label: '用户反馈', value: 'feedback' }
]

const users = ref([])
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)
const page = ref(1)

const feedbacks = ref([])
const feedbackLoading = ref(false)
const feedbackFinished = ref(false)
const feedbackRefreshing = ref(false)

const activityStats = ref({ daily_active_users: 128, weekly_active_users: 456, monthly_active_users: 1234, retention_rate: 68.5 })
const behaviorData = ref({ feature_usage: [] })

const logs = ref([])
const logLoading = ref(false)
const logFinished = ref(false)
const logRefreshing = ref(false)

const showUserActions = ref(false)
const selectedUser = ref(null)
const userActions = [
  { name: '查看详情', action: 'detail' },
  { name: '设为管理员', action: 'makeAdmin' },
  { name: '取消管理员', action: 'removeAdmin' },
  { name: '删除用户', action: 'delete' }
]

const showChunkPicker = ref(false)
const showEmbeddingPicker = ref(false)

const chunkColumns = [
  { text: '固定大小分块', value: 'fixed' },
  { text: '句子分块', value: 'sentence' },
  { text: '段落分块', value: 'paragraph' },
  { text: '递归分块', value: 'recursive' }
]

const embeddingColumns = [
  { text: 'DashScope Text Embedding V4', value: 'text-embedding-v4' },
  { text: 'OpenAI Embedding 3 Large', value: 'text-embedding-3-large' }
]

const fileList = ref([])
const uploading = ref(false)
const parseResult = ref(null)
const showProgressPanel = ref(false)
const progressData = ref(null)
const currentStageIndex = ref(0)
const showAllChunks = ref(false)
let pollTimer = null
let startTime = null

const TASK_STORAGE_KEY = 'upload_task_progress'

const stages = [
  { key: 'upload', label: '上传文件' },
  { key: 'parse', label: '解析文本' },
  { key: 'embed', label: '生成向量' },
  { key: 'store', label: '存储知识' }
]

const stageLabel = computed(() => {
  if (currentStageIndex.value < stages.length) return stages[currentStageIndex.value].label
  return '处理中'
})

const elapsedText = computed(() => {
  if (!startTime) return ''
  const sec = Math.floor((Date.now() - startTime) / 1000)
  const m = Math.floor(sec / 60)
  const s = sec % 60
  return `${m}分${s.toString().padStart(2, '0')}秒`
})

const hasActiveTask = computed(() => {
  const saved = getTaskFromStorage()
  return saved && saved.status === 'processing'
})

const uploadForm = ref({
  contentType: 'nutrition',
  category: 'general',
  chunkMethod: 'fixed',
  chunkMethodLabel: '固定大小分块',
  embeddingModel: 'text-embedding-v4',
  embeddingModelLabel: 'DashScope Text Embedding V4'
})

const knowledgeStats = ref({ nutrition: 0, recipe: 0, ingredient: 0, seasonal: 0 })
const llmSettings = ref({ model_name: 'doubao-seed-2-0-lite-260215', temperature: 0.7, max_tokens: 500 })
const embeddingSettings = ref({ embedding_model: 'text-embedding-v4', current_chunk_method: '固定大小分块' })

function switchMainTab(val) {
  activeTab.value = val
  if (val === 'users') {
    if (userTab.value === 'activity') { loadActivityStats(); loadBehaviorData() }
    else if (userTab.value === 'feedback') loadFeedbacks()
  } else if (val === 'knowledge') {
    loadKnowledgeStats()
    restoreActiveTask()
  } else if (val === 'settings') { loadSettings(); loadLogs() }
}

function switchUserSubTab(val) {
  userTab.value = val
  if (val === 'list') loadUsers()
  else if (val === 'activity') { loadActivityStats(); loadBehaviorData() }
  else if (val === 'feedback') loadFeedbacks()
}

async function loadUsers() {
  try {
    const res = await adminAPI.getUsers(page.value, 20)
    if (page.value === 1) users.value = res.users
    else users.value = [...users.value, ...res.users]
    page.value++
    if (res.users.length < 20) finished.value = true
  } catch (error) { showToast('加载失败') }
  finally { loading.value = false; refreshing.value = false }
}

async function loadFeedbacks() {
  try {
    const res = await adminAPI.getFeedbacks(1, 20)
    feedbacks.value = res.feedbacks
    feedbackFinished.value = true
  } catch (error) { showToast('加载失败') }
  finally { feedbackLoading.value = false; feedbackRefreshing.value = false }
}

async function loadActivityStats() {
  try { activityStats.value = await adminAPI.getActivityStats() } catch (e) {}
}

async function loadBehaviorData() {
  try { behaviorData.value = await adminAPI.getBehaviorAnalysis() } catch (e) {}
}

async function loadKnowledgeStats() {
  try { knowledgeStats.value = await adminAPI.getKnowledgeStats() } catch (e) {}
}

async function loadLogs() {
  try {
    const res = await adminAPI.getLogs(1, 50, logTab.value === 'all' ? null : logTab.value)
    logs.value = res.logs
    logFinished.value = true
  } catch (error) { showToast('加载失败') }
  finally { logLoading.value = false; logRefreshing.value = false }
}

async function loadSettings() {
  try {
    llmSettings.value = await adminAPI.getLLMSettings()
    embeddingSettings.value = await adminAPI.getEmbeddingSettings()
  } catch (e) {}
}

function showUserDetail(user) {
  selectedUser.value = user
  showUserActions.value = true
}

function onUserAction(action) {
  if (action.action === 'makeAdmin') updateUserRole(selectedUser.value.id, true)
  else if (action.action === 'removeAdmin') updateUserRole(selectedUser.value.id, false)
  else if (action.action === 'delete') confirmDeleteUser(selectedUser.value.id)
  else showToast(`用户ID: ${selectedUser.value.id}`)
}

async function updateUserRole(userId, isAdmin) {
  try {
    await adminAPI.updateUserRole(userId, isAdmin)
    showToast(isAdmin ? '已设为管理员' : '已取消管理员')
    loadUsers()
  } catch (e) { showToast('操作失败') }
}

async function confirmDeleteUser(userId) {
  try {
    await showConfirmDialog({ title: '确认删除', message: '确定要删除该用户吗？此操作不可恢复。' })
    await adminAPI.deleteUser(userId)
    showToast('删除成功')
    loadUsers()
  } catch (e) { if (e !== 'cancel') showToast('删除失败') }
}

async function uploadDocument() {
  if (fileList.value.length === 0) return
  if (!uploadForm.value.contentType) { showToast('请输入知识类型'); return }

  const file = fileList.value[0]
  uploading.value = true
  showProgressPanel.value = true
  startTime = Date.now()
  currentStageIndex.value = 0

  progressData.value = {
    filename: file.name,
    fileSize: file.size,
    total_chunks: 0,
    stored_count: 0,
    progress: 2,
    status: 'processing',
    message: '正在上传文件到服务器...'
  }

  try {
    const formData = new FormData()
    formData.append('file', file.file)
    formData.append('chunk_method', uploadForm.value.chunkMethod)
    formData.append('embedding_model', uploadForm.value.embeddingModel)
    formData.append('content_type', uploadForm.value.contentType)
    formData.append('category', uploadForm.value.category || 'general')

    currentStageIndex.value = 1
    progressData.value.message = '正在上传文件...'
    progressData.value.progress = 5

    const res = await adminAPI.uploadDocument(formData)

    if (res.success && res.task_id) {
      saveTaskToStorage(res.task_id, file.name, file.size)

      progressData.value.total_chunks = res.total_chunks || 0
      progressData.value.stored_count = 0
      progressData.value.progress = 10
      progressData.value.message = '文件已接收，开始解析文本...'

      startPolling(res.task_id, file.name, file.size)
    } else {
      finishProgress('failed', res.error || '上传失败')
    }
  } catch (error) {
    if (error.code === 'ECONNABORTED') {
      finishProgress('failed', '请求超时，请检查网络连接后重试')
    } else {
      finishProgress('failed', error.response?.data?.detail || error.message || '上传失败')
    }
  }
}

function startPolling(taskId, filename, fileSize) {
  currentStageIndex.value = 1

  pollTimer = setInterval(async () => {
    try {
      const statusRes = await adminAPI.getDocumentTaskStatus(taskId)

      if (statusRes.success) {
        const p = statusRes.progress || 0
        progressData.value = {
          filename: statusRes.filename || filename,
          fileSize: fileSize,
          total_chunks: statusRes.total_chunks || 0,
          stored_count: statusRes.stored_count || 0,
          progress: p,
          status: statusRes.status || 'processing',
          message: statusRes.message || '',
          error: statusRes.error || ''
        }

        if (p > 10 && p < 40) currentStageIndex.value = 1
        else if (p >= 40 && p < 75) currentStageIndex.value = 2
        else if (p >= 75) currentStageIndex.value = 3

        if (statusRes.status === 'completed' || statusRes.status === 'failed') {
          clearInterval(pollTimer)
          pollTimer = null
          uploading.value = false
          progressData.value.status = statusRes.status
          if (statusRes.status === 'completed') {
            currentStageIndex.value = 4
            progressData.value.progress = 100
            loadKnowledgeStats()
          }
          clearTaskStorage()
        }
      }
    } catch (e) {
      console.log('轮询状态失败，继续等待...')
    }
  }, 2000)
}

function finishProgress(status, message) {
  if (pollTimer) { clearInterval(pollTimer); pollTimer = null }
  uploading.value = false
  if (progressData.value) {
    progressData.value.status = status
    progressData.value.error = message
    progressData.value.message = message
  }

  const saved = getTaskFromStorage()
  if (saved) {
    saved.status = status
    localStorage.setItem(TASK_STORAGE_KEY, JSON.stringify(saved))
    if (status === 'completed' || status === 'failed') {
      setTimeout(() => clearTaskStorage(), 3000)
    }
  }
}

function closeProgressPanel() {
  if (progressData.value && progressData.value.status === 'processing') {
    showProgressPanel.value = false
  } else {
    showProgressPanel.value = false
    progressData.value = null
    fileList.value = []
    clearTaskStorage()
  }
}

function retryUpload() {
  closeProgressPanel()
}

function formatFileSize(bytes) {
  if (!bytes) return ''
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function formatTextLength(len) {
  if (!len) return ''
  if (len < 1000) return len + ' 字符'
  return (len / 1000).toFixed(1) + 'K 字符'
}

function getChunkMethodLabel(method) {
  const map = { fixed: '固定大小分块', sentence: '句子分块', paragraph: '段落分块', recursive: '递归分块' }
  return map[method] || method
}

function saveTaskToStorage(taskId, filename, fileSize) {
  const taskInfo = {
    taskId,
    filename,
    fileSize,
    startTime: Date.now(),
    status: 'processing'
  }
  localStorage.setItem(TASK_STORAGE_KEY, JSON.stringify(taskInfo))
}

function getTaskFromStorage() {
  try {
    const raw = localStorage.getItem(TASK_STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch (e) {
    return null
  }
}

function clearTaskStorage() {
  localStorage.removeItem(TASK_STORAGE_KEY)
}

async function restoreActiveTask() {
  if (pollTimer) return
  const saved = getTaskFromStorage()
  if (!saved || saved.status === 'completed' || saved.status === 'failed') {
    if (saved && (saved.status === 'completed' || saved.status === 'failed')) clearTaskStorage()
    return
  }

  uploading.value = true
  showProgressPanel.value = true
  startTime = saved.startTime

  progressData.value = {
    filename: saved.filename,
    fileSize: saved.fileSize,
    total_chunks: 0,
    stored_count: 0,
    progress: 0,
    status: 'processing',
    message: '恢复任务进度中...'
  }

  try {
    const statusRes = await adminAPI.getDocumentTaskStatus(saved.taskId)
    if (statusRes.success) {
      const p = statusRes.progress || 0
      progressData.value = {
        filename: statusRes.filename || saved.filename,
        fileSize: saved.fileSize,
        total_chunks: statusRes.total_chunks || 0,
        stored_count: statusRes.stored_count || 0,
        progress: p,
        status: statusRes.status || 'processing',
        message: statusRes.message || '',
        error: statusRes.error || ''
      }

      if (p > 10 && p < 40) currentStageIndex.value = 1
      else if (p >= 40 && p < 75) currentStageIndex.value = 2
      else if (p >= 75) currentStageIndex.value = 3

      if (statusRes.status === 'completed' || statusRes.status === 'failed') {
        uploading.value = false
        progressData.value.status = statusRes.status
        if (statusRes.status === 'completed') {
          currentStageIndex.value = 4
          progressData.value.progress = 100
          loadKnowledgeStats()
        }
        clearTaskStorage()
      } else {
        startPolling(saved.taskId, saved.filename, saved.fileSize)
      }
    } else {
      finishProgress('failed', '任务不存在或已过期')
      clearTaskStorage()
    }
  } catch (e) {
    finishProgress('failed', '无法连接服务器，请检查后端是否运行')
  }
}

function beforeRead(file) {
  if (file.size > 30 * 1024 * 1024) { showToast('文件大小不能超过 30MB'); return false }
  return true
}

function afterRead(file) { parseResult.value = null }

function onChunkConfirm(col) {
  uploadForm.value.chunkMethod = col.value
  uploadForm.value.chunkMethodLabel = col.text
  showChunkPicker.value = false
}

function onEmbeddingConfirm(col) {
  uploadForm.value.embeddingModel = col.value
  uploadForm.value.embeddingModelLabel = col.text
  showEmbeddingPicker.value = false
}

async function updateLLMSettings() {
  try {
    await adminAPI.updateLLMSettings({ temperature: llmSettings.value.temperature, max_tokens: llmSettings.value.max_tokens })
    showToast('设置已保存')
  } catch (e) { showToast('保存失败') }
}

async function updateEmbeddingSettings() {
  try {
    await adminAPI.updateEmbeddingSettings({ chunk_method: uploadForm.value.chunkMethod })
    showToast('设置已保存')
  } catch (e) { showToast('保存失败') }
}

function getFeedbackType(status) {
  const map = { '待处理': 'warning', '处理中': 'primary', '已处理': 'success' }
  return map[status] || 'default'
}

onMounted(() => {
  loadUsers()
  const saved = getTaskFromStorage()
  if (saved && saved.status === 'processing') {
    activeTab.value = 'knowledge'
    restoreActiveTask()
  }
})

onUnmounted(() => {
  if (pollTimer) { clearInterval(pollTimer); pollTimer = null }
})
</script>

<style scoped>
.admin-container {
  min-height: 100vh;
  background-color: #f0fdf4;
  padding-bottom: 20px;
}

.admin-tabs {
  display: flex;
  gap: 8px;
  padding: 14px 16px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}

.admin-tabs::-webkit-scrollbar { display: none; }

.admin-tab-item {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  border-radius: 22px;
  background: white;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--transition);
  box-shadow: var(--shadow-sm);
}

.admin-tab-item.active {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  box-shadow: 0 3px 10px rgba(16, 185, 129, 0.3);
}

.task-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #f59e0b;
  animation: task-pulse 1.5s ease-in-out infinite;
  flex-shrink: 0;
}

@keyframes task-pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.7); }
}

.tab-content {
  padding: 0 16px;
}

.sub-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.sub-tab {
  padding: 7px 16px;
  border-radius: 16px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  background: white;
  cursor: pointer;
  transition: var(--transition);
  box-shadow: var(--shadow-sm);
}

.sub-tab.active {
  background: var(--primary);
  color: white;
}

.user-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: white;
  border-radius: var(--radius-md);
  padding: 14px 16px;
  margin-bottom: 10px;
  box-shadow: var(--shadow-sm);
  transition: var(--transition);
  cursor: pointer;
}

.user-card:active { transform: scale(0.98); }

.user-avatar {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 16px;
  flex-shrink: 0;
}

.user-info { flex: 1; }

.user-info h4 { margin: 0 0 2px; font-size: 15px; font-weight: 600; color: var(--text-primary); }
.user-info p { margin: 0; font-size: 12px; color: var(--text-muted); }

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  border-radius: var(--radius-md);
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: var(--shadow-sm);
}

.stat-icon-wrap {
  width: 42px;
  height: 42px;
  border-radius: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.stat-card-blue .stat-icon-wrap { background: linear-gradient(135deg, #3b82f6, #2563eb); }
.stat-card-green .stat-icon-wrap { background: linear-gradient(135deg, #10b981, #059669); }
.stat-card-orange .stat-icon-wrap { background: linear-gradient(135deg, #f59e0b, #d97706); }
.stat-card-purple .stat-icon-wrap { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }

.stat-data { display: flex; flex-direction: column; }

.stat-num { font-size: 20px; font-weight: 700; color: var(--text-primary); }
.stat-label { font-size: 11px; color: var(--text-muted); margin-top: 2px; }

.behavior-section { background: white; border-radius: var(--radius-md); padding: 16px; box-shadow: var(--shadow-sm); }

.behavior-section h4 { margin: 0 0 14px; font-size: 15px; font-weight: 600; }

.behavior-item { margin-bottom: 14px; }

.behavior-item:last-child { margin-bottom: 0; }

.behavior-header {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  margin-bottom: 6px;
}

.behavior-header span { color: var(--text-secondary); }
.behavior-header strong { color: var(--text-primary); font-weight: 600; }

.progress-track {
  height: 8px;
  background: #f1f5f9;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981, #059669);
  border-radius: 4px;
  transition: width 0.5s ease;
}

.feedback-card {
  background: white;
  border-radius: var(--radius-md);
  padding: 14px 16px;
  margin-bottom: 10px;
  box-shadow: var(--shadow-sm);
}

.feedback-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }

.feedback-user { font-size: 14px; font-weight: 600; color: var(--text-primary); }

.feedback-text { margin: 0 0 6px; font-size: 13px; line-height: 1.6; color: var(--text-secondary); }

.feedback-time { font-size: 11px; color: var(--text-muted); }

.section-block {
  background: white;
  border-radius: var(--radius-lg);
  padding: 18px;
  margin-bottom: 16px;
  box-shadow: var(--shadow-sm);
}

.block-title {
  margin: 0 0 14px;
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.config-field {
  background: #f8fafc;
  border-radius: var(--radius-sm);
  padding: 12px 14px;
  border: 1.5px solid #e2e8f0;
  transition: var(--transition);
}

.config-field.full { grid-column: span 2; }

.config-field:focus-within { border-color: #10b981; background: white; }

.config-field label { display: block; font-size: 11px; font-weight: 600; color: var(--text-muted); margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px; }

.config-value { display: flex; justify-content: space-between; align-items: center; cursor: pointer; }

.config-value span { font-size: 14px; color: var(--text-primary); }

.config-input {
  width: 100%;
  border: none;
  outline: none;
  font-size: 14px;
  color: var(--text-primary);
  background: transparent;
  padding: 4px 0;
}

.upload-info-row { display: flex; gap: 8px; margin-bottom: 12px; }

.info-tag {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  background: #ecfdf5;
  color: #059669;
}

.info-tag-limit { background: #fef3c7; color: #92400e; }

.upload-area-admin { margin-bottom: 14px; }

.upload-trigger-admin {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 36px 20px;
  border: 2px dashed #d1d5db;
  border-radius: var(--radius-md);
  background: #fafafa;
  cursor: pointer;
  gap: 8px;
  transition: var(--transition);
}

.upload-trigger-admin:active { border-color: #10b981; background: #f0fdf4; }

.upload-trigger-admin span { font-size: 13px; color: var(--text-muted); }

.upload-submit-btn {
  width: 100%;
  padding: 14px;
  border: none;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: var(--transition);
  box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35);
}

.upload-submit-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.progress-panel {
  margin-top: 16px;
  background: linear-gradient(135deg, #ecfdf5, #f0fdf4);
  border-radius: var(--radius-lg);
  padding: 20px;
  border: 1px solid #bbf7d0;
}

.progress-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.progress-file-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.pf-detail { display: flex; flex-direction: column; }

.pf-detail strong {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.pf-detail span {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 1px;
}

.close-progress-btn {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-muted);
  box-shadow: var(--shadow-sm);
  transition: var(--transition);
  flex-shrink: 0;
}

.close-progress-btn:active { background: #fee2e2; color: #ef4444; }

.progress-stages {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 22px;
  position: relative;
}

.progress-stages::before {
  content: '';
  position: absolute;
  top: 11px;
  left: 24px;
  right: 24px;
  height: 2px;
  background: #d1d5db;
  z-index: 0;
}

.stage-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  z-index: 1;
  position: relative;
}

.stage-dot {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #e5e7eb;
  border: 3px solid white;
  box-shadow: 0 0 0 1px #d1d5db;
  transition: all 0.4s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 10px;
}

.stage-item.active .stage-dot {
  background: linear-gradient(135deg, #10b981, #059669);
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.25), 0 0 12px rgba(16, 185, 129, 0.35);
  animation: pulse-dot 1.8s ease-in-out infinite;
}

.stage-item.done .stage-dot {
  background: linear-gradient(135deg, #10b981, #059669);
  box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
}

.stage-item.error .stage-dot {
  background: #ef4444;
  box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.2);
}

@keyframes pulse-dot {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.15); }
}

.stage-item span {
  font-size: 10px;
  font-weight: 500;
  color: var(--text-muted);
  white-space: nowrap;
}

.stage-item.active span,
.stage-item.done span { color: #059669; font-weight: 600; }

.main-progress-section { margin-bottom: 14px; }

.progress-bar-track {
  width: 100%;
  height: 14px;
  background: #dbeafe;
  border-radius: 7px;
  overflow: visible;
  position: relative;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981, #34d399, #10b981);
  background-size: 200% 100%;
  border-radius: 7px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  animation: shimmer 2s infinite linear;
  min-width: 2px;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.progress-glow {
  position: absolute;
  top: -6px;
  width: 12px;
  height: 26px;
  transform: translateX(-50%);
  border-radius: 6px;
  background: radial-gradient(ellipse at center, rgba(16, 185, 129, 0.5), transparent 70%);
  pointer-events: none;
  transition: left 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.progress-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.progress-pct {
  font-size: 24px;
  font-weight: 800;
  color: #059669;
  letter-spacing: -0.5px;
}

.progress-chunks {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  background: white;
  padding: 3px 10px;
  border-radius: 10px;
}

.progress-elapsed {
  font-size: 12px;
  color: var(--text-muted);
}

.progress-message {
  text-align: center;
  font-size: 13px;
  color: #047857;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 8px;
  margin-bottom: 10px;
}

.progress-result-success,
.progress-result-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px;
  text-align: center;
}

.success-header {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  text-align: left;
  margin-bottom: 4px;
}

.success-text {
  display: flex;
  flex-direction: column;
}

.success-text strong {
  font-size: 16px;
  font-weight: 700;
  color: #065f46;
}

.success-text span {
  font-size: 13px;
  color: #047857;
  margin-top: 2px;
}

.result-stats-row {
  display: flex;
  justify-content: center;
  gap: 12px;
  width: 100%;
  margin: 14px 0;
  padding: 10px 0;
  border-top: 1px solid #bbf7d0;
  border-bottom: 1px solid #bbf7d0;
}

.rs-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.rs-label {
  font-size: 11px;
  color: #059669;
  font-weight: 500;
}

.rs-value {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.chunks-preview-section {
  width: 100%;
  text-align: left;
}

.cp-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.cp-header h5 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #065f46;
}

.cp-toggle {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 12px;
  font-weight: 500;
  color: #10b981;
  cursor: pointer;
  padding: 4px 10px;
  border-radius: 12px;
  background: white;
  transition: var(--transition);
}

.cp-toggle:active { transform: scale(0.96); }

.chunks-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 280px;
  overflow: hidden;
  transition: max-height 0.4s ease;
}

.chunks-list.expanded { max-height: none; }

.chunk-card {
  background: white;
  border-radius: var(--radius-sm);
  padding: 12px 14px;
  border-left: 3px solid #10b981;
  box-shadow: var(--shadow-sm);
}

.chunk-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.chunk-index {
  font-size: 12px;
  font-weight: 700;
  color: #059669;
  background: #ecfdf5;
  padding: 2px 8px;
  border-radius: 6px;
}

.chunk-length {
  font-size: 11px;
  color: var(--text-muted);
}

.chunk-content {
  margin: 0;
  font-size: 13px;
  line-height: 1.7;
  color: #374151;
  white-space: pre-wrap;
  word-break: break-word;
}

.cp-more-hint {
  text-align: center;
  font-size: 12px;
  color: #92400e;
  background: #fef3c7;
  padding: 8px;
  border-radius: var(--radius-sm);
  margin-top: 8px;
}

.progress-result-error p {
  margin: 0;
  font-size: 13px;
  color: #991b1b;
}

.retry-btn {
  margin-top: 8px;
  padding: 8px 24px;
  border: none;
  border-radius: 20px;
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition);
}

.retry-btn:active { transform: scale(0.96); }

.progress-tips {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px;
  font-size: 13px;
  color: #047857;
}

.result-panel { margin-top: 16px; }

.panel-title { margin: 0 0 12px; font-size: 15px; font-weight: 700; color: var(--text-primary); }

.result-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }

.result-cell { display: flex; flex-direction: column; gap: 4px; }

.result-cell.full { grid-column: span 2; }

.cell-label { font-size: 11px; color: var(--text-muted); font-weight: 500; }

.cell-value { font-size: 14px; font-weight: 600; color: var(--text-primary); }

.cell-value.highlight { color: #10b981; }

.mini-progress {
  height: 6px;
  background: #f1f5f9;
  border-radius: 3px;
  overflow: hidden;
}

.mini-progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #10b981, #059669);
  border-radius: 3px;
  transition: width 0.3s;
}

.knowledge-stats-single {
  background: linear-gradient(135deg, #ecfdf5, #d1fae5);
  border-radius: var(--radius-lg);
  padding: 18px 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  margin-top: 16px;
  border: 1px solid #bbf7d0;
}

.kss-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: linear-gradient(135deg, #10b981, #059669);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
}

.kss-info { display: flex; flex-direction: column; }

.kss-num {
  font-size: 26px;
  font-weight: 800;
  color: #065f46;
  line-height: 1.2;
}

.kss-label {
  font-size: 13px;
  color: #047857;
  margin-top: 2px;
}

.setting-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.setting-row label {
  width: 80px;
  flex-shrink: 0;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
}

.setting-input {
  flex: 1;
  padding: 10px 14px;
  border: 1.5px solid #e2e8f0;
  border-radius: var(--radius-sm);
  font-size: 14px;
  color: var(--text-primary);
  outline: none;
  transition: var(--transition);
  background: #f8fafc;
}

.setting-input:focus { border-color: #10b981; background: white; box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.08); }

.setting-input-readonly { background: #f1f5f9; color: var(--text-muted); }

.setting-right { display: flex; align-items: center; gap: 6px; flex: 1; font-size: 14px; color: var(--text-primary); }

.setting-row.clickable { cursor: pointer; }

.save-btn {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 4px;
  transition: var(--transition);
}

.save-btn-secondary { background: linear-gradient(135deg, #6366f1, #8b5cf6); }

.log-filters { display: flex; gap: 8px; margin-bottom: 14px; }

.log-filter {
  padding: 6px 14px;
  border-radius: 14px;
  font-size: 12px;
  font-weight: 500;
  background: #f1f5f9;
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--transition);
}

.log-filter.active { background: #10b981; color: white; }

.log-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: #f8fafc;
  border-radius: var(--radius-sm);
  margin-bottom: 8px;
  font-size: 13px;
}

.log-level-badge {
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  flex-shrink: 0;
}

.log-info .log-level-badge { background: #dbeafe; color: #2563eb; }
.log-warning .log-level-badge { background: #fef3c7; color: #d97706; }
.log-error .log-level-badge { background: #fee2e2; color: #dc2626; }

.log-msg { flex: 1; color: var(--text-secondary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.log-time { font-size: 11px; color: var(--text-muted); flex-shrink: 0; }

.picker-header-custom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  font-size: 15px;
  border-bottom: 1px solid #f1f5f9;
}

.picker-header-custom span:first-child { color: var(--text-secondary); cursor: pointer; }

.picker-header-custom strong { font-weight: 600; }

.picker-options-list { padding: 8px 0; }

.picker-opt {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 24px;
  font-size: 15px;
  color: var(--text-primary);
  cursor: pointer;
  transition: var(--transition);
}

.picker-opt:active { background: #f8fafc; }

.picker-opt.active { color: #10b981; font-weight: 600; }
</style>
