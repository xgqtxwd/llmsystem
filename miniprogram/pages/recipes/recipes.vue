<template>
  <view class="recipes-container">
    <view class="tabs">
      <view class="tab" :class="{ active: activeTab === 'recommend' }" @click="activeTab = 'recommend'">AI推荐</view>
      <view class="tab" :class="{ active: activeTab === 'list' }" @click="activeTab = 'list'">食谱列表</view>
      <view class="tab" :class="{ active: activeTab === 'ingredient' }" @click="activeTab = 'ingredient'">食材识别</view>
    </view>

    <view class="tab-content" v-if="activeTab === 'recommend'">
      <view class="recommend-form">
        <view class="form-group">
          <text class="label">餐型</text>
          <picker :value="mealTypeIndex" :range="mealTypes" @change="onMealTypeChange">
            <view class="picker">{{ mealTypes[mealTypeIndex] }}</view>
          </picker>
        </view>

        <view class="form-group">
          <text class="label">可用食材</text>
          <input 
            class="input" 
            v-model="availableIngredients" 
            placeholder="例如：鸡蛋、番茄、豆腐"
            placeholder-class="placeholder"
          />
        </view>

        <button class="submit-btn" @click="getRecommendation" :loading="loading">
          获取推荐
        </button>
      </view>

      <view class="recommend-result" v-if="recommendation">
        <text class="result-title">推荐结果</text>
        <text class="result-content">{{ recommendation }}</text>
      </view>
    </view>

    <view class="tab-content" v-if="activeTab === 'list'">
      <scroll-view scroll-y class="recipe-list" @scrolltolower="loadMore">
        <view class="recipe-item" v-for="recipe in recipes" :key="recipe.id" @click="showRecipeDetail(recipe)">
          <view class="recipe-header">
            <text class="recipe-name">{{ recipe.name }}</text>
            <view class="recipe-tags">
              <text class="tag">{{ recipe.meal_type }}</text>
              <text class="tag">{{ recipe.difficulty }}</text>
            </view>
          </view>
          <text class="recipe-desc">{{ recipe.description }}</text>
          <view class="recipe-footer">
            <text class="recipe-time">⏱ {{ recipe.cook_time }}分钟</text>
          </view>
        </view>

        <view class="loading-more" v-if="loadingMore">
          <text>加载中...</text>
        </view>
      </scroll-view>
    </view>

    <view class="tab-content" v-if="activeTab === 'ingredient'">
      <view class="upload-section">
        <text class="upload-title">拍照或选择图片识别食材</text>
        <view class="upload-actions">
          <button class="upload-btn" @click="chooseImage('camera')">📷 拍照识别</button>
          <button class="upload-btn" @click="chooseImage('album')">🖼️ 选择图片</button>
        </view>

        <view class="preview-image" v-if="previewUrl">
          <image :src="previewUrl" mode="aspectFit"></image>
        </view>

        <view class="recognition-result" v-if="recognitionResult">
          <text class="result-title">识别结果</text>
          <text class="result-content">{{ recognitionResult }}</text>
        </view>
      </view>
    </view>

    <view class="recipe-modal" v-if="showDetail" @click="showDetail = false">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">{{ currentRecipe.name }}</text>
          <text class="modal-close" @click="showDetail = false">✕</text>
        </view>
        <scroll-view scroll-y class="modal-body">
          <view class="detail-section">
            <text class="section-title">基本信息</text>
            <view class="detail-row">
              <text class="detail-label">餐型：</text>
              <text class="detail-value">{{ currentRecipe.meal_type }}</text>
            </view>
            <view class="detail-row">
              <text class="detail-label">难度：</text>
              <text class="detail-value">{{ currentRecipe.difficulty }}</text>
            </view>
            <view class="detail-row">
              <text class="detail-label">时间：</text>
              <text class="detail-value">{{ currentRecipe.cook_time }}分钟</text>
            </view>
          </view>

          <view class="detail-section" v-if="currentRecipe.ingredients && currentRecipe.ingredients.length">
            <text class="section-title">食材</text>
            <view class="ingredient-item" v-for="(ing, idx) in currentRecipe.ingredients" :key="idx">
              <text class="ingredient-name">{{ ing.name }}</text>
              <text class="ingredient-quantity">{{ ing.quantity }} {{ ing.unit }}</text>
            </view>
          </view>

          <view class="detail-section" v-if="currentRecipe.nutrition">
            <text class="section-title">营养信息</text>
            <view class="nutrition-grid">
              <view class="nutrition-item">
                <text class="nutrition-value">{{ currentRecipe.nutrition.calories || 0 }}</text>
                <text class="nutrition-label">热量</text>
              </view>
              <view class="nutrition-item">
                <text class="nutrition-value">{{ currentRecipe.nutrition.protein || 0 }}g</text>
                <text class="nutrition-label">蛋白质</text>
              </view>
              <view class="nutrition-item">
                <text class="nutrition-value">{{ currentRecipe.nutrition.fat || 0 }}g</text>
                <text class="nutrition-label">脂肪</text>
              </view>
              <view class="nutrition-item">
                <text class="nutrition-value">{{ currentRecipe.nutrition.carbohydrate || 0 }}g</text>
                <text class="nutrition-label">碳水</text>
              </view>
            </view>
          </view>

          <view class="detail-section" v-if="currentRecipe.description">
            <text class="section-title">做法</text>
            <text class="description-text">{{ currentRecipe.description }}</text>
          </view>
        </scroll-view>
      </view>
    </view>
  </view>
</template>

<script>
import { recipesAPI } from '@/utils/api.js'

export default {
  data() {
    return {
      activeTab: 'recommend',
      mealTypes: ['不限', '早餐', '午餐', '晚餐', '加餐'],
      mealTypeIndex: 0,
      availableIngredients: '',
      loading: false,
      recommendation: '',
      recipes: [],
      page: 1,
      loadingMore: false,
      previewUrl: '',
      recognitionResult: '',
      showDetail: false,
      currentRecipe: {}
    }
  },
  onShow() {
    if (this.activeTab === 'list' && this.recipes.length === 0) {
      this.loadRecipes()
    }
  },
  methods: {
    onMealTypeChange(e) {
      this.mealTypeIndex = e.detail.value
    },
    async getRecommendation() {
      this.loading = true
      try {
        const mealType = this.mealTypeIndex > 0 ? this.mealTypes[this.mealTypeIndex] : ''
        const res = await recipesAPI.getAIRecommendation(mealType, this.availableIngredients)
        this.recommendation = res.recommendation || '暂无推荐结果'
      } catch (error) {
        uni.showToast({ title: '获取推荐失败', icon: 'none' })
      } finally {
        this.loading = false
      }
    },
    async loadRecipes() {
      this.loadingMore = true
      try {
        const res = await recipesAPI.list({ page: this.page, page_size: 10 })
        this.recipes = res
      } catch (error) {
        console.error('加载食谱失败', error)
      } finally {
        this.loadingMore = false
      }
    },
    loadMore() {
      if (this.loadingMore) return
      this.page++
      this.loadRecipes()
    },
    showRecipeDetail(recipe) {
      this.currentRecipe = recipe
      this.showDetail = true
    },
    chooseImage(sourceType) {
      uni.chooseImage({
        count: 1,
        sourceType: [sourceType],
        success: (res) => {
          this.previewUrl = res.tempFilePaths[0]
          this.recognizeImage(res.tempFilePaths[0])
        }
      })
    },
    async recognizeImage(filePath) {
      this.loading = true
      try {
        const res = await recipesAPI.recognizeIngredients(filePath)
        this.recognitionResult = res.result || JSON.stringify(res)
      } catch (error) {
        uni.showToast({ title: '识别失败', icon: 'none' })
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.recipes-container {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 30rpx;
}

.tabs {
  display: flex;
  background: #fff;
  padding: 10rpx 30rpx;
  gap: 20rpx;
}

.tab {
  flex: 1;
  text-align: center;
  padding: 20rpx 0;
  font-size: 28rpx;
  color: #666;
  border-radius: 12rpx;
}

.tab.active {
  color: #10b981;
  font-weight: bold;
  background: #f0fdf4;
}

.tab-content {
  padding: 30rpx;
}

.recommend-form {
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
}

.form-group {
  margin-bottom: 30rpx;
}

.label {
  font-size: 28rpx;
  color: #333;
  font-weight: bold;
  margin-bottom: 16rpx;
  display: block;
}

.picker {
  height: 80rpx;
  line-height: 80rpx;
  background: #f5f5f5;
  border-radius: 12rpx;
  padding: 0 20rpx;
  font-size: 28rpx;
  color: #666;
}

.input {
  height: 80rpx;
  background: #f5f5f5;
  border-radius: 12rpx;
  padding: 0 20rpx;
  font-size: 28rpx;
}

.placeholder {
  color: #999;
}

.submit-btn {
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  background: linear-gradient(135deg, #10b981, #059669);
  color: #fff;
  border: none;
  border-radius: 12rpx;
  font-size: 32rpx;
  font-weight: bold;
  margin-top: 20rpx;
}

.submit-btn::after {
  border: none;
}

.recommend-result {
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-top: 30rpx;
}

.result-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 20rpx;
  display: block;
}

.result-content {
  font-size: 28rpx;
  line-height: 1.8;
  color: #666;
}

.recipe-list {
  height: calc(100vh - 200rpx);
}

.recipe-item {
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
}

.recipe-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.recipe-name {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.recipe-tags {
  display: flex;
  gap: 10rpx;
}

.tag {
  font-size: 22rpx;
  color: #10b981;
  background: #f0fdf4;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
}

.recipe-desc {
  font-size: 26rpx;
  color: #666;
  line-height: 1.6;
  margin-bottom: 16rpx;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
}

.recipe-footer {
  display: flex;
  justify-content: flex-end;
}

.recipe-time {
  font-size: 24rpx;
  color: #999;
}

.loading-more {
  text-align: center;
  padding: 30rpx;
  color: #999;
  font-size: 26rpx;
}

.upload-section {
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
}

.upload-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 30rpx;
  display: block;
  text-align: center;
}

.upload-actions {
  display: flex;
  gap: 20rpx;
  margin-bottom: 30rpx;
}

.upload-btn {
  flex: 1;
  height: 88rpx;
  line-height: 88rpx;
  background: linear-gradient(135deg, #10b981, #059669);
  color: #fff;
  border: none;
  border-radius: 12rpx;
  font-size: 28rpx;
}

.upload-btn::after {
  border: none;
}

.preview-image {
  margin: 30rpx 0;
  border-radius: 16rpx;
  overflow: hidden;
}

.preview-image image {
  width: 100%;
  height: 400rpx;
}

.recognition-result {
  background: #f0fdf4;
  border-radius: 16rpx;
  padding: 30rpx;
}

.recipe-modal {
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

.detail-section {
  margin-bottom: 30rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 20rpx;
  display: block;
}

.detail-row {
  display: flex;
  margin-bottom: 16rpx;
}

.detail-label {
  font-size: 28rpx;
  color: #666;
  width: 120rpx;
}

.detail-value {
  font-size: 28rpx;
  color: #333;
  flex: 1;
}

.ingredient-item {
  display: flex;
  justify-content: space-between;
  padding: 16rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.ingredient-name {
  font-size: 26rpx;
  color: #333;
}

.ingredient-quantity {
  font-size: 26rpx;
  color: #666;
}

.nutrition-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20rpx;
}

.nutrition-item {
  text-align: center;
  background: #f5f5f5;
  padding: 20rpx;
  border-radius: 12rpx;
}

.nutrition-value {
  font-size: 28rpx;
  font-weight: bold;
  color: #10b981;
  display: block;
  margin-bottom: 8rpx;
}

.nutrition-label {
  font-size: 22rpx;
  color: #999;
}

.description-text {
  font-size: 26rpx;
  line-height: 1.8;
  color: #666;
  white-space: pre-wrap;
}
</style>
