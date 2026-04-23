<template>
  <div class="knowledge-list-container">
    <van-nav-bar :title="pageTitle" left-arrow @click-left="$router.back()" />
    
    <div class="content">
      <van-pull-refresh v-model="refreshing" @refresh="loadKnowledge">
        <van-list
          v-model:loading="loading"
          :finished="finished"
          @load="loadKnowledge"
        >
          <van-cell
            v-for="item in knowledgeList"
            :key="item.id"
            :title="item.content.substring(0, 50) + '...'"
            :label="item.content_type"
            is-link
            @click="viewDetail(item)"
          >
            <template #value>
              <span style="color: #969799; font-size: 12px;">
                {{ formatSimilarity(item.similarity) }}
              </span>
            </template>
          </van-cell>
        </van-list>
      </van-pull-refresh>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { knowledgeBaseAPI } from '@/api'
import { showToast } from 'vant'

const route = useRoute()

const knowledgeList = ref([])
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)
const page = ref(1)
const contentType = ref('')

const typeMap = {
  nutrition: '营养知识',
  recipe: '食谱',
  ingredient: '食材',
  advice: '饮食建议',
  seasonal: '季节性知识'
}

const pageTitle = computed(() => {
  return typeMap[contentType.value] || '知识列表'
})

function formatSimilarity(similarity) {
  if (similarity === undefined || similarity === null) return ''
  return `相似度: ${(similarity * 100).toFixed(1)}%`
}

async function loadKnowledge() {
  try {
    const res = await knowledgeBaseAPI.getList(contentType.value, page.value, 20)
    if (res.success) {
      if (page.value === 1) {
        knowledgeList.value = res.data
      } else {
        knowledgeList.value = [...knowledgeList.value, ...res.data]
      }
      
      if (res.data.length < 20) {
        finished.value = true
      }
      page.value++
    }
  } catch (error) {
    showToast('加载失败')
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

function viewDetail(item) {
  console.log('查看详情', item)
}

onMounted(() => {
  contentType.value = route.query.type || ''
  loadKnowledge()
})
</script>

<style scoped>
.knowledge-list-container {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.content {
  padding-bottom: 50px;
}
</style>
