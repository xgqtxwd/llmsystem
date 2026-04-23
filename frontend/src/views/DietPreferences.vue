<template>
  <div class="diet-preferences-container">
    <van-nav-bar title="饮食偏好" left-arrow @click-left="$router.back()" />
    
    <div class="content">
      <van-form @submit="onSave">
        <van-cell-group inset title="口味偏好">
          <van-field
            v-model="form.tastePreference"
            is-link
            readonly
            name="tastePreference"
            label="口味偏好"
            placeholder="请选择口味偏好"
            @click="showTastePicker = true"
          />
        </van-cell-group>
        
        <van-cell-group inset title="饮食类型">
          <van-field
            v-model="form.dietType"
            is-link
            readonly
            name="dietType"
            label="饮食类型"
            placeholder="请选择饮食类型"
            @click="showDietTypePicker = true"
          />
        </van-cell-group>
        
        <van-cell-group inset title="过敏食物">
          <van-field
            name="allergies"
            label="过敏食物"
            placeholder="点击添加过敏食物"
          >
            <template #input>
              <div class="tags-container">
                <van-tag
                  v-for="(item, index) in allergiesList"
                  :key="index"
                  type="danger"
                  closable
                  @close="removeAllergy(item)"
                  class="tag-item"
                >
                  {{ item }}
                </van-tag>
                <van-button size="small" type="primary" @click="showAddAllergy = true">
                  添加
                </van-button>
              </div>
            </template>
          </van-field>
        </van-cell-group>
        
        <van-cell-group inset title="禁忌食物">
          <van-field
            name="forbiddenFoods"
            label="禁忌食物"
            placeholder="点击添加禁忌食物"
          >
            <template #input>
              <div class="tags-container">
                <van-tag
                  v-for="(item, index) in forbiddenFoodsList"
                  :key="index"
                  type="warning"
                  closable
                  @close="removeForbiddenFood(item)"
                  class="tag-item"
                >
                  {{ item }}
                </van-tag>
                <van-button size="small" type="primary" @click="showAddForbidden = true">
                  添加
                </van-button>
              </div>
            </template>
          </van-field>
        </van-cell-group>
        
        <div class="save-btn">
          <van-button round block type="primary" native-type="submit" :loading="loading">
            保存
          </van-button>
        </div>
      </van-form>
      
      <van-popup v-model:show="showTastePicker" position="bottom">
        <van-picker
          :columns="tasteColumns"
          @confirm="onTasteConfirm"
          @cancel="showTastePicker = false"
        />
      </van-popup>
      
      <van-popup v-model:show="showDietTypePicker" position="bottom">
        <van-picker
          :columns="dietTypeColumns"
          @confirm="onDietTypeConfirm"
          @cancel="showDietTypePicker = false"
        />
      </van-popup>
      
      <van-dialog v-model:show="showAddAllergy" title="添加过敏食物" show-cancel-button @confirm="addAllergy">
        <van-field v-model="newAllergy" placeholder="请输入过敏食物" />
      </van-dialog>
      
      <van-dialog v-model:show="showAddForbidden" title="添加禁忌食物" show-cancel-button @confirm="addForbiddenFood">
        <van-field v-model="newForbiddenFood" placeholder="请输入禁忌食物" />
      </van-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { dietPreferencesAPI } from '@/api'
import { showToast } from 'vant'

const router = useRouter()

const form = ref({
  tastePreference: '',
  dietType: ''
})

const allergiesList = ref([])
const forbiddenFoodsList = ref([])
const loading = ref(false)

const showTastePicker = ref(false)
const showDietTypePicker = ref(false)
const showAddAllergy = ref(false)
const showAddForbidden = ref(false)

const newAllergy = ref('')
const newForbiddenFood = ref('')

const tasteColumns = [
  { text: '清淡', value: '清淡' },
  { text: '麻辣', value: '麻辣' },
  { text: '酸甜', value: '酸甜' },
  { text: '咸鲜', value: '咸鲜' },
  { text: '苦味', value: '苦味' }
]

const dietTypeColumns = [
  { text: '普通饮食', value: '普通饮食' },
  { text: '素食', value: '素食' },
  { text: '低脂饮食', value: '低脂饮食' },
  { text: '低糖饮食', value: '低糖饮食' },
  { text: '高蛋白饮食', value: '高蛋白饮食' }
]

function onTasteConfirm({ selectedOptions }) {
  form.value.tastePreference = selectedOptions[0].value
  showTastePicker.value = false
}

function onDietTypeConfirm({ selectedOptions }) {
  form.value.dietType = selectedOptions[0].value
  showDietTypePicker.value = false
}

function addAllergy() {
  if (newAllergy.value && !allergiesList.value.includes(newAllergy.value)) {
    allergiesList.value.push(newAllergy.value)
  }
  newAllergy.value = ''
}

function removeAllergy(item) {
  const index = allergiesList.value.indexOf(item)
  if (index > -1) {
    allergiesList.value.splice(index, 1)
  }
}

function addForbiddenFood() {
  if (newForbiddenFood.value && !forbiddenFoodsList.value.includes(newForbiddenFood.value)) {
    forbiddenFoodsList.value.push(newForbiddenFood.value)
  }
  newForbiddenFood.value = ''
}

function removeForbiddenFood(item) {
  const index = forbiddenFoodsList.value.indexOf(item)
  if (index > -1) {
    forbiddenFoodsList.value.splice(index, 1)
  }
}

async function onSave() {
  loading.value = true
  try {
    const data = {
      taste_preference: form.value.tastePreference,
      diet_type: form.value.dietType,
      allergies: allergiesList.value.join(','),
      forbidden_foods: forbiddenFoodsList.value.join(',')
    }
    
    await dietPreferencesAPI.create(data)
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
    const pref = await dietPreferencesAPI.get()
    if (pref) {
      form.value.tastePreference = pref.taste_preference || ''
      form.value.dietType = pref.diet_type || ''
      if (pref.allergies) {
        allergiesList.value = pref.allergies.split(',').filter(a => a.trim())
      }
      if (pref.forbidden_foods) {
        forbiddenFoodsList.value = pref.forbidden_foods.split(',').filter(f => f.trim())
      }
    }
  } catch (e) {
    console.log('暂无饮食偏好')
  }
})
</script>

<style scoped>
.diet-preferences-container {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.content {
  padding: 20px 0;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.tag-item {
  margin-right: 5px;
}

.save-btn {
  padding: 20px;
}
</style>
