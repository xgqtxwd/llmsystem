<template>
  <view class="login-container">
    <view class="login-header">
      <image class="logo" src="/static/logo.png" mode="aspectFit"></image>
      <text class="title">智能营养顾问</text>
      <text class="subtitle">您的AI营养健康管家</text>
    </view>

    <view class="login-form">
      <view class="form-tabs">
        <view 
          class="tab-item" 
          :class="{ active: isLogin }" 
          @click="isLogin = true"
        >登录</view>
        <view 
          class="tab-item" 
          :class="{ active: !isLogin }" 
          @click="isLogin = false"
        >注册</view>
      </view>

      <view class="form-group">
        <view class="input-wrapper">
          <text class="input-icon">👤</text>
          <input 
            class="input" 
            v-model="form.username" 
            placeholder="用户名/邮箱/手机号"
            placeholder-class="placeholder"
          />
        </view>
      </view>

      <view class="form-group">
        <view class="input-wrapper">
          <text class="input-icon">🔒</text>
          <input 
            class="input" 
            v-model="form.password" 
            type="password"
            placeholder="密码"
            placeholder-class="placeholder"
          />
        </view>
      </view>

      <view class="form-group" v-if="!isLogin">
        <view class="input-wrapper">
          <text class="input-icon">🔒</text>
          <input 
            class="input" 
            v-model="form.confirmPassword" 
            type="password"
            placeholder="确认密码"
            placeholder-class="placeholder"
          />
        </view>
      </view>

      <button 
        class="submit-btn" 
        :loading="loading" 
        @click="handleSubmit"
      >
        {{ isLogin ? '登录' : '注册' }}
      </button>

      <view class="tips" v-if="!isLogin">
        <text>注册即表示同意用户协议和隐私政策</text>
      </view>
    </view>
  </view>
</template>

<script>
import { authAPI } from '@/utils/api.js'

export default {
  data() {
    return {
      isLogin: true,
      form: {
        username: '',
        password: '',
        confirmPassword: ''
      },
      loading: false
    }
  },
  methods: {
    async handleSubmit() {
      if (!this.form.username || !this.form.password) {
        uni.showToast({ title: '请填写完整信息', icon: 'none' })
        return
      }
      if (!this.isLogin && this.form.password !== this.form.confirmPassword) {
        uni.showToast({ title: '两次密码不一致', icon: 'none' })
        return
      }

      this.loading = true
      try {
        if (this.isLogin) {
          await this.handleLogin()
        } else {
          await this.handleRegister()
        }
      } catch (error) {
        uni.showToast({ 
          title: error.message || '操作失败', 
          icon: 'none' 
        })
      } finally {
        this.loading = false
      }
    },
    async handleLogin() {
      const res = await authAPI.login({
        username: this.form.username,
        password: this.form.password
      })
      
      uni.setStorageSync('token', res.access_token)
      uni.setStorageSync('userInfo', JSON.stringify(res.user))
      if (res.user.is_admin) {
        uni.setStorageSync('is_admin', 'true')
      }
      
      uni.showToast({ title: '登录成功', icon: 'success' })
      setTimeout(() => {
        uni.switchTab({ url: '/pages/index/index' })
      }, 500)
    },
    async handleRegister() {
      const res = await authAPI.register({
        username: this.form.username,
        password: this.form.password
      })
      
      uni.setStorageSync('token', res.access_token)
      uni.setStorageSync('userInfo', JSON.stringify(res.user))
      
      uni.showToast({ title: '注册成功', icon: 'success' })
      setTimeout(() => {
        uni.switchTab({ url: '/pages/index/index' })
      }, 500)
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  padding: 60rpx 40rpx;
}

.login-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 80rpx;
  margin-bottom: 80rpx;
}

.logo {
  width: 120rpx;
  height: 120rpx;
  margin-bottom: 20rpx;
}

.title {
  font-size: 48rpx;
  font-weight: bold;
  color: #fff;
  margin-bottom: 10rpx;
}

.subtitle {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.8);
}

.login-form {
  background: #fff;
  border-radius: 24rpx;
  padding: 40rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.1);
}

.form-tabs {
  display: flex;
  margin-bottom: 40rpx;
  border-bottom: 2rpx solid #f0f0f0;
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 20rpx 0;
  font-size: 32rpx;
  color: #666;
  position: relative;
}

.tab-item.active {
  color: #10b981;
  font-weight: bold;
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: -2rpx;
  left: 50%;
  transform: translateX(-50%);
  width: 60rpx;
  height: 4rpx;
  background: #10b981;
  border-radius: 2rpx;
}

.form-group {
  margin-bottom: 30rpx;
}

.input-wrapper {
  display: flex;
  align-items: center;
  background: #f5f5f5;
  border-radius: 12rpx;
  padding: 0 20rpx;
  height: 88rpx;
}

.input-icon {
  font-size: 32rpx;
  margin-right: 16rpx;
}

.input {
  flex: 1;
  font-size: 28rpx;
  color: #333;
}

.placeholder {
  color: #999;
}

.submit-btn {
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: #fff;
  border: none;
  border-radius: 12rpx;
  font-size: 32rpx;
  font-weight: bold;
  margin-top: 40rpx;
}

.submit-btn::after {
  border: none;
}

.tips {
  text-align: center;
  margin-top: 20rpx;
  font-size: 24rpx;
  color: #999;
}
</style>
