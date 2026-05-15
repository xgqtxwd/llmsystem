<template>
  <view class="health-profile-container">
    <view class="info-section">
      <view class="form-item">
        <text class="label">年龄</text>
        <input class="input" type="number" v-model="form.age" placeholder="请输入年龄" />
      </view>

      <view class="form-item">
        <text class="label">性别</text>
        <picker :value="genderIndex" :range="genders" @change="onGenderChange">
          <view class="picker">{{ form.gender || '请选择性别' }}</view>
        </picker>
      </view>

      <view class="form-item">
        <text class="label">身高 (cm)</text>
        <input class="input" type="digit" v-model="form.height" placeholder="请输入身高" />
      </view>

      <view class="form-item">
        <text class="label">体重 (kg)</text>
        <input class="input" type="digit" v-model="form.weight" placeholder="请输入体重" />
      </view>

      <view class="form-item">
        <text class="label">活动水平</text>
        <picker :value="activityLevelIndex" :range="activityLevels" @change="onActivityLevelChange">
          <view class="picker">{{ form.activity_level || '请选择活动水平' }}</view>
        </picker>
      </view>

      <view class="form-item">
        <text class="label">健康状况</text>
        <textarea class="textarea" v-model="form.health_conditions" placeholder="请输入健康状况，如糖尿病、高血压等" placeholder-class="placeholder" />
      </view>

      <view class="bmi-card" v-if="form.height && form.weight">
        <text class="bmi-title">BMI 指数</text>
        <view class="bmi-value">{{ bmiValue }}</view>
        <text class="bmi-status">{{ bmiStatus }}</text>
      </view>
    </view>

    <view class="actions">
      <button class="submit-btn" @click="handleSubmit" :loading="loading">保存</button>
      <button class="delete-btn" @click="handleDelete" :loading="loading" v-if="hasProfile">删除档案</button>
    </view>
  </view>
</template>

<script>
import { healthProfileAPI } from '@/utils/api.js'

export default {
  data() {
    return {
      form: {
        age: '',
        gender: '',
        height: '',
        weight: '',
        activity_level: '',
        health_conditions: ''
      },
      genders: ['男', '女'],
      genderIndex: 0,
      activityLevels: ['久坐', '轻度活动', '中度活动', '重度活动'],
      activityLevelIndex: 0,
      loading: false,
      hasProfile: false
    }
  },
  computed: {
    bmiValue() {
      const height = parseFloat(this.form.height) / 100
      const weight = parseFloat(this.form.weight)
      if (height > 0 && weight > 0) {
        return (weight / (height * height)).toFixed(1)
      }
      return '--'
    },
    bmiStatus() {
      const bmi = parseFloat(this.bmiValue)
      if (isNaN(bmi)) return ''
      if (bmi < 18.5) return '偏瘦'
      if (bmi < 25) return '正常'
      if (bmi < 30) return '偏胖'
      return '肥胖'
    }
  },
  onShow() {
    this.loadProfile()
  },
  methods: {
    async loadProfile() {
      try {
        const profile = await healthProfileAPI.get()
        this.form = {
          age: profile.age || '',
          gender: profile.gender || '',
          height: profile.height || '',
          weight: profile.weight || '',
          activity_level: profile.activity_level || '',
          health_conditions: profile.health_conditions || ''
        }
        this.hasProfile = true
        if (this.form.gender) {
          this.genderIndex = this.genders.indexOf(this.form.gender)
        }
        if (this.form.activity_level) {
          this.activityLevelIndex = this.activityLevels.indexOf(this.form.activity_level)
        }
      } catch (e) {
        console.log('暂无健康档案')
      }
    },
    onGenderChange(e) {
      this.genderIndex = e.detail.value
      this.form.gender = this.genders[this.genderIndex]
    },
    onActivityLevelChange(e) {
      this.activityLevelIndex = e.detail.value
      this.form.activity_level = this.activityLevels[this.activityLevelIndex]
    },
    async handleSubmit() {
      if (!this.form.height || !this.form.weight) {
        uni.showToast({ title: '请填写身高和体重', icon: 'none' })
        return
      }

      this.loading = true
      try {
        if (this.hasProfile) {
          await healthProfileAPI.update(this.form)
          uni.showToast({ title: '更新成功', icon: 'success' })
        } else {
          await healthProfileAPI.create(this.form)
          this.hasProfile = true
          uni.showToast({ title: '创建成功', icon: 'success' })
        }
      } catch (error) {
        uni.showToast({ title: '保存失败', icon: 'none' })
      } finally {
        this.loading = false
      }
    },
    handleDelete() {
      uni.showModal({
        title: '确认删除',
        content: '确定要删除健康档案吗？',
        success: async (res) => {
          if (res.confirm) {
            try {
              await healthProfileAPI.delete()
              this.form = {
                age: '',
                gender: '',
                height: '',
                weight: '',
                activity_level: '',
                health_conditions: ''
              }
              this.hasProfile = false
              uni.showToast({ title: '删除成功', icon: 'success' })
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
.health-profile-container {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 30rpx;
  padding-bottom: 200rpx;
}

.info-section {
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
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

.textarea {
  height: 160rpx;
  background: #f5f5f5;
  border-radius: 12rpx;
  padding: 20rpx;
  font-size: 28rpx;
  width: 100%;
}

.placeholder {
  color: #999;
}

.bmi-card {
  background: linear-gradient(135deg, #f0fdf4, #dcfce7);
  border-radius: 20rpx;
  padding: 30rpx;
  text-align: center;
  margin-top: 20rpx;
}

.bmi-title {
  font-size: 28rpx;
  color: #666;
  display: block;
  margin-bottom: 10rpx;
}

.bmi-value {
  font-size: 72rpx;
  font-weight: bold;
  color: #10b981;
  display: block;
  margin-bottom: 10rpx;
}

.bmi-status {
  font-size: 28rpx;
  color: #059669;
  display: block;
}

.actions {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 30rpx;
  background: #fff;
  box-shadow: 0 -4rpx 12rpx rgba(0, 0, 0, 0.05);
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
  margin-bottom: 20rpx;
}

.submit-btn::after {
  border: none;
}

.delete-btn {
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  background: #ff4444;
  color: #fff;
  border: none;
  border-radius: 12rpx;
  font-size: 32rpx;
}

.delete-btn::after {
  border: none;
}
</style>
