<template>
  <div class="knowledge-container">
    <van-nav-bar title="营养知识" left-arrow @click-left="$router.back()" />

    <div class="search-wrapper">
      <div class="search-bar">
        <van-icon name="search" size="18" color="#94a3b8" />
        <input
          v-model="searchKeyword"
          type="text"
          placeholder="搜索营养知识..."
          @keyup.enter="onSearch"
          class="search-input"
        />
        <button v-if="searchKeyword" class="search-clear" @click="clearSearch">
          <van-icon name="cross" size="14" />
        </button>
      </div>
    </div>

    <div class="content">
      <div class="tab-bar" :class="{ 'sticky': isSticky }">
        <div class="tab-scroll">
          <span
            v-for="cat in allCategories"
            :key="cat.value"
            class="tab-item"
            :class="{ active: activeTab === cat.value }"
            @click="switchTab(cat.value)"
          >
            {{ cat.label }}
          </span>
        </div>
      </div>

      <div v-if="activeTab !== 'resources'" class="knowledge-list-section">
        <van-pull-refresh v-model="refreshing" @refresh="() => loadKnowledge(activeTab)">
          <van-list
            v-model:loading="loading"
            :finished="finished"
            finished-text="没有更多了"
            @load="() => loadKnowledge(activeTab)"
          >
            <div
              v-for="(item, index) in knowledgeList"
              :key="item.id + '-' + (item.source || 'kb')"
              class="knowledge-card animate-fadeInUp"
              :class="{ 'card-vector': item.source === 'vector_db' }"
              :style="{ animationDelay: (index * 0.05) + 's' }"
              @click="viewDetail(item)"
            >
              <div class="card-left">
                <div class="card-icon" :style="{ background: getCategoryColor(item.category || activeTab) }">
                  <van-icon :name="item.source === 'vector_db' ? 'bookmark-o' : 'description'" size="16" />
                </div>
                <div class="card-info">
                  <h4>{{ item.title }}</h4>
                  <p>
                    {{ item.category }}
                    <span v-if="item.source === 'vector_db'" class="source-tag">文档入库</span>
                  </p>
                </div>
              </div>
              <van-icon name="arrow" size="14" color="#c4cbd5" />
            </div>

            <template #finished>
              <div class="finished-tip" v-if="knowledgeList.length > 0">已加载全部内容</div>
            </template>

            <template #loading>
              <div class="list-loading">
                <van-loading size="20" />
                <span>加载中...</span>
              </div>
            </template>
          </van-list>
        </van-pull-refresh>

        <div v-if="!loading && knowledgeList.length === 0 && !refreshing" class="empty-state">
          <van-icon name="info-o" size="48" color="#d1d5db" />
          <p>暂无相关知识</p>
          <span>试试搜索其他关键词</span>
        </div>
      </div>

      <div v-else class="resources-page">
        <div class="resource-group">
          <div class="group-header group-header-official">
            <div class="group-icon">
              <van-icon name="shield-o" size="18" />
            </div>
            <h4>权威营养机构</h4>
          </div>
          <div class="resource-cards">
            <a
              v-for="item in officialResources"
              :key="item.name"
              class="resource-card"
              :href="item.url"
              target="_blank"
            >
              <div class="resource-top">
                <span class="resource-tag tag-official">{{ item.tag }}</span>
                <van-icon name="arrow-up" size="12" class="resource-link-icon" />
              </div>
              <h5>{{ item.name }}</h5>
              <p>{{ item.description }}</p>
            </a>
          </div>
        </div>

        <div class="resource-group">
          <div class="group-header group-header-encyclopedia">
            <div class="group-icon">
              <van-icon name="book-o" size="18" />
            </div>
            <h4>营养百科</h4>
          </div>
          <div class="resource-cards">
            <a
              v-for="item in encyclopediaResources"
              :key="item.name"
              class="resource-card"
              :href="item.url"
              target="_blank"
            >
              <div class="resource-top">
                <span class="resource-tag" :class="'tag-' + getTagClass(item.tag)">{{ item.tag }}</span>
                <van-icon name="arrow-up" size="12" class="resource-link-icon" />
              </div>
              <h5>{{ item.name }}</h5>
              <p>{{ item.description }}</p>
            </a>
          </div>
        </div>

        <div class="resource-group">
          <div class="group-header group-header-guide">
            <div class="group-icon">
              <van-icon name="guide-o" size="18" />
            </div>
            <h4>健康饮食指南</h4>
          </div>
          <div class="resource-cards">
            <a
              v-for="item in guideResources"
              :key="item.name"
              class="resource-card"
              :href="item.url"
              target="_blank"
            >
              <div class="resource-top">
                <span class="resource-tag tag-guide">{{ item.tag }}</span>
                <van-icon name="arrow-up" size="12" class="resource-link-icon" />
              </div>
              <h5>{{ item.name }}</h5>
              <p>{{ item.description }}</p>
            </a>
          </div>
        </div>

        <div class="resource-group">
          <div class="group-header group-header-tool">
            <div class="group-icon">
              <van-icon name="calculator-o" size="18" />
            </div>
            <h4>营养计算工具</h4>
          </div>
          <div class="resource-cards">
            <a
              v-for="item in toolResources"
              :key="item.name"
              class="resource-card"
              :href="item.url"
              target="_blank"
            >
              <div class="resource-top">
                <span class="resource-tag tag-tool">{{ item.tag }}</span>
                <van-icon name="arrow-up" size="12" class="resource-link-icon" />
              </div>
              <h5>{{ item.name }}</h5>
              <p>{{ item.description }}</p>
            </a>
          </div>
        </div>
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
            <span class="dm-tag dm-vector">文档入库</span>
            <span class="dm-type">{{ detailItem.category }}</span>
            <span class="dm-source" v-if="detailItem.metadata?.filename">
              来源: {{ detailItem.metadata.filename }}
            </span>
          </div>
          <h4 class="detail-title">{{ detailItem.title }}</h4>
          <div class="detail-content-text">
            {{ detailItem.content }}
          </div>
          <div class="detail-extra" v-if="detailItem.metadata">
            <p v-if="detailItem.metadata.chunk_index !== undefined">
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
import { useRouter } from 'vue-router'
import { knowledgeAPI, knowledgeBaseAPI } from '@/api'
import { showToast } from 'vant'

const router = useRouter()

const activeTab = ref('all')
const searchKeyword = ref('')
const knowledgeList = ref([])
const categories = ref([])
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)
const page = ref(1)
const isSticky = ref(false)
const showDetailPopup = ref(false)
const detailItem = ref(null)

const allCategories = ref([
  { label: '全部', value: 'all' },
  { label: '推荐资源', value: 'resources' }
])

const officialResources = ref([
  { name: '中国营养学会', url: 'http://www.cnsoc.org/', description: '中国营养领域的权威学术组织', tag: '官方' },
  { name: '中国疾病预防控制中心', url: 'http://www.chinacdc.cn/', description: '国家级疾病预防控制机构', tag: '官方' },
  { name: '世界卫生组织 (WHO)', url: 'https://www.who.int/news-room/fact-sheets/detail/healthy-diet', description: '世界卫生组织健康饮食指南', tag: '国际' },
  { name: '美国农业部营养标准', url: 'https://www.nal.usda.gov/fnic', description: '美国国家营养标准数据库', tag: '国际' }
])

const encyclopediaResources = ref([
  { name: '食物营养成分查询', url: 'https://www.boohe.com/tpgn/', description: '常见食物营养成分查询', tag: '工具' },
  { name: '薄荷营养师', url: 'https://www.mhttc.com/', description: '在线营养咨询和食谱推荐', tag: '工具' },
  { name: '营养派', url: 'https://www.yingyang.org/', description: '营养知识科普平台', tag: '科普' },
  { name: '营养素参考值', url: 'https://www.fda.gov.cn/food/labeling/', description: '中国食品营养标签解读', tag: '指南' }
])

const guideResources = ref([
  { name: '中国居民膳食指南', url: 'http://dg.cnsoc.org/', description: '最新版中国居民膳食指南', tag: '指南' },
  { name: '糖尿病饮食指南', url: 'https://www.cdschina.org/', description: '中华医学会糖尿病学分会', tag: '指南' },
  { name: '高血压饮食建议', url: 'http://www.heart.org.cn/', description: '中国心脏大会饮食建议', tag: '指南' },
  { name: '儿童营养指南', url: 'http://www.mch.org.cn/', description: '妇幼营养健康指导', tag: '指南' }
])

const toolResources = ref([
  { name: '卡路里计算器', url: 'https://www.boohe.com/kaluli/', description: '食物卡路里和营养素计算', tag: '计算' },
  { name: 'BMI计算器', url: 'https://www.boohe.com/bmi/', description: '身体质量指数计算', tag: '计算' },
  { name: '基础代谢率计算', url: 'https://www.boohe.com/daimi/', description: 'BMR基础代谢率计算', tag: '计算' },
  { name: '食物交换份', url: 'https://www.boohe.com/jiaohuan/', description: '糖尿病食物交换份计算', tag: '计算' }
])

function handleScroll() {
  isSticky.value = window.scrollY > 120
}

function switchTab(value) {
  activeTab.value = value
  page.value = 1
  finished.value = false
  knowledgeList.value = []
  if (value === 'all') {
    loadKnowledge()
  } else if (value === 'resources') {
    finished.value = true
  } else {
    loadKnowledge(value)
  }
}

function clearSearch() {
  searchKeyword.value = ''
}

function getTagClass(tag) {
  const map = {
    '工具': 'tool',
    '科普': 'science',
    '指南': 'guide',
    '官方': 'official',
    '国际': 'international',
    '计算': 'calc'
  }
  return map[tag] || 'default'
}

function getCategoryColor(category) {
  const colors = {
    nutrition: 'linear-gradient(135deg, #10b981, #059669)',
    recipe: 'linear-gradient(135deg, #f97316, #ea580c)',
    ingredient: 'linear-gradient(135deg, #eab308, #ca8a04)',
    advice: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
    seasonal: 'linear-gradient(135deg, #ec4899, #db2777)'
  }
  return colors[category] || 'linear-gradient(135deg, #10b981, #059669)'
}

async function loadKnowledge(category = '') {
  try {
    const params = {
      page: page.value,
      page_size: 10
    }

    let traditionalData = []
    let vectorData = []

    if (searchKeyword.value) {
      traditionalData = await knowledgeAPI.search(searchKeyword.value, page.value, 10)
      try { vectorData = (await knowledgeBaseAPI.searchKnowledge(searchKeyword.value, '', 10))?.data || [] } catch(e) {}
    } else if (category && category !== 'all') {
      params.category = category
      traditionalData = await knowledgeAPI.list(params)
    } else {
      traditionalData = await knowledgeAPI.list(params)
      try {
        const kbRes = await knowledgeBaseAPI.getList('', page.value, 10)
        vectorData = kbRes.data || kbRes || []
      } catch(e) {}
    }

    let mergedData = []

    traditionalData.forEach(item => {
      mergedData.push({
        id: item.id,
        title: item.title || '知识条目',
        content: item.content || '',
        category: item.category || 'nutrition',
        source: 'knowledge_base'
      })
    })

    vectorData.forEach(item => {
      mergedData.push({
        id: item.id,
        title: item.metadata?.filename ? `📄 ${item.metadata.filename}` : (item.content_type === 'nutrition' ? '营养知识' : '知识条目'),
        content: item.content || '',
        category: item.content_type || 'nutrition',
        source: 'vector_db',
        metadata: item.metadata
      })
    })

    if (page.value === 1) {
      knowledgeList.value = mergedData
    } else {
      knowledgeList.value = [...knowledgeList.value, ...mergedData]
    }

    page.value++
    loading.value = false

    if ((traditionalData.length < 10 && !searchKeyword.value) || mergedData.length < 3) {
      finished.value = true
    }
  } catch (error) {
    showToast('加载失败')
  } finally {
    refreshing.value = false
  }
}

async function loadCategories() {
  try {
    const cats = await knowledgeAPI.getCategories()
    categories.value = cats
    const dynamicTabs = cats.map(c => ({ label: c, value: c }))
    allCategories.value = [
      { label: '全部', value: 'all' },
      ...dynamicTabs,
      { label: '推荐资源', value: 'resources' }
    ]
  } catch (error) {
    console.log('加载分类失败')
  }
}

function onSearch() {
  page.value = 1
  finished.value = false
  knowledgeList.value = []
  loadKnowledge()
}

function viewDetail(item) {
  if (item.source === 'vector_db') {
    detailItem.value = item
    showDetailPopup.value = true
  } else {
    router.push(`/knowledge-detail/${item.id}`)
  }
}

onMounted(() => {
  loadKnowledge()
  loadCategories()
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.knowledge-container {
  min-height: 100vh;
  background-color: #f0fdf4;
}

.search-wrapper {
  padding: 14px 16px 0;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: white;
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
  transition: var(--transition);
}

.search-bar:focus-within {
  box-shadow: var(--shadow-md), 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 15px;
  color: var(--text-primary);
  background: transparent;
}

.search-input::placeholder {
  color: #c4cbd5;
}

.search-clear {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: none;
  background: #f1f5f9;
  cursor: pointer;
  padding: 0;
}

.content {
  padding: 0 16px 30px;
}

.tab-bar {
  margin-top: 14px;
  margin-bottom: 16px;
  position: relative;
  z-index: 10;
}

.tab-bar.sticky {
  position: sticky;
  top: 46px;
  background: #f0fdf4;
  padding: 8px 0;
  z-index: 100;
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

.knowledge-list-section {
  min-height: 200px;
}

.knowledge-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: white;
  border-radius: var(--radius-md);
  padding: 16px;
  margin-bottom: 10px;
  box-shadow: var(--shadow-sm);
  transition: var(--transition);
  cursor: pointer;
}

.knowledge-card.card-vector {
  border-left: 3px solid #f59e0b;
  background: linear-gradient(135deg, #fffbeb, #fef3c7);
}

.knowledge-card:active { transform: scale(0.98); box-shadow: var(--shadow-md); }

.card-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  overflow: hidden;
}

.card-icon {
  width: 42px;
  height: 42px;
  border-radius: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.card-info {
  flex: 1;
  overflow: hidden;
}

.card-info h4 {
  margin: 0 0 4px;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-info p {
  margin: 0;
  font-size: 12px;
  color: var(--text-muted);
}

.source-tag {
  display: inline-block;
  margin-left: 6px;
  padding: 1px 7px;
  border-radius: 8px;
  font-size: 10px;
  font-weight: 600;
  background: #f59e0b;
  color: white;
}

.finished-tip {
  text-align: center;
  padding: 20px;
  font-size: 13px;
  color: var(--text-muted);
}

.list-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px;
  font-size: 13px;
  color: var(--text-muted);
}

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

.resources-page {
  padding-top: 4px;
}

.resource-group {
  margin-bottom: 24px;
}

.group-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  padding: 0 2px;
}

.group-icon {
  width: 34px;
  height: 34px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.group-header-official .group-icon { background: linear-gradient(135deg, #ef4444, #dc2626); }
.group-header-encyclopedia .group-icon { background: linear-gradient(135deg, #10b981, #059669); }
.group-header-guide .group-icon { background: linear-gradient(135deg, #f59e0b, #d97706); }
.group-header-tool .group-icon { background: linear-gradient(135deg, #6366f1, #8b5cf6); }

.group-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.resource-cards {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.resource-card {
  background: white;
  border-radius: var(--radius-md);
  padding: 16px;
  box-shadow: var(--shadow-sm);
  transition: var(--transition);
  text-decoration: none;
  display: block;
}

.resource-card:active {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.resource-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.resource-tag {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.tag-official { background: #fee2e2; color: #dc2626; }
.tag-international { background: #dbeafe; color: #2563eb; }
.tag-tool { background: #d1fae5; color: #059669; }
.tag-science { background: #fef3c7; color: #d97706; }
.tag-guide { background: #ede9fe; color: #7c3aed; }
.tag-calc { background: #e0e7ff; color: #4338ca; }

.resource-link-icon {
  transform: rotate(45deg);
  color: #c4cbd5;
}

.resource-card h5 {
  margin: 0 0 6px;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.resource-card p {
  margin: 0;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
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
  display: flex; gap: 8px; margin-bottom: 14px; flex-wrap: wrap;
}

.dm-tag {
  padding: 3px 10px; border-radius: 10px; font-size: 11px; font-weight: 600;
}
.dm-vector { background: #fef3c7; color: #92400e; }
.dm-type { background: #ecfdf5; color: #065f46; }
.dm-source { background: #e0e7ff; color: #3730a3; font-weight: 500; padding: 3px 10px; border-radius: 10px; font-size: 11px; }

.detail-title { margin: 0 0 12px; font-size: 17px; font-weight: 700; color: var(--text-primary); }

.detail-content-text {
  background: #f8fafc; border-radius: var(--radius-md); padding: 16px;
  font-size: 14px; line-height: 1.8; color: #374151; white-space: pre-wrap; word-break: break-word;
}

.detail-extra { margin-top: 14px; }
.detail-extra p { margin: 4px 0; font-size: 12px; color: var(--text-muted); }
</style>
