<template>
  <view class="profile-container">
    <view class="profile-header">
      <view class="avatar-section">
        <view class="avatar-circle">
          <text class="avatar-text">{{ user ? (user.username || user.email || user.phone || 'U').charAt(0).toUpperCase() : 'U' }}</text>
        </view>
        <text class="username">{{ user ? (user.username || user.email || user.phone) : '用户' }}</text>
      </view>
    </view>

    <view class="menu-list">
      <view class="menu-section">
        <text class="section-title">健康管理</text>
        <view class="menu-item" @click="navigateTo('/pages/health-profile/health-profile')">
          <text class="menu-icon">📋</text>
          <text class="menu-text">健康档案</text>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @click="navigateTo('/pages/diet-preferences/diet-preferences')">
          <text class="menu-icon">🥗</text>
          <text class="menu-text">饮食偏好</text>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @click="navigateTo('/pages/health-goals/health-goals')">
          <text class="menu-icon">🎯</text>
          <text class="menu-text">健康目标</text>
          <text class="menu-arrow">›</text>
        </view>
      </view>

      <view class="menu-section">
        <text class="section-title">使用帮助</text>
        <view class="menu-item" @click="showAbout">
          <text class="menu-icon">ℹ️</text>
          <text class="menu-text">关于</text>
          <text class="menu-arrow">›</text>
        </view>
      </view>

      <view class="menu-section">
        <text class="section-title">账号</text>
        <view class="menu-item logout" @click="handleLogout">
          <text class="menu-icon">🚪</text>
          <text class="menu-text">退出登录</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { authAPI } from '@/utils/api.js'

export default {
  data() {
    return {
      user: null
    }
  },
  onShow() {
    this.user = this.getUserInfo()
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
    navigateTo(url) {
      uni.navigateTo({ url })
    },
    showAbout() {
      uni.showModal({
        title: '关于',
        content: '智能营养顾问小程序 v1.0.0\n基于AI大模型的个性化营养健康管理平台',
        showCancel: false
      })
    },
    handleLogout() {
      uni.showModal({
        title: '确认退出',
        content: '确定要退出登录吗？',
        success: async (res) => {
          if (res.confirm) {
            try {
              await authAPI.logout()
            } catch (e) {
              // Ignore logout errors
            }
            uni.removeStorageSync('token')
            uni.removeStorageSync('userInfo')
            uni.removeStorageSync('is_admin')
            uni.reLaunch({ url: '/pages/login/login' })
          }
        }
      })
    }
  }
}
</script>

<style scoped>
.profile-container {
  min-height: 100vh;
  background: #f5f5f5;
}

.profile-header {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  padding: 60rpx 30rpx 40rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.avatar-circle {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20rpx;
  border: 4rpx solid rgba(255, 255, 255, 0.5);
}

.avatar-text {
  font-size: 48rpx;
  font-weight: bold;
  color: #fff;
}

.username {
  font-size: 36rpx;
  color: #fff;
  font-weight: bold;
}

.menu-list {
  padding: 30rpx;
}

.menu-section {
  background: #fff;
  border-radius: 20rpx;
  margin-bottom: 30rpx;
  overflow: hidden;
}

.section-title {
  padding: 24rpx 30rpx 10rpx;
  font-size: 24rpx;
  color: #999;
  display: block;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-item.logout {
  color: #ff4444;
}

.menu-icon {
  font-size: 40rpx;
  margin-right: 20rpx;
}

.menu-text {
  flex: 1;
  font-size: 30rpx;
  color: #333;
}

.menu-arrow {
  font-size: 40rpx;
  color: #ccc;
}

.menu-item.logout .menu-text {
  color: #ff4444;
}
</style>
