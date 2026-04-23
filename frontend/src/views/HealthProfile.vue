<template>
  <div class="health-profile-container">
    <van-nav-bar title="健康档案" left-arrow @click-left="$router.back()" />
    
    <div class="profile-content">
      <van-form @submit="onSave">
        <van-cell-group inset title="基本信息">
          <van-field
            v-model="form.age"
            type="digit"
            name="age"
            label="年龄"
            placeholder="请输入年龄"
            :rules="[{ validator: validateAge, message: '年龄必须在1-150之间' }]"
          />
          <van-field
            v-model="form.gender"
            is-link
            readonly
            name="gender"
            label="性别"
            placeholder="请选择性别"
            @click="showGenderPicker = true"
          />
          <van-field
            v-model="form.height"
            type="digit"
            name="height"
            label="身高(cm)"
            placeholder="请输入身高"
          />
          <van-field
            v-model="form.weight"
            type="digit"
            name="weight"
            label="体重(kg)"
            placeholder="请输入体重"
          />
        </van-cell-group>
        
        <van-cell-group inset title="活动水平">
          <van-field
            v-model="form.activityLevel"
            is-link
            readonly
            name="activityLevel"
            label="活动水平"
            placeholder="请选择活动水平"
            @click="showActivityPicker = true"
          />
        </van-cell-group>
        
        <van-cell-group inset title="健康状况">
          <van-field
            v-model="form.healthConditions"
            type="textarea"
            name="healthConditions"
            label="健康状况"
            placeholder="请描述您的健康状况"
            rows="3"
            autosize
          />
        </van-cell-group>
        
        <van-cell-group inset v-if="bmi">
          <van-cell title="BMI指数" :value="bmi" />
          <van-cell title="健康评估" :value="bmiStatus" />
        </van-cell-group>
        
        <div class="save-btn">
          <van-button round block type="primary" native-type="submit" :loading="loading">
            保存
          </van-button>
        </div>
      </van-form>
      
      <van-popup v-model:show="showGenderPicker" position="bottom">
        <van-picker
          :columns="genderColumns"
          @confirm="onGenderConfirm"
          @cancel="showGenderPicker = false"
        />
      </van-popup>
      
      <van-popup v-model:show="showActivityPicker" position="bottom">
        <van-picker
          :columns="activityColumns"
          @confirm="onActivityConfirm"
          @cancel="showActivityPicker = false"
        />
      </van-popup>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { healthProfileAPI } from '@/api'
import { showToast } from 'vant'

const router = useRouter()

const form = ref({
  age: '',
  gender: '',
  height: '',
  weight: '',
  activityLevel: '',
  healthConditions: ''
})

const loading = ref(false)
const showGenderPicker = ref(false)
const showActivityPicker = ref(false)

const genderColumns = [
  { text: '男', value: 'male' },
  { text: '女', value: 'female' },
  { text: '其他', value: 'other' }
]

const activityColumns = [
  { text: '久坐', value: 'sedentary' },
  { text: '轻度活动', value: 'light' },
  { text: '中等活动', value: 'moderate' },
  { text: '活跃', value: 'active' },
  { text: '非常活跃', value: 'very_active' }
]

const bmi = computed(() => {
  const h = parseFloat(form.value.height)
  const w = parseFloat(form.value.weight)
  if (h && w) {
    return (w / ((h / 100) ** 2)).toFixed(2)
  }
  return null
})

const bmiStatus = computed(() => {
  if (!bmi.value) return '--'
  const val = parseFloat(bmi.value)
  if (val < 18.5) return '偏瘦'
  if (val < 24) return '正常'
  if (val < 28) return '偏胖'
  return '肥胖'
})

function validateAge(val) {
  if (!val) return true
  return parseInt(val) >= 1 && parseInt(val) <= 150
}

function onGenderConfirm({ selectedOptions }) {
  form.value.gender = selectedOptions[0].value
  showGenderPicker.value = false
}

function onActivityConfirm({ selectedOptions }) {
  form.value.activityLevel = selectedOptions[0].value
  showActivityPicker.value = false
}

async function onSave() {
  loading.value = true
  try {
    const data = {}
    if (form.value.age) data.age = parseInt(form.value.age)
    if (form.value.gender) data.gender = form.value.gender
    if (form.value.height) data.height = parseFloat(form.value.height)
    if (form.value.weight) data.weight = parseFloat(form.value.weight)
    if (form.value.activityLevel) data.activity_level = form.value.activityLevel
    if (form.value.healthConditions) data.health_conditions = form.value.healthConditions
    
    await healthProfileAPI.create(data)
    showToast('保存成功')
    router.back()
  } catch (error) {
    showToast(error.response?.data?.detail || '保存失败')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    const profile = await healthProfileAPI.get()
    if (profile) {
      form.value.age = profile.age?.toString() || ''
      form.value.gender = profile.gender || ''
      form.value.height = profile.height?.toString() || ''
      form.value.weight = profile.weight?.toString() || ''
      form.value.activityLevel = profile.activity_level || ''
      form.value.healthConditions = profile.health_conditions || ''
    }
  } catch (e) {
    console.log('暂无健康档案')
  }
})
</script>

<style scoped>
.health-profile-container {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.profile-content {
  padding: 20px 0;
}

.save-btn {
  padding: 20px;
}
</style>
