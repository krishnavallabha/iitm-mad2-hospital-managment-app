<template>
  <div class="card card-soft text-center">
    <div class="card-body">
      <p class="text-muted text-uppercase small mb-2">Capacity Overview</p>
      <h4 class="fw-bold mb-4">SerenityCare</h4>
      <div class="gauge-wrapper mx-auto mb-4">
        <div class="gauge">
          <div class="gauge-fill" :style="{ transform: `rotate(${gaugeValue}deg)` }"></div>
          <div class="gauge-cover">
            <span class="fs-3 fw-bold">{{ occupancy }}%</span>
            <p class="text-muted small mb-0">Occupancy</p>
          </div>
        </div>
      </div>
      <p class="text-muted small mb-4">
        Live snapshot of bed utilization across SerenityCare departments.
      </p>
      <div class="d-grid gap-2">
        <button class="btn btn-primary rounded-pill">View Capacity</button>
        <button class="btn btn-outline-secondary rounded-pill">Update Status</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';

const occupancy = ref(72);
const gaugeValue = computed(() => (occupancy.value / 100) * 180);
</script>

<style scoped>
.gauge-wrapper {
  width: 220px;
  height: 110px;
}

.gauge {
  width: 100%;
  height: 100%;
  background: rgba(108, 99, 255, 0.1);
  border-radius: 110px 110px 0 0;
  position: relative;
  overflow: hidden;
}

.gauge-fill {
  position: absolute;
  top: 100%;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, var(--serenity-primary), var(--serenity-accent));
  transform-origin: center top;
  transition: transform 0.5s ease;
}

.gauge-cover {
  width: 180px;
  height: 90px;
  background: #fff;
  border-radius: 90px 90px 0 0;
  position: absolute;
  top: calc(100% - 90px);
  left: 50%;
  transform: translateX(-50%);
  box-shadow: inset 0 0 0 1px rgba(108, 99, 255, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
</style>

