<template>
  <view class="knowledge-container">
    <view class="search-bar">
      <input 
        class="search-input" 
        v-model="searchQuery" 
        placeholder="搜索营养知识..."
        placeholder-class="placeholder"
        confirm-type="search"
        @confirm="searchKnowledge"
      />
      <button class="search-btn" @click="searchKnowledge">搜索</button>
    </view>

    <view class="filter-bar">
      <scroll-view scroll-x class="category-scroll">
        <view class="category-list">
          <view 
            class="category-item" 
            :class="{ active: selectedCategory === '' }"
            @click="selectCategory('')"
          >
            <text>全部</text>
          </view>
          <view 
            class="category-item" 
            :class="{ active: selectedCategory === cat }"
            v-for="cat in categories" 
            :key="cat"
            @click="selectCategory(cat)"
          >
            <text>{{ cat }}</text>
          </view>
        </view>
      </scroll-view>
    </view>

    <scroll-view scroll-y class="knowledge-list" @scrolltolower="loadMore">
      <view class="knowledge-item" v-for="item in knowledgeList" :key="item.id" @click="showDetail(item)">
        <view class="knowledge-header">
          <text class="knowledge-title">{{ item.title }}</text>
          <text class="knowledge-category" v-if="item.category">{{ item.category }}</text>
        </view>
        <text class="knowledge-content">{{ item.content }}</text>
        <view class="knowledge-footer">
          <text class="knowledge-source" v-if="item.source">来源：{{ item.source }}</text>
          <text class="knowledge-time">{{ formatDate(item.created_at) }}</text>
        </view>
      </view>

      <view class="loading-more" v-if="loadingMore">
        <text>加载中...</text>
      </view>

      <view class="empty-state" v-if="!loading && knowledgeList.length === 0">
        <text class="empty-icon">📚</text>
        <text class="empty-text">暂无知识内容</text>
      </view>
    </scroll-view>

    <view class="detail-modal" v-if="showModal" @click="showModal = false">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">{{ currentItem.title }}</text>
          <text class="modal-close" @click="showModal = false">✕</text>
        </view>
        <scroll-view scroll-y class="modal-body">
          <text class="detail-content">{{ currentItem.content }}</text>
          <view class="detail-footer" v-if="currentItem.source || currentItem.created_at">
            <text class="detail-source" v-if="currentItem.source">来源：{{ currentItem.source }}</text>
            <text class="detail-time" v-if="currentItem.created_at">{{ formatDate(currentItem.created_at) }}</text>
          </view>
        </scroll-view>
      </view>
    </view>
  </view>
</template>

<script>
import { knowledgeAPI } from '@/utils/api.js'

export default {
  data() {
    return {
      searchQuery: '',
      selectedCategory: '',
      categories: [],
      knowledgeList: [],
      page: 1,
      loading: false,
      loadingMore: false,
      showModal: false,
      currentItem: {}
    }
  },
  onShow() {
    this.loadCategories()
    this.loadKnowledge()
  },
  methods: {
    async loadCategories() {
      try {
        this.categories = await knowledgeAPI.getCategories()
      } catch (e) {
        console.error('加载分类失败', e)
      }
    },
    async loadKnowledge() {
      this.loading = true
      try {
        const params = {
          page: this.page,
          page_size: 10
        }
        if (this.selectedCategory) {
          params.category = this.selectedCategory
        }
        if (this.searchQuery) {
          this.knowledgeList = await knowledgeAPI.search(this.searchQuery, this.page, 10)
        } else {
          this.knowledgeList = await knowledgeAPI.list(params)
        }
      } catch (e) {
        console.error('加载知识失败', e)
      } finally {
        this.loading = false
      }
    },
    async loadMore() {
      if (this.loadingMore) return
      this.page++
      this.loadingMore = true
      try {
        const params = {
          page: this.page,
          page_size: 10
        }
        if (this.selectedCategory) {
          params.category = this.selectedCategory
        }
        if (this.searchQuery) {
          const list = await knowledgeAPI.search(this.searchQuery, this.page, 10)
          this.knowledgeList = [...this.knowledgeList, ...list]
        } else {
          const list = await knowledgeAPI.list(params)
          this.knowledgeList = [...this.knowledgeList, ...list]
        }
      } catch (e) {
        this.page--
      } finally {
        this.loadingMore = false
      }
    },
    selectCategory(category) {
      this.selectedCategory = category
      this.page = 1
      this.loadKnowledge()
    },
    searchKnowledge() {
      this.page = 1
      this.loadKnowledge()
    },
    showDetail(item) {
      this.currentItem = item
      this.showModal = true
    },
    formatDate(dateStr) {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`
    }
  }
}
</script>

<style scoped>
.knowledge-container {
  min-height: 100vh;
  background: #f5f5f5;
  display: flex;
  flex-direction: column;
}

.search-bar {
  display: flex;
  gap: 20rpx;
  padding: 30rpx;
  background: #fff;
}

.search-input {
  flex: 1;
  height: 80rpx;
  background: #f5f5f5;
  border-radius: 12rpx;
  padding: 0 30rpx;
  font-size: 28rpx;
}

.placeholder {
  color: #999;
}

.search-btn {
  height: 80rpx;
  line-height: 80rpx;
  padding: 0 30rpx;
  background: linear-gradient(135deg, #10b981, #059669);
  color: #fff;
  border: none;
  border-radius: 12rpx;
  font-size: 28rpx;
}

.search-btn::after {
  border: none;
}

.filter-bar {
  background: #fff;
  padding: 0 30rpx 20rpx;
}

.category-scroll {
  white-space: nowrap;
}

.category-list {
  display: inline-flex;
  gap: 20rpx;
}

.category-item {
  padding: 12rpx 24rpx;
  background: #f5f5f5;
  border-radius: 20rpx;
  font-size: 26rpx;
  color: #666;
}

.category-item.active {
  background: linear-gradient(135deg, #10b981, #059669);
  color: #fff;
}

.knowledge-list {
  flex: 1;
  padding: 30rpx;
}

.knowledge-item {
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
}

.knowledge-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.knowledge-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  flex: 1;
  margin-right: 20rpx;
}

.knowledge-category {
  font-size: 22rpx;
  color: #10b981;
  background: #f0fdf4;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
}

.knowledge-content {
  font-size: 26rpx;
  line-height: 1.6;
  color: #666;
  margin-bottom: 16rpx;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  overflow: hidden;
}

.knowledge-footer {
  display: flex;
  justify-content: space-between;
  font-size: 22rpx;
  color: #999;
}

.loading-more {
  text-align: center;
  padding: 30rpx;
  color: #999;
  font-size: 26rpx;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 120rpx 0;
}

.empty-icon {
  font-size: 120rpx;
  margin-bottom: 20rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #999;
}

.detail-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  width: 90%;
  max-height: 80vh;
  background: #fff;
  border-radius: 24rpx;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx;
  border-bottom: 2rpx solid #f0f0f0;
}

.modal-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
  flex: 1;
}

.modal-close {
  font-size: 40rpx;
  color: #999;
  padding: 0 10rpx;
}

.modal-body {
  max-height: calc(80vh - 100rpx);
  padding: 30rpx;
}

.detail-content {
  font-size: 28rpx;
  line-height: 1.8;
  color: #333;
  white-space: pre-wrap;
}

.detail-footer {
  margin-top: 30rpx;
  padding-top: 20rpx;
  border-top: 2rpx solid #f0f0f0;
  font-size: 24rpx;
  color: #999;
}

.detail-source {
  display: block;
  margin-bottom: 10rpx;
}

.detail-time {
  display: block;
}
</style>
