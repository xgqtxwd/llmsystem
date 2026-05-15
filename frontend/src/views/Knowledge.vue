<template>
  <div class="knowledge-container">
    <van-nav-bar title="营养知识" left-arrow @click-left="$router.back()" />

    <div class="search-wrapper">
      <van-search
        v-model="searchQuery"
        placeholder="搜索知识库..."
        shape="round"
        @search="onSearch"
        @clear="searchQuery = ''; resetAndLoad()"
      />
    </div>

    <div class="content">
      <div class="tab-bar">
        <div class="tab-scroll">
          <span
            v-for="kt in knowledgeTypes"
            :key="kt.value"
            class="tab-item"
            :class="{ active: activeType === kt.value }"
            @click="activeType = kt.value; resetAndLoad()"
          >
            {{ kt.label }}
          </span>
        </div>
      </div>

      <van-pull-refresh v-model="refreshing" @refresh="resetAndLoad">
        <van-list
          v-model:loading="loading"
          :finished="finished"
          finished-text="没有更多条目了"
          @load="loadKnowledgeList"
        >
          <div
            v-for="item in knowledgeList"
            :key="item.id"
            class="knowledge-item-card animate-fadeInUp"
            @click="viewDetail(item)"
          >
            <div class="knowledge-item-top">
              <van-tag :type="getKnowledgeTypeTag(item.content_type)" round size="small">
                {{ getKnowledgeTypeLabel(item.content_type) }}
              </van-tag>
              <span v-if="item.metadata?.filename" class="source-tag">文档入库</span>
            </div>
            <p class="knowledge-item-content">{{ item.content }}</p>
            <div class="knowledge-item-footer">
              <span class="knowledge-item-id">ID: {{ item.id }}</span>
              <span v-if="item.metadata?.filename" class="knowledge-item-meta">
                来源: {{ item.metadata.filename }}
              </span>
            </div>
          </div>
        </van-list>
      </van-pull-refresh>

      <div v-if="!loading && knowledgeList.length === 0 && !refreshing" class="empty-state">
        <van-icon name="info-o" size="48" color="#d1d5db" />
        <p>暂无相关知识</p>
        <span>试试搜索其他关键词</span>
      </div>
    </div>

    <van-popup v-model:show="showDetailPopup" position="bottom" round :style="{ height: '75%' }">
      <div class="detail-popup-content" v-if="detailItem">
        <div class="detail-popup-header">
          <h3>知识详情</h3>
          <span class="close-popup-btn" @click="showDetailPopup = false">✕</span>
        </div>
        <div class="detail-body">
          <div class="detail-meta-row">
            <van-tag type="warning" round size="medium">
              {{ getKnowledgeTypeLabel(detailItem.content_type) }}
            </van-tag>
            <span class="dm-source" v-if="detailItem.metadata?.filename">
              来源: {{ detailItem.metadata.filename }}
            </span>
          </div>
          <div class="detail-content-text">
            {{ detailItem.content }}
          </div>
          <div class="detail-extra">
            <p v-if="detailItem.metadata?.chunk_index !== undefined">
              文本块索引: #{{ detailItem.metadata.chunk_index + 1 }} / 共{{ detailItem.metadata.total_chunks || '?' }}块
            </p>
            <p v-if="detailItem.created_at">
              入库时间: {{ new Date(detailItem.created_at).toLocaleString() }}
            </p>
          </div>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { knowledgeBaseAPI } from '@/api'
import { showToast } from 'vant'

const activeType = ref('')
const searchQuery = ref('')
const knowledgeList = ref([])
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)
const knowledgePage = ref(1)
const showDetailPopup = ref(false)
const detailItem = ref(null)

const knowledgeTypes = [
  { label: '全部', value: '' },
  { label: '营养知识', value: 'nutrition' },
  { label: '食谱', value: 'recipe' },
  { label: '食材', value: 'ingredient' },
  { label: '饮食建议', value: 'advice' },
  { label: '季节性', value: 'seasonal' }
]

function getKnowledgeTypeTag(type) {
  const map = { nutrition: 'success', recipe: 'warning', ingredient: 'primary', advice: 'default', seasonal: 'danger' }
  return map[type] || 'default'
}

function getKnowledgeTypeLabel(type) {
  const map = { nutrition: '营养知识', recipe: '食谱', ingredient: '食材', advice: '饮食建议', seasonal: '季节性' }
  return map[type] || type
}

function viewDetail(item) {
  detailItem.value = item
  showDetailPopup.value = true
}

function resetAndLoad() {
  knowledgePage.value = 1
  finished.value = false
  knowledgeList.value = []
  loadKnowledgeList()
}

async function loadKnowledgeList() {
  try {
    if (searchQuery.value) {
      const res = await knowledgeBaseAPI.searchKnowledge(searchQuery.value, activeType.value || null, 20)
      if (res.success) {
        knowledgeList.value = res.results || res.data || []
        finished.value = true
      }
    } else {
      const res = await knowledgeBaseAPI.getList(activeType.value || null, knowledgePage.value, 20)
      if (res.success) {
        if (knowledgePage.value === 1) {
          knowledgeList.value = res.data || []
        } else {
          knowledgeList.value = [...knowledgeList.value, ...(res.data || [])]
        }
        knowledgePage.value++
        if ((res.data || []).length < 20) {
          finished.value = true
        }
      }
    }
  } catch (error) {
    showToast('加载失败')
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

function onSearch() {
  knowledgePage.value = 1
  finished.value = false
  knowledgeList.value = []
  loadKnowledgeList()
}

onMounted(() => {
  loadKnowledgeList()
})
</script>

<style scoped>
.knowledge-container {
  min-height: 100vh;
  background-color: #f0fdf4;
  padding-bottom: 30px;
}

.search-wrapper {
  padding: 12px 16px 0;
}

.content {
  padding: 0 16px;
}

.tab-bar {
  margin-top: 8px;
  margin-bottom: 12px;
}

.tab-scroll {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  padding-bottom: 4px;
}

.tab-scroll::-webkit-scrollbar {
  display: none;
}

.tab-item {
  flex-shrink: 0;
  padding: 8px 18px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  background: white;
  cursor: pointer;
  transition: var(--transition);
  box-shadow: var(--shadow-sm);
}

.tab-item.active {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  box-shadow: 0 3px 10px rgba(16, 185, 129, 0.3);
}

.knowledge-item-card {
  background: white;
  border-radius: var(--radius-md);
  padding: 14px 16px;
  margin-bottom: 10px;
  box-shadow: var(--shadow-sm);
  transition: var(--transition);
  cursor: pointer;
}

.knowledge-item-card:active { transform: scale(0.98); }

.knowledge-item-top {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.source-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 10px;
  font-weight: 600;
  background: #f59e0b;
  color: white;
}

.knowledge-item-content {
  margin: 0 0 8px;
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-primary);
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
  white-space: pre-wrap;
  word-break: break-word;
}

.knowledge-item-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  color: var(--text-muted);
}

.knowledge-item-id { font-weight: 500; }
.knowledge-item-meta { max-width: 50%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 50px 20px;
  gap: 10px;
}

.empty-state p {
  margin: 0;
  font-size: 15px;
  font-weight: 500;
  color: var(--text-secondary);
}

.empty-state span {
  font-size: 13px;
  color: var(--text-muted);
}

.detail-popup-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.detail-popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 20px;
  border-bottom: 1px solid #f1f5f9;
  flex-shrink: 0;
}

.detail-popup-header h3 { margin: 0; font-size: 17px; font-weight: 700; }

.close-popup-btn {
  width: 28px; height: 28px; border-radius: 50%;
  background: #f1f5f9; display: flex; align-items: center; justify-content: center;
  cursor: pointer; font-size: 14px; color: var(--text-muted);
}

.close-popup-btn:active { background: #fee2e2; color: #ef4444; }

.detail-body {
  flex: 1; overflow-y: auto; padding: 16px 20px 24px;
}

.detail-meta-row {
  display: flex; gap: 8px; margin-bottom: 14px; flex-wrap: wrap; align-items: center;
}

.dm-source {
  background: #e0e7ff; color: #3730a3; font-weight: 500;
  padding: 3px 10px; border-radius: 10px; font-size: 11px;
}

.detail-content-text {
  background: #f8fafc; border-radius: var(--radius-md); padding: 16px;
  font-size: 14px; line-height: 1.8; color: #374151; white-space: pre-wrap; word-break: break-word;
}

.detail-extra { margin-top: 14px; }
.detail-extra p { margin: 4px 0; font-size: 12px; color: var(--text-muted); }
</style>
