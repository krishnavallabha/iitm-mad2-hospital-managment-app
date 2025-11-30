<template>
  <div class="card card-soft">
    <div class="card-body">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h6 class="fw-bold mb-0">Appointment Schedule</h6>
        <span class="text-muted small">Week View</span>
      </div>
      <div class="scroll-horizontal mb-3">
        <div class="d-inline-flex gap-2">
          <button
            v-for="day in days"
            :key="day.label"
            class="btn btn-light rounded-pill px-3"
            :class="{ 'btn-primary text-white': day.isToday }"
          >
            <div class="small text-uppercase">{{ day.label }}</div>
            <div class="fw-bold">{{ day.date }}</div>
          </button>
        </div>
      </div>
      <div class="d-flex flex-column gap-3">
        <div
          v-for="slot in slots"
          :key="slot.time"
          class="d-flex align-items-center justify-content-between p-3 rounded-4 bg-light"
        >
          <div>
            <p class="mb-0 fw-semibold">{{ slot.time }}</p>
            <small class="text-muted">{{ slot.patient }}</small>
          </div>
          <span class="badge rounded-pill" :class="slot.badgeClass">{{ slot.type }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const days = [
  { label: 'Mon', date: '12', isToday: false },
  { label: 'Tue', date: '13', isToday: true },
  { label: 'Wed', date: '14', isToday: false },
  { label: 'Thu', date: '15', isToday: false },
  { label: 'Fri', date: '16', isToday: false },
  { label: 'Sat', date: '17', isToday: false },
  { label: 'Sun', date: '18', isToday: false }
];

const slots = [
  { time: '09:00 AM', patient: 'Anna Taylor', type: 'Consultation', badgeClass: 'bg-primary-subtle text-primary' },
  { time: '11:30 AM', patient: 'James Carter', type: 'Follow-up', badgeClass: 'bg-success-subtle text-success' }
];
</script>

