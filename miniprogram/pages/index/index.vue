<template>
  <view class="index-container">
    <view class="hero-section">
      <view class="hero-content">
        <view class="greeting">
          <text class="greeting-time">{{ greetingText }}</text>
          <text class="username">{{ user ? (user.username || user.email || user.phone) : '用户' }}</text>
          <text class="greeting-sub">您的智能营养健康管家</text>
        </view>
      </view>
    </view>

    <view class="content">
      <view class="stats-row" v-if="healthProfile">
        <view class="stat-card">
          <view class="stat-icon bmi-icon">📊</view>
          <view class="stat-info">
            <text class="stat-value">{{ healthProfile.bmi || '--' }}</text>
            <text class="stat-label">BMI指数</text>
          </view>
        </view>
        <view class="stat-card">
          <view class="stat-icon weight-icon">⚖️</view>
          <view class="stat-info">
            <text class="stat-value">{{ healthProfile.weight || '--' }}<text class="unit">kg</text></text>
            <text class="stat-label">体重</text>
          </view>
        </view>
        <view class="stat-card">
          <view class="stat-icon height-icon">📏</view>
          <view class="stat-info">
            <text class="stat-value">{{ healthProfile.height || '--' }}<text class="unit">cm</text></text>
            <text class="stat-label">身高</text>
          </view>
        </view>
      </view>

      <view class="section-header">
        <text class="section-title">功能服务</text>
        <text class="section-more" @click="goToProfile">更多</text>
      </view>

      <view class="feature-grid">
        <view class="feature-card" @click="goTo('/pages/chat/chat')">
          <view class="feature-icon chat-icon">💬</view>
          <text class="feature-name">营养咨询</text>
          <text class="feature-desc">AI智能问答</text>
        </view>
        <view class="feature-card" @click="goTo('/pages/recipes/recipes')">
          <view class="feature-icon recipe-icon">🍲</view>
          <text class="feature-name">食谱推荐</text>
          <text class="feature-desc">个性化定制</text>
        </view>
        <view class="feature-card" @click="goTo('/pages/health-profile/health-profile')">
          <view class="feature-icon health-icon">🏥</view>
          <text class="feature-name">健康档案</text>
          <text class="feature-desc">数据追踪</text>
        </view>
        <view class="feature-card" @click="goTo('/pages/diet-preferences/diet-preferences')">
          <view class="feature-icon diet-icon">🥗</view>
          <text class="feature-name">饮食偏好</text>
          <text class="feature-desc">个性设置</text>
        </view>
        <view class="feature-card" @click="goTo('/pages/health-goals/health-goals')">
          <view class="feature-icon goal-icon">🎯</view>
          <text class="feature-name">健康目标</text>
          <text class="feature-desc">目标管理</text>
        </view>
        <view class="feature-card" @click="goTo('/pages/knowledge/knowledge')">
          <view class="feature-icon knowledge-icon">📚</view>
          <text class="feature-name">营养知识</text>
          <text class="feature-desc">科普学习</text>
        </view>
      </view>

      <view class="daily-tip">
        <view class="tip-header">
          <text class="tip-icon">💡</text>
          <text class="tip-title">今日小贴士</text>
        </view>
        <text class="tip-content">{{ dailyTip }}</text>
      </view>
    </view>
  </view>
</template>

<script>
import { healthProfileAPI } from '@/utils/api.js'

export default {
  data() {
    return {
      user: null,
      healthProfile: null,
      dailyTips: [
        '每天饮水建议1500-2000ml，保持身体水分平衡',
        '早餐是一天中最重要的一餐，建议包含蛋白质和膳食纤维',
        '每餐蔬菜应占餐盘的一半以上，有助于增加饱腹感',
        '减少精制糖的摄入，选择天然水果作为甜味来源',
        '适量摄入优质蛋白，如鱼类、豆类、鸡蛋等',
        '细嚼慢咽有助于消化吸收，每口食物咀嚼15-20次',
        '睡前2小时避免大量进食，保证睡眠质量'
      ]
    }
  },
  computed: {
    dailyTip() {
      return this.dailyTips[new Date().getDate() % this.dailyTips.length]
    },
    greetingText() {
      const hour = new Date().getHours()
      if (hour < 6) return '夜深了'
      if (hour < 9) return '早上好'
      if (hour < 12) return '上午好'
      if (hour < 14) return '中午好'
      if (hour < 18) return '下午好'
      if (hour < 22) return '晚上好'
      return '夜深了'
    }
  },
  onShow() {
    const token = uni.getStorageSync('token')
    if (!token) {
      uni.reLaunch({ url: '/pages/login/login' })
      return
    }
    this.user = this.getUserInfo()
    this.loadHealthProfile()
  },
  methods: {
    getUserInfo() {
      try {
        const user = uni.getStorageSync('userInfo')
        return user ? JSON.parse(user) : null
      } catch (e) {
        return null
      }
    },
    async loadHealthProfile() {
      try {
        this.healthProfile = await healthProfileAPI.get()
      } catch (e) {
        console.log('暂无健康档案')
      }
    },
    goTo(url) {
      uni.navigateTo({ url })
    },
    goToProfile() {
      uni.switchTab({ url: '/pages/profile/profile' })
    }
  }
}
</script>

<style scoped>
.index-container {
  min-height: 100vh;
  background: #f0fdf4;
  padding-bottom: 120rpx;
}

.hero-section {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  padding: 40rpx 30rpx 80rpx;
  position: relative;
  overflow: hidden;
}

.hero-content {
  position: relative;
  z-index: 1;
}

.greeting {
  padding-top: 20rpx;
}

.greeting-time {
  display: block;
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.85);
  letter-spacing: 2rpx;
}

.username {
  display: block;
  margin: 16rpx 0 8rpx;
  font-size: 48rpx;
  font-weight: bold;
  color: #fff;
}

.greeting-sub {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.75);
}

.content {
  padding: 0 30rpx;
  margin-top: -40rpx;
  position: relative;
  z-index: 1;
}

.stats-row {
  display: flex;
  gap: 20rpx;
  margin-bottom: 40rpx;
}

.stat-card {
  flex: 1;
  background: #fff;
  border-radius: 20rpx;
  padding: 24rpx;
  display: flex;
  align-items: center;
  gap: 16rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 70rpx;
  height: 70rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
  flex-shrink: 0;
}

.bmi-icon { background: linear-gradient(135deg, #6366f1, #8b5cf6); }
.weight-icon { background: linear-gradient(135deg, #10b981, #059669); }
.height-icon { background: linear-gradient(135deg, #f59e0b, #d97706); }

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.stat-value .unit {
  font-size: 20rpx;
  font-weight: normal;
  color: #666;
  margin-left: 4rpx;
}

.stat-label {
  font-size: 22rpx;
  color: #999;
  margin-top: 4rpx;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
  padding: 0 4rpx;
}

.section-title {
  font-size: 34rpx;
  font-weight: bold;
  color: #333;
}

.section-more {
  font-size: 26rpx;
  color: #10b981;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20rpx;
  margin-bottom: 40rpx;
}

.feature-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx 20rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.feature-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40rpx;
}

.chat-icon { background: linear-gradient(135deg, #06b6d4, #0891b2); }
.recipe-icon { background: linear-gradient(135deg, #f97316, #ea580c); }
.health-icon { background: linear-gradient(135deg, #ec4899, #db2777); }
.diet-icon { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }
.goal-icon { background: linear-gradient(135deg, #eab308, #ca8a04); }
.knowledge-icon { background: linear-gradient(135deg, #14b8a6, #0d9488); }

.feature-name {
  font-size: 26rpx;
  font-weight: bold;
  color: #333;
}

.feature-desc {
  font-size: 22rpx;
  color: #999;
}

.daily-tip {
  background: linear-gradient(135deg, #fefce8, #fef3c7);
  border-radius: 20rpx;
  padding: 30rpx;
  border-left: 8rpx solid #f59e0b;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.tip-header {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 16rpx;
}

.tip-icon {
  font-size: 36rpx;
}

.tip-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #92400e;
}

.tip-content {
  font-size: 26rpx;
  line-height: 1.8;
  color: #78350f;
}
</style>
