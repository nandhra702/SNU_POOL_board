<template>
  <div class="dashboard">
    <div class="flex justify-between items-center mb-6 mt-6">
      <h2>Calendar Board</h2>
      <router-link to="/create-pool" class="btn btn-primary">
        + New Pool
      </router-link>
    </div>

    <!-- Filters -->
    <div class="card mb-6 filters-card">
      <div class="filter-grid">
        <div class="form-group" style="margin-bottom: 0;">
          <label class="form-label">Source</label>
          <input type="text" v-model="filters.source" class="form-control" placeholder="Leaving from...">
        </div>
        <div class="form-group" style="margin-bottom: 0;">
          <label class="form-label">Destination</label>
          <input type="text" v-model="filters.destination" class="form-control" placeholder="Going to...">
        </div>
        <div class="flex items-end">
          <button @click="fetchPools" class="btn btn-secondary btn-block">Filter</button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-center mt-10">
      <p>Loading calendar...</p>
    </div>

    <div v-else-if="pools.length === 0" class="card text-center mt-10 empty-state">
      <div class="empty-icon">📅</div>
      <h3>No carpools scheduled</h3>
      <p>There are no active carpools matching your criteria.</p>
      <button @click="resetFilters" class="btn btn-secondary mt-4" v-if="filters.source || filters.destination">
        Clear Filters
      </button>
      <router-link to="/create-pool" class="btn btn-primary mt-4" v-else>
        Schedule the first carpool
      </router-link>
    </div>

    <div v-else class="calendar-view">
      <div v-for="(group, dateStr) in groupedPools" :key="dateStr" class="date-group mb-8">
        <h3 class="date-header mb-4 text-accent border-b pb-2">{{ dateStr }}</h3>
        <div class="pools-grid">
          <router-link 
            v-for="pool in group" 
            :key="pool.id" 
            :to="`/pools/${pool.id}`"
            style="text-decoration: none; color: inherit;"
          >
            <PoolCard :pool="pool" />
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import PoolCard from '../components/PoolCard.vue'

const pools = ref([])
const loading = ref(true)
const filters = ref({
  source: '',
  destination: ''
})

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const groupedPools = computed(() => {
  const groups = {}
  pools.value.forEach(pool => {
    const d = new Date(pool.departure_time)
    const dateStr = d.toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })
    if (!groups[dateStr]) groups[dateStr] = []
    groups[dateStr].push(pool)
  })
  return groups
})

const fetchPools = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (filters.value.source) params.append('source', filters.value.source)
    if (filters.value.destination) params.append('destination', filters.value.destination)
    
    const res = await axios.get(`${API_URL}/pools/?${params.toString()}`)
    pools.value = res.data
  } catch (error) {
    console.error("Failed to fetch pools:", error)
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.value.source = ''
  filters.value.destination = ''
  fetchPools()
}

onMounted(() => {
  fetchPools()
})
</script>

<style scoped>
.filter-grid {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 1rem;
  align-items: flex-end;
}

@media (max-width: 640px) {
  .filter-grid {
    grid-template-columns: 1fr;
  }
}

.pools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.date-header {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--accent-color);
  border-bottom: 2px solid var(--border-color);
  padding-bottom: 0.5rem;
}

.empty-state {
  padding: 4rem 2rem;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}
</style>
