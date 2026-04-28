<template>
  <div class="max-w-md mx-auto mt-10">
    <div class="card">
      <div class="text-center mb-6">
        <h2>Complete Your Profile</h2>
        <p>We need a few more details before you can join or create pools.</p>
      </div>

      <div v-if="error" class="alert-error mb-4">
        {{ error }}
      </div>

      <form @submit.prevent="saveProfile">
        <div class="form-group">
          <label class="form-label">Full Name</label>
          <input type="text" v-model="profile.name" class="form-control" required
            pattern="[a-zA-Z\s]+" title="Name should only contain letters and spaces">
        </div>

        <div class="form-group">
          <label class="form-label">Phone Number</label>
          <input type="tel" v-model="profile.phone" class="form-control" required placeholder="e.g. 9876543210"
            pattern="\d{10}" maxlength="10" title="Phone number must be exactly 10 digits">
        </div>

        <div class="form-group">
          <label class="form-label">Year of Study</label>
          <select v-model="profile.year" class="form-control" required>
            <option value="" disabled>Select Year</option>
            <option value="1st Year">1st Year</option>
            <option value="2nd Year">2nd Year</option>
            <option value="3rd Year">3rd Year</option>
            <option value="4th Year">4th Year</option>
            <option value="PG/PhD">PG / PhD</option>
            <option value="Faculty/Staff">Faculty / Staff</option>
          </select>
        </div>

        <div class="form-group mb-6">
          <label class="form-label">Department / Major</label>
          <input type="text" v-model="profile.department" class="form-control" required placeholder="e.g. Computer Science"
            pattern="[a-zA-Z\s]+" title="Department should only contain letters and spaces">
        </div>

        <button type="submit" class="btn btn-primary btn-block" :disabled="loading">
          <span v-if="loading">Saving...</span>
          <span v-else>Save Profile & Continue</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const loading = ref(false)
const error = ref('')

const profile = ref({
  name: '',
  phone: '',
  year: '',
  department: ''
})

const API_URL = 'http://localhost:8000/api'

const saveProfile = async () => {
  loading.value = true
  error.value = ''
  
  // Validation
  const nameRegex = /^[a-zA-Z\s]+$/
  const phoneRegex = /^\d{10}$/
  const deptRegex = /^[a-zA-Z\s]+$/

  if (!nameRegex.test(profile.value.name)) {
    error.value = 'Name should only contain letters and spaces.'
    loading.value = false
    return
  }
  if (!phoneRegex.test(profile.value.phone)) {
    error.value = 'Phone number must be exactly 10 digits.'
    loading.value = false
    return
  }
  if (!deptRegex.test(profile.value.department)) {
    error.value = 'Department should only contain letters and spaces.'
    loading.value = false
    return
  }
  
  try {
    const token = localStorage.getItem('token')
    await axios.put(`${API_URL}/users/me`, profile.value, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    localStorage.setItem('isProfileComplete', 'true')
    router.push('/')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to update profile. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.max-w-md { max-width: 28rem; }
.mx-auto { margin-left: auto; margin-right: auto; }
.mt-10 { margin-top: 2.5rem; }
.mb-4 { margin-bottom: 1rem; }
.alert-error {
  background-color: #fef2f2;
  color: var(--error-color);
  padding: 0.75rem;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  border: 1px solid #fecaca;
}
</style>
