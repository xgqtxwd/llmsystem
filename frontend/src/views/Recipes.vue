<template>
  <div class="recipes-container">
    <van-nav-bar title="食谱推荐" left-arrow @click-left="$router.back()" />

    <div class="content">
      <div class="ai-section">
        <div class="section-card">
          <div class="card-header">
            <div class="header-icon">
              <van-icon name="fire-o" size="20" />
            </div>
            <div class="header-text">
              <h3>AI 智能推荐</h3>
              <p>根据您的需求定制专属食谱</p>
            </div>
          </div>

          <div class="form-row">
            <div class="form-field" @click="showMealPicker = true">
              <label>餐次</label>
              <div class="field-value">
                <span :class="{ placeholder: !selectedMealType }">{{ selectedMealType || '选择餐次' }}</span>
                <van-icon name="arrow-down" size="12" color="#94a3b8" />
              </div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-field full">
              <label>可用食材</label>
              <input
                v-model="availableIngredients"
                type="text"
                placeholder="输入您已有的食材，用逗号分隔"
                class="field-input"
              />
            </div>
          </div>

          <button class="recommend-btn" @click="getAIRecommendation" :disabled="aiLoading">
            <van-icon v-if="!aiLoading" name="guide-o" size="18" />
            <van-loading v-else size="18" color="#fff" />
            <span>{{ aiLoading ? '正在生成...' : '为我推荐食谱' }}</span>
          </button>
        </div>

        <div v-if="aiRecommendation" class="result-card animate-fadeInUp">
          <div class="result-header">
            <van-icon name="description" size="16" />
            <span>推荐结果</span>
          </div>
          <div class="result-body">{{ aiRecommendation }}</div>
        </div>
      </div>

      <div class="feature-section">
        <h4 class="section-title">
          <van-icon name="photograph" size="16" />
          食材识别
        </h4>
        <div class="section-card">
          <div class="recognize-area">
            <div class="url-input-row">
              <input
                v-model="imageUrl"
                type="text"
                placeholder="粘贴图片URL进行识别"
                class="url-input"
              />
              <button class="url-btn" @click="recognizeFromUrl" :disabled="recognizeLoading">
                识别
              </button>
            </div>
            <div class="upload-area">
              <van-uploader
                v-model:file-list="fileList"
                :after-read="afterRead"
                accept="image/*"
                max-count="1"
              >
                <div class="upload-trigger">
                  <van-icon name="plus" size="24" color="#94a3b8" />
                  <span>上传图片识别</span>
                </div>
              </van-uploader>
            </div>
          </div>
          <div v-if="recognizedIngredients" class="recognize-result">
            <div class="result-tag">
              <van-icon name="passed" size="14" />
              <span>识别成功</span>
            </div>
            <p class="result-text">{{ recognizedIngredients }}</p>
            <button class="use-btn" @click="useRecognizedIngredients">使用此结果</button>
          </div>
        </div>
      </div>

      <div class="feature-section">
        <h4 class="section-title">
          <van-icon name="flower-o" size="16" />
          季节推荐
        </h4>
        <div class="season-grid">
          <div
            v-for="season in seasons"
            :key="season.value"
            class="season-card"
            :class="'season-' + season.value"
            @click="getSeasonalRecipes(season.value)"
          >
            <div class="season-emoji">{{ season.emoji }}</div>
            <span class="season-name">{{ season.text }}</span>
            <van-icon name="arrow" size="12" class="season-arrow" />
          </div>
        </div>
      </div>

      <div class="feature-section">
        <h4 class="section-title">
          <van-icon name="exchange" size="16" />
          食材替代
        </h4>
        <div class="section-card">
          <div class="substitute-search">
            <input
              v-model="substituteIngredient"
              type="text"
              placeholder="输入要查询的食材名称"
              class="substitute-input"
              @keyup.enter="getSubstitute"
            />
            <button class="substitute-btn" @click="getSubstitute" :disabled="aiLoading">
              查询替代
            </button>
          </div>
          <div v-if="substituteResult" class="substitute-result">
            <div class="result-header">
              <van-icon name="info-o" size="14" />
              <span>替代建议</span>
            </div>
            <p>{{ substituteResult }}</p>
          </div>
        </div>
      </div>
    </div>

    <van-popup v-model:show="showMealPicker" position="bottom" round>
      <div class="picker-header">
        <span @click="showMealPicker = false">取消</span>
        <strong>选择餐次</strong>
        <span></span>
      </div>
      <div class="picker-options">
        <div
          v-for="opt in mealTypePickerOptions"
          :key="opt.value"
          class="picker-option"
          :class="{ active: selectedMealType === opt.text && opt.value !== '' || selectedMealType === opt.value }"
          @click="selectMealType(opt)"
        >
          {{ opt.text }}
          <van-icon v-if="(opt.value === '' ? !selectedMealType : selectedMealType === (opt.value || opt.text))" name="success" size="16" color="#10b981" />
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { recipesAPI } from '@/api'
import { showToast } from 'vant'

const router = useRouter()

const activeTab = ref('ai')
const aiLoading = ref(false)
const recognizeLoading = ref(false)

const selectedMealType = ref('')
const availableIngredients = ref('')
const aiRecommendation = ref('')
const imageUrl = ref('')
const recognizedIngredients = ref('')
const fileList = ref([])
const substituteIngredient = ref('')
const substituteResult = ref('')
const showMealPicker = ref(false)

const seasons = [
  { text: '春季', value: 'spring', emoji: '🌸' },
  { text: '夏季', value: 'summer', emoji: '☀️' },
  { text: '秋季', value: 'autumn', emoji: '🍂' },
  { text: '冬季', value: 'winter', emoji: '❄️' }
]

const mealTypePickerOptions = [
  { text: '不限', value: '' },
  { text: '早餐', value: 'breakfast' },
  { text: '午餐', value: 'lunch' },
  { text: '晚餐', value: 'dinner' },
  { text: '零食', value: 'snack' }
]

function selectMealType(opt) {
  if (opt.value === '') {
    selectedMealType.value = ''
  } else {
    selectedMealType.value = opt.text
  }
  showMealPicker.value = false
}

async function getAIRecommendation() {
  aiLoading.value = true
  try {
    const response = await recipesAPI.getAIRecommendation(
      selectedMealType.value,
      availableIngredients.value
    )
    aiRecommendation.value = response.recommendation
  } catch (error) {
    showToast('推荐失败')
  } finally {
    aiLoading.value = false
  }
}

function afterRead(file) {
  const formData = new FormData()
  formData.append('image', file.file)
  
  recognizeLoading.value = true
  recipesAPI.recognizeIngredients(formData)
    .then(res => {
      if (res.success) {
        recognizedIngredients.value = res.result
      } else {
        showToast(res.error || '识别失败')
      }
    })
    .finally(() => {
      recognizeLoading.value = false
    })
}

async function recognizeFromUrl() {
  if (!imageUrl.value) {
    showToast('请输入图片URL')
    return
  }
  
  recognizeLoading.value = true
  try {
    const res = await recipesAPI.recognizeIngredientsUrl(imageUrl.value)
    if (res.success) {
      recognizedIngredients.value = res.result
    } else {
      showToast(res.error || '识别失败')
    }
  } catch (error) {
    showToast('识别失败')
  } finally {
    recognizeLoading.value = false
  }
}

function useRecognizedIngredients() {
  if (availableIngredients.value) {
    availableIngredients.value += ', ' + recognizedIngredients.value
  } else {
    availableIngredients.value = recognizedIngredients.value
  }
}

async function getSeasonalRecipes(season) {
  aiLoading.value = true
  try {
    const res = await recipesAPI.getSeasonalRecipes(season)
    if (res && res.recommendation) {
      let text = ''
      if (res.season) {
        text = `【${res.season}推荐】\n\n`
      }
      text += res.recommendation
      aiRecommendation.value = text
    } else {
      showToast(res?.error || '获取推荐失败')
    }
  } catch (error) {
    showToast('获取推荐失败')
  } finally {
    aiLoading.value = false
  }
}

async function getSubstitute() {
  if (!substituteIngredient.value) {
    showToast('请输入要查询的食材')
    return
  }
  
  aiLoading.value = true
  try {
    const res = await recipesAPI.getIngredientSubstitute(substituteIngredient.value)
    if (res && res.success) {
      substituteResult.value = res.suggestion
    } else {
      showToast(res?.error || '查询失败')
    }
  } catch (error) {
    showToast('查询失败')
  } finally {
    aiLoading.value = false
  }
}

onMounted(() => {})
</script>

<style scoped>
.recipes-container {
  min-height: 100vh;
  background-color: #f0fdf4;
  padding-bottom: 30px;
}

.content {
  padding: 0 16px;
}

.ai-section {
  margin-bottom: 20px;
}

.section-card {
  background: white;
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--shadow-sm);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.header-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, #f97316, #ea580c);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.header-text h3 {
  margin: 0;
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
}

.header-text p {
  margin: 2px 0 0;
  font-size: 12px;
  color: var(--text-muted);
}

.form-row {
  display: flex;
  gap: 10px;
  margin-bottom: 14px;
}

.form-field {
  flex: 1;
  background: #f8fafc;
  border-radius: var(--radius-sm);
  padding: 12px 14px;
  border: 1.5px solid #e2e8f0;
  transition: var(--transition);
}

.form-field:focus-within {
  border-color: #10b981;
  background: white;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.form-field.full {
  width: 100%;
}

.form-field label {
  display: block;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.field-value {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
}

.field-value span {
  font-size: 15px;
  color: var(--text-primary);
}

.field-value span.placeholder {
  color: #c4cbd5;
}

.field-input {
  width: 100%;
  border: none;
  background: transparent;
  font-size: 15px;
  color: var(--text-primary);
  outline: none;
}

.recommend-btn {
  width: 100%;
  padding: 14px;
  border: none;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: var(--transition);
  box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35);
}

.recommend-btn:active:not(:disabled) {
  transform: scale(0.98);
  opacity: 0.9;
}

.recommend-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.result-card {
  background: white;
  border-radius: var(--radius-lg);
  margin-top: 14px;
  box-shadow: var(--shadow-md);
  overflow: hidden;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 14px 18px;
  background: linear-gradient(135deg, #ecfdf5, #d1fae5);
  color: #065f46;
  font-size: 13px;
  font-weight: 600;
}

.result-body {
  padding: 18px;
  font-size: 14px;
  line-height: 1.8;
  color: #374151;
  white-space: pre-wrap;
}

.feature-section {
  margin-bottom: 22px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 12px 2px;
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.recognize-area {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.url-input-row {
  display: flex;
  gap: 8px;
}

.url-input {
  flex: 1;
  padding: 10px 14px;
  border: 1.5px solid #e2e8f0;
  border-radius: var(--radius-sm);
  font-size: 14px;
  outline: none;
  transition: var(--transition);
  background: #f8fafc;
}

.url-input:focus {
  border-color: #10b981;
  background: white;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.08);
}

.url-btn {
  padding: 10px 18px;
  border: none;
  border-radius: var(--radius-sm);
  background: var(--primary);
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: var(--transition);
}

.url-btn:active {
  opacity: 0.85;
}

.upload-trigger {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  border: 2px dashed #d1d5db;
  border-radius: var(--radius-md);
  background: #fafafa;
  cursor: pointer;
  transition: var(--transition);
  gap: 6px;
}

.upload-trigger:active {
  border-color: #10b981;
  background: #f0fdf4;
}

.upload-trigger span {
  font-size: 13px;
  color: var(--text-muted);
}

.recognize-result {
  margin-top: 14px;
  padding: 14px;
  background: linear-gradient(135deg, #ecfdf5, #f0fdf4);
  border-radius: var(--radius-md);
  border-left: 3px solid #10b981;
}

.result-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
  color: #059669;
  margin-bottom: 8px;
}

.result-text {
  margin: 0 0 10px;
  font-size: 14px;
  color: #374151;
  line-height: 1.5;
}

.use-btn {
  padding: 8px 20px;
  border: none;
  border-radius: 20px;
  background: #10b981;
  color: white;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}

.use-btn:active {
  transform: scale(0.96);
}

.season-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

.season-card {
  background: white;
  border-radius: var(--radius-md);
  padding: 16px 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: var(--transition);
  box-shadow: var(--shadow-sm);
  position: relative;
  overflow: hidden;
}

.season-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
}

.season-spring::before { background: linear-gradient(90deg, #f9a8d4, #fb7185); }
.season-summer::before { background: linear-gradient(90deg, #fbbf24, #f59e0b); }
.season-autumn::before { background: linear-gradient(90deg, #fb923c, #ea580c); }
.season-winter::before { background: linear-gradient(90deg, #93c5fd, #60a5fa); }

.season-card:active {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.season-emoji {
  font-size: 28px;
}

.season-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.season-arrow {
  color: var(--text-muted);
}

.substitute-search {
  display: flex;
  gap: 8px;
}

.substitute-input {
  flex: 1;
  padding: 12px 14px;
  border: 1.5px solid #e2e8f0;
  border-radius: var(--radius-sm);
  font-size: 14px;
  outline: none;
  transition: var(--transition);
  background: #f8fafc;
}

.substitute-input:focus {
  border-color: #6366f1;
  background: white;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.08);
}

.substitute-btn {
  padding: 12px 18px;
  border: none;
  border-radius: var(--radius-sm);
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: var(--transition);
}

.substitute-btn:active {
  opacity: 0.85;
}

.substitute-result {
  margin-top: 14px;
  padding: 14px;
  background: linear-gradient(135deg, #eef2ff, #e0e7ff);
  border-radius: var(--radius-md);
  border-left: 3px solid #6366f1;
}

.substitute-result .result-header {
  background: transparent;
  color: #4338ca;
  padding: 0 0 8px;
}

.substitute-result p {
  margin: 0;
  font-size: 14px;
  line-height: 1.7;
  color: #374151;
}

.picker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  font-size: 15px;
  border-bottom: 1px solid #f1f5f9;
}

.picker-header span:first-child {
  color: var(--text-secondary);
  cursor: pointer;
}

.picker-header strong {
  font-weight: 600;
}

.picker-options {
  padding: 8px 0;
}

.picker-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 24px;
  font-size: 15px;
  color: var(--text-primary);
  cursor: pointer;
  transition: var(--transition);
}

.picker-option:active {
  background: #f8fafc;
}

.picker-option.active {
  color: #10b981;
  font-weight: 600;
}
</style>
