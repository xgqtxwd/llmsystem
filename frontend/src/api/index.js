import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
  refresh: () => api.post('/auth/refresh'),
  logout: () => api.post('/auth/logout')
}

export const healthProfileAPI = {
  get: () => api.get('/health-profile/'),
  create: (data) => api.post('/health-profile/', data),
  update: (data) => api.post('/health-profile/', data),
  delete: () => api.delete('/health-profile/')
}

export const dietPreferencesAPI = {
  get: () => api.get('/diet-preferences/'),
  create: (data) => api.post('/diet-preferences/', data),
  update: (data) => api.post('/diet-preferences/', data),
  delete: () => api.delete('/diet-preferences/'),
  addAllergy: (allergy) => api.post(`/diet-preferences/allergies?allergy=${encodeURIComponent(allergy)}`),
  removeAllergy: (allergy) => api.delete(`/diet-preferences/allergies?allergy=${encodeURIComponent(allergy)}`),
  addForbiddenFood: (food) => api.post(`/diet-preferences/forbidden-foods?food=${encodeURIComponent(food)}`),
  removeForbiddenFood: (food) => api.delete(`/diet-preferences/forbidden-foods?food=${encodeURIComponent(food)}`)
}

export const healthGoalsAPI = {
  list: () => api.get('/health-goals/'),
  get: (id) => api.get(`/health-goals/${id}`),
  create: (data) => api.post('/health-goals/', data),
  update: (id, data) => api.put(`/health-goals/${id}`, data),
  delete: (id) => api.delete(`/health-goals/${id}`),
  getProgress: () => api.get('/health-goals/progress/summary')
}

export const chatAPI = {
  sendMessage: (message) => api.post('/chat/message', { message }),
  getHistory: (page = 1, pageSize = 20) => api.get(`/chat/history?page=${page}&page_size=${pageSize}`),
  getMessage: (id) => api.get(`/chat/history/${id}`),
  clearHistory: () => api.delete('/chat/history'),
  getStats: () => api.get('/chat/stats')
}

export const recipesAPI = {
  list: (params) => api.get('/recipes/', { params }),
  getDetail: (id) => api.get(`/recipes/${id}`),
  getAIRecommendation: (mealType, availableIngredients) => {
    let url = `/recipes/recommend/ai?`
    if (mealType) url += `meal_type=${mealType}&`
    if (availableIngredients) url += `available_ingredients=${encodeURIComponent(availableIngredients)}`
    return api.get(url)
  },
  recognizeIngredients: (formData) => api.post('/recipes/recognize', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  recognizeIngredientsUrl: (imageUrl) => api.get(`/recipes/recognize?image_url=${encodeURIComponent(imageUrl)}`),
  getIngredientSubstitute: (ingredient) => api.get(`/recipes/substitute?ingredient=${encodeURIComponent(ingredient)}`),
  getSeasonalRecipes: (season) => api.get(`/recipes/recommend/ai?season=${season}`),
  getIngredients: (params) => api.get('/recipes/ingredients', { params }),
  getIngredientDetail: (id) => api.get(`/recipes/ingredients/${id}`)
}

export const knowledgeBaseAPI = {
  getStats: () => api.get('/knowledge-base/stats'),
  getList: (contentType, page, pageSize) => api.get(`/knowledge-base/?content_type=${contentType || ''}&page=${page}&page_size=${pageSize}`),
  addKnowledge: (data) => api.post('/knowledge-base/', data),
  deleteKnowledge: (id) => api.delete(`/knowledge-base/${id}`),
  searchKnowledge: (query, contentType, topK) => api.post('/knowledge-base/search', { query, content_type: contentType, top_k: topK }),
  getTypes: () => api.get('/knowledge-base/types'),
  batchAdd: (list) => api.post('/knowledge-base/batch-add', list)
}

export const knowledgeAPI = {
  list: (params) => api.get('/knowledge/', { params }),
  getDetail: (id) => api.get(`/knowledge/${id}`),
  getCategories: () => api.get('/knowledge/categories'),
  search: (keyword, page = 1, pageSize = 10) => api.get(`/knowledge/search?keyword=${encodeURIComponent(keyword)}&page=${page}&page_size=${pageSize}`)
}

export const adminAPI = {
  getUsers: (page = 1, pageSize = 20) => api.get(`/admin/users?page=${page}&page_size=${pageSize}`),
  getUserDetail: (userId) => api.get(`/admin/users/${userId}`),
  updateUserRole: (userId, isAdmin) => api.put(`/admin/users/${userId}/role`, { is_admin: isAdmin }),
  deleteUser: (userId) => api.delete(`/admin/users/${userId}`),

  getOverviewStats: () => api.get('/admin/stats/overview'),
  getActivityStats: () => api.get('/admin/stats/activity'),
  getBehaviorAnalysis: () => api.get('/admin/stats/behavior'),

  getFeedbacks: (page = 1, pageSize = 20) => api.get(`/admin/feedbacks?page=${page}&page_size=${pageSize}`),
  processFeedback: (feedbackId, status, response) => api.post(`/admin/feedbacks/${feedbackId}/process`, { status, response }),

  getLLMSettings: () => api.get('/admin/settings/llm'),
  updateLLMSettings: (settings) => api.put('/admin/settings/llm', settings),
  getEmbeddingSettings: () => api.get('/admin/settings/embedding'),
  updateEmbeddingSettings: (settings) => api.put('/admin/settings/embedding', settings),

  getLogs: (page = 1, pageSize = 50, level = null) => api.get(`/admin/logs?page=${page}&page_size=${pageSize}${level ? '&level=' + level : ''}`),

  getParseOptions: () => api.get('/admin/document/parse-options'),
  getKnowledgeStats: () => api.get('/knowledge-base/stats'),
  uploadDocument: (formData) => api.post('/admin/document/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 300000
  }),
  getDocumentTaskStatus: (taskId) => api.get(`/admin/document/task/${taskId}`),
  getDocumentTasks: () => api.get('/admin/document/tasks')
}

export default api
