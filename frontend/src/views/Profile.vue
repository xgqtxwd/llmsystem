<template>
  <div class="profile-container">
    <van-nav-bar title="个人中心" left-arrow @click-left="$router.back()" />

    <div class="profile-content">
      <div class="profile-header-card">
        <div class="header-bg">
          <div class="header-circle c1"></div>
          <div class="header-circle c2"></div>
        </div>
        <div class="profile-main">
          <div class="avatar-wrapper">
            <div class="avatar-ring">
              <van-icon name="user-circle-o" size="52" color="#10b981" />
            </div>
            <div class="avatar-badge">
              <van-icon name="edit" size="8" color="white" />
            </div>
          </div>
          <div class="user-detail">
            <h2>{{ user?.username || user?.email || user?.phone || '用户' }}</h2>
            <p>{{ user?.email || user?.phone || '暂无联系方式' }}</p>
          </div>
        </div>
      </div>

      <div class="menu-section">
        <h4 class="section-label">健康管理</h4>
        <div class="menu-group">
          <div class="menu-item" @click="$router.push('/health-profile')">
            <div class="menu-icon icon-health">
              <van-icon name="medical-o" size="20" />
            </div>
            <div class="menu-info">
              <span class="menu-name">健康档案</span>
              <span class="menu-desc">查看您的健康数据</span>
            </div>
            <van-icon name="arrow" size="14" color="#c4cbd5" />
          </div>
          <div class="menu-item" @click="$router.push('/diet-preferences')">
            <div class="menu-icon icon-diet">
              <van-icon name="setting-o" size="20" />
            </div>
            <div class="menu-info">
              <span class="menu-name">饮食偏好</span>
              <span class="menu-desc">定制您的饮食方案</span>
            </div>
            <van-icon name="arrow" size="14" color="#c4cbd5" />
          </div>
          <div class="menu-item" @click="$router.push('/health-goals')">
            <div class="menu-icon icon-goal">
              <van-icon name="flag-o" size="20" />
            </div>
            <div class="menu-info">
              <span class="menu-name">健康目标</span>
              <span class="menu-desc">追踪您的目标进度</span>
            </div>
            <van-icon name="arrow" size="14" color="#c4cbd5" />
          </div>
        </div>
      </div>

      <div class="menu-section">
        <h4 class="section-label">更多服务</h4>
        <div class="menu-group">
          <div class="menu-item" @click="$router.push('/recipes')">
            <div class="menu-icon icon-recipe">
              <van-icon name="notes-o" size="20" />
            </div>
            <div class="menu-info">
              <span class="menu-name">我的食谱</span>
              <span class="menu-desc">AI智能推荐食谱</span>
            </div>
            <van-icon name="arrow" size="14" color="#c4cbd5" />
          </div>
          <div class="menu-item" @click="$router.push('/knowledge')">
            <div class="menu-icon icon-knowledge">
              <van-icon name="bulb-o" size="20" />
            </div>
            <div class="menu-info">
              <span class="menu-name">营养知识</span>
              <span class="menu-desc">学习专业营养知识</span>
            </div>
            <van-icon name="arrow" size="14" color="#c4cbd5" />
          </div>
          <div class="menu-item" @click="$router.push('/chat')">
            <div class="menu-icon icon-chat">
              <van-icon name="chat-o" size="20" />
            </div>
            <div class="menu-info">
              <span class="menu-name">对话历史</span>
              <span class="menu-desc">查看咨询记录</span>
            </div>
            <van-icon name="arrow" size="14" color="#c4cbd5" />
          </div>
        </div>
      </div>

      <button class="logout-btn" @click="handleLogout">
        <van-icon name="revoke" size="18" />
        <span>退出登录</span>
      </button>
    </div>

    <van-tabbar v-model="activeTab">
      <van-tabbar-item icon="home-o" to="/home">首页</van-tabbar-item>
      <van-tabbar-item icon="chat-o" to="/chat">咨询</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/profile">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { showToast, showConfirmDialog } from 'vant'

const router = useRouter()
const authStore = useAuthStore()
const user = ref(null)
const activeTab = ref(2)

onMounted(async () => {
  user.value = authStore.user || await authStore.fetchUser()
})

async function handleLogout() {
  try {
    await showConfirmDialog({
      title: '退出登录',
      message: '确定要退出当前账号吗？',
      confirmButtonText: '退出',
      cancelButtonText: '取消',
      confirmButtonColor: '#ef4444'
    })
    authStore.logout()
    showToast('已退出登录')
    router.push('/login')
  } catch (e) {}
}
</script>

<style scoped>
.profile-container {
  min-height: 100vh;
  background-color: #f0fdf4;
  padding-bottom: 60px;
}

.profile-content {
  padding: 0 16px;
}

.profile-header-card {
  position: relative;
  background: white;
  border-radius: var(--radius-xl);
  padding: 28px 20px 24px;
  margin-bottom: 24px;
  overflow: hidden;
  box-shadow: var(--shadow-md);
}

.header-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.header-circle {
  position: absolute;
  border-radius: 50%;
}

.c1 {
  width: 160px;
  height: 160px;
  background: linear-gradient(135deg, #d1fae5, #a7f3d0);
  top: -50px;
  right: -30px;
  opacity: 0.6;
}

.c2 {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #ccfbf1, #99f6e4);
  bottom: -20px;
  left: -15px;
  opacity: 0.5;
}

.profile-main {
  position: relative;
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar-wrapper {
  position: relative;
  flex-shrink: 0;
}

.avatar-ring {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ecfdf5, #d1fae5);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px rgba(16, 185, 129, 0.2);
}

.avatar-badge {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: linear-gradient(135deg, #10b981, #059669);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid white;
  box-shadow: var(--shadow-sm);
}

.user-detail h2 {
  margin: 0 0 4px;
  font-size: 19px;
  font-weight: 700;
  color: var(--text-primary);
}

.user-detail p {
  margin: 0;
  font-size: 13px;
  color: var(--text-muted);
}

.menu-section {
  margin-bottom: 22px;
}

.section-label {
  margin: 0 0 10px 2px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.menu-group {
  background: white;
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 16px 18px;
  gap: 14px;
  transition: var(--transition);
  cursor: pointer;
  border-bottom: 1px solid #f1f5f9;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-item:active {
  background: #f0fdf4;
}

.menu-icon {
  width: 42px;
  height: 42px;
  border-radius: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.icon-health { background: linear-gradient(135deg, #ec4899, #db2777); }
.icon-diet { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }
.icon-goal { background: linear-gradient(135deg, #eab308, #ca8a04); }
.icon-recipe { background: linear-gradient(135deg, #f97316, #ea580c); }
.icon-knowledge { background: linear-gradient(135deg, #14b8a6, #0d9488); }
.icon-chat { background: linear-gradient(135deg, #06b6d4, #0891b2); }

.menu-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.menu-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.menu-desc {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 2px;
}

.logout-btn {
  width: 100%;
  padding: 15px;
  border: none;
  border-radius: var(--radius-lg);
  background: linear-gradient(135deg, #fef2f2, #fee2e2);
  color: #dc2626;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: var(--transition);
  margin-top: 10px;
  box-shadow: var(--shadow-sm);
}

.logout-btn:active {
  transform: scale(0.98);
  background: linear-gradient(135deg, #fee2e2, #fecaca);
}
</style>
