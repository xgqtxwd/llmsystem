<template>
  <div class="login-container">
    <div class="login-hero">
      <div class="hero-pattern">
        <div class="pattern-circle pc1"></div>
        <div class="pattern-circle pc2"></div>
        <div class="pattern-circle pc3"></div>
      </div>
      <div class="hero-content">
        <div class="brand-icon">
          <van-icon name="flower-o" size="36" color="white" />
        </div>
        <h1>智能营养顾问</h1>
        <p>AI驱动的个性化营养健康管家</p>
      </div>
    </div>

    <div class="login-body">
      <div class="form-header">
        <h2>欢迎回来</h2>
        <p>登录您的账号，开始健康之旅</p>
      </div>

      <div class="login-form">
        <div class="input-group">
          <div class="input-icon">
            <van-icon name="contact" size="18" color="#94a3b8" />
          </div>
          <input
            v-model="loginForm.username"
            type="text"
            placeholder="用户名 / 邮箱 / 手机号"
            class="form-input"
          />
        </div>

        <div class="input-group">
          <div class="input-icon">
            <van-icon name="lock" size="18" color="#94a3b8" />
          </div>
          <input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            class="form-input"
            @keyup.enter="onLogin"
          />
        </div>

        <button
          class="submit-btn"
          :class="{ loading: loading }"
          :disabled="loading"
          @click="onLogin"
        >
          <span v-if="!loading">登 录</span>
          <van-loading v-else size="20" color="#fff" />
        </button>
      </div>

      <div class="login-footer">
        <div class="divider-line">
          <span>或</span>
        </div>
        <button class="register-link" @click="$router.push('/register')">
          创建新账号
          <van-icon name="arrow" size="12" style="transform: rotate(-90deg)" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { showToast } from 'vant'

const router = useRouter()
const authStore = useAuthStore()

const loginForm = ref({
  username: '',
  password: ''
})

const loading = ref(false)

async function onLogin() {
  if (!loginForm.value.username || !loginForm.value.password) {
    showToast('请填写完整信息')
    return
  }

  loading.value = true
  try {
    const credentials = {}
    if (loginForm.value.username.includes('@')) {
      credentials.email = loginForm.value.username
    } else if (/^\d+$/.test(loginForm.value.username)) {
      credentials.phone = loginForm.value.username
    } else {
      credentials.username = loginForm.value.username
    }
    credentials.password = loginForm.value.password

    await authStore.login(credentials)
    showToast({ message: '登录成功', icon: 'success' })
    router.push('/home')
  } catch (error) {
    showToast(error.response?.data?.detail || '登录失败，请检查账号密码')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background-color: #f0fdf4;
  display: flex;
  flex-direction: column;
}

.login-hero {
  position: relative;
  background: var(--primary-gradient);
  padding: 60px 30px 50px;
  overflow: hidden;
}

.hero-pattern {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.pattern-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
}

.pc1 {
  width: 200px;
  height: 200px;
  top: -60px;
  right: -40px;
  animation: float 6s ease-in-out infinite;
}

.pc2 {
  width: 120px;
  height: 120px;
  bottom: -30px;
  left: -20px;
  animation: float 8s ease-in-out infinite reverse;
}

.pc3 {
  width: 70px;
  height: 70px;
  top: 50%;
  left: 30%;
  animation: float 7s ease-in-out infinite 1.5s;
}

.hero-content {
  position: relative;
  text-align: center;
  color: white;
}

.brand-icon {
  width: 68px;
  height: 68px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  border: 2px solid rgba(255, 255, 255, 0.25);
}

.hero-content h1 {
  margin: 0 0 8px;
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 1px;
}

.hero-content p {
  margin: 0;
  font-size: 14px;
  opacity: 0.85;
}

.login-body {
  flex: 1;
  padding: 28px 24px;
  margin-top: -20px;
  position: relative;
  z-index: 1;
}

.form-header {
  text-align: center;
  margin-bottom: 28px;
}

.form-header h2 {
  margin: 0 0 6px;
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
}

.form-header p {
  margin: 0;
  font-size: 14px;
  color: var(--text-muted);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.input-group {
  display: flex;
  align-items: center;
  gap: 10px;
  background: white;
  border-radius: var(--radius-md);
  padding: 4px 16px;
  box-shadow: var(--shadow-sm);
  transition: var(--transition);
  border: 2px solid transparent;
}

.input-group:focus-within {
  border-color: #10b981;
  box-shadow: var(--shadow-md), 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.input-icon {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.form-input {
  flex: 1;
  border: none;
  outline: none;
  padding: 15px 0;
  font-size: 15px;
  color: var(--text-primary);
  background: transparent;
}

.form-input::placeholder {
  color: #c4cbd5;
}

.submit-btn {
  width: 100%;
  padding: 15px;
  border: none;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  font-size: 17px;
  font-weight: 600;
  cursor: pointer;
  letter-spacing: 2px;
  transition: var(--transition);
  margin-top: 6px;
  box-shadow: 0 4px 16px rgba(16, 185, 129, 0.35);
}

.submit-btn:active:not(:disabled) {
  transform: scale(0.98);
  opacity: 0.9;
}

.submit-btn.loading {
  opacity: 0.85;
  pointer-events: none;
}

.login-footer {
  margin-top: 32px;
  text-align: center;
}

.divider-line {
  position: relative;
  margin-bottom: 22px;
}

.divider-line::before,
.divider-line::after {
  content: '';
  position: absolute;
  top: 50%;
  width: calc(50% - 24px);
  height: 1px;
  background: #e2e8f0;
}

.divider-line::before { left: 0; }
.divider-line::after { right: 0; }

.divider-line span {
  position: relative;
  padding: 0 12px;
  font-size: 13px;
  color: var(--text-muted);
  background: #f0fdf4;
}

.register-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 10px 24px;
  border: none;
  border-radius: 25px;
  background: white;
  color: #10b981;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  box-shadow: var(--shadow-sm);
  transition: var(--transition);
}

.register-link:active {
  transform: scale(0.97);
  box-shadow: var(--shadow-md);
}
</style>
