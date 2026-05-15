<template>
  <view class="health-goals-container">
    <view class="progress-summary" v-if="progressSummary">
      <view class="summary-header">
        <text class="summary-title">目标进度</text>
      </view>
      <view class="summary-content">
        <view class="summary-item">
          <text class="summary-label">当前体重</text>
          <text class="summary-value">{{ progressSummary.current_weight || '--' }} kg</text>
        </view>
        <view class="summary-item">
          <text class="summary-label">当前BMI</text>
          <text class="summary-value">{{ progressSummary.current_bmi || '--' }}</text>
        </view>
      </view>
    </view>

    <view class="goals-section">
      <view class="section-header">
        <text class="section-title">我的目标</text>
        <text class="add-btn" @click="showAddGoal">+ 添加目标</text>
      </view>

      <view class="goal-list">
        <view class="goal-item" v-for="goal in goals" :key="goal.id">
          <view class="goal-header">
            <text class="goal-type">{{ getGoalTypeLabel(goal.goal_type) }}</text>
            <view class="goal-actions">
              <text class="edit-btn" @click="editGoal(goal)">✏️</text>
              <text class="delete-btn" @click="deleteGoal(goal.id)">🗑️</text>
            </view>
          </view>
          <view class="goal-details">
            <view class="detail-row" v-if="goal.target_weight">
              <text class="detail-label">目标体重：</text>
              <text class="detail-value">{{ goal.target_weight }} kg</text>
            </view>
            <view class="detail-row" v-if="goal.daily_calorie_target">
              <text class="detail-label">每日卡路里：</text>
              <text class="detail-value">{{ goal.daily_calorie_target }} kcal</text>
            </view>
            <view class="progress-bar" v-if="progressSummary && goal.goal_type === 'weight_loss' && goal.target_weight">
              <view class="progress-fill" :style="{ width: getProgressPercentage(goal) + '%' }"></view>
            </view>
            <text class="progress-text" v-if="progressSummary && goal.goal_type === 'weight_loss' && goal.target_weight">
              进度：{{ getProgressPercentage(goal) }}%
            </text>
          </view>
        </view>

        <view class="empty-state" v-if="goals.length === 0">
          <text class="empty-icon">🎯</text>
          <text class="empty-text">暂无健康目标</text>
        </view>
      </view>
    </view>

    <view class="goal-modal" v-if="showModal" @click="closeModal">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">{{ editingGoal ? '编辑目标' : '添加目标' }}</text>
          <text class="modal-close" @click="closeModal">✕</text>
        </view>
        <view class="modal-body">
          <view class="form-item">
            <text class="label">目标类型</text>
            <picker :value="goalTypeIndex" :range="goalTypes" @change="onGoalTypeChange">
              <view class="picker">{{ goalForm.goal_type || '请选择目标类型' }}</view>
            </picker>
          </view>
          <view class="form-item">
            <text class="label">目标体重 (kg)</text>
            <input class="input" type="digit" v-model="goalForm.target_weight" placeholder="请输入目标体重" />
          </view>
          <view class="form-item">
            <text class="label">每日卡路里目标</text>
            <input class="input" type="number" v-model="goalForm.daily_calorie_target" placeholder="请输入每日卡路里目标" />
          </view>
          <button class="submit-btn" @click="submitGoal" :loading="loading">
            {{ editingGoal ? '保存' : '添加' }}
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { healthGoalsAPI } from '@/utils/api.js'

export default {
  data() {
    return {
      goals: [],
      progressSummary: null,
      showModal: false,
      editingGoal: null,
      goalForm: {
        goal_type: '',
        target_weight: '',
        daily_calorie_target: ''
      },
      goalTypes: ['weight_loss', 'muscle_gain', 'blood_sugar_control', 'health_maintenance'],
      goalTypeLabels: {
        'weight_loss': '减重',
        'muscle_gain': '增肌',
        'blood_sugar_control': '控糖',
        'health_maintenance': '健康维持'
      },
      goalTypeIndex: 0,
      loading: false
    }
  },
  onShow() {
    this.loadGoals()
    this.loadProgress()
  },
  methods: {
    async loadGoals() {
      try {
        this.goals = await healthGoalsAPI.list()
      } catch (e) {
        console.error('加载目标失败', e)
      }
    },
    async loadProgress() {
      try {
        this.progressSummary = await healthGoalsAPI.getProgress()
      } catch (e) {
        console.error('加载进度失败', e)
      }
    },
    getGoalTypeLabel(type) {
      return this.goalTypeLabels[type] || type
    },
    getProgressPercentage(goal) {
      if (!this.progressSummary || !goal.target_weight || !this.progressSummary.current_weight) {
        return 0
      }
      const current = this.progressSummary.current_weight
      const target = goal.target_weight
      const start = current > target ? current : current * 1.1
      const progress = ((start - current) / (start - target)) * 100
      return Math.min(Math.max(Math.round(progress), 0), 100)
    },
    showAddGoal() {
      this.editingGoal = null
      this.goalForm = {
        goal_type: '',
        target_weight: '',
        daily_calorie_target: ''
      }
      this.goalTypeIndex = 0
      this.showModal = true
    },
    editGoal(goal) {
      this.editingGoal = goal
      this.goalForm = {
        goal_type: goal.goal_type,
        target_weight: goal.target_weight || '',
        daily_calorie_target: goal.daily_calorie_target || ''
      }
      this.goalTypeIndex = this.goalTypes.indexOf(goal.goal_type)
      this.showModal = true
    },
    closeModal() {
      this.showModal = false
    },
    onGoalTypeChange(e) {
      this.goalTypeIndex = e.detail.value
      this.goalForm.goal_type = this.goalTypes[this.goalTypeIndex]
    },
    async submitGoal() {
      if (!this.goalForm.goal_type) {
        uni.showToast({ title: '请选择目标类型', icon: 'none' })
        return
      }

      this.loading = true
      try {
        if (this.editingGoal) {
          await healthGoalsAPI.update(this.editingGoal.id, this.goalForm)
          uni.showToast({ title: '更新成功', icon: 'success' })
        } else {
          await healthGoalsAPI.create(this.goalForm)
          uni.showToast({ title: '添加成功', icon: 'success' })
        }
        this.closeModal()
        this.loadGoals()
        this.loadProgress()
      } catch (error) {
        uni.showToast({ title: '操作失败', icon: 'none' })
      } finally {
        this.loading = false
      }
    },
    deleteGoal(id) {
      uni.showModal({
        title: '确认删除',
        content: '确定要删除这个目标吗？',
        success: async (res) => {
          if (res.confirm) {
            try {
              await healthGoalsAPI.delete(id)
              uni.showToast({ title: '删除成功', icon: 'success' })
              this.loadGoals()
              this.loadProgress()
            } catch (error) {
              uni.showToast({ title: '删除失败', icon: 'none' })
            }
          }
        }
      })
    }
  }
}
</script>

<style scoped>
.health-goals-container {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 30rpx;
}

.progress-summary {
  background: linear-gradient(135deg, #10b981, #059669);
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  color: #fff;
}

.summary-header {
  margin-bottom: 20rpx;
}

.summary-title {
  font-size: 32rpx;
  font-weight: bold;
}

.summary-content {
  display: flex;
  gap: 40rpx;
}

.summary-item {
  flex: 1;
}

.summary-label {
  font-size: 24rpx;
  opacity: 0.8;
  display: block;
  margin-bottom: 10rpx;
}

.summary-value {
  font-size: 36rpx;
  font-weight: bold;
  display: block;
}

.goals-section {
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.add-btn {
  font-size: 28rpx;
  color: #10b981;
}

.goal-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.goal-item {
  background: #f9f9f9;
  border-radius: 16rpx;
  padding: 24rpx;
}

.goal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.goal-type {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
}

.goal-actions {
  display: flex;
  gap: 20rpx;
}

.edit-btn, .delete-btn {
  font-size: 32rpx;
}

.goal-details {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.detail-row {
  display: flex;
  font-size: 26rpx;
}

.detail-label {
  color: #666;
  width: 180rpx;
}

.detail-value {
  color: #333;
  flex: 1;
}

.progress-bar {
  height: 16rpx;
  background: #e5e7eb;
  border-radius: 8rpx;
  overflow: hidden;
  margin-top: 10rpx;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(135deg, #10b981, #059669);
  border-radius: 8rpx;
}

.progress-text {
  font-size: 24rpx;
  color: #666;
  margin-top: 8rpx;
  text-align: right;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80rpx 0;
}

.empty-icon {
  font-size: 100rpx;
  margin-bottom: 20rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #999;
}

.goal-modal {
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
  padding: 30rpx;
}

.form-item {
  margin-bottom: 30rpx;
}

.label {
  font-size: 28rpx;
  color: #333;
  font-weight: bold;
  margin-bottom: 16rpx;
  display: block;
}

.input {
  height: 80rpx;
  background: #f5f5f5;
  border-radius: 12rpx;
  padding: 0 20rpx;
  font-size: 28rpx;
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
</style>
