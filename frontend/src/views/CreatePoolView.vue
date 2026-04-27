<template>
  <div class="max-w-md mx-auto mt-6">
    <div class="flex items-center mb-6">
      <router-link to="/" class="btn btn-secondary mr-4" style="padding: 0.25rem 0.5rem; margin-right: 1rem;">
        &larr; Back
      </router-link>
      <h2 style="margin: 0;">Schedule a Carpool</h2>
    </div>

    <div class="card">
      <div v-if="error" class="alert-error mb-4">
        {{ error }}
      </div>

      <form @submit.prevent="createPool">
        <h3 class="mb-4 border-b pb-2">Carpool Details</h3>
        <div class="form-group">
          <label class="form-label">Leaving From (Source)</label>
          <input type="text" v-model="form.source" class="form-control" required placeholder="e.g. SNU Campus">
        </div>

        <div class="form-group">
          <label class="form-label">Going To (Destination)</label>
          <input type="text" v-model="form.destination" class="form-control" required placeholder="e.g. Delhi Airport (T3)">
        </div>

        <div class="form-group">
          <label class="form-label">Departure Date & Time</label>
          <input type="datetime-local" v-model="form.departure_time" class="form-control" required :min="minDateTime">
        </div>

        <div class="form-group">
          <label class="form-label">Luggage Constraints (Optional)</label>
          <input type="text" v-model="form.luggage" class="form-control" placeholder="e.g. 1 medium bag per person">
        </div>

        <div class="form-group flex items-center mb-6">
          <input type="checkbox" id="open" v-model="form.open_to_pool" class="mr-2" style="margin-right: 0.5rem; width: 1rem; height: 1rem;">
          <label for="open" class="form-label" style="margin-bottom: 0;">Open to Pool (Allow others to join)</label>
        </div>

        <h3 class="mb-4 border-b pb-2 mt-6">Your Details</h3>
        <div class="form-group">
          <label class="form-label">Name</label>
          <input type="text" v-model="userForm.name" class="form-control" required>
        </div>
        <div class="form-group">
          <label class="form-label">Phone Number</label>
          <input type="tel" v-model="userForm.phone" class="form-control" required>
        </div>
        <div class="flex gap-4 mb-6">
          <div class="form-group flex-1" style="margin-bottom: 0;">
            <label class="form-label">Year of Study</label>
            <select v-model="userForm.year" class="form-control" required>
              <option value="" disabled>Select Year</option>
              <option value="1st Year">1st Year</option>
              <option value="2nd Year">2nd Year</option>
              <option value="3rd Year">3rd Year</option>
              <option value="4th Year">4th Year</option>
              <option value="PG/PhD">PG/PhD</option>
              <option value="Faculty/Staff">Faculty/Staff</option>
            </select>
          </div>
          <div class="form-group flex-1" style="margin-bottom: 0;">
            <label class="form-label">Major/Department</label>
            <input type="text" v-model="userForm.department" class="form-control" required placeholder="e.g. CSE">
          </div>
        </div>

        <button type="submit" class="btn btn-primary btn-block" :disabled="loading">
          <span v-if="loading">Scheduling...</span>
          <span v-else>Schedule Carpool</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const loading = ref(false)
const error = ref('')

const form = ref({
  source: '',
  destination: '',
  departure_time: '',
  luggage: '',
  open_to_pool: true
})

const userForm = ref({
  name: '',
  phone: '',
  year: '',
  department: ''
})

let API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
if (!API_URL.endsWith('/api') && !API_URL.endsWith('/api/')) {
  API_URL = API_URL.replace(/\/$/, '') + '/api'
}
API_URL = API_URL.replace(/\/$/, '')

// Set min datetime to current time
const minDateTime = computed(() => {
  const now = new Date()
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset())
  return now.toISOString().slice(0, 16)
})

onMounted(() => {
  const savedUser = localStorage.getItem('snu_pool_user')
  if (savedUser) {
    try {
      userForm.value = JSON.parse(savedUser)
    } catch(e) {}
  }
})

const createPool = async () => {
  loading.value = true
  error.value = ''
  
  try {
    // Save user details for next time
    localStorage.setItem('snu_pool_user', JSON.stringify(userForm.value))
    
    const payload = {
      ...form.value,
      departure_time: new Date(form.value.departure_time).toISOString(),
      user: userForm.value
    }
    
    const res = await axios.post(`${API_URL}/pools/`, payload)
    router.push(`/pools/${res.data.id}`)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to create pool.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.max-w-md { max-width: 32rem; }
.mx-auto { margin-left: auto; margin-right: auto; }
.mb-4 { margin-bottom: 1rem; }
.mt-6 { margin-top: 1.5rem; }
.gap-4 { gap: 1rem; }
.flex-1 { flex: 1; }
.border-b { border-bottom: 2px solid var(--border-color); }
.pb-2 { padding-bottom: 0.5rem; }
.alert-error {
  background-color: #fef2f2;
  color: var(--error-color);
  padding: 0.75rem;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  border: 1px solid #fecaca;
}
</style>
