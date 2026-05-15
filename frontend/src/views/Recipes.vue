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

          <div class="form-row meal-type-row">
            <label class="meal-label">餐次</label>
            <div class="meal-chips">
              <div
                v-for="opt in mealTypePickerOptions"
                :key="opt.value"
                class="meal-chip"
                :class="{ active: selectedMealType === opt.text || (opt.value === '' && !selectedMealType) }"
                @click="selectMealType(opt)"
              >
                {{ opt.text }}
              </div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-field full">
              <label>可用食材</label>
              <div class="field-input-wrapper">
                <input
                  v-model="availableIngredients"
                  type="text"
                  placeholder="输入或选择您已有的食材"
                  class="field-input"
                />
                <button class="select-btn" @click="showIngredientPicker = true">
                  <van-icon name="add-o" size="18" />
                </button>
              </div>
            </div>
          </div>

          <div class="recognize-section">
            <div class="recognize-header">
              <van-icon name="photograph" size="14" />
              <span>拍照识别食材</span>
            </div>
            <div class="recognize-area">
              <div class="url-input-row">
                <input
                  v-model="imageUrl"
                  type="text"
                  placeholder="粘贴图片URL"
                  class="url-input"
                />
                <button class="url-btn" @click="recognizeFromUrl" :disabled="recognizeLoading">
                  <van-loading v-if="recognizeLoading" size="14" />
                  <span v-else>识别</span>
                </button>
              </div>
              <div class="upload-area">
                <van-uploader
                  v-model:file-list="fileList"
                  :after-read="afterRead"
                  accept="image/*"
                  max-count="1"
                  :disabled="recognizeLoading"
                >
                  <div class="upload-trigger" :class="{ loading: recognizeLoading }">
                    <van-loading v-if="recognizeLoading" size="20" />
                    <template v-else>
                      <van-icon name="photograph" size="24" color="#94a3b8" />
                      <span>上传图片识别</span>
                    </template>
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
              <button class="use-btn" @click="useRecognizedIngredients">
                <van-icon name="add-o" size="14" />
                <span>添加到可用食材</span>
              </button>
            </div>
          </div>

          <div class="season-quick-select">
            <div class="season-label">
              <van-icon name="calendar" size="14" />
              <span>快速季节推荐</span>
            </div>
            <div class="season-chips">
              <div
                v-for="season in seasons"
                :key="season.value"
                class="season-chip"
                :class="'chip-' + season.value"
                @click="getSeasonalRecipes(season.value)"
              >
                <span>{{ season.emoji }}</span>
                <span class="chip-text">{{ season.text }}</span>
              </div>
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

    <van-popup
      :show="showIngredientPicker"
      position="bottom"
      round
      teleport="body"
      :style="{ height: '70vh' }"
      @update:show="showIngredientPicker = $event"
    >
      <div class="ingredient-picker">
        <div class="picker-header">
          <span @click="showIngredientPicker = false">取消</span>
          <strong>选择食材</strong>
          <span @click="confirmIngredients" style="color: #10b981;">确认</span>
        </div>

        <div class="ingredient-search">
          <input
            v-model="ingredientSearch"
            type="text"
            placeholder="搜索食材..."
            class="search-input"
          />
        </div>

        <div class="ingredient-content">
          <div
            v-for="category in filteredIngredientCategories"
            :key="category.name"
            class="ingredient-category"
          >
            <div class="category-header">
              <span>{{ category.emoji }}</span>
              <span class="category-name">{{ category.name }}</span>
              <span class="category-count">{{ category.items.filter(i => selectedIngredients.includes(i.name)).length }}/{{ category.items.length }}</span>
            </div>
            <div class="ingredient-grid">
              <div
                v-for="item in category.items"
                :key="item.name"
                class="ingredient-item"
                :class="{ selected: selectedIngredients.includes(item.name) }"
                @click="toggleIngredient(item.name)"
              >
                <span class="item-emoji">{{ item.emoji }}</span>
                <span class="item-name">{{ item.name }}</span>
                <van-icon v-if="selectedIngredients.includes(item.name)" name="success" size="14" color="#10b981" class="item-check" />
              </div>
            </div>
          </div>
        </div>

        <div class="selected-summary">
          <div class="summary-header">
            <span>已选择 {{ selectedIngredients.length }} 种食材</span>
            <span class="clear-btn" @click="selectedIngredients = []">清空</span>
          </div>
          <div v-if="selectedIngredients.length > 0" class="summary-tags">
            <span
              v-for="ingredient in selectedIngredients"
              :key="ingredient"
              class="summary-tag"
            >
              {{ ingredient }}
              <van-icon name="cross" size="12" @click="toggleIngredient(ingredient)" />
            </span>
          </div>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
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
const showIngredientPicker = ref(false)
const selectedIngredients = ref([])
const ingredientSearch = ref('')

const seasons = [
  { text: '春季', value: 'spring', emoji: '🌸' },
  { text: '夏季', value: 'summer', emoji: '☀️' },
  { text: '秋季', value: 'autumn', emoji: '🍂' },
  { text: '冬季', value: 'winter', emoji: '❄️' }
]

const ingredientCategories = [
  {
    name: '蛋白质',
    emoji: '🥩',
    items: [
      { name: '鸡胸肉', emoji: '🍗' },
      { name: '牛肉', emoji: '🥩' },
      { name: '猪肉', emoji: '🥓' },
      { name: '羊肉', emoji: '🍖' },
      { name: '三文鱼', emoji: '🐟' },
      { name: '虾', emoji: '🦐' },
      { name: '鸡蛋', emoji: '🥚' },
      { name: '豆腐', emoji: '🧈' },
      { name: '牛奶', emoji: '🥛' },
      { name: '酸奶', emoji: '🥛' }
    ]
  },
  {
    name: '蔬菜',
    emoji: '🥬',
    items: [
      { name: '西兰花', emoji: '🥦' },
      { name: '菠菜', emoji: '🥬' },
      { name: '胡萝卜', emoji: '🥕' },
      { name: '西红柿', emoji: '🍅' },
      { name: '黄瓜', emoji: '🥒' },
      { name: '茄子', emoji: '🍆' },
      { name: '青椒', emoji: '🫑' },
      { name: '洋葱', emoji: '🧅' },
      { name: '土豆', emoji: '🥔' },
      { name: '南瓜', emoji: '🎃' },
      { name: '玉米', emoji: '🌽' },
      { name: '芹菜', emoji: '🥬' }
    ]
  },
  {
    name: '水果',
    emoji: '🍎',
    items: [
      { name: '苹果', emoji: '🍎' },
      { name: '香蕉', emoji: '🍌' },
      { name: '橙子', emoji: '🍊' },
      { name: '葡萄', emoji: '🍇' },
      { name: '蓝莓', emoji: '🫐' },
      { name: '草莓', emoji: '🍓' },
      { name: '猕猴桃', emoji: '🥝' },
      { name: '梨', emoji: '🍐' },
      { name: '西瓜', emoji: '🍉' },
      { name: '芒果', emoji: '🥭' }
    ]
  },
  {
    name: '谷物',
    emoji: '🍚',
    items: [
      { name: '糙米', emoji: '🍚' },
      { name: '燕麦', emoji: '🥣' },
      { name: '全麦面包', emoji: '🍞' },
      { name: '荞麦', emoji: '🌾' },
      { name: '紫米', emoji: '🍚' },
      { name: '小米', emoji: '🌾' },
      { name: '藜麦', emoji: '🍚' },
      { name: '面条', emoji: '🍝' }
    ]
  },
  {
    name: '坚果',
    emoji: '🥜',
    items: [
      { name: '杏仁', emoji: '🌰' },
      { name: '核桃', emoji: '🥜' },
      { name: '花生', emoji: '🥜' },
      { name: '腰果', emoji: '🌰' },
      { name: '开心果', emoji: '🌰' },
      { name: '芝麻', emoji: '🌾' }
    ]
  },
  {
    name: '其他',
    emoji: '🧂',
    items: [
      { name: '橄榄油', emoji: '🫒' },
      { name: '蜂蜜', emoji: '🍯' },
      { name: '黑木耳', emoji: '🍄' },
      { name: '香菇', emoji: '🍄' },
      { name: '海带', emoji: '🌿' },
      { name: '紫菜', emoji: '🌿' }
    ]
  }
]

const filteredIngredientCategories = ref([])

function updateFilteredCategories() {
  if (!ingredientSearch.value) {
    filteredIngredientCategories.value = ingredientCategories
  } else {
    const search = ingredientSearch.value.toLowerCase()
    filteredIngredientCategories.value = ingredientCategories
      .map(cat => ({
        ...cat,
        items: cat.items.filter(item => item.name.toLowerCase().includes(search))
      }))
      .filter(cat => cat.items.length > 0)
  }
}

watch(ingredientSearch, updateFilteredCategories)

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
}

function toggleIngredient(name) {
  const index = selectedIngredients.value.indexOf(name)
  if (index > -1) {
    selectedIngredients.value.splice(index, 1)
  } else {
    selectedIngredients.value.push(name)
  }
}

function confirmIngredients() {
  availableIngredients.value = selectedIngredients.value.join(', ')
  showIngredientPicker.value = false
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

onMounted(() => {
  updateFilteredCategories()
})
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

.meal-type-row {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.meal-label {
  display: block;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.meal-chips {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
}

.meal-chip {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px 8px;
  background: #f8fafc;
  border: 1.5px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.meal-chip:active {
  transform: scale(0.95);
}

.meal-chip.active {
  border-color: #10b981;
  background: #f0fdf4;
  color: #059669;
  font-weight: 600;
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

.season-quick-select {
  margin-bottom: 16px;
  padding: 14px;
  background: linear-gradient(135deg, #fff7ed, #fef3c7);
  border-radius: var(--radius-md);
  border: 1.5px dashed #fbbf24;
}

.season-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  color: #92400e;
  margin-bottom: 10px;
}

.season-chips {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.season-chip {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 8px 10px;
  background: white;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.season-chip:active {
  transform: scale(0.95);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.chip-spring {
  border: 1.5px solid #fecdd3;
  color: #be123c;
}

.chip-spring:active {
  background: #fff1f2;
}

.chip-summer {
  border: 1.5px solid #fef08a;
  color: #a16207;
}

.chip-summer:active {
  background: #fefce8;
}

.chip-autumn {
  border: 1.5px solid #fed7aa;
  color: #c2410c;
}

.chip-autumn:active {
  background: #fff7ed;
}

.chip-winter {
  border: 1.5px solid #bfdbfe;
  color: #1d4ed8;
}

.chip-winter:active {
  background: #eff6ff;
}

.chip-text {
  font-size: 12px;
}

.recognize-section {
  margin-bottom: 16px;
  padding: 14px;
  background: linear-gradient(135deg, #eff6ff, #dbeafe);
  border-radius: var(--radius-md);
  border: 1.5px dashed #3b82f6;
}

.recognize-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  color: #1e40af;
  margin-bottom: 10px;
}

.upload-area {
  margin-top: 10px;
}

.upload-trigger.loading {
  opacity: 0.6;
  cursor: not-allowed;
}

.use-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  padding: 10px;
  border: none;
  border-radius: 20px;
  background: #3b82f6;
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}

.use-btn:active {
  transform: scale(0.98);
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

.ingredient-picker {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.ingredient-search {
  padding: 12px 16px;
  border-bottom: 1px solid #f1f5f9;
}

.search-input {
  width: 100%;
  padding: 10px 14px;
  border: 1.5px solid #e2e8f0;
  border-radius: 20px;
  font-size: 14px;
  outline: none;
  transition: var(--transition);
  background: #f8fafc;
}

.search-input:focus {
  border-color: #10b981;
  background: white;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.08);
}

.ingredient-content {
  flex: 1;
  overflow-y: auto;
  padding: 12px 16px;
}

.ingredient-category {
  margin-bottom: 20px;
}

.category-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1.5px solid #e2e8f0;
}

.category-header span:first-child {
  font-size: 20px;
}

.category-name {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
  flex: 1;
}

.category-count {
  font-size: 12px;
  color: var(--text-muted);
  background: #f1f5f9;
  padding: 2px 8px;
  border-radius: 10px;
}

.ingredient-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.ingredient-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 12px 8px;
  background: white;
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.ingredient-item:active {
  transform: scale(0.95);
}

.ingredient-item.selected {
  border-color: #10b981;
  background: #f0fdf4;
}

.item-emoji {
  font-size: 24px;
  margin-bottom: 4px;
}

.item-name {
  font-size: 12px;
  color: var(--text-primary);
  text-align: center;
}

.item-check {
  position: absolute;
  top: 4px;
  right: 4px;
}

.selected-summary {
  padding: 12px 16px;
  border-top: 1px solid #e2e8f0;
  background: #f8fafc;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-size: 13px;
  color: var(--text-secondary);
}

.clear-btn {
  color: #ef4444;
  cursor: pointer;
  font-weight: 500;
}

.summary-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.summary-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: #10b981;
  color: white;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.summary-tag .van-icon {
  cursor: pointer;
  opacity: 0.8;
  transition: opacity 0.2s;
}

.summary-tag .van-icon:hover {
  opacity: 1;
}

.field-input-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.field-input-wrapper .field-input {
  flex: 1;
}

.select-btn {
  padding: 8px 12px;
  border: none;
  border-radius: 8px;
  background: #10b981;
  color: white;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.select-btn:active {
  transform: scale(0.95);
  background: #059669;
}
</style>
