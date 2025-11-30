<template>
  <div class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.75) !important; backdrop-filter: blur(4px);">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content border-0 shadow-lg rounded-4">
        <div class="modal-header border-0 pb-0">
          <h5 class="modal-title fw-bold">Doctor Details</h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <div class="text-center mb-4">
            <div class="avatar-lg bg-primary-subtle text-primary rounded-circle d-flex align-items-center justify-content-center mx-auto mb-3" style="width: 80px; height: 80px; font-size: 2rem;">
              <i class="bi bi-person-fill"></i>
            </div>
            <h4 class="fw-bold mb-1">{{ doctor.full_name }}</h4>
            <p class="text-muted mb-0">{{ doctor.specialization }}</p>
          </div>
          
          <div class="card bg-light border-0 rounded-4 mb-4">
            <div class="card-body">
              <h6 class="fw-bold mb-3">Availability</h6>
              <div v-if="availability.length" class="d-flex flex-wrap gap-2">
                <div v-for="slot in availability" :key="slot.id" class="badge bg-white text-dark border p-2 rounded-3 fw-normal">
                  <i class="bi bi-calendar-event me-1 text-primary"></i>
                  {{ formatDate(slot.date) }}
                  <span class="text-muted mx-1">|</span>
                  {{ slot.start_time }} - {{ slot.end_time }}
                </div>
              </div>
              <p v-else class="text-muted small mb-0">No availability slots listed currently.</p>
            </div>
          </div>
          
          <div class="d-grid">
            <button class="btn btn-primary rounded-pill" @click="$emit('book', doctor)">
              Book Appointment
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../../services/api';

const props = defineProps({
  doctor: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['close', 'book']);
const availability = ref([]);

const fetchAvailability = async () => {
  try {
    const { data } = await api.get(`/patient/doctors/${props.doctor.id}`);
    availability.value = data.doctor.availability;
  } catch (error) {
    console.error('Failed to fetch doctor details', error);
  }
};

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric'
  });
};

onMounted(() => {
  fetchAvailability();
});
</script>
