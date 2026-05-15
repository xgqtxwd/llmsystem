<template>
  <view class="diet-preferences-container">
    <view class="info-section">
      <view class="form-item">
        <text class="label">口味偏好</text>
        <picker :value="tasteIndex" :range="tasteOptions" @change="onTasteChange">
          <view class="picker">{{ form.taste_preference || '请选择口味偏好' }}</view>
        </picker>
      </view>

      <view class="form-item">
        <text class="label">饮食类型</text>
        <picker :value="dietTypeIndex" :range="dietTypes" @change="onDietTypeChange">
          <view class="picker">{{ form.diet_type || '请选择饮食类型' }}</view>
        </picker>
      </view>

      <view class="form-item">
        <text class="label">过敏食物</text>
        <view class="tag-list">
          <view class="tag-item" v-for="(allergy, index) in allergies" :key="index">
            <text class="tag-text">{{ allergy }}</text>
            <text class="tag-remove" @click="removeAllergy(index)">✕</text>
          </view>
          <view class="add-tag" @click="showAddAllergy">
            <text class="add-text">+ 添加</text>
          </view>
        </view>
      </view>

      <view class="form-item">
        <text class="label">禁忌食物</text>
        <view class="tag-list">
          <view class="tag-item" v-for="(food, index) in forbiddenFoods" :key="index">
            <text class="tag-text">{{ food }}</text>
            <text class="tag-remove" @click="removeForbiddenFood(index)">✕</text>
          </view>
          <view class="add-tag" @click="showAddForbiddenFood">
            <text class="add-text">+ 添加</text>
          </view>
        </view>
      </view>
    </view>

    <view class="actions">
      <button class="submit-btn" @click="handleSubmit" :loading="loading">保存</button>
      <button class="delete-btn" @click="handleDelete" :loading="loading" v-if="hasPreferences">删除偏好</button>
    </view>
  </view>
</template>

<script>
import { dietPreferencesAPI } from '@/utils/api.js'

export default {
  data() {
    return {
      form: {
        taste_preference: '',
        diet_type: ''
      },
      allergies: [],
      forbiddenFoods: [],
      tasteOptions: ['清淡', '适中', '偏重', '甜', '咸', '辣', '酸'],
      tasteIndex: 0,
      dietTypes: ['均衡饮食', '素食', '低碳水', '高蛋白', '低脂', '生酮', '地中海饮食'],
      dietTypeIndex: 0,
      loading: false,
      hasPreferences: false
    }
  },
  onShow() {
    this.loadPreferences()
  },
  methods: {
    async loadPreferences() {
      try {
        const prefs = await dietPreferencesAPI.get()
        this.form = {
          taste_preference: prefs.taste_preference || '',
          diet_type: prefs.diet_type || ''
        }
        this.allergies = prefs.allergies ? prefs.allergies.split(',').filter(a => a) : []
        this.forbiddenFoods = prefs.forbidden_foods ? prefs.forbidden_foods.split(',').filter(f => f) : []
        this.hasPreferences = true
        if (this.form.taste_preference) {
          this.tasteIndex = this.tasteOptions.indexOf(this.form.taste_preference)
        }
        if (this.form.diet_type) {
          this.dietTypeIndex = this.dietTypes.indexOf(this.form.diet_type)
        }
      } catch (e) {
        console.log('暂无饮食偏好')
      }
    },
    onTasteChange(e) {
      this.tasteIndex = e.detail.value
      this.form.taste_preference = this.tasteOptions[this.tasteIndex]
    },
    onDietTypeChange(e) {
      this.dietTypeIndex = e.detail.value
      this.form.diet_type = this.dietTypes[this.dietTypeIndex]
    },
    showAddAllergy() {
      uni.showPrompt({
        title: '添加过敏食物',
        placeholderText: '请输入过敏食物',
        success: (res) => {
          if (res.confirm && res.value) {
            this.addAllergy(res.value)
          }
        }
      })
    },
    async addAllergy(allergy) {
      try {
        await dietPreferencesAPI.addAllergy(allergy)
        this.allergies.push(allergy)
        uni.showToast({ title: '添加成功', icon: 'success' })
      } catch (error) {
        uni.showToast({ title: '添加失败', icon: 'none' })
      }
    },
    async removeAllergy(index) {
      const allergy = this.allergies[index]
      try {
        await dietPreferencesAPI.removeAllergy(allergy)
        this.allergies.splice(index, 1)
        uni.showToast({ title: '删除成功', icon: 'success' })
      } catch (error) {
        uni.showToast({ title: '删除失败', icon: 'none' })
      }
    },
    showAddForbiddenFood() {
      uni.showPrompt({
        title: '添加禁忌食物',
        placeholderText: '请输入禁忌食物',
        success: (res) => {
          if (res.confirm && res.value) {
            this.addForbiddenFood(res.value)
          }
        }
      })
    },
    async addForbiddenFood(food) {
      try {
        await dietPreferencesAPI.addForbiddenFood(food)
        this.forbiddenFoods.push(food)
        uni.showToast({ title: '添加成功', icon: 'success' })
      } catch (error) {
        uni.showToast({ title: '添加失败', icon: 'none' })
      }
    },
    async removeForbiddenFood(index) {
      const food = this.forbiddenFoods[index]
      try {
        await dietPreferencesAPI.removeForbiddenFood(food)
        this.forbiddenFoods.splice(index, 1)
        uni.showToast({ title: '删除成功', icon: 'success' })
      } catch (error) {
        uni.showToast({ title: '删除失败', icon: 'none' })
      }
    },
    async handleSubmit() {
      this.loading = true
      try {
        if (this.hasPreferences) {
          await dietPreferencesAPI.update(this.form)
          uni.showToast({ title: '更新成功', icon: 'success' })
        } else {
          await dietPreferencesAPI.create(this.form)
          this.hasPreferences = true
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
        content: '确定要删除饮食偏好吗？',
        success: async (res) => {
          if (res.confirm) {
            try {
              await dietPreferencesAPI.delete()
              this.form = { taste_preference: '', diet_type: '' }
              this.allergies = []
              this.forbiddenFoods = []
              this.hasPreferences = false
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
.diet-preferences-container {
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

.picker {
  height: 80rpx;
  line-height: 80rpx;
  background: #f5f5f5;
  border-radius: 12rpx;
  padding: 0 20rpx;
  font-size: 28rpx;
  color: #666;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.tag-item {
  display: flex;
  align-items: center;
  background: #f0fdf4;
  border-radius: 12rpx;
  padding: 10rpx 16rpx;
  gap: 10rpx;
}

.tag-text {
  font-size: 26rpx;
  color: #059669;
}

.tag-remove {
  font-size: 24rpx;
  color: #999;
}

.add-tag {
  background: #f5f5f5;
  border-radius: 12rpx;
  padding: 10rpx 16rpx;
}

.add-text {
  font-size: 26rpx;
  color: #999;
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
