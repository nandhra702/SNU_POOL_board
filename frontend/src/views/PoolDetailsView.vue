<template>
  <div class="max-w-lg mx-auto mt-6 pb-10">
    <div class="flex items-center mb-6">
      <router-link to="/" class="btn btn-secondary mr-4" style="padding: 0.25rem 0.5rem; margin-right: 1rem;">
        &larr; Back
      </router-link>
      <h2 style="margin: 0;">Carpool Details</h2>
    </div>

    <div v-if="loading" class="text-center mt-10">
      <p>Loading details...</p>
    </div>
    
    <div v-else-if="error" class="card text-center mt-10">
      <p class="text-error">{{ error }}</p>
      <router-link to="/" class="btn btn-secondary mt-4">Return to Board</router-link>
    </div>

    <div v-else class="pool-details">
      <!-- Main Info Card -->
      <div class="card mb-6 header-card">
        <div class="route-display flex flex-col gap-4">
          <div class="route-item flex items-start gap-4">
            <div class="dot source-dot mt-1"></div>
            <div>
              <p class="text-sm text-secondary mb-0">Leaving from</p>
              <h3>{{ pool.source }}</h3>
            </div>
          </div>
          
          <div class="route-divider"></div>
          
          <div class="route-item flex items-start gap-4">
            <div class="dot dest-dot mt-1"></div>
            <div>
              <p class="text-sm text-secondary mb-0">Going to</p>
              <h3>{{ pool.destination }}</h3>
            </div>
          </div>
        </div>
        
        <hr class="my-6" />
        
        <div class="info-grid">
          <div class="info-item">
            <span class="text-secondary text-sm block">Departure</span>
            <span class="font-medium">{{ formattedDate }} at {{ formattedTime }}</span>
          </div>
          <div class="info-item">
            <span class="text-secondary text-sm block">Luggage</span>
            <span class="font-medium">{{ pool.luggage || 'No specific limit' }}</span>
          </div>
          <div class="info-item">
            <span class="text-secondary text-sm block">Status</span>
            <span class="badge" :class="pool.open_to_pool ? 'badge-success' : 'badge-warning'">
              {{ pool.open_to_pool ? 'Open to join' : 'Closed' }}
            </span>
          </div>
          <div class="info-item">
            <span class="text-secondary text-sm block">Joined</span>
            <span class="font-medium">{{ pool.people_count }} people</span>
          </div>
        </div>
      </div>

      <!-- Participants Area -->
      <div class="card mb-6">
        <h4 class="mb-4 border-b pb-2">Participants ({{ pool.participants?.length || 0 }})</h4>
        
        <div class="participants-list flex flex-col gap-3">
          <div v-for="(p, i) in pool.participants" :key="i" class="participant-item flex justify-between items-center p-3">
            <div class="flex items-center gap-3">
              <div class="avatar">{{ p.name ? p.name.charAt(0).toUpperCase() : '?' }}</div>
              <div>
                <span class="font-medium block">{{ p.name || 'Unknown' }}</span>
                <span class="text-sm text-secondary">{{ p.department }} &middot; {{ p.year }}</span>
              </div>
            </div>
            <a :href="`tel:${p.phone}`" class="btn btn-secondary btn-sm" v-if="p.phone">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 4px;">
                <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
              </svg>
              Call
            </a>
          </div>
        </div>
      </div>

      <!-- Join Action Area -->
      <div class="card mb-6 action-card" v-if="!hasJoined && pool.open_to_pool && !isPast">
        <h3 class="mb-4">Join this Carpool</h3>
        <form @submit.prevent="joinPool">
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
          <button type="submit" class="btn btn-primary btn-block btn-lg" :disabled="joining">
            <span v-if="joining">Joining...</span>
            <span v-else>Join Carpool</span>
          </button>
          <p v-if="joinError" class="text-error text-sm mt-4">{{ joinError }}</p>
        </form>
      </div>
      
      <div v-else-if="hasJoined" class="card text-center mb-6 bg-success-light">
        <div class="success-icon mx-auto mb-2" style="margin-left: auto; margin-right: auto;">✓</div>
        <h3>You are in this carpool</h3>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const pool = ref({})
const loading = ref(true)
const error = ref('')
const joining = ref(false)
const joinError = ref('')

const userForm = ref({
  name: '',
  phone: '',
  year: '',
  department: ''
})

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const fetchPoolDetails = async () => {
  loading.value = true
  try {
    const res = await axios.get(`${API_URL}/pools/${route.params.id}`)
    pool.value = res.data
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load pool details.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  const savedUser = localStorage.getItem('snu_pool_user')
  if (savedUser) {
    try {
      userForm.value = JSON.parse(savedUser)
    } catch(e) {}
  }
  fetchPoolDetails()
})

const hasJoined = computed(() => {
  if (!pool.value.participants || !userForm.value.phone) return false
  return pool.value.participants.some(p => p.phone === userForm.value.phone)
})

const joinPool = async () => {
  joining.value = true
  joinError.value = ''
  
  try {
    localStorage.setItem('snu_pool_user', JSON.stringify(userForm.value))
    await axios.post(`${API_URL}/pools/${route.params.id}/join`, { user: userForm.value })
    await fetchPoolDetails()
  } catch (err) {
    joinError.value = err.response?.data?.detail || 'Failed to join pool.'
  } finally {
    joining.value = false
  }
}

const dateObj = computed(() => new Date(pool.value.departure_time))
const isPast = computed(() => dateObj.value < new Date())

const formattedDate = computed(() => {
  if (!pool.value.departure_time) return ''
  return dateObj.value.toLocaleDateString('default', { 
    weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' 
  })
})

const formattedTime = computed(() => {
  if (!pool.value.departure_time) return ''
  return dateObj.value.toLocaleTimeString('default', { 
    hour: 'numeric', minute: '2-digit', hour12: true 
  })
})
</script>

<style scoped>
.max-w-lg { max-width: 42rem; }
.mx-auto { margin-left: auto; margin-right: auto; }
.mt-6 { margin-top: 1.5rem; }
.pb-10 { padding-bottom: 2.5rem; }
.mb-6 { margin-bottom: 1.5rem; }
.mb-0 { margin-bottom: 0; }
.my-6 { margin-top: 1.5rem; margin-bottom: 1.5rem; border-color: var(--border-color); opacity: 0.5; }
.my-4 { margin-top: 1rem; margin-bottom: 1rem; border-color: var(--border-color); opacity: 0.5; }
.p-3 { padding: 0.75rem; }
.block { display: block; }
.font-medium { font-weight: 500; }
.gap-4 { gap: 1rem; }
.flex-1 { flex: 1; }
.border-b { border-bottom: 2px solid var(--border-color); }
.pb-2 { padding-bottom: 0.5rem; }

.text-error { color: var(--error-color); }
.text-secondary { color: var(--text-secondary); }
.text-sm { font-size: 0.875rem; }

.header-card {
  border-top: 4px solid var(--accent-color);
}

.route-item .dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background-color: var(--surface-color);
  border: 3px solid;
  margin-top: 4px;
}

.source-dot { border-color: var(--success-color); }
.dest-dot { border-color: var(--accent-color); }

.route-divider {
  height: 24px;
  border-left: 2px dashed var(--border-color);
  margin-left: 6px;
  margin-top: -8px;
  margin-bottom: -8px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  line-height: 1;
}

.badge-success { background-color: #d1fae5; color: #065f46; }
.badge-warning { background-color: #fef3c7; color: #92400e; }

.btn-lg {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
}

.success-icon {
  width: 32px;
  height: 32px;
  background-color: var(--success-color);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}
.bg-success-light {
  background-color: #ecfdf5;
  border: 1px solid #a7f3d0;
}

.participant-item {
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  background-color: var(--bg-color);
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: var(--accent-color);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1.125rem;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  display: inline-flex;
  align-items: center;
}
</style>
