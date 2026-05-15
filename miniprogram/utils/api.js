const BASE_URL = 'http://localhost:8000/api/v1'

function getToken() {
  return uni.getStorageSync('token') || ''
}

function setToken(token) {
  uni.setStorageSync('token', token)
}

function removeToken() {
  uni.removeStorageSync('token')
}

function getUserInfo() {
  try {
    const user = uni.getStorageSync('userInfo')
    return user ? JSON.parse(user) : null
  } catch (e) {
    return null
  }
}

function setUserInfo(user) {
  uni.setStorageSync('userInfo', JSON.stringify(user))
}

function removeUserInfo() {
  uni.removeStorageSync('userInfo')
}

function isAdmin() {
  return uni.getStorageSync('is_admin') === 'true'
}

function setAdmin(isAdmin) {
  uni.setStorageSync('is_admin', isAdmin ? 'true' : 'false')
}

function request({ url, method = 'GET', data, header = {}, isUpload = false }) {
  return new Promise((resolve, reject) => {
    const token = getToken()
    const defaultHeader = {
      'Content-Type': 'application/json'
    }
    if (token) {
      defaultHeader['Authorization'] = `Bearer ${token}`
    }
    if (isUpload) {
      delete defaultHeader['Content-Type']
    }
    
    uni.request({
      url: `${BASE_URL}${url}`,
      method,
      data,
      header: { ...defaultHeader, ...header },
      timeout: 30000,
      success: (res) => {
        if (res.statusCode === 401) {
          removeToken()
          removeUserInfo()
          uni.reLaunch({ url: '/pages/login/login' })
          reject(new Error('登录已过期，请重新登录'))
          return
        }
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          reject(res.data || new Error('请求失败'))
        }
      },
      fail: (err) => {
        reject(err)
      }
    })
  })
}

function uploadFile({ url, filePath, name, formData }) {
  return new Promise((resolve, reject) => {
    const token = getToken()
    uni.uploadFile({
      url: `${BASE_URL}${url}`,
      filePath,
      name,
      formData,
      header: {
        'Authorization': `Bearer ${token}`
      },
      timeout: 300000,
      success: (res) => {
        if (res.statusCode === 401) {
          removeToken()
          removeUserInfo()
          uni.reLaunch({ url: '/pages/login/login' })
          reject(new Error('登录已过期，请重新登录'))
          return
        }
        try {
          const data = JSON.parse(res.data)
          resolve(data)
        } catch (e) {
          reject(new Error('解析响应失败'))
        }
      },
      fail: (err) => {
        reject(err)
      }
    })
  })
}

export const authAPI = {
  register: (data) => request({ url: '/auth/register', method: 'POST', data }),
  login: (data) => request({ url: '/auth/login', method: 'POST', data }),
  getMe: () => request({ url: '/auth/me' }),
  logout: () => request({ url: '/auth/logout', method: 'POST' })
}

export const healthProfileAPI = {
  get: () => request({ url: '/health-profile/' }),
  create: (data) => request({ url: '/health-profile/', method: 'POST', data }),
  update: (data) => request({ url: '/health-profile/', method: 'POST', data }),
  delete: () => request({ url: '/health-profile/', method: 'DELETE' })
}

export const dietPreferencesAPI = {
  get: () => request({ url: '/diet-preferences/' }),
  create: (data) => request({ url: '/diet-preferences/', method: 'POST', data }),
  update: (data) => request({ url: '/diet-preferences/', method: 'POST', data }),
  delete: () => request({ url: '/diet-preferences/', method: 'DELETE' }),
  addAllergy: (allergy) => request({ url: `/diet-preferences/allergies?allergy=${encodeURIComponent(allergy)}`, method: 'POST' }),
  removeAllergy: (allergy) => request({ url: `/diet-preferences/allergies?allergy=${encodeURIComponent(allergy)}`, method: 'DELETE' }),
  addForbiddenFood: (food) => request({ url: `/diet-preferences/forbidden-foods?food=${encodeURIComponent(food)}`, method: 'POST' }),
  removeForbiddenFood: (food) => request({ url: `/diet-preferences/forbidden-foods?food=${encodeURIComponent(food)}`, method: 'DELETE' })
}

export const healthGoalsAPI = {
  list: () => request({ url: '/health-goals/' }),
  get: (id) => request({ url: `/health-goals/${id}` }),
  create: (data) => request({ url: '/health-goals/', method: 'POST', data }),
  update: (id, data) => request({ url: `/health-goals/${id}`, method: 'PUT', data }),
  delete: (id) => request({ url: `/health-goals/${id}`, method: 'DELETE' }),
  getProgress: () => request({ url: '/health-goals/progress/summary' })
}

export const chatAPI = {
  sendMessage: (message) => request({ url: '/chat/message', method: 'POST', data: { message } }),
  getHistory: (page = 1, pageSize = 20) => request({ url: `/chat/history?page=${page}&page_size=${pageSize}` }),
  getMessage: (id) => request({ url: `/chat/history/${id}` }),
  clearHistory: () => request({ url: '/chat/history', method: 'DELETE' }),
  getStats: () => request({ url: '/chat/stats' })
}

export const recipesAPI = {
  list: (params) => request({ url: '/recipes/', data: params }),
  getDetail: (id) => request({ url: `/recipes/${id}` }),
  getAIRecommendation: (mealType, availableIngredients) => {
    let url = `/recipes/recommend/ai?`
    if (mealType) url += `meal_type=${mealType}&`
    if (availableIngredients) url += `available_ingredients=${encodeURIComponent(availableIngredients)}`
    return request({ url })
  },
  recognizeIngredients: (filePath) => uploadFile({ url: '/recipes/recognize', filePath, name: 'image' }),
  recognizeIngredientsUrl: (imageUrl) => request({ url: `/recipes/recognize?image_url=${encodeURIComponent(imageUrl)}` }),
  getIngredientSubstitute: (ingredient) => request({ url: `/recipes/substitute?ingredient=${encodeURIComponent(ingredient)}` }),
  getSeasonalRecipes: (season) => request({ url: `/recipes/recommend/ai?season=${season}` }),
  getIngredients: (params) => request({ url: '/recipes/ingredients', data: params }),
  getIngredientDetail: (id) => request({ url: `/recipes/ingredients/${id}` })
}

export const knowledgeBaseAPI = {
  getStats: () => request({ url: '/knowledge-base/stats' }),
  getList: (contentType, page, pageSize) => request({ url: `/knowledge-base/?content_type=${contentType || ''}&page=${page}&page_size=${pageSize}` }),
  searchKnowledge: (query, contentType, topK) => request({ url: '/knowledge-base/search', method: 'POST', data: { query, content_type: contentType, top_k: topK } }),
  getTypes: () => request({ url: '/knowledge-base/types' })
}

export const knowledgeAPI = {
  list: (params) => request({ url: '/knowledge/', data: params }),
  getDetail: (id) => request({ url: `/knowledge/${id}` }),
  getCategories: () => request({ url: '/knowledge/categories' }),
  search: (keyword, page = 1, pageSize = 10) => request({ url: `/knowledge/search?keyword=${encodeURIComponent(keyword)}&page=${page}&page_size=${pageSize}` })
}

export default {
  request,
  uploadFile,
  getToken,
  setToken,
  removeToken,
  getUserInfo,
  setUserInfo,
  removeUserInfo,
  isAdmin,
  setAdmin,
  BASE_URL
}
