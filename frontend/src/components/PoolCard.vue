<template>
  <div class="card pool-card hover-lift">
    <div class="pool-header flex justify-between items-center mb-4">
      <div class="date-badge">
        <span class="day">{{ formattedDay }}</span>
        <span class="month">{{ formattedMonth }}</span>
      </div>
      <div class="time">{{ formattedTime }}</div>
    </div>
    
    <div class="route flex items-center mb-4">
      <div class="route-point">
        <div class="dot source-dot"></div>
        <div class="point-name">{{ pool.source }}</div>
      </div>
      <div class="route-line"></div>
      <div class="route-point">
        <div class="dot dest-dot"></div>
        <div class="point-name">{{ pool.destination }}</div>
      </div>
    </div>

    <div class="pool-footer flex justify-between items-center">
      <div class="people-count flex items-center gap-2">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-secondary">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
          <circle cx="9" cy="7" r="4"></circle>
          <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
          <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
        </svg>
        <span class="text-sm">{{ pool.people_count }} joined</span>
      </div>
      <div class="luggage" v-if="pool.luggage">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-secondary">
          <path d="M20 16V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v10"></path>
          <path d="M4 16h16v4a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-4z"></path>
          <path d="M10 22v-6"></path>
          <path d="M14 22v-6"></path>
          <path d="M9 4v2"></path>
          <path d="M15 4v2"></path>
        </svg>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  pool: {
    type: Object,
    required: true
  }
})

const dateObj = computed(() => new Date(props.pool.departure_time))

const formattedDay = computed(() => {
  return dateObj.value.getDate()
})

const formattedMonth = computed(() => {
  return dateObj.value.toLocaleString('default', { month: 'short' })
})

const formattedTime = computed(() => {
  return dateObj.value.toLocaleString('default', { hour: 'numeric', minute: '2-digit', hour12: true })
})
</script>

<style scoped>
.pool-card {
  cursor: pointer;
  padding: 1.25rem;
}

.hover-lift {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.hover-lift:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}

.date-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #eff6ff;
  color: var(--accent-color);
  border-radius: var(--radius-md);
  padding: 0.25rem 0.75rem;
  min-width: 3.5rem;
}

.date-badge .day {
  font-weight: 700;
  font-size: 1.125rem;
  line-height: 1;
}

.date-badge .month {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.time {
  font-weight: 600;
  color: var(--text-primary);
}

.route {
  position: relative;
}

.route-point {
  flex: 1;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-bottom: 0.5rem;
  position: relative;
  z-index: 2;
  background-color: var(--surface-color);
  border: 2px solid;
}

.source-dot {
  border-color: var(--success-color);
}

.dest-dot {
  border-color: var(--accent-color);
}

.route-line {
  position: absolute;
  top: 5px;
  left: 6px;
  right: calc(50% + 6px);
  height: 2px;
  background-color: var(--border-color);
  z-index: 1;
}

.point-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.route-point:last-child {
  text-align: right;
}

.route-point:last-child .dot {
  margin-left: auto;
}

.route-point:last-child .point-name {
  text-align: right;
}

.text-secondary { color: var(--text-secondary); }
.text-sm { font-size: 0.875rem; }
.gap-2 { gap: 0.5rem; }
</style>
