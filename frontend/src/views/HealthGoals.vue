<template>
  <div class="health-goals-container">
    <van-nav-bar title="健康目标" left-arrow @click-left="$router.back()" />
    
    <div class="content">
      <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
        <div class="goals-section" v-if="goals.length > 0">
          <van-cell-group inset>
            <van-cell
              v-for="goal in goals"
              :key="goal.id"
              :title="getGoalTypeText(goal.goal_type)"
              is-link
              @click="editGoal(goal)"
            >
              <template #label>
                <div class="goal-info">
                  <span v-if="goal.target_weight">目标体重: {{ goal.target_weight }}kg</span>
                  <span v-if="goal.daily_calorie_target">每日热量: {{ goal.daily_calorie_target }}kcal</span>
                </div>
              </template>
              <template #value>
                <van-tag :type="getGoalTagType(goal.goal_type)">
                  {{ getGoalTypeText(goal.goal_type) }}
                </van-tag>
              </template>
            </van-cell>
          </van-cell-group>
        </div>
        
        <van-empty v-else description="暂无健康目标" />
      </van-pull-refresh>
      
      <div class="add-btn">
        <van-button round block type="primary" icon="plus" @click="showAddDialog = true">
          添加健康目标
        </van-button>
      </div>
      
      <van-dialog
        v-model:show="showAddDialog"
        title="添加健康目标"
        show-cancel-button
        @confirm="onSaveGoal"
      >
        <van-form>
          <van-field
            v-model="goalForm.goalType"
            is-link
            readonly
            label="目标类型"
            placeholder="请选择目标类型"
            @click="showGoalTypePicker = true"
          />
          <van-field
            v-model="goalForm.targetWeight"
            type="digit"
            label="目标体重(kg)"
            placeholder="请输入目标体重"
          />
          <van-field
            v-model="goalForm.dailyCalorieTarget"
            type="digit"
            label="每日热量(kcal)"
            placeholder="请输入每日目标热量"
          />
        </van-form>
      </van-dialog>
      
      <van-popup v-model:show="showGoalTypePicker" position="bottom">
        <van-picker
          :columns="goalTypeColumns"
          @confirm="onGoalTypeConfirm"
          @cancel="showGoalTypePicker = false"
        />
      </van-popup>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { healthGoalsAPI } from '@/api'
import { showToast, showConfirmDialog } from 'vant'

const router = useRouter()

const goals = ref([])
const loading = ref(false)
const refreshing = ref(false)
const showAddDialog = ref(false)
const showGoalTypePicker = ref(false)

const goalForm = ref({
  goalType: '',
  targetWeight: '',
  dailyCalorieTarget: ''
})

const goalTypeColumns = [
  { text: '减肥', value: 'weight_loss' },
  { text: '增肌', value: 'muscle_gain' },
  { text: '控糖', value: 'blood_sugar_control' },
  { text: '健康维持', value: 'health_maintenance' }
]

function getGoalTypeText(type) {
  const map = {
    'weight_loss': '减肥',
    'muscle_gain': '增肌',
    'blood_sugar_control': '控糖',
    'health_maintenance': '健康维持'
  }
  return map[type] || type
}

function getGoalTagType(type) {
  const map = {
    'weight_loss': 'danger',
    'muscle_gain': 'success',
    'blood_sugar_control': 'warning',
    'health_maintenance': 'primary'
  }
  return map[type] || 'primary'
}

function onGoalTypeConfirm({ selectedOptions }) {
  goalForm.value.goalType = selectedOptions[0].value
  showGoalTypePicker.value = false
}

function editGoal(goal) {
  showConfirmDialog({
    title: '操作',
    message: '是否删除该目标?'
  }).then(async () => {
    try {
      await healthGoalsAPI.delete(goal.id)
      showToast('删除成功')
      loadGoals()
    } catch (error) {
      showToast('删除失败')
    }
  }).catch(() => {})
}

async function onSaveGoal() {
  if (!goalForm.value.goalType) {
    showToast('请选择目标类型')
    return
  }
  
  loading.value = true
  try {
    const data = {
      goal_type: goalForm.value.goalType,
      target_weight: goalForm.value.targetWeight ? parseFloat(goalForm.value.targetWeight) : null,
      daily_calorie_target: goalForm.value.dailyCalorieTarget ? parseFloat(goalForm.value.dailyCalorieTarget) : null
    }
    
    await healthGoalsAPI.create(data)
    showToast('保存成功')
    showAddDialog.value = false
    goalForm.value = { goalType: '', targetWeight: '', dailyCalorieTarget: '' }
    loadGoals()
  } catch (error) {
    showToast(error.response?.data?.detail || '保存失败')
  } finally {
    loading.value = false
  }
}

async function loadGoals() {
  try {
    goals.value = await healthGoalsAPI.list()
  } catch (error) {
    console.error('加载目标失败', error)
  }
}

async function onRefresh() {
  await loadGoals()
  refreshing.value = false
}

onMounted(() => {
  loadGoals()
})
</script>

<style scoped>
.health-goals-container {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.content {
  padding: 20px 0;
}

.goal-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
  color: #969799;
}

.add-btn {
  position: fixed;
  bottom: 50px;
  left: 20px;
  right: 20px;
}
</style>
