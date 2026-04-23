<template>
  <div class="home-container">
    <div class="hero-section">
      <div class="hero-bg">
        <div class="hero-circle hero-circle-1"></div>
        <div class="hero-circle hero-circle-2"></div>
        <div class="hero-circle hero-circle-3"></div>
      </div>
      <div class="hero-content">
        <div class="greeting">
          <span class="greeting-time">{{ greetingText }}</span>
          <h1>{{ user ? (user.username || user.email || user.phone) : '用户' }}</h1>
          <p class="greeting-sub">您的智能营养健康管家</p>
        </div>
        <div class="hero-avatar" v-if="user">
          <div class="avatar-ring">
            <van-icon name="user-circle-o" size="48" color="white" />
          </div>
        </div>
      </div>
    </div>

    <div class="home-content">
      <div class="stats-row" v-if="healthProfile">
        <div class="stat-card animate-fadeInUp" style="animation-delay: 0.1s">
          <div class="stat-icon stat-icon-bmi">
            <van-icon name="bar-chart-o" size="22" />
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ healthProfile.bmi || '--' }}</span>
            <span class="stat-label">BMI指数</span>
          </div>
        </div>
        <div class="stat-card animate-fadeInUp" style="animation-delay: 0.2s">
          <div class="stat-icon stat-icon-weight">
            <van-icon name="gold-coin-o" size="22" />
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ healthProfile.weight || '--' }}<small>kg</small></span>
            <span class="stat-label">体重</span>
          </div>
        </div>
        <div class="stat-card animate-fadeInUp" style="animation-delay: 0.3s">
          <div class="stat-icon stat-icon-height">
            <van-icon name="guide-o" size="22" />
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ healthProfile.height || '--' }}<small>cm</small></span>
            <span class="stat-label">身高</span>
          </div>
        </div>
      </div>

      <div class="section-header animate-fadeInUp" style="animation-delay: 0.4s">
        <h3>功能服务</h3>
        <span class="section-more" @click="$router.push('/profile')">更多</span>
      </div>

      <div class="feature-grid animate-fadeInUp" style="animation-delay: 0.5s">
        <div class="feature-card" @click="$router.push('/chat')">
          <div class="feature-icon feature-icon-chat">
            <van-icon name="chat-o" size="26" />
          </div>
          <span class="feature-name">营养咨询</span>
          <span class="feature-desc">AI智能问答</span>
        </div>
        <div class="feature-card" @click="$router.push('/recipes')">
          <div class="feature-icon feature-icon-recipe">
            <van-icon name="notes-o" size="26" />
          </div>
          <span class="feature-name">食谱推荐</span>
          <span class="feature-desc">个性化定制</span>
        </div>
        <div class="feature-card" @click="$router.push('/health-profile')">
          <div class="feature-icon feature-icon-health">
            <van-icon name="shield-o" size="26" />
          </div>
          <span class="feature-name">健康档案</span>
          <span class="feature-desc">数据追踪</span>
        </div>
        <div class="feature-card" @click="$router.push('/diet-preferences')">
          <div class="feature-icon feature-icon-diet">
            <van-icon name="setting-o" size="26" />
          </div>
          <span class="feature-name">饮食偏好</span>
          <span class="feature-desc">个性设置</span>
        </div>
        <div class="feature-card" @click="$router.push('/health-goals')">
          <div class="feature-icon feature-icon-goal">
            <van-icon name="flag-o" size="26" />
          </div>
          <span class="feature-name">健康目标</span>
          <span class="feature-desc">目标管理</span>
        </div>
        <div class="feature-card" @click="$router.push('/knowledge')">
          <div class="feature-icon feature-icon-knowledge">
            <van-icon name="bulb-o" size="26" />
          </div>
          <span class="feature-name">营养知识</span>
          <span class="feature-desc">科普学习</span>
        </div>
        <div class="feature-card admin-card" v-if="isAdmin" @click="$router.push('/admin')">
          <div class="feature-icon feature-icon-admin">
            <van-icon name="manager-o" size="26" />
          </div>
          <span class="feature-name">管理后台</span>
          <span class="feature-desc">系统管理</span>
        </div>
      </div>

      <div class="daily-tip animate-fadeInUp" style="animation-delay: 0.6s">
        <div class="tip-header">
          <van-icon name="info-o" size="18" color="#f59e0b" />
          <span>今日小贴士</span>
        </div>
        <p class="tip-content">{{ dailyTip }}</p>
      </div>
    </div>

    <van-tabbar v-model="activeTab">
      <van-tabbar-item icon="home-o" to="/home">首页</van-tabbar-item>
      <van-tabbar-item icon="chat-o" to="/chat">咨询</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/profile">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { healthProfileAPI } from '@/api'

const authStore = useAuthStore()
const user = ref(null)
const healthProfile = ref(null)
const activeTab = ref(0)
const isAdmin = computed(() => localStorage.getItem('is_admin') === 'true')

const dailyTips = [
  '每天饮水建议1500-2000ml，保持身体水分平衡',
  '早餐是一天中最重要的一餐，建议包含蛋白质和膳食纤维',
  '每餐蔬菜应占餐盘的一半以上，有助于增加饱腹感',
  '减少精制糖的摄入，选择天然水果作为甜味来源',
  '适量摄入优质蛋白，如鱼类、豆类、鸡蛋等',
  '细嚼慢咽有助于消化吸收，每口食物咀嚼15-20次',
  '睡前2小时避免大量进食，保证睡眠质量'
]

const dailyTip = ref(dailyTips[new Date().getDate() % dailyTips.length])

const greetingText = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '夜深了'
  if (hour < 9) return '早上好'
  if (hour < 12) return '上午好'
  if (hour < 14) return '中午好'
  if (hour < 18) return '下午好'
  if (hour < 22) return '晚上好'
  return '夜深了'
})

onMounted(async () => {
  user.value = authStore.user || await authStore.fetchUser()
  try {
    healthProfile.value = await healthProfileAPI.get()
  } catch (e) {
    console.log('暂无健康档案')
  }
})
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background-color: #f0fdf4;
  padding-bottom: 60px;
}

.hero-section {
  position: relative;
  background: var(--primary-gradient);
  padding: 20px 20px 40px;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.hero-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.12;
}

.hero-circle-1 {
  width: 200px;
  height: 200px;
  background: white;
  top: -60px;
  right: -30px;
  animation: float 5s ease-in-out infinite;
}

.hero-circle-2 {
  width: 120px;
  height: 120px;
  background: white;
  bottom: -20px;
  left: -20px;
  animation: float 7s ease-in-out infinite reverse;
}

.hero-circle-3 {
  width: 80px;
  height: 80px;
  background: white;
  top: 50%;
  right: 20%;
  animation: float 6s ease-in-out infinite 1s;
}

.hero-content {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.greeting {
  padding-top: 10px;
}

.greeting-time {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.85);
  letter-spacing: 1px;
}

.greeting h1 {
  margin: 8px 0 4px;
  font-size: 24px;
  font-weight: 700;
  color: white;
  letter-spacing: 0.5px;
}

.greeting-sub {
  margin: 0;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.75);
}

.hero-avatar {
  margin-top: 5px;
}

.avatar-ring {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.35);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.home-content {
  padding: 0 16px;
  margin-top: -20px;
  position: relative;
  z-index: 1;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: var(--radius-md);
  padding: 14px 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: var(--shadow-md);
  transition: var(--transition);
}

.stat-card:active {
  transform: scale(0.97);
}

.stat-icon {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.stat-icon-bmi {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
}

.stat-icon-weight {
  background: linear-gradient(135deg, #10b981, #059669);
}

.stat-icon-height {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.stat-value small {
  font-size: 11px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-left: 1px;
}

.stat-label {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
  padding: 0 2px;
}

.section-header h3 {
  margin: 0;
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
}

.section-more {
  font-size: 13px;
  color: var(--primary);
  cursor: pointer;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.feature-card {
  background: white;
  border-radius: var(--radius-md);
  padding: 18px 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  box-shadow: var(--shadow-sm);
  transition: var(--transition);
  cursor: pointer;
}

.feature-card:active {
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
}

.feature-icon {
  width: 50px;
  height: 50px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  transition: var(--transition);
}

.feature-card:active .feature-icon {
  transform: scale(1.08);
}

.feature-icon-chat {
  background: linear-gradient(135deg, #06b6d4, #0891b2);
}

.feature-icon-recipe {
  background: linear-gradient(135deg, #f97316, #ea580c);
}

.feature-icon-health {
  background: linear-gradient(135deg, #ec4899, #db2777);
}

.feature-icon-diet {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
}

.feature-icon-goal {
  background: linear-gradient(135deg, #eab308, #ca8a04);
}

.feature-icon-knowledge {
  background: linear-gradient(135deg, #14b8a6, #0d9488);
}

.feature-icon-admin {
  background: linear-gradient(135deg, #64748b, #475569);
}

.feature-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.feature-desc {
  font-size: 11px;
  color: var(--text-muted);
}

.admin-card {
  border: 1px dashed #cbd5e1;
  background: #fafafa;
}

.daily-tip {
  background: linear-gradient(135deg, #fefce8, #fef3c7);
  border-radius: var(--radius-md);
  padding: 16px;
  border-left: 4px solid #f59e0b;
  box-shadow: var(--shadow-sm);
}

.tip-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #92400e;
}

.tip-content {
  margin: 0;
  font-size: 13px;
  line-height: 1.7;
  color: #78350f;
}
</style>
