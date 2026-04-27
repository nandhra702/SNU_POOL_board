<template>
  <div class="login-container">
    <div class="card login-card">
      <div class="text-center mb-6">
        <div class="logo justify-center" style="margin-bottom: 1rem; font-size: 1.5rem;">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2"/>
            <circle cx="7" cy="17" r="2"/>
            <path d="M9 17h6"/>
            <circle cx="17" cy="17" r="2"/>
          </svg>
          SNU Pool
        </div>
        <h2>Welcome Back</h2>
        <p>Sign in with your @snu.edu.in email</p>
      </div>

      <div v-if="error" class="alert-error">
        {{ error }}
      </div>

      <form @submit.prevent="step === 1 ? requestOTP() : verifyOTP()">
        <div class="form-group">
          <label class="form-label">Email Address</label>
          <input 
            type="email" 
            v-model="email" 
            class="form-control" 
            placeholder="netid@snu.edu.in" 
            :disabled="step === 2"
            required
          >
        </div>

        <div class="form-group" v-if="step === 2">
          <label class="form-label">One-Time Password (OTP)</label>
          <input 
            type="text" 
            v-model="otp" 
            class="form-control text-center" 
            placeholder="123456" 
            style="letter-spacing: 0.5em; font-size: 1.25rem;"
            required
          >
          <p class="text-sm mt-2" style="font-size: 0.75rem; text-align: center;">
            Check your backend console logs for the OTP.
          </p>
        </div>

        <button type="submit" class="btn btn-primary btn-block" :disabled="loading">
          <span v-if="loading">Processing...</span>
          <span v-else-if="step === 1">Send OTP</span>
          <span v-else>Verify & Sign In</span>
        </button>
      </form>
      
      <div v-if="step === 2" class="text-center mt-4">
        <button @click="step = 1; error = ''" class="btn btn-secondary text-sm" style="border: none;">
          Use a different email
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const email = ref('')
const otp = ref('')
const step = ref(1)
const loading = ref(false)
const error = ref('')

const API_URL = 'http://localhost:8000/api'

const requestOTP = async () => {
  if (!email.value.endsWith('@snu.edu.in')) {
    error.value = 'Please use a valid @snu.edu.in email address.'
    return
  }

  loading.value = true
  error.value = ''

  try {
    await axios.post(`${API_URL}/auth/request-otp`, { email: email.value })
    step.value = 2
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to request OTP. Please try again.'
  } finally {
    loading.value = false
  }
}

const verifyOTP = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await axios.post(`${API_URL}/auth/verify-otp`, { 
      email: email.value,
      otp: otp.value 
    })
    
    const token = response.data.access_token
    localStorage.setItem('token', token)
    
    // Check if profile is complete
    const profileRes = await axios.get(`${API_URL}/users/me`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    localStorage.setItem('isProfileComplete', profileRes.data.is_profile_complete)
    
    if (profileRes.data.is_profile_complete) {
      router.push('/')
    } else {
      router.push('/profile-setup')
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Invalid OTP. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 80vh;
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: 2.5rem 2rem;
}

.alert-error {
  background-color: #fef2f2;
  color: var(--error-color);
  padding: 0.75rem;
  border-radius: var(--radius-md);
  margin-bottom: 1rem;
  font-size: 0.875rem;
  border: 1px solid #fecaca;
}
</style>
