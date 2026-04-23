<template>
  <div class="register-container">
    <div class="register-hero">
      <div class="hero-pattern">
        <div class="pattern-circle pc1"></div>
        <div class="pattern-circle pc2"></div>
        <div class="pattern-circle pc3"></div>
      </div>
      <div class="hero-content">
        <div class="brand-icon">
          <van-icon name="friends-o" size="36" color="white" />
        </div>
        <h1>创建账号</h1>
        <p>加入我们，开启智能营养之旅</p>
      </div>
    </div>

    <div class="register-body">
      <div class="form-header">
        <h2>填写信息</h2>
        <p>至少填写用户名、邮箱或手机号中的一种</p>
      </div>

      <div class="register-form">
        <div class="input-group">
          <div class="input-icon">
            <van-icon name="user-o" size="18" color="#94a3b8" />
          </div>
          <input
            v-model="registerForm.username"
            type="text"
            placeholder="用户名（可选）"
            class="form-input"
          />
        </div>

        <div class="input-group">
          <div class="input-icon">
            <van-icon name="envelop-o" size="18" color="#94a3b8" />
          </div>
          <input
            v-model="registerForm.email"
            type="email"
            placeholder="邮箱地址（可选）"
            class="form-input"
          />
        </div>

        <div class="input-group">
          <div class="input-icon">
            <van-icon name="phone-o" size="18" color="#94a3b8" />
          </div>
          <input
            v-model="registerForm.phone"
            type="tel"
            placeholder="手机号（可选）"
            class="form-input"
          />
        </div>

        <div class="input-group">
          <div class="input-icon">
            <van-icon name="lock" size="18" color="#94a3b8" />
          </div>
          <input
            v-model="registerForm.password"
            type="password"
            placeholder="设置密码（至少6位）"
            class="form-input"
          />
        </div>

        <div class="input-group">
          <div class="input-icon">
            <van-icon name="shield-o" size="18" color="#94a3b8" />
          </div>
          <input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="确认密码"
            class="form-input"
            @keyup.enter="onRegister"
          />
        </div>

        <button
          class="submit-btn"
          :class="{ loading: loading }"
          :disabled="loading"
          @click="onRegister"
        >
          <span v-if="!loading">注 册</span>
          <van-loading v-else size="20" color="#fff" />
        </button>
      </div>

      <div class="register-footer">
        <div class="divider-line">
          <span>已有账号？</span>
        </div>
        <button class="login-link" @click="$router.push('/login')">
          立即登录
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

const registerForm = ref({
  username: '',
  email: '',
  phone: '',
  password: '',
  confirmPassword: ''
})

const loading = ref(false)

async function onRegister() {
  if (!registerForm.value.username && !registerForm.value.email && !registerForm.value.phone) {
    showToast('请至少填写一种联系方式')
    return
  }

  if (!registerForm.value.password || registerForm.value.password.length < 6) {
    showToast('密码至少需要6位')
    return
  }

  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    showToast('两次输入的密码不一致')
    return
  }

  loading.value = true
  try {
    const userData = {}
    if (registerForm.value.username) userData.username = registerForm.value.username
    if (registerForm.value.email) userData.email = registerForm.value.email
    if (registerForm.value.phone) userData.phone = registerForm.value.phone
    userData.password = registerForm.value.password

    await authStore.register(userData)
    showToast({ message: '注册成功', icon: 'success' })
    router.push('/home')
  } catch (error) {
    showToast(error.response?.data?.detail || '注册失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  background-color: #f0fdf4;
  display: flex;
  flex-direction: column;
}

.register-hero {
  position: relative;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #7c3aed 100%);
  padding: 50px 30px 45px;
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
  width: 180px;
  height: 180px;
  top: -50px;
  right: -30px;
  animation: float 6s ease-in-out infinite;
}

.pc2 {
  width: 110px;
  height: 110px;
  bottom: -25px;
  left: -15px;
  animation: float 8s ease-in-out infinite reverse;
}

.pc3 {
  width: 65px;
  height: 65px;
  top: 45%;
  left: 25%;
  animation: float 7s ease-in-out infinite 1.5s;
}

.hero-content {
  position: relative;
  text-align: center;
  color: white;
}

.brand-icon {
  width: 64px;
  height: 64px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 14px;
  border: 2px solid rgba(255, 255, 255, 0.25);
}

.hero-content h1 {
  margin: 0 0 6px;
  font-size: 23px;
  font-weight: 700;
  letter-spacing: 1px;
}

.hero-content p {
  margin: 0;
  font-size: 14px;
  opacity: 0.85;
}

.register-body {
  flex: 1;
  padding: 26px 24px;
  margin-top: -20px;
  position: relative;
  z-index: 1;
}

.form-header {
  text-align: center;
  margin-bottom: 22px;
}

.form-header h2 {
  margin: 0 0 6px;
  font-size: 21px;
  font-weight: 700;
  color: var(--text-primary);
}

.form-header p {
  margin: 0;
  font-size: 13px;
  color: var(--text-muted);
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
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
  border-color: #6366f1;
  box-shadow: var(--shadow-md), 0 0 0 3px rgba(99, 102, 241, 0.1);
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
  padding: 13px 0;
  font-size: 15px;
  color: var(--text-primary);
  background: transparent;
}

.form-input::placeholder {
  color: #c4cbd5;
}

.submit-btn {
  width: 100%;
  padding: 14px;
  border: none;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  font-size: 17px;
  font-weight: 600;
  cursor: pointer;
  letter-spacing: 2px;
  transition: var(--transition);
  margin-top: 4px;
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.35);
}

.submit-btn:active:not(:disabled) {
  transform: scale(0.98);
  opacity: 0.9;
}

.submit-btn.loading {
  opacity: 0.85;
  pointer-events: none;
}

.register-footer {
  margin-top: 28px;
  text-align: center;
}

.divider-line {
  position: relative;
  margin-bottom: 20px;
}

.divider-line::before,
.divider-line::after {
  content: '';
  position: absolute;
  top: 50%;
  width: calc(50% - 40px);
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

.login-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 10px 24px;
  border: none;
  border-radius: 25px;
  background: white;
  color: #6366f1;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  box-shadow: var(--shadow-sm);
  transition: var(--transition);
}

.login-link:active {
  transform: scale(0.97);
  box-shadow: var(--shadow-md);
}
</style>
